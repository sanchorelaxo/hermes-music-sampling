#!/usr/bin/env python3
"""
Example 1: Slow down vocal sample 15% while preserving formants (vocal timbre).
Uses Rubber Band's high-quality mode.
"""
from daw_master.rubber_band_engine import transform

result = transform(
    input="vocals.wav",
    pipeline=[
        {"op": "time_stretch", "factor": 0.88, "formant": True, "quality": "high"},
    ],
    output="vocals_slow_preserve_formant.wav"
)

print("Result:", result)
if result.get('success'):
    print(f"Wrote: {result['output']}")
else:
    print(f"Error: {result.get('error')}")
