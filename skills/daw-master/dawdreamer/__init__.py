
"""
DawDreamer Skill — wrapper around the DawDreamer Python framework.

Exposes a pipeline-friendly interface for audio transformations:
  transform(input, pipeline=[...], output=...)
  mix(tracks=[...], output=...)
  analyze(file) -> dict

All operations are file-based: reads from disk, writes to disk.
No in-memory buffers leak between calls — clean, stateless, composable.
"""

from .pipeline import transform, mix, analyze, DawDreamerEngine
from .operations import (
    op_normalize,
    op_gain,
    op_time_stretch,
    op_pitch_shift,
    op_fade_in,
    op_fade_out,
    op_trim,
    op_compress,
    op_reverb,
    op_chain,
)

__all__ = [
    'transform',
    'mix',
    'analyze',
    'DawDreamerEngine',
    # individual ops for pipeline construction
    'op_normalize',
    'op_gain',
    'op_time_stretch',
    'op_pitch_shift',
    'op_fade_in',
    'op_fade_out',
    'op_trim',
    'op_compress',
    'op_reverb',
    'op_chain',
]
