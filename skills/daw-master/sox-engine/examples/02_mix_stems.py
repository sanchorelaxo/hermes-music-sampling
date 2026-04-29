#!/usr/bin/env python3
"""
Example 2: Mix two stems (vocals + instrumental) with different levels.
"""
from daw_master.sox_engine import mix

result = mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0},
        {"path": "instrumental.wav", "gain": 0.7},
    ],
    output="full_mix.wav",
    normalize_final=True
)

print("Mix result:")
print(f"  success: {result.get('success')}")
if result.get('success'):
    print(f"  output: {result['output']}")
    print(f"  tracks: {result['track_count']}")
else:
    print(f"  error: {result.get('error')}")
