"""
FFmpeg Audio Engine — FFmpeg filtergraph wrapper.

Example:
    from daw_master.ffmpeg_audio import transform, mix, analyze, ebu_r128_analysis

    transform("input.wav", [
        {"op": "volume", "gain": "-3dB"},
        {"op": "acompressor", "threshold": "-20dB", "ratio": 3},
        {"op": "loudnorm", "i": -16}
    ], "output.m4a", codec="aac")
"""

from .pipeline import transform, mix, analyze, probe, ebu_r128_analysis

__all__ = ['transform', 'mix', 'analyze', 'probe', 'ebu_r128_analysis']
