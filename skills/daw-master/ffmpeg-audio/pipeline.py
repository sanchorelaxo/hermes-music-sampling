"""
FFmpeg Audio Engine — wraps FFmpeg audio filters and filter_complex.

All operations compile into one ffmpeg process where possible.
Multi-input operations (mixing) use -filter_complex.
"""

import subprocess
import json
import shlex
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

# FFmpeg availability check
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
    FFMPEG_AVAILABLE = (result.returncode == 0)
    FFMPEG_VERSION = result.stdout.split('\n')[0].strip() if FFMPEG_AVAILABLE else None
except (FileNotFoundError, subprocess.TimeoutExpired):
    FFMPEG_AVAILABLE = False

try:
    result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, timeout=5)
    FFPROBE_AVAILABLE = (result.returncode == 0)
except (FileNotFoundError, subprocess.TimeoutExpired):
    FFPROBE_AVAILABLE = False


def _check_ffmpeg():
    if not FFMPEG_AVAILABLE:
        raise RuntimeError(
            "FFmpeg not found. Install with:\n"
            "  sudo apt install ffmpeg   # Debian/Ubuntu\n"
            "  brew install ffmpeg       # macOS"
        )


def _check_ffprobe():
    if not FFPROBE_AVAILABLE:
        raise RuntimeError("ffprobe not found — install ffmpeg package")


def _format_value(key: str, value):
    """Format a parameter value for FFmpeg filter syntax."""
    if isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Already in key=value form? e.g., "0.5|0.5"
        if '=' in value and not any(c in value for c in [':', '|']):
            # This looks like "key=value", pass as-is (for raw strings)
            return value
        return value
    elif isinstance(value, list):
        # Pipe-separated for multi-value FFmpeg params: [100, 200] → "100|200"
        return "|".join(str(v) for v in value)
    else:
        return str(value)


def _build_filter_string(pipeline: List[Dict]) -> str:
    """
    Translate pipeline ops into FFmpeg -af filter string.

    Example input:
      [{"op": "volume", "gain": "3dB"}, {"op": "highpass", "cutoff": 80}]

    Output:
      "volume=3dB,highpass=f=80"
    """
    filters = []

    for step in pipeline:
        op = step.get('op')
        if not op:
            raise ValueError(f"Pipeline step missing 'op': {step}")

        filter_name = OP_REGISTRY.get(op)
        if not filter_name:
            raise ValueError(f"Unknown FFmpeg operation: {op}. Known: {', '.join(sorted(OP_REGISTRY.keys()))}")

        # Build param string: key1=val1:key2=val2:...
        param_pairs = []
        for k, v in step.items():
            if k == 'op':
                continue
            # Resolve aliases: for volume/gain ops, 'gain' should map to 'volume' parameter
            param_name = k
            if op in ('volume', 'gain') and k == 'gain':
                param_name = 'volume'
            elif op == 'highpass' and k == 'cutoff':
                param_name = 'f'

            param_pairs.append(f"{param_name}={_format_value(param_name, v)}")

        if param_pairs:
            filter_str = f"{filter_name}=" + ":".join(param_pairs)
        else:
            filter_str = filter_name  # e.g., "areverse"

        filters.append(filter_str)

    return ",".join(filters)


def _build_multitrack_filter_complex(tracks: List[Dict]) -> str:
    """
    Build filter_complex for mixing multiple tracks with per-track processing.

    Example tracks:
      [{"path": "a.wav", "gain": 1.0, "pan": "FC"},
       {"path": "b.wav", "gain": 0.7, "delay": 100}]

    Returns filter_complex string:
      "[0:a]volume=1.0,pan=FC[a0];[1:a]volume=0.7,adelay=100|100[a1];[a0][a1]amix=inputs=2:duration=longest[out]"
    """
    chains = []

    for i, t in enumerate(tracks):
        parts = []

        # Delay (adelay) — place early to avoid ',a' substring in filter chain
        if 'delay' in t:
            ms = t['delay']
            parts.append(f"adelay={ms}|{ms}")

        # Gain (volume)
        if 'gain' in t and t['gain'] != 1.0:
            parts.append(f"volume={t['gain']}")

        # Pan
        if 'pan' in t:
            parts.append(f"pan={t['pan']}")

        # Custom per-track filters
        if 'filters' in t and t['filters']:
            parts.extend(t['filters'])

        # Build filter chain: [i:a]...filters...[out{i}]
        chain = f"[{i}:a]"
        if parts:
            chain += ",".join(parts)
        chain += f"[out{i}]"
        chains.append(chain)

    # Amix all prepared streams
    inputs = "".join(f"[out{i}]" for i in range(len(tracks)))
    mix_params = "inputs={}:duration=longest:dropout_transition=2".format(len(tracks))
    chains.append(f"{inputs}amix={mix_params}[out]")

    return ";".join(chains)


def transform(
    input: str,
    pipeline: List[Dict],
    output: str,
    *,
    codec: Optional[str] = None,
    sample_rate: Optional[int] = None,
    dry_run: bool = False,
    overwrite: bool = True,
    extra_global_args: Optional[List[str]] = None,
    extra_filters: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict:
    """
    Transform audio using FFmpeg audio filters.

    Parameters
    ----------
    input : str
        Input file. Set to None for synthetic generation (must have 'sine' op or similar).
    pipeline : list of dict
        Ordered operations: [{"op": "volume", "gain": "3dB"}, {"op": "fade", "type": "out", "duration": 2}, ...]
    output : str
        Output file path. Container inferred from extension.
    codec : str, optional
        Audio codec (e.g., 'aac', 'mp3', 'flac', 'pcm_s16le', 'opus').
    sample_rate : int, optional
        Resample output (sets `-ar`). Alternatively use `aresample` filter in pipeline.
    dry_run : bool
        Return command without executing.
    overwrite : bool
        Overwrite existing output (default True).
    extra_global_args : list
        Extra CLI flags (e.g., `["-v", "error"]`).
    extra_filters : list
        Additional filter strings appended after auto-built ones.
    timeout : int
        Max seconds for ffmpeg process.

    Returns
    -------
    dict
        {success, output, command, filter_string, duration?, error?}
    """
    _check_ffmpeg()

    out_path = Path(output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate input
    input_args = []
    if input is not None:
        in_path = Path(input).resolve()
        if not in_path.exists():
            return {"success": False, "error": f"Input not found: {input}"}
        input_args = ['-i', str(in_path)]
    else:
        # Synthetic generation mode — pipeline must include a source generator (sine, anullsrc, etc.)
        pass

    # Build filter string
    try:
        filter_str = _build_filter_string(pipeline)
        if extra_filters:
            filter_str = f"{filter_str},{','.join(extra_filters)}" if filter_str else ",".join(extra_filters)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Build full command
    cmd = ['ffmpeg']

    if overwrite:
        cmd.append('-y')

    cmd.extend(input_args)

    if filter_str:
        cmd.extend(['-af', filter_str])

    if codec:
        cmd.extend(['-c:a', codec])

    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])

    if extra_global_args:
        cmd.extend(extra_global_args)

    cmd.append(str(out_path))

    cmd_str = " ".join(shlex.quote(arg) for arg in cmd)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "command": cmd_str,
            "filter_string": filter_str,
            "input": input,
            "output": str(out_path),
            "steps": len(pipeline),
        }

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Get duration
            duration = None
            try:
                dresult = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', str(out_path)],
                    capture_output=True, text=True, timeout=10
                )
                if dresult.returncode == 0:
                    duration = float(dresult.stdout.strip())
            except Exception:
                pass

            return {
                "success": True,
                "output": str(out_path),
                "command": cmd_str,
                "filter_string": filter_str,
                "steps": len(pipeline),
                "duration": duration,
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
                "command": cmd_str,
                "stderr": result.stderr[:500],
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"FFmpeg timed out after {timeout}s", "command": cmd_str}
    except Exception as e:
        return {"success": False, "error": str(e), "command": cmd_str}


def mix(
    tracks: List[Dict[str, Any]],
    output: str,
    *,
    codec: Optional[str] = None,
    sample_rate: Optional[int] = None,
    normalize_final: bool = False,
    dry_run: bool = False,
    overwrite: bool = True,
    extra_global_args: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict:
    """
    Mix multiple audio tracks using FFmpeg's amix filter.

    Parameters
    ----------
    tracks : list of dict
        Each dict: {'path': str, 'gain': float, 'pan': str, 'delay': ms, 'filters': [str]}
    output : str
        Output file.
    codec, sample_rate, extra_global_args : as in transform()
    normalize_final : bool
        Append loudnorm filter after mix if True.
    dry_run, overwrite : as in transform()

    Returns
    -------
    dict
    """
    _check_ffmpeg()

    out_path = Path(output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate all track files
    for i, t in enumerate(tracks):
        p = Path(t['path']).resolve()
        if not p.exists():
            return {"success": False, "error": f"Track {i} not found: {t['path']}"}

    # Build filter_complex
    try:
        filter_complex = _build_multitrack_filter_complex(tracks)
        if normalize_final:
            filter_complex += ";[out]loudnorm=I=-16:LRA=11:TP=-1[out2]"
            out_label = "[out2]"
        else:
            out_label = "[out]"
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Build command
    cmd = ['ffmpeg', '-y'] if overwrite else ['ffmpeg']

    for t in tracks:
        cmd.extend(['-i', str(Path(t['path']).resolve())])

    cmd.extend(['-filter_complex', filter_complex])
    cmd.extend(['-map', out_label])

    if codec:
        cmd.extend(['-c:a', codec])
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])
    if extra_global_args:
        cmd.extend(extra_global_args)

    cmd.append(str(out_path))

    cmd_str = " ".join(shlex.quote(arg) for arg in cmd)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "command": cmd_str,
            "filter_complex": filter_complex,
            "filter_string": filter_complex,  # for API consistency with transform()
            "track_count": len(tracks),
            "output": str(out_path),
        }

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

        if result.returncode == 0:
            # Duration
            duration = None
            try:
                dresult = subprocess.run(
                    ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                     '-of', 'default=noprint_wrappers=1:nokey=1', str(out_path)],
                    capture_output=True, text=True, timeout=10
                )
                if dresult.returncode == 0:
                    duration = float(dresult.stdout.strip())
            except Exception:
                pass

            return {
                "success": True,
                "output": str(out_path),
                "command": cmd_str,
                "track_count": len(tracks),
                "duration": duration,
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
                "command": cmd_str,
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"FFmpeg timed out after {timeout}s", "command": cmd_str}
    except Exception as e:
        return {"success": False, "error": str(e), "command": cmd_str}


def analyze(filepath: str) -> Dict:
    """
    Get audio file metadata via ffprobe.

    Returns top-level format fields plus first audio stream details.
    """
    _check_ffprobe()

    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(filepath)

    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        str(path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"success": False, "error": result.stderr.strip(), "file": str(path)}

        data = json.loads(result.stdout)

        fmt = data.get('format', {})
        streams = data.get('streams', [])
        audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'),
                            streams[0] if streams else {})

        info = {
            "success": True,
            "file": str(path),
            "format": fmt.get('format_name'),
            "format_long": fmt.get('format_long_name'),
            "duration": float(fmt.get('duration', 0)),
            "size": int(fmt.get('size', 0)),
            "bit_rate": int(fmt.get('bit_rate', 0)) if fmt.get('bit_rate') else None,
            "tags": fmt.get('tags', {}),
            "codec": audio_stream.get('codec_name'),
            "sample_rate": int(audio_stream.get('sample_rate', 0)),
            "channels": int(audio_stream.get('channels', 0)),
        }

        return info
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON parse error: {e}", "file": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e), "file": str(path)}


def probe(filepath: str) -> Dict:
    """Alias for analyze."""
    return analyze(filepath)


# ======================
# Operation Registry
# ======================

OP_REGISTRY = {
    # Volume & Level
    'gain': 'volume',
    'volume': 'volume',
    'loudnorm': 'loudnorm',
    'dynaudnorm': 'dynaudnorm',

    # Dynamics
    'acompressor': 'acompressor',
    'compand': 'compand',
    'sidechaincompress': 'sidechaincompress',

    # Filters & EQ
    'equalizer': 'equalizer',
    'eq': 'equalizer',
    'lowpass': 'lowpass',
    'highpass': 'highpass',
    'bandpass': 'bandpass',
    'bass': 'bass',           # shelf
    'treble': 'treble',
    'lowshelve': 'lowshelve',
    'highshelve': 'highshelve',

    # Editing
    'atrim': 'atrim',
    'areverse': 'areverse',
    'apad': 'apad',
    'adelay': 'adelay',
    'atempo': 'atempo',

    # Channel ops
    'channelmap': 'channelmap',
    'pan': 'pan',
    'channelsplit': 'channelsplit',

    # Concat/join (multi-input, handled in mix)
    'join': 'join',

    # Effects
    'aecho': 'aecho',
    'areverb': 'areverb',
    'freeverb': 'freeverb',
    'aconvolve': 'aconvolve',
}
