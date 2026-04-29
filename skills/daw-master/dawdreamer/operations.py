"""
Operations module — each function creates and returns a DawDreamer processor
configured for the requested transformation.
"""

import dawdreamer as dd


def op_normalize(engine, target_level=-0.1, **kwargs):
    """Normalize peak amplitude via gain processor (applied later via automation)."""
    # Simple: compute gain needed from analysis, then apply gain processor.
    # This will be applied as a two-pass: first analyze peak, then set gain.
    # Return a processor that applies the computed gain.
    # For now, return processor that will apply a gain (set during pipeline execution)
    return {
        'type': 'gain',
        'gain_db': target_level,  # will be resolved at execution time
        'category': 'level',
    }


def op_gain(engine, amount_db=0.0, **kwargs):
    """Apply linear gain amplification or attenuation."""
    return {
        'type': 'gain',
        'gain_db': float(amount_db),
        'category': 'level',
    }


def op_time_stretch(engine, factor=1.0, preset="Studio", **kwargs):
    """Time-stretch without pitch change using the built-in time-stretch processor."""
    # DawDreamer's PlaybackWarp processor handles time-stretching
    return {
        'type': 'time_stretch',
        'factor': float(factor),
        'preserve_formants': kwargs.get('preserve_formants', True),
        'preset': preset,
        'category': 'tempo',
    }


def op_pitch_shift(engine, semitones=0.0, **kwargs):
    """Pitch shift without tempo change."""
    # Implemented as time-stretch with inverse factor + pitch offset?
    # Actually, use PlaybackWarp with pitch shift parameter
    return {
        'type': 'pitch_shift',
        'semitones': float(semitones),
        'preserve_formants': kwargs.get('preserve_formants', True),
        'category': 'pitch',
    }


def op_fade_in(engine, duration=0.0, **kwargs):
    """Fade in from silence."""
    return {
        'type': 'fade',
        'direction': 'in',
        'duration': float(duration),
        'category': 'edit',
    }


def op_fade_out(engine, duration=0.0, **kwargs):
    """Fade out to silence."""
    return {
        'type': 'fade',
        'direction': 'out',
        'duration': float(duration),
        'category': 'edit',
    }


def op_trim(engine, start=0.0, end=None, duration=None, **kwargs):
    """Extract audio segment."""
    return {
        'type': 'trim',
        'start': float(start),
        'end': float(end) if end is not None else None,
        'duration': float(duration) if duration is not None else None,
        'category': 'edit',
    }


def op_compress(engine, threshold=-20.0, ratio=4.0, attack=2.0, release=50.0, **kwargs):
    """Dynamic range compression."""
    return {
        'type': 'compressor',
        'threshold': float(threshold),
        'ratio': float(ratio),
        'attack': float(attack),
        'release': float(release),
        'category': 'dynamics',
    }


def op_filter(engine, mode='low', freq=1000.0, q=0.707, gain=1.0, **kwargs):
    """IIR filter — modes: low, high, band, low_shelf, high_shelf, notch."""
    return {
        'type': 'filter',
        'mode': str(mode),
        'freq': float(freq),
        'q': float(q),
        'gain': float(gain),
        'category': 'filter',
    }


def op_reverb(engine, room_size=0.5, damping=0.5, wet=0.33, dry=0.4, width=1.0, **kwargs):
    """Algorithmic reverb."""
    return {
        'type': 'reverb',
        'room_size': float(room_size),
        'damping': float(damping),
        'wet': float(wet),
        'dry': float(dry),
        'width': float(width),
        'category': 'spatial',
    }


def op_equalizer(engine, bands=None, **kwargs):
    """Multi-band EQ.

    bands: list of dicts with {freq, gain, q}
    """
    if bands is None:
        bands = []
    return {
        'type': 'equalizer',
        'bands': bands,
        'category': 'filter',
    }


def op_overlay(engine, track_b, **kwargs):
    """Mix another file on top of this one (sample-aligned overlay)."""
    return {
        'type': 'overlay',
        'track_b': str(track_b),
        'position': float(kwargs.get('position', 0.0)),
        'gain_a': float(kwargs.get('gain_a', 0.0)),
        'gain_b': float(kwargs.get('gain_b', 0.0)),
        'category': 'mixing',
    }


def op_add_track(engine, track_path, gain_db=0.0, pan=0.0, **kwargs):
    """Add a stem to the mix (used in multi-track builds)."""
    return {
        'type': 'add_track',
        'track': str(track_path),
        'gain_db': float(gain_db),
        'pan': float(pan),
        'category': 'mixing',
    }


def op_load_vst(engine, path, plugin_idx=0, **kwargs):
    """Load a VST/VST3 plugin host."""
    return {
        'type': 'load_vst',
        'path': str(path),
        'plugin_idx': int(plugin_idx),
        'category': 'plugin',
    }


def op_set_param(engine, plugin_idx=0, param='', value=0.0, **kwargs):
    """Set a VST plugin parameter."""
    return {
        'type': 'set_param',
        'plugin_idx': int(plugin_idx),
        'param': str(param),
        'value': float(value),
        'category': 'plugin',
    }


def op_chain(audio, engine, operations, **kwargs):
    """Execute a sub-chain of operations (nested pipeline)."""
    # This is handled at pipeline level, not as a processor
    raise NotImplementedError("op_chain is handled by pipeline executor")


# Registry
OP_REGISTRY = {
    'normalize': op_normalize,
    'gain': op_gain,
    'volume': op_gain,
    'time_stretch': op_time_stretch,
    'stretch': op_time_stretch,
    'pitch_shift': op_pitch_shift,
    'fade_in': op_fade_in,
    'fade_out': op_fade_out,
    'trim': op_trim,
    'crop': op_trim,
    'compress': op_compress,
    'compressor': op_compress,
    'filter': op_filter,
    'eq': op_equalizer,
    'equalizer': op_equalizer,
    'reverb': op_reverb,
    'overlay': op_overlay,
    'add_track': op_add_track,
    'load_vst': op_load_vst,
    'set_param': op_set_param,
}
