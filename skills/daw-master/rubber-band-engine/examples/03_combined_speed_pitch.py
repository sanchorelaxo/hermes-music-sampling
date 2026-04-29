#!/usr/bin/env python3
"""
Example 3: Speed up sample 20% and pitch up 3 semitones (chipmunk-style, formants OFF).
Good for sound design or making samples brighter/faster.
"""
from daw_master.rubber_band_engine import transform

result = transform(
    input="vocal_phrase.wav",
    pipeline=[
        {"op": "time_stretch", "factor": 1.20, "formant": False, "quality": "high"},
        {"op": "pitch_shift", "semitones": 3.0, "formant": False},
    ],
    output="vocal_phrase_chipmunk.wav"
)

print("Chipmunk result:", result)
