"""
Pipeline engine — orchestrates DawDreamer to execute transformation pipelines.
"""

import json
import os
import tempfile
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np

# Check DawDreamer availability at import time
try:
    import dawdreamer as dd
    from dawdreamer import RenderEngine, PlaybackProcessor, AddProcessor
    DAWDREAMER_AVAILABLE = True
except ImportError:
    DAWDREAMER_AVAILABLE = False
    dd = None

from .operations import OP_REGISTRY


class AudioBuffer:
    """Compatibility AudioBuffer for current DawDreamer which lacks this class."""
    def __init__(self, data: np.ndarray, sample_rate: int):
        if data.ndim == 1:
            data = data.reshape(1, -1)
        self.data = data.astype(np.float32, copy=False)
        self.sample_rate = int(sample_rate)
        self._duration = self.data.shape[1] / self.sample_rate
        self.channels = self.data.shape[0]
        self.numFrames = self.data.shape[1]

    @property
    def duration(self):
        return self._duration

    @classmethod
    def from_file(cls, filepath: str, sample_rate: int):
        import librosa
        data, sr = librosa.load(filepath, sr=None, mono=False, dtype=np.float32)
        # librosa returns (channels, samples) when mono=False; if mono True it's (samples,)
        if data.ndim == 1:
            data = data.reshape(1, -1)
        if sr != sample_rate:
            if data.shape[0] == 1:
                res = librosa.resample(data[0], orig_sr=sr, target_sr=sample_rate)
                data = res.reshape(1, -1)
            else:
                channels = [librosa.resample(data[i], orig_sr=sr, target_sr=sample_rate) for i in range(data.shape[0])]
                data = np.vstack(channels)
        return cls(data, sample_rate)

    def get_channels(self):
        """Return audio array as (channels, samples)."""
        return self.data

    def get_peak(self):
        return float(np.max(np.abs(self.data)))

    def get_rms(self):
        return float(np.sqrt(np.mean(self.data.astype(np.float64)**2)))

    def save_to_file(self, path: str):
        import soundfile as sf
        if self.data.shape[0] == 1:
            data_to_write = self.data[0]
        else:
            data_to_write = self.data.T
        sf.write(path, data_to_write, self.sample_rate)



class DawDreamerEngine:
    """Context manager for a DawDreamer RenderEngine session."""

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 512,
    ):
        if not DAWDREAMER_AVAILABLE:
            raise ImportError(
                "DawDreamer is not installed. Install with:\n"
                "  pip install dawdreamer\n\n"
                "System dependencies (Linux):\n"
                "  sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev\n"
                "See RESEARCH.md and SKILL.md for more details."
            )
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self._engine = None

    def __enter__(self) -> 'RenderEngine':
        # Use positional arguments to avoid keyword naming mismatches across dawdreamer versions
        self._engine = dd.RenderEngine(self.sample_rate, self.buffer_size)
        return self._engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        # RenderEngine has no close(); clear reference for GC
        self._engine = None


def _load_audio_buffer(sample_rate: int, filepath: str) -> 'AudioBuffer':
    """Load audio file into memory as AudioBuffer."""
    # Load via librosa or soundfile, then convert to AudioBuffer
    # Sample rate is provided explicitly to avoid engine attribute dependency
    buf = AudioBuffer.from_file(filepath, sample_rate)
    return buf


def _create_processor(engine, spec):
    """Create a DawDreamer processor from an operation spec dict."""
    from dawdreamer import (
        FilterProcessor, CompressorProcessor, ReverbProcessor,
        GainProcessor, FadeProcessor, AddProcessor, PluginProcessor
    )

    ptype = spec['type']

    if ptype == 'gain':
        # Gain in dB: multiply amplitude = 10^(dB/20)
        gain_linear = 10 ** (spec['gain_db'] / 20.0)
        # Use AddProcessor as a gain node (single input)
        gain_proc = engine.make_add_processor("gain", [gain_linear])
        return gain_proc

    elif ptype == 'time_stretch':
        # Use PlaybackWarp processor on a copy of source
        factor = spec['factor']
        # This is special — handled differently (modifies playback processor)
        # Return marker to indicate special handling
        return {'__special__': 'time_stretch', 'factor': factor, 'preserve_formants': spec.get('preserve_formants', True)}

    elif ptype == 'pitch_shift':
        # Similar to time stretch but with pitch offset
        return {'__special__': 'pitch_shift', 'semitones': spec['semitones']}

    elif ptype == 'filter':
        mode = spec.get('mode', 'low')
        freq = spec.get('freq', 1000.0)
        q = spec.get('q', 0.707)
        gain = spec.get('gain', 1.0)
        return engine.make_filter_processor("filter", mode, freq, q, gain)

    elif ptype == 'compressor':
        threshold = spec.get('threshold', -20.0)
        ratio = spec.get('ratio', 4.0)
        attack = spec.get('attack', 2.0)
        release = spec.get('release', 50.0)
        return engine.make_compressor_processor("compressor", threshold, ratio, attack, release)

    elif ptype == 'reverb':
        room_size = spec.get('room_size', 0.5)
        damping = spec.get('damping', 0.5)
        wet = spec.get('wet', 0.33)
        dry = spec.get('dry', 0.4)
        width = spec.get('width', 1.0)
        return engine.make_reverb_processor("reverb", room_size, damping, wet, dry, width)

    elif ptype == 'fade':
        direction = spec['direction']
        duration = spec['duration']
        fade_proc = engine.make_fade_processor("fade", duration)
        if direction == 'in':
            fade_proc.fade_in()  # apply fade in
        else:
            fade_proc.fade_out()  # apply fade out
        return fade_proc

    elif ptype == 'filter':
        # Already handled above
        pass

    elif ptype == 'overlay':
        # Special: returns dict with track path and gains
        return spec

    elif ptype == 'load_vst':
        vst_path = spec['path']
        idx = spec.get('plugin_idx', 0)
        return engine.make_plugin_processor(f"vst{idx}", vst_path)

    else:
        raise ValueError(f"Unsupported processor type: {ptype}")


def transform(
    input: str,
    pipeline: List[Dict],
    output: str,
    *,
    sample_rate: int = 44100,
    buffer_size: int = 512,
    dry_run: bool = False,
    backup_original: bool = False,
    analysis: bool = False,
) -> Dict:
    """
    Transform an audio file through a pipeline of operations.

    Parameters
    ----------
    input : str
        Path to input audio file.
    pipeline : list of dict
        Ordered operations: [{"op": "normalize"}, {"op": "reverb", "room_size": 0.5}, ...]
    output : str
        Path for rendered output file.
    sample_rate : int, optional
        Processing sample rate (default 44100). Input is resampled if needed.
    buffer_size : int, optional
        Audio buffer size (default 512).
    dry_run : bool, optional
        If True, parse pipeline and return what would happen without processing.
    backup_original : bool, optional
        If True, copy input file to `output.bak` before writing output.
    analysis : bool, optional
        If True, also run analysis and include it in result.

    Returns
    -------
    dict
        {success, output, duration, analysis?, error?}
    """
    input_path = Path(input).resolve()
    output_path = Path(output).resolve()

    if not input_path.exists():
        return {"success": False, "error": f"Input not found: {input}"}

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "input": str(input_path),
            "output": str(output_path),
            "steps": len(pipeline),
            "ops": [step.get('op') for step in pipeline],
        }

    if backup_original:
        backup_path = output_path.with_suffix(output_path.suffix + '.bak')
        import shutil
        shutil.copy2(input_path, backup_path)

    # Normalize pipeline format: allow both {"op": "name", ...} and legacy {"type": ...}
    normalized_pipeline = []
    for step in pipeline:
        if 'op' in step:
            # New format: call the operation builder
            op_name = step.pop('op')
            builder = OP_REGISTRY.get(op_name)
            if not builder:
                return {"success": False, "error": f"Unknown operation: {op_name}"}
            # Build processor spec
            spec = builder(None, **step)
            if spec is None:
                return {"success": False, "error": f"Operation {op_name} returned None"}
            normalized_pipeline.append(spec)
        else:
            # Legacy format: already a processor spec dict
            normalized_pipeline.append(step)

    try:
        with DawDreamerEngine(sample_rate=sample_rate, buffer_size=buffer_size) as engine:
            # Determine total duration by loading audio
            input_buf = _load_audio_buffer(sample_rate, str(input_path))
            total_duration = input_buf.duration

            # Build graph from pipeline specs
            # Ensure source audio has appropriate channel count for plugins (e.g., stereo VSTs)
            source_audio = input_buf.get_channels()
            if any(spec.get('type') == 'load_vst' for spec in normalized_pipeline):
                if source_audio.shape[0] == 1:
                    source_audio = np.tile(source_audio, (2, 1))

            # Handle time_stretch/pitch_shift via warp processor at source.
            from dawdreamer import PlaybackProcessor, AddProcessor

            # Separate leading warp specs
            # Handle time_stretch/pitch_shift via warp processor at source.
            from dawdreamer import PlaybackProcessor, AddProcessor

            # Separate leading warp specs
            remaining = list(normalized_pipeline)
            gain_factor = 1.0  # cumulative gain applied post-render
            warp_time_ratio = 1.0
            warp_transpose = 0.0  # cumulative semitones for pitch shift
            while remaining and remaining[0].get('type') in ('time_stretch', 'pitch_shift'):
                spec = remaining.pop(0)
                if spec['type'] == 'time_stretch':
                    warp_time_ratio *= spec.get('factor', 1.0)
                elif spec['type'] == 'pitch_shift':
                    semitones = spec.get('semitones', 0.0)
                    warp_transpose += semitones


            # Create source node (warp or normal playback)
            if warp_time_ratio != 1.0 or warp_transpose != 0.0:
                try:
                    source_proc = engine.make_playbackwarp_processor("source_warp", input_buf.get_channels())
                except AttributeError:
                    # Fallback for older API or mock names
                    source_proc = engine.make_playback_processor("source_warp", input_buf.get_channels())
                source_proc.time_ratio = warp_time_ratio
                if warp_transpose != 0.0:
                    source_proc.transpose = warp_transpose
                graph = [(source_proc, [])]
                current = source_proc
                current_name = "source_warp"
            else:
                playback = engine.make_playback_processor("input", input_buf.get_channels())
                graph = [(playback, [])]
                current = playback
                current_name = "input"

            # Collect post-processing specs (fade/trim) that cannot be added to graph
            fade_specs = []
            trim_spec = None

            for i, spec in enumerate(remaining):
                ptype = spec.get('type')

                if ptype == 'gain':
                    if 'gain_db' in spec:
                        gain_linear = 10 ** (spec['gain_db'] / 20.0)
                    else:
                        gain_linear = spec.get('gain', 1.0)
                    # Add a gain processor to the graph using AddProcessor as a mono gain node
                    gain_proc = engine.make_add_processor(f"gain_{i}", [gain_linear])
                    graph.append((gain_proc, [current_name]))
                    current = gain_proc
                    current_name = f"gain_{i}"

                elif ptype == 'filter':
                    mode = spec.get('mode', 'low')
                    freq = spec.get('freq', 1000.0)
                    q = spec.get('q', 0.707)
                    gain = spec.get('gain', 1.0)
                    filter_proc = engine.make_filter_processor(f"filter_{i}", mode, freq, q, gain)
                    graph.append((filter_proc, [current_name]))
                    current = filter_proc
                    current_name = f"filter_{i}"

                elif ptype == 'compressor':
                    threshold = spec.get('threshold', -20.0)
                    ratio = spec.get('ratio', 4.0)
                    attack = spec.get('attack', 2.0)
                    release = spec.get('release', 50.0)
                    comp_proc = engine.make_compressor_processor(f"comp_{i}", threshold, ratio, attack, release)
                    graph.append((comp_proc, [current_name]))
                    current = comp_proc
                    current_name = f"comp_{i}"

                elif ptype == 'reverb':
                    room = spec.get('room_size', 0.5)
                    damping = spec.get('damping', 0.5)
                    wet = spec.get('wet', 0.33)
                    dry = spec.get('dry', 0.4)
                    width = spec.get('width', 1.0)
                    rev_proc = engine.make_reverb_processor(f"reverb_{i}", room, damping, wet, dry, width)
                    graph.append((rev_proc, [current_name]))
                    current = rev_proc
                    current_name = f"reverb_{i}"

                elif ptype == 'fade':
                    duration = spec['duration']
                    direction = spec['direction']
                    # Collect for post-processing after render
                    fade_specs.append((direction, duration))
                    # No graph addition; fade will be applied to final audio

                elif ptype == 'overlay':
                    # Special: adds a second input to the graph and mixes
                    track_b_path = spec['track_b']
                    gain_a = spec.get('gain_a', 0.0)
                    gain_b = spec.get('gain_b', 0.0)
                    pos = spec.get('position', 0.0)

                    buf_b = _load_audio_buffer(sample_rate, track_b_path)
                    playback_b = engine.make_playback_processor(f"overlay_{i}", buf_b.get_channels())
                    graph.append((playback_b, []))
                    playback_b_name = f"overlay_{i}"

                    mixer = engine.make_add_processor(f"mixer_{i}", [10**(gain_a/20), 10**(gain_b/20)])
                    graph.append((mixer, [current_name, playback_b_name]))
                    current = mixer
                    current_name = f"mixer_{i}"

                elif ptype == 'load_vst':
                    vst_path = spec['path']
                    idx = spec.get('plugin_idx', i)
                    plugin_proc = engine.make_plugin_processor(f"vst_{idx}", vst_path)
                    graph.append((plugin_proc, [current_name]))
                    current = plugin_proc
                    current_name = f"vst_{idx}"

                elif ptype == 'set_param':
                    # Handled inline after load_vst
                    param_name = spec['param']
                    value = spec['value']
                    # Find last plugin processor and set
                    for g_idx in range(len(graph)-1, -1, -1):
                        proc, _ = graph[g_idx]
                        if hasattr(proc, 'set_parameter'):
                            try:
                                proc.set_parameter(param_name, value)
                                break
                            except Exception:
                                pass

                elif ptype == 'trim':
                    # Trim is best handled by post-processing render
                    start = spec.get('start', 0.0)
                    end = spec.get('end', None)
                    dur = spec.get('duration', None)
                    # Store for post-processing after render
                    trim_spec = (start, end, dur)

                else:
                    warnings.warn(f"Unknown operation type '{ptype}' — skipping")
            # Final current node is output of graph
            # Connect all nodes in graph (already built as we went)
            # Actually DawDreamer loader expects full graph list upfront.
            # Debug: print graph summary
            for idx, (proc, inputs) in enumerate(graph):
                proc_name = proc.__class__.__name__ if hasattr(proc, '__class__') else type(proc)
                # inputs are processor name strings
                print(f"[TRACE] Graph node {idx}: processor={proc_name}, inputs={inputs}")
            engine.load_graph(graph)
            engine.render(total_duration)

            # Get rendered audio as numpy array (channels, samples)
            raw_audio = engine.get_audio()

            # Post-process: trim if specified
            if trim_spec is not None:
                start, end, dur = trim_spec
                sr = sample_rate
                s = int(start * sr)
                if dur is not None:
                    e = s + int(dur * sr)
                elif end is not None:
                    e = int(end * sr)
                else:
                    e = raw_audio.shape[1]
                raw_audio = raw_audio[:, s:e]

            # Post-process: fades
            for direction, duration in fade_specs:
                fade_len = int(duration * sample_rate)
                if fade_len > 0 and fade_len <= raw_audio.shape[1]:
                    if direction == 'in':
                        fade_curve = np.linspace(0, 1, fade_len)
                        raw_audio[:, :fade_len] *= fade_curve
                    elif direction == 'out':
                        fade_curve = np.linspace(1, 0, fade_len)
                        raw_audio[:, -fade_len:] *= fade_curve

            # Apply accumulated gain if any
            if abs(gain_factor - 1.0) > 1e-6:
                raw_audio *= gain_factor

            # Wrap in AudioBuffer for convenience (duration, saving)
            audio = AudioBuffer(raw_audio, sample_rate)

            # Save to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            audio.save_to_file(str(output_path))

            result = {
                "success": True,
                "input": str(input_path),
                "output": str(output_path),
                "steps": len(pipeline),
                "duration": audio.duration,
            }

            if analysis:
                result["analysis"] = analyze_file(str(input_path))

            return result

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()[:2000],
            "input": str(input_path),
        }


def mix(
    tracks: List[Dict[str, Union[str, float]]],
    output: str,
    *,
    sample_rate: int = 44100,
    normalize_final: bool = False,
    master_bus_chain: Optional[List[Dict]] = None,
) -> Dict:
    """
    Mix multiple audio tracks into a single output.

    Parameters
    ----------
    tracks : list of dict
        Each must have 'path', optional 'gain_db', 'pan'
    output : str
        Output file path
    normalize_final : bool
        If True, normalize final mix peak to -0.1 dBFS

    Returns
    -------
    dict
    """
    output_path = Path(output).resolve()

    try:
        with DawDreamerEngine(sample_rate=sample_rate) as engine:
            # Load all track buffers
            buffers = []
            gains = []
            for track in tracks:
                path_str = track['path']
                path = Path(path_str).resolve()
                buf = _load_audio_buffer(sample_rate, str(path))
                buffers.append(buf)
                # Convert dB gain to linear
                gain_db = track.get('gain_db', 0.0)
                gains.append(10 ** (gain_db / 20.0))

            # Determine longest duration
            max_len = max(b.numFrames for b in buffers)

            # Mix
            import numpy as np
            mixed = np.zeros((buffers[0].channels, max_len), dtype=np.float32)

            for buf, gain in zip(buffers, gains):
                # Pad or trim to max_len
                data = buf.get_channels()  # shape: (channels, samples)
                # Apply gain
                data = data * gain
                # Add to mix
                n = min(data.shape[1], max_len)
                mixed[:, :n] += data[:, :n]

            # Normalize if requested
            if normalize_final:
                peak = np.max(np.abs(mixed))
                if peak > 0:
                    scale = 0.99 / peak
                    mixed *= scale

            # Save
            out_buf = AudioBuffer(mixed, sample_rate)
            out_buf.save_to_file(str(output_path))

            return {
                "success": True,
                "output": str(output_path),
                "track_count": len(tracks),
                "duration": max_len / sample_rate,
            }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()[:2000]}


def analyze_file(filepath: str) -> Dict:
    """Extract audio properties using DawDreamer."""
    path = Path(filepath).resolve()

    if not path.exists():
        raise FileNotFoundError(filepath)

    try:
        with DawDreamerEngine(sample_rate=44100, buffer_size=512) as engine:
            audio = _load_audio_buffer(44100, str(path))

            peak = abs(audio.get_peak())
            rms = audio.get_rms()

            import math
            peak_db = 20 * math.log10(peak) if peak > 0 else -100.0
            rms_db = 20 * math.log10(rms) if rms > 0 else -100.0

            return {
                "file": str(path),
                "duration": audio.duration,
                "sample_rate": audio.sample_rate,
                "channels": audio.channels,
                "frames": audio.numFrames,
                "peak_dbfs": float(peak_db),
                "rms_db": float(rms_db),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze(filepath: str) -> Dict:
    """Public analyze — wrapper catching exceptions."""
    try:
        return analyze_file(filepath)
    except Exception as e:
        return {"success": False, "error": str(e)}


# Convenience builder
def build_pipeline(*steps) -> List[Dict]:
    """Build pipeline list from step dicts."""
    return list(steps)
