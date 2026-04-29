#!/usr/bin/env python3
"""
Example: mix two stems (vocals + instrumental) with level balance.
"""
from dawdreamer import mix

result = mix(
    tracks=[
        {"path": "vocals.wav", "gain_db": 0.0, "pan": 0.0},
        {"path": "instrumental.wav", "gain_db": -3.0, "pan": 0.2},
    ],
    output="full_mix.wav",
    normalize_final=True
)

print("Mix result:", result)
