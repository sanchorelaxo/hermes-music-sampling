#!/usr/bin/env python3
"""
Example: slow down a file by 15% and fade out over 2 seconds.
"""
from dawdreamer import transform

result = transform(
    input="input.wav",
    pipeline=[
        {"op": "time_stretch", "factor": 0.88, "preserve_formants": True},
        {"op": "normalize", "target_level": -6},
        {"op": "fade_out", "duration": 2.0},
    ],
    output="output_slow_fade.wav"
)

print("Result:", result)
if result.get("success"):
    print(f"Wrote: {result['output']}")
else:
    print(f"Error: {result.get('error')}")
