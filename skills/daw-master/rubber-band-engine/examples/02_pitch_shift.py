#!/usr/bin/env python3
"""
Example 2: Pitch-shift a piano sample up a perfect fifth (7 semitones) with formant correction.
"""
from daw_master.rubber_band_engine import transform

result = transform(
    input="piano_C4.wav",
    pipeline=[
        {"op": "pitch_shift", "semitones": 7.0, "formant": True, "quality": "ultra"},
    ],
    output="piano_G4.wav"
)

print(result)
