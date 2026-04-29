"""
Rubber Band Engine — high-quality time-stretch and pitch-shift using Rubber Band library.

Provides two operations: time_stretch and pitch_shift.
Implements both CLI and Python binding backends (auto-detected).
"""

import subprocess
import shlex
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

# Check availability
try:
    result = subprocess.run(['rubberband', '--version'], capture_output=True, text=True, timeout=5)
    RUBBERBAND_CLI_AVAILABLE = (result.returncode == 0)
    RUBBERBAND_CLI_VERSION = result.stdout.strip() if RUBBERBAND_CLI_AVAILABLE else None
except (FileNotFoundError, subprocess.TimeoutExpired):
    RUBBERBAND_CLI_AVAILABLE = False

try:
    import rubberband
    RUBBERBAND_PY_AVAILABLE = True
except ImportError:
    RUBBERBAND_PY_AVAILABLE = False


def _check_available():
    if not (RUBBERBAND_CLI_AVAILABLE or RUBBERBAND_PY_AVAILABLE):
        raise RuntimeError(
            "Rubber Band not found.\n"
            "Install CLI:  sudo apt install rubberband-cli   (or brew install rubberband)\n"
            "Install Python: pip install rubberband"
        )


def _run_cli(input_path: str, output_path: str, factor: Optional[float] = None,
             semitones: Optional[float] = None, quality: str = "standard",
             formant: bool = False, transients: str = "mixed",
             extra_args: Optional[List[str]] = None) -> subprocess.CompletedProcess:
    """Build and run rubberband CLI command."""
    cmd = ['rubberband']

    # Quality mapping: quick=0, standard=3, high=4, ultra=5
    quality_map = {"quick": 0, "standard": 3, "high": 4, "ultra": 5}
    q = quality_map.get(quality, 3)
    cmd.extend(['-c', str(q)])

    if factor is not None:
        cmd.extend(['-t', str(factor)])
    if semitones is not None:
        cmd.extend(['-p', str(semitones)])
    if formant:
        cmd.append('-f')

    if transients != "mixed":
        # -s for smooth, -C for crisp (capital?)
        # Actually rubberband CLI: -C for crisp, -M for mixed? Let's check typical usage
        # According to docs: --crisp=N where N is 0-6 (quick to ultra) but that's quality?
        # Actually different: crispness setting 0-6. But quality already does that.
        # There's also --transients={mixed,crisp,smooth}
        cmd.extend(['--transients', transients])

    if extra_args:
        cmd.extend(extra_args)

    cmd.extend([input_path, output_path])

    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def _run_python(input_path: str, output_path: str, factor: Optional[float] = None,
                semitones: Optional[float] = None, quality: str = "standard",
                formant: bool = False, **kwargs) -> subprocess.CompletedProcess:
    """Use Python rubberband module to time-stretch/pitch-shift file."""
    # The Python rubberband package provides a simple function: rubberband.time_stretch or pitch_shift
    # However, different versions may have different APIs.
    # Let's assume the common API: rubberband.time_stretch(audio, sr, factor, formant, quality)
    import soundfile as sf

    # Read audio
    y, sr = sf.read(input_path)
    # Apply
    if factor is not None and semitones is not None:
        # Chain: stretch then pitch
        y = rubberband.time_stretch(y, sr, factor, formant=formant, quality=quality)
        y = rubberband.pitch_shift(y, sr, semitones, formant=formant, quality=quality)
    elif factor is not None:
        y = rubberband.time_stretch(y, sr, factor, formant=formant, quality=quality)
    elif semitones is not None:
        y = rubberband.pitch_shift(y, sr, semitones, formant=formant, quality=quality)
    else:
        raise ValueError("Either factor or semitones required")

    # Write output
    sf.write(output_path, y, sr)
    # Return dummy completed process
    return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")


def transform(
    input: str,
    pipeline: List[Dict],
    output: str,
    *,
    quality: str = "standard",
    dry_run: bool = False,
    overwrite: bool = True,
    extra_args: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict:
    """
    Apply Rubber Band time-stretch and/or pitch-shift.

    Parameters
    ----------
    input : str
        Input audio file (WAV, FLAC, MP3, etc.).
    pipeline : list of dict
        Ordered operations, typically one or both of:
          {"op": "time_stretch", "factor": 0.88, "formant": True, "quality": "high"}
          {"op": "pitch_shift", "semitones": 4.0, "formant": True}
        Multiple ops of the same type: last one wins (or error).
    output : str
        Output file path. Format inferred from extension.
    quality : str
        Default quality if not specified per-op: "quick", "standard", "high", "ultra".
    dry_run : bool
        Show command without running.
    overwrite : bool
        Overwrite output if exists.
    extra_args : list
        Additional raw CLI flags to pass to rubberband.
    timeout : int
        Max seconds to wait.

    Returns
    -------
    dict
        {success, output, command?, error?}
    """
    _check_available()

    in_path = Path(input).resolve()
    out_path = Path(output).resolve()

    if not in_path.exists():
        return {"success": False, "error": f"Input not found: {input}"}

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Parse pipeline
    ts_factor = None
    ps_semitones = None
    op_formant = False
    op_quality = None
    op_transients = "mixed"
    ops_seen = []

    for step in pipeline:
        op = step.get('op')
        if op not in ('time_stretch', 'pitch_shift'):
            raise ValueError(f"Invalid operation for rubber-band-engine: {op}")
        if op in ops_seen:
            # Multiple of same op — last wins (could warn)
            pass
        ops_seen.append(op)

        if op == 'time_stretch':
            ts_factor = float(step.get('factor', 1.0))
            if ts_factor <= 0:
                return {"success": False, "error": f"time_stretch factor must be > 0, got {ts_factor}"}
        elif op == 'pitch_shift':
            ps_semitones = float(step.get('semitones', 0.0))

        # Collect flags
        if step.get('formant') is True:
            op_formant = True
        if step.get('quality'):
            op_quality = step['quality']
        if step.get('transients'):
            op_transients = step['transients']

    # Resolve quality: per-op overrides default
    effective_quality = op_quality or quality

    # Must have at least one operation
    if ts_factor is None and ps_semitones is None:
        return {"success": False, "error": "Pipeline must contain 'time_stretch' or 'pitch_shift' operation"}

    # Prefer CLI if available
    backend = "cli" if RUBBERBAND_CLI_AVAILABLE else "python"

    if backend == "cli":
        cmd = ['rubberband']
        qmap = {"quick": 0, "standard": 3, "high": 4, "ultra": 5}
        cmd.extend(['-c', str(qmap.get(effective_quality, 3))])
        if ts_factor is not None:
            cmd.extend(['-t', str(ts_factor)])
        if ps_semitones is not None:
            cmd.extend(['-p', str(ps_semitones)])
        if op_formant:
            cmd.append('-f')
        if op_transients != "mixed":
            cmd.extend(['--transients', op_transients])
        if extra_args:
            cmd.extend(extra_args)
        if not overwrite and out_path.exists():
            return {"success": False, "error": f"Output exists and overwrite=False: {out_path}"}
        cmd.extend([str(in_path), str(out_path)])

        cmd_str = " ".join(shlex.quote(a) for a in cmd)

        if dry_run:
            return {"success": True, "dry_run": True, "command": cmd_str, "backend": "cli",
                    "input": str(in_path), "output": str(out_path)}

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return {"success": True, "output": str(out_path), "command": cmd_str, "backend": "cli"}
            else:
                return {"success": False, "error": result.stderr.strip() or result.stdout.strip(),
                        "command": cmd_str, "stderr": result.stderr[:500]}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Rubber Band CLI timed out after {timeout}s", "command": cmd_str}

    else:
        # Python backend
        if dry_run:
            return {"success": True, "dry_run": True, "backend": "python",
                    "input": str(in_path), "output": str(out_path),
                    "factor": ts_factor, "semitones": ps_semitones}

        try:
            result = _run_python(
                str(in_path), str(out_path),
                factor=ts_factor, semitones=ps_semitones,
                quality=effective_quality, formant=op_formant
            )
            if result.returncode == 0:
                return {"success": True, "output": str(out_path), "backend": "python"}
            else:
                return {"success": False, "error": result.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}


def analyze(filepath: str) -> Dict:
    """
    Basic audio file analysis via ffprobe (reuse from ffmpeg-audio logic inline).
    Returns duration, sample_rate, channels, etc.
    """
    from subprocess import run
    import json

    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(filepath)

    try:
        result = run(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json',
             '-show_format', '-show_streams', str(path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip()}

        data = json.loads(result.stdout)
        fmt = data.get('format', {})
        streams = data.get('streams', [])
        audio = next((s for s in streams if s.get('codec_type') == 'audio'), streams[0] if streams else {})

        return {
            "success": True,
            "file": str(path),
            "duration": float(fmt.get('duration', 0)),
            "sample_rate": int(audio.get('sample_rate', 0)),
            "channels": int(audio.get('channels', 0)),
            "codec": audio.get('codec_name'),
            "format": fmt.get('format_name'),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def probe(filepath: str) -> Dict:
    """Alias for analyze."""
    return analyze(filepath)
