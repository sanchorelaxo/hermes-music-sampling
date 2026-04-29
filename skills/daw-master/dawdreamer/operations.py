def op_load_vst(engine, path, plugin_idx=None, **kwargs):
    """Load a VST/VST3 plugin host.

    plugin_idx: Optional explicit index for naming/parameter targeting.
    If omitted, the pipeline executor will auto-assign a sequential ID.

    For VST3 bundles on Linux, pass the .vst3 directory as a file:// URI
    to satisfy VST3 SDK requirements.
    """
    from pathlib import Path

    p = Path(path)
    # Use plain absolute path for VST2 (.so/.dll) and file URI for .vst3 bundles
    if p.is_dir() and p.suffix == '.vst3':
        # VST3 bundles require a file URI to be loaded correctly
        path_str = p.absolute().as_uri()
    else:
        path_str = str(p.absolute())

    spec = {
        'type': 'load_vst',
        'path': path_str,
        'category': 'plugin',
    }
    if plugin_idx is not None:
        spec['plugin_idx'] = plugin_idx
    return spec


def op_set_param(engine, param, value, plugin_idx=0, **kwargs):
    """Set a plugin parameter."""
    return {'type': 'set_param', 'param': param, 'value': value, 'plugin_idx': plugin_idx}


def op_gain(engine, amount_db=None, gain=None, **kwargs):
    """Gain adjustment."""
    if amount_db is not None:
        return {'type': 'gain', 'gain_db': amount_db}
    else:
        return {'type': 'gain', 'gain': gain if gain is not None else 1.0}


def op_normalize(engine, target_level=-0.1, **kwargs):
    """Normalize audio to target level. Placeholder: actual gain computation not possible at build time."""
    # Since we cannot compute required gain without analyzing audio, return identity gain.
    return {'type': 'gain', 'gain_db': 0.0}


def op_fade_in(engine, duration, **kwargs):
    """Fade in over duration."""
    return {'type': 'fade', 'direction': 'in', 'duration': duration}


def op_fade_out(engine, duration, **kwargs):
    """Fade out over duration."""
    return {'type': 'fade', 'direction': 'out', 'duration': duration}


def op_time_stretch(engine, factor, preserve_formants=True, **kwargs):
    """Time stretch without pitch change."""
    return {'type': 'time_stretch', 'factor': factor, 'preserve_formants': preserve_formants}


def op_pitch_shift(engine, semitones, **kwargs):
    """Pitch shift by semitones."""
    return {'type': 'pitch_shift', 'semitones': semitones}


def op_fade_out(engine, duration, **kwargs):
    """Fade out over duration."""
    return {'type': 'fade', 'direction': 'out', 'duration': duration}


def op_trim(engine, start=None, end=None, **kwargs):
    """Trim audio segment."""
    return {'type': 'trim', 'start': start, 'end': end}


# ---------------------------------------------------------------------------
# Additional operations (aliases and extended effects)
# ---------------------------------------------------------------------------

def op_volume(engine, amount_db=None, gain=None, **kwargs):
    """Volume adjustment — alias for gain."""
    if amount_db is not None:
        return {'type': 'gain', 'gain_db': amount_db}
    else:
        return {'type': 'gain', 'gain': gain if gain is not None else 1.0}


def op_stretch(engine, factor, preserve_formants=True, **kwargs):
    """Time stretch — alias for time_stretch."""
    return {'type': 'time_stretch', 'factor': factor, 'preserve_formants': preserve_formants}


def op_crop(engine, start=None, end=None, **kwargs):
    """Crop audio — alias for trim."""
    return {'type': 'trim', 'start': start, 'end': end}


def op_compress(engine, threshold=-20.0, ratio=4.0, attack=2.0, release=50.0, **kwargs):
    """Dynamic range compression."""
    return {
        'type': 'compressor',
        'threshold': threshold,
        'ratio': ratio,
        'attack': attack,
        'release': release,
    }


def op_compressor(engine, threshold=-20.0, ratio=4.0, attack=2.0, release=50.0, **kwargs):
    """Dynamic range compression — alias for compress."""
    return op_compress(engine, threshold, ratio, attack, release)


def op_filter(engine, mode='low', freq=1000.0, q=0.707, gain=1.0, **kwargs):
    """Filter (lowpass/highpass/bandpass etc.)."""
    return {'type': 'filter', 'mode': mode, 'freq': freq, 'q': q, 'gain': gain}


def op_eq(engine, frequency=1000, width='2q', gain=0, **kwargs):
    """Equalizer — maps to filter with appropriate mode."""
    # Simple EQ maps to filter; width interpreted as q
    return {'type': 'filter', 'mode': 'peak', 'freq': frequency, 'q': float(width.replace('q', '')) if 'q' in str(width) else float(width), 'gain': gain}


def op_equalizer(engine, frequency=1000, width='2q', gain=0, **kwargs):
    """Equalizer — alias for eq."""
    return op_eq(engine, frequency, width, gain, **kwargs)


def op_reverb(engine, room_size=0.5, damping=0.5, wet=0.33, dry=0.4, width=1.0, **kwargs):
    """Convolution reverb."""
    return {
        'type': 'reverb',
        'room_size': room_size,
        'damping': damping,
        'wet': wet,
        'dry': dry,
        'width': width,
    }


def op_overlay(engine, track_b, gain_a=0.0, gain_b=0.0, position=0.0, **kwargs):
    """Overlay a second track on top of the input."""
    return {
        'type': 'overlay',
        'track_b': track_b,
        'gain_a': gain_a,
        'gain_b': gain_b,
        'position': position,
    }


def op_add_track(engine, track_b, gain_a=0.0, gain_b=0.0, **kwargs):
    """Add a track — alias for overlay."""
    return op_overlay(engine, track_b, gain_a, gain_b, **kwargs)


# Registry of operation builders for pipeline construction.
OP_REGISTRY = {
    'load_vst': op_load_vst,
    'set_param': op_set_param,
    'gain': op_gain,
    'volume': op_volume,
    'normalize': op_normalize,
    'fade_in': op_fade_in,
    'fade_out': op_fade_out,
    'time_stretch': op_time_stretch,
    'stretch': op_stretch,
    'pitch_shift': op_pitch_shift,
    'trim': op_trim,
    'crop': op_crop,
    'compress': op_compress,
    'compressor': op_compressor,
    'filter': op_filter,
    'eq': op_eq,
    'equalizer': op_equalizer,
    'reverb': op_reverb,
    'overlay': op_overlay,
    'add_track': op_add_track,
}
