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


def op_trim(engine, start=None, end=None, **kwargs):
    """Trim audio segment."""
    return {'type': 'trim', 'start': start, 'end': end}


# Registry of operation builders for pipeline construction.
OP_REGISTRY = {
    'load_vst': op_load_vst,
    'set_param': op_set_param,
    'gain': op_gain,
    'normalize': op_normalize,
    'fade_in': op_fade_in,
    'fade_out': op_fade_out,
    'time_stretch': op_time_stretch,
    'pitch_shift': op_pitch_shift,
    'trim': op_trim,
}
