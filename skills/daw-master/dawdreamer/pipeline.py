"""
Pipeline engine — orchestrates DawDreamer to execute transformation pipelines.
"""

import json
import os
import tempfile
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union

# Check DawDreamer availability at import time
try:
    import dawdreamer as dd
    from dawdreamer import RenderEngine, AudioBuffer, PlaybackProcessor, AddProcessor
    DAWDREAMER_AVAILABLE = True
except ImportError:
    DAWDREAMER_AVAILABLE = False
    dd = None


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
        self._engine = dd.RenderEngine(
            sampleRate=self.sample_rate,
            bufferSize=self.buffer_size,
        )
        return self._engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._engine is not None:
            self._engine.close()
            self._engine = None


def _load_audio_buffer(engine: 'RenderEngine', filepath: str) -> 'AudioBuffer':
    """Load audio file into memory as AudioBuffer."""
    from dawdreamer import AudioBuffer
    # Load via librosa or soundfile, then convert to AudioBuffer
    # DawDreamer can load from file using path, but we need to know sample rate
    # Use engine to get consistent sample rate
    buf = AudioBuffer.from_file(filepath, engine.sampleRate)
    return buf


def _create_processor(engine, spec):
    """Create a DawDreamer processor from an operation spec dict."""
    from dawdreamer import (
        FilterProcessor, CompressorProcessor, ReverbProcessor,
        GainProcessor, FadeProcessor, AddProcessor, PluginProcessor
    )

    ptype = spec['type']

    if ptype == 'gain':
        # Simple gain processor (in dB)
        gain_proc = engine.make_gain_processor("gain", 0.0)  # start at 0 dB
        # Gain in dB: multiply amplitude = 10^(dB/20)
        gain_proc.gain = 10 ** (spec['gain_db'] / 20.0)
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


def _build_graph(engine, input_buffer, pipeline_specs):
    """
    Build DawDreamer processor graph from pipeline.

    Returns (output_node, graph) where graph is list of tuples (processor, inputs).
    """
    from dawdreamer import PlaybackProcessor

    graph = []

    # Step 1: Create the initial playback processor from input buffer
    playback = engine.make_playback_processor("input", input_buffer)
    graph.append((playback, []))  # no inputs

    current = playback

    # Step 2: Create processors for each pipeline step
    vst_idx = 0
    for i, spec in enumerate(pipeline_specs):
        spec_type = spec.get('type', spec.get('op'))  # handle both internal formats

        if spec_type == 'time_stretch':
            # Time-stretch: recreate playback processor with warp
            # This requires wrapping the audio buffer in a warp processor
            factor = spec['factor']
            warp_proc = engine.make_playback_warp_processor(
                f"warped_{i}",
                input_buffer,
                initial_bpm=120.0
            )
            warp_proc.time_ratio = factor
            warp_proc.pitch_ratio = 1.0  # preserve pitch
            # Reconnect: warp processor takes no inputs (replaces playback)
            # We need to rewire previous processor's output to go through warp
            # Easiest: just replace current with warp_proc in graph's source
            # But DawDreamer graph is static — rebuild from start with modified playback
            # Strategy: rebuild graph with time_stretch applied at source
            raise NotImplementedError(
                "time_stretch currently requires re-creating playback processor. "
                "Support for warping after loading is pending."
            )

        elif spec_type == 'gain':
            gain_proc = engine.make_gain_processor(f"gain_{i}")
            gain_proc.gain = 10 ** (spec['gain_db'] / 20.0)
            graph.append((gain_proc, [current]))
            current = gain_proc

        elif spec_type == 'filter':
            mode = spec.get('mode', 'low')
            freq = spec.get('freq', 1000.0)
            q = spec.get('q', 0.707)
            gain = spec.get('gain', 1.0)
            filter_proc = engine.make_filter_processor(f"filter_{i}", mode, freq, q, gain)
            graph.append((filter_proc, [current]))
            current = filter_proc

        elif spec_type == 'compressor':
            threshold = spec.get('threshold', -20.0)
            ratio = spec.get('ratio', 4.0)
            attack = spec.get('attack', 2.0)
            release = spec.get('release', 50.0)
            comp_proc = engine.make_compressor_processor(f"comp_{i}", threshold, ratio, attack, release)
            graph.append((comp_proc, [current]))
            current = comp_proc

        elif spec_type == 'reverb':
            room = spec.get('room_size', 0.5)
            damping = spec.get('damping', 0.5)
            wet = spec.get('wet', 0.33)
            dry = spec.get('dry', 0.4)
            width = spec.get('width', 1.0)
            rev_proc = engine.make_reverb_processor(f"reverb_{i}", room, damping, wet, dry, width)
            graph.append((rev_proc, [current]))
            current = rev_proc

        elif spec_type == 'fade':
            # Fade is applied at output stage via render parameters or separate processor
            # DawDreamer has FadeProcessor
            duration = spec['duration']
            direction = spec['direction']
            fade_proc = engine.make_fade_processor(f"fade_{i}", duration)
            if direction == 'in':
                fade_proc.fade_in()
            else:
                fade_proc.fade_out()
            graph.append((fade_proc, [current]))
            current = fade_proc

        elif spec_type == 'load_vst':
            vst_path = spec['path']
            idx = spec.get('plugin_idx', 0) or vst_idx
            if not Path(vst_path).exists():
                raise FileNotFoundError(f"VST plugin not found: {vst_path}")
            plugin_proc = engine.make_plugin_processor(f"vst_{idx}", vst_path)
            # Set parameters if provided in subsequent steps
            graph.append((plugin_proc, [current]))
            current = plugin_proc
            vst_idx += 1

        elif spec_type == 'set_param':
            # modify the last VST plugin processor
            # Find last plugin in graph
            param_name = spec['param']
            value = spec['value']
            # Look for last plugin processor
            for g_idx in range(len(graph)-1, -1, -1):
                proc, _ = graph[g_idx]
                if hasattr(proc, 'set_parameter'):
                    try:
                        proc.set_parameter(param_name, value)
                        break
                    except Exception:
                        pass
            else:
                warnings.warn(f"set_param called but no plugin found in chain: {spec}")

        elif spec_type == 'overlay':
            # Overlay requires second track — we'll need to build multi-input graph
            track_b_path = spec['track_b']
            gain_a = 10 ** (spec.get('gain_a', 0.0) / 20.0)
            gain_b = 10 ** (spec.get('gain_b', 0.0) / 20.0)
            # Load track_b as playback processor
            buf_b = _load_audio_buffer(engine, track_b_path)
            playback_b = engine.make_playback_processor("track_b", buf_b)
            graph.append((playback_b, []))

            # Create an add (mix) processor
            mixer = engine.make_add_processor("mixer", [gain_a, gain_b])
            graph.append((mixer, [current, playback_b]))
            current = mixer

        else:
            raise ValueError(f"Unknown operation type: {spec_type}")

    # Final output node is `current`
    # Note: We haven't handled trimming/filters that need custom processing
    # For trim, we may need to render then cut post, or use offline approach

    return current, graph


def _render_graph(engine, graph, output_buffer, duration):
    """Execute graph render."""
    engine.load_graph(graph)
    engine.render(duration)
    # Get audio
    audio = engine.get_audio()
    # Save
    audio.save_to_file(str(output_buffer))


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
        with DawDreamerEngine(sampleRate=sample_rate, bufferSize=buffer_size) as engine:
            # Determine total duration by loading audio
            input_buf = _load_audio_buffer(engine, str(input_path))
            total_duration = input_buf.duration

            # Build graph from pipeline specs
            # Note: For complex pipelines (with overlays), we need to build
            # a multi-node graph. We'll handle simple linear chains first.
            from dawdreamer import PlaybackProcessor, AddProcessor

            # Start with playback node
            playback = engine.make_playback_processor("input", input_buf)
            graph = [(playback, [])]
            current = playback

            # Track special processors that need post-processing (fade, trim)
            fade_proc = None

            for i, spec in enumerate(normalized_pipeline):
                ptype = spec.get('type')

                if ptype == 'gain':
                    gain_proc = engine.make_gain_processor(f"gain_{i}")
                    gain_proc.gain = spec.get('gain', 1.0)  # linear amplitude
                    graph.append((gain_proc, [current]))
                    current = gain_proc

                elif ptype == 'filter':
                    mode = spec.get('mode', 'low')
                    freq = spec.get('freq', 1000.0)
                    q = spec.get('q', 0.707)
                    gain = spec.get('gain', 1.0)
                    filter_proc = engine.make_filter_processor(f"filter_{i}", mode, freq, q, gain)
                    graph.append((filter_proc, [current]))
                    current = filter_proc

                elif ptype == 'compressor':
                    threshold = spec.get('threshold', -20.0)
                    ratio = spec.get('ratio', 4.0)
                    attack = spec.get('attack', 2.0)
                    release = spec.get('release', 50.0)
                    comp_proc = engine.make_compressor_processor(f"comp_{i}", threshold, ratio, attack, release)
                    graph.append((comp_proc, [current]))
                    current = comp_proc

                elif ptype == 'reverb':
                    room = spec.get('room_size', 0.5)
                    damping = spec.get('damping', 0.5)
                    wet = spec.get('wet', 0.33)
                    dry = spec.get('dry', 0.4)
                    width = spec.get('width', 1.0)
                    rev_proc = engine.make_reverb_processor(f"reverb_{i}", room, damping, wet, dry, width)
                    graph.append((rev_proc, [current]))
                    current = rev_proc

                elif ptype == 'fade':
                    duration = spec['duration']
                    direction = spec['direction']
                    fade_proc = engine.make_fade_processor(f"fade_{i}", duration)
                    if direction == 'in':
                        fade_proc.fade_in()
                    elif direction == 'out':
                        fade_proc.fade_out()
                    else:
                        # fade can also take custom curve
                        fade_proc.fade_in()  # default
                    graph.append((fade_proc, [current]))
                    current = fade_proc

                elif ptype == 'overlay':
                    # Special: adds a second input to the graph and mixes
                    track_b_path = spec['track_b']
                    gain_a = spec.get('gain_a', 0.0)
                    gain_b = spec.get('gain_b', 0.0)
                    pos = spec.get('position', 0.0)

                    buf_b = _load_audio_buffer(engine, track_b_path)
                    playback_b = engine.make_playback_processor(f"overlay_{i}", buf_b)
                    graph.append((playback_b, []))

                    mixer = engine.make_add_processor(f"mixer_{i}", [10**(gain_a/20), 10**(gain_b/20)])
                    graph.append((mixer, [current, playback_b]))
                    current = mixer

                elif ptype == 'load_vst':
                    vst_path = spec['path']
                    idx = spec.get('plugin_idx', i)
                    plugin_proc = engine.make_plugin_processor(f"vst_{idx}", vst_path)
                    graph.append((plugin_proc, [current]))
                    current = plugin_proc

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
                    # Mark for post-processing: store start/end times
                    start = spec.get('start', 0.0)
                    end = spec.get('end', None)
                    dur = spec.get('duration', None)
                    # We'll handle trim after render
                    # Store on current node for post-processing
                    current._trim_spec = (start, end, dur)

                else:
                    warnings.warn(f"Unknown operation type '{ptype}' — skipping")

            # Final current node is output of graph
            # Connect all nodes in graph (already built as we went)
            # Actually DawDreamer loader expects full graph list upfront.
            # Let's rewrite to build full graph first:

            # Rebuild: we built incrementally with append; the graph list is correct
            # Now set output to last node and render
            engine.load_graph(graph)
            engine.render(total_duration)

            audio = engine.get_audio()

            # Post-process: trim if marked
            if hasattr(current, '_trim_spec'):
                start, end, dur = current._trim_spec
                # Compute sample indices
                sr = engine.sampleRate
                s = int(start * sr)
                if dur is not None:
                    e = s + int(dur * sr)
                elif end is not None:
                    e = int(end * sr)
                else:
                    e = len(audio)
                # Slice audio buffer (channels, samples)
                audio = audio[:, s:e]

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
            "traceback": traceback.format_exc()[:500],
            "input": str(input_path),
        }


def mix(
    tracks: List[Dict[str, Union[str, float]]],
    output: str,
    *,
    sample_rate: int = 44100,
    normalize_final: bool = False,
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
        with DawDreamerEngine(sampleRate=sample_rate) as engine:
            # Load all track buffers
            buffers = []
            gains = []
            for track in tracks:
                path_str = track['path']
                path = Path(path_str).resolve()
                buf = _load_audio_buffer(engine, str(path))
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
            from dawdreamer import AudioBuffer
            out_buf = AudioBuffer(mixed, engine.sampleRate)
            out_buf.save_to_file(str(output_path))

            return {
                "success": True,
                "output": str(output_path),
                "track_count": len(tracks),
                "duration": max_len / sample_rate,
            }
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()[:300]}


def analyze_file(filepath: str) -> Dict:
    """Extract audio properties using DawDreamer."""
    path = Path(filepath).resolve()

    if not path.exists():
        raise FileNotFoundError(filepath)

    try:
        with DawDreamerEngine(sampleRate=44100, bufferSize=512) as engine:
            audio = _load_audio_buffer(engine, str(path))

            peak = abs(audio.get_peak())
            rms = audio.get_rms()

            import math
            peak_db = 20 * math.log10(peak) if peak > 0 else -100.0
            rms_db = 20 * math.log10(rms) if rms > 0 else -100.0

            return {
                "file": str(path),
                "duration": audio.duration,
                "sample_rate": audio.sampleRate,
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
