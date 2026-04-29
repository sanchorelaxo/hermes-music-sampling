"""
Rubber Band Engine — high-quality time-stretch & pitch-shift.

Example:
    from daw_master.rubber_band_engine import transform
    transform("in.wav", [{"op": "time_stretch", "factor": 0.88, "formant": True}], "out.wav")
"""

from .pipeline import transform, analyze, probe

__all__ = ['transform', 'analyze', 'probe']
