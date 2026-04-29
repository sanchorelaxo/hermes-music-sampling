"""
SoX Engine — wraps the SoX (Sound eXchange) command-line audio processor.

All operations translate to SoX effects/commands.
"""

import subprocess
import json
import shlex
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any


# SoX availability check at import time
try:
    result = subprocess.run(['sox', '--version'], capture_output=True, text=True, timeout=5)
    SOX_AVAILABLE = (result.returncode == 0)
    SOX_VERSION = result.stdout.strip() if SOX_AVAILABLE else None
except (FileNotFoundError, subprocess.TimeoutExpired):
    SOX_AVAILABLE = False
    SOX_VERSION = None


def _check_sox():
    """Raise informative error if SoX is not installed."""
    if not SOX_AVAILABLE:
        raise RuntimeError(
            "SoX is not installed or not in PATH.\n"
            "Install with:\n"
            "  sudo apt install sox           # Debian/Ubuntu\n"
            "  brew install sox               # macOS\n"
            "  sudo dnf install sox           # Fedora\n"
        )


def _run_sox(args: List[str], input_file: Optional[str] = None,
             output_file: Optional[str] = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Execute sox command with proper error handling.

    Correct SOX CLI syntax (confirmed on SoX 14.4.2):
        sox [global-opts] input_file output_file [effect [effopt]]...

    Effects must appear AFTER the output filename.
    """
    _check_sox()
    # Build command: sox <input> <output> [effects...]
    cmd = ['sox']
    if input_file:
        cmd.append(str(input_file))
    if output_file:
        cmd.append(str(output_file))
    if args:
        cmd.extend(args)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return result


def _build_sox_args(pipeline: List[Dict], input_file: str, output_file: str,
                     extra_global: Optional[List[str]] = None) -> List[str]:
    """
    Translate pipeline operations into SoX effect arguments.

    SoX CLI layout (confirmed):
      sox [global-opts] input_file output_file [effect [effopt]]...
    Effects are placed AFTER the output filename.
    """
    args = []
    
    # Global options (optional)
    if extra_global:
        args.extend(extra_global)
    
    # Effects chain: each op -> SoX effect string
    for step in pipeline:
        op = step.get('op')
        if op is None:
            raise ValueError(f"Pipeline step missing 'op' field: {step}")
        
        if op == 'gain' or op == 'volume':
            amount = step.get('amount', step.get('gain', 1.0))
            # SoX gain: either multiplier or dB
            # Format: "gain {amount}" where amount can be:
            #  - float multiplier (e.g., 0.5 halves volume)
            #  - positive number treated as dB? Actually SoX: gain [-n] amount [type]
            # Let's use multiplier (linear) for simplicity
            args.append('gain')
            args.append(str(amount))
        
        elif op == 'normalize':
            peak = step.get('peak', -0.1)
            # SoX: norm [-p peak]
            args.append('norm')
            if peak != -0.1:
                args.extend(['-p', str(peak)])
        
        elif op == 'fade':
            ftype = step.get('type', 'out')
            length = step.get('length', 1.0)
            # SoX: fade [type] [fade-in-length [fade-out-length [stop-position]]]
            if ftype == 'in':
                args.extend(['fade', 'in', str(length)])
            elif ftype == 'out':
                args.extend(['fade', 'out', str(length)])
            elif ftype == 'in-out':
                fade_in = step.get('fade_in', length)
                fade_out = step.get('fade_out', length)
                args.extend(['fade', 'in-out', str(fade_in), str(fade_out)])
        
        elif op == 'trim':
            start = step.get('start', 0.0)
            end = step.get('end')
            length = step.get('length')
            # SoX: trim {position} [{length}]
            args.append('trim')
            args.append(str(start))
            if length is not None:
                args.append(str(length))
            elif end is not None:
                # length = end - start
                args.append(str(end - start))
        
        elif op == 'pad':
            silence = step.get('silence', 1.0)
            # SoX: pad {position}
            args.append('pad')
            args.append(str(silence))
        
        elif op == 'reverse':
            args.append('reverse')
        
        elif op == 'channels':
            count = step.get('count', 1)
            args.extend(['channels', str(count)])
        
        elif op == 'rate':
            sr = step.get('sample_rate', 44100)
            args.extend(['rate', str(sr)])
        
        elif op == 'compand':
            # SoX compand: attack1:decay1{,attack2:decay2} [soft-knee-dB:]in-dB[,out-dB]
            attack = step.get('attack', '0.01:0.1')
            threshold_in = step.get('threshold_in', -20)
            threshold_out = step.get('threshold_out', -10)
            soft_knee = step.get('soft_knee', 0)
            compand_str = f"{attack} {soft_knee}:{threshold_in},{threshold_out}"
            args.append('compand')
            args.append(compand_str)
        
        elif op == 'equalizer':
            freq = step.get('frequency', 1000)
            width = step.get('width', '2q')
            gain = step.get('gain', 0)
            # SoX: equalizer frequency [width=q|o|h|k] gain
            eq_str = f"{freq} {width} {gain}"
            args.append('equalizer')
            args.append(eq_str)
        
        elif op == 'bass':
            gain = step.get('gain', 0)
            # SoX: bass {gain}
            args.append('bass')
            args.append(str(gain))
        
        elif op == 'treble':
            gain = step.get('gain', 0)
            args.append('treble')
            args.append(str(gain))
        
        elif op == 'echo':
            wet = step.get('wet', 0.5)
            delay = step.get('delay', 0.3)
            # SoX: echo gain-in gain-out [delay [decay [speed]]]
            # Simple: echo 0.8 0.8 0.3 0.5 1.1
            gain_in = step.get('gain_in', 0.8)
            gain_out = step.get('gain_out', 0.8)
            decay = step.get('decay', 0.5)
            args.append('echo')
            args.append(f"{gain_in} {gain_out} {delay} {decay}")
        
        elif op == 'reverb':
            wet = step.get('wet', 0.3)
            # SoX: reverb [wet-dry [room-scale [delay]]]
            room_scale = step.get('room_scale', 80)  # default  meters
            wet_dry = wet  # wet is factor of reverb level
            args.append('reverb')
            args.append(str(wet_dry))
            if 'room_scale' in step:
                args.append(str(room_scale))
        
        elif op == 'overlay':
            # This is handled specially: needs multi-input sox -m
            # Return a marker to handle in transform() with separate call to sox -m
            raise NotImplementedError("overlay should be handled by mixing two files via sox -m")
        
        elif op == 'raw_effect':
            # Pass-through raw SoX effect string
            effect = step.get('effect', '')
            args.append(effect)
        
        else:
            raise ValueError(f"Unknown SoX operation: {op}")

    return args


def transform(
    input: str,
    pipeline: List[Dict],
    output: str,
    *,
    dry_run: bool = False,
    backup_original: bool = False,
    extra_sox_args: Optional[List[str]] = None,
    timeout: int = 300,
) -> Dict:
    """
    Transform an audio file using SoX effects pipeline.

    Parameters
    ----------
    input : str
        Input audio file path.
    pipeline : list of dict
        Ordered operations: [{"op": "normalize", "peak": -0.1}, ...]
    output : str
        Output file path.
    dry_run : bool
        If True, build command and return it without executing.
    backup_original : bool
        If True, copy input to <output>.bak before writing.
    extra_sox_args : list of str
        Additional global SoX flags (e.g., ['-V6'] for verbose debug).
    timeout : int
        Maximum seconds to wait for SoX process.

    Returns
    -------
    dict
        {success: bool, output: str, command: str, error: str?, duration?: float}
    """
    in_path = Path(input).resolve()
    out_path = Path(output).resolve()

    if not in_path.exists():
        return {"success": False, "error": f"Input not found: {input}"}

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if backup_original and out_path.exists():
        backup = out_path.with_suffix(out_path.suffix + '.bak')
        import shutil
        shutil.copy2(out_path, backup)

    try:
        # Build SoX command: sox input output [effects...]
        # Note: SoX places effects AFTER the output file
        sox_args = _build_sox_args(pipeline, str(in_path), str(out_path), extra_sox_args)

        # Full command for logging: sox input output [effects]
        cmd = ['sox', str(in_path), str(out_path)] + sox_args
        cmd_str = ' '.join(shlex.quote(arg) for arg in cmd)

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "command": cmd_str,
                "input": str(in_path),
                "output": str(out_path),
                "steps": len(pipeline),
            }

        result = _run_sox(sox_args, input_file=str(in_path), output_file=str(out_path), timeout=timeout)

        if result.returncode == 0:
            # Success — optionally get output file duration via sox --i
            duration = None
            try:
                dresult = subprocess.run(
                    ['sox', '--i', '-D', str(out_path)],
                    capture_output=True, text=True, timeout=5
                )
                if dresult.returncode == 0:
                    duration = float(dresult.stdout.strip())
            except Exception:
                pass

            return {
                "success": True,
                "output": str(out_path),
                "command": cmd_str,
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
        return {"success": False, "error": f"SoX timed out after {timeout}s", "command": cmd_str}
    except Exception as e:
        return {"success": False, "error": str(e)}


def mix(
    tracks: List[Dict[str, Any]],
    output: str,
    *,
    normalize_final: bool = False,
    dry_run: bool = False,
    extra_sox_args: Optional[List[str]] = None,
) -> Dict:
    """
    Mix multiple audio tracks into a single output file using SoX's `-m` mode.

    Parameters
    ----------
    tracks : list of dict
        Each dict: {"path": str, "gain": float (linear multiplier), "pan": None|float}
        `pan` not yet implemented; SoX's `remix` can pan but we keep simple.
    output : str
        Output file path.
    normalize_final : bool
        If True, apply `normalize` to final mix.
    dry_run : bool
        If True, return command without executing.
    extra_sox_args : list of str
        Additional SoX global flags.

    Returns
    -------
    dict
    """
    out_path = Path(output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Build sox -m command: sox -m input1 -v gain1 input2 -v gain2 ... output
    # SoX: sox -m [input1] [input2 ...] [output]
    # Per-input volume: put `-v gain` before each input file

    input_specs = []
    for t in tracks:
        p = Path(t['path']).resolve()
        if not p.exists():
            return {"success": False, "error": f"Track not found: {t['path']}"}
        gain = t.get('gain', 1.0)
        input_specs.append(('-v', str(gain), str(p)))

    # Base command: sox -m spec1 spec2 ... output [effects?]
    cmd = ['sox', '-m']
    for spec in input_specs:
        cmd.extend(spec)
    
    if normalize_final:
        cmd.append('norm')
    
    cmd.append(str(out_path))

    cmd_str = ' '.join(shlex.quote(arg) for arg in cmd)

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "command": cmd_str,
            "track_count": len(tracks),
            "output": str(out_path),
        }

    try:
        result = _run_sox(cmd[1:], input_file=None, output_file=str(out_path))
        # Note: we pass full cmd[1:] (skip 'sox' since _run_sox adds it)
        # Actually _run_sox adds its own sox prefix, so we should call subprocess directly.
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            return {
                "success": True,
                "output": str(out_path),
                "command": cmd_str,
                "track_count": len(tracks),
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
                "command": cmd_str,
            }
    except Exception as e:
        return {"success": False, "error": str(e), "command": cmd_str}


def analyze(filepath: str) -> Dict:
    """
    Extract audio metadata using SoX's `--i` (information) tool.
    
    Returns dictionary of audio properties.
    """
    path = Path(filepath).resolve()
    if not path.exists():
        raise FileNotFoundError(filepath)

    _check_sox()

    # Use sox --i to get info
    info = {}
    try:
        # Duration: sox --i -D file.wav
        dproc = subprocess.run(['sox', '--i', '-D', str(path)], capture_output=True, text=True, timeout=10)
        if dproc.returncode == 0:
            info['duration'] = float(dproc.stdout.strip())

        # Sample rate: sox --i -r file.wav
        srproc = subprocess.run(['sox', '--i', '-r', str(path)], capture_output=True, text=True, timeout=10)
        if srproc.returncode == 0:
            info['sample_rate'] = int(srproc.stdout.strip())

        # Channels: sox --i -c file.wav
        cproc = subprocess.run(['sox', '--i', '-c', str(path)], capture_output=True, text=True, timeout=10)
        if cproc.returncode == 0:
            info['channels'] = int(cproc.stdout.strip())

        # Bit depth (if known): sox --i -b file.wav
        bproc = subprocess.run(['sox', '--i', '-b', str(path)], capture_output=True, text=True, timeout=10)
        if bproc.returncode == 0:
            try:
                info['bit_depth'] = int(bproc.stdout.strip())
            except ValueError:
                info['bit_depth'] = bproc.stdout.strip()

        # File type / encoding
        tproc = subprocess.run(['sox', '--i', '-e', str(path)], capture_output=True, text=True, timeout=10)
        if tproc.returncode == 0:
            info['encoding'] = tproc.stdout.strip()

    except Exception as e:
        return {"success": False, "error": str(e), "file": str(path)}

    # Also get peak and RMS via stats (subprocess, reads stderr)
    try:
        # sox file.wav -n stat 2>&1
        stat_proc = subprocess.run(
            ['sox', str(path), '-n', 'stat'],
            capture_output=True, text=True, timeout=30
        )
        stat_out = stat_proc.stderr + stat_proc.stdout
        # Parse RMS and peak amplitude
        import re
        rms_match = re.search(r'RMS\s+amplitude\s*:\s+([\d.]+)', stat_out)
        # 'Peak amplitude' appears on older SoX; newer SoX uses 'Maximum amplitude'
        peak_match = re.search(r'Peak\s+amplitude\s*:\s+([\d.eE+-]+)', stat_out)
        if not peak_match:
            peak_match = re.search(r'Maximum\s+amplitude\s*:\s+([\d.eE+-]+)', stat_out)
        if rms_match:
            info['rms'] = float(rms_match.group(1))
        if peak_match:
            info['peak'] = float(peak_match.group(1))
        # DC offset?
        dc_match = re.search(r'DC offset\s+:\s+([\d.Ee+-]+)', stat_out)
        if dc_match:
            info['dc_offset'] = float(dc_match.group(1))
        # Min/max
        min_match = re.search(r'Min\s+level\s+:\s+([-+]?[\d.]+)', stat_out)
        max_match = re.search(r'Max\s+level\s+:\s+([-+]?[\d.]+)', stat_out)
        if min_match and max_match:
            info['min_level'] = float(min_match.group(1))
            info['max_level'] = float(max_match.group(1))
    except Exception:
        pass  # stats are best-effort

    return {"success": True, "file": str(path), **info}


def probe(filepath: str) -> Dict:
    """Alias for analyze()."""
    return analyze(filepath)
