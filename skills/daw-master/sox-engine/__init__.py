"""
SoX Engine — high-level API for audio transformation and analysis.

Example usage:

    from daw_master.sox_engine import transform, mix, analyze

    # Transform
    transform("in.wav", [{"op": "normalize"}, {"op": "fade", "type": "out", "length": 2.0}], "out.wav")

    # Mix tracks
    mix([{"path": "a.wav", "gain": 1.0}, {"path": "b.wav", "gain": 0.7}], "mix.wav", normalize_final=True)

    # Analyze
    info = analyze("sample.wav")
    print(f"Duration: {info['duration']}s, Peak: {info['peak']:.2f}")
"""

from .pipeline import transform, mix, analyze, probe

__all__ = ['transform', 'mix', 'analyze', 'probe']
