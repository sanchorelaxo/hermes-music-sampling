#!/usr/bin/env python3
"""
Example 1: Normalize, fade, and compress a sample.
"""
from daw_master.sox_engine import transform

result = transform(
    input="input.wav",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10},
        {"op": "fade", "type": "out", "length": 1.5},
    ],
    output="output_balanced.wav"
)

print("Transform result:")
print(f"  success: {result.get('success')}")
if result.get('success'):
    print(f"  output: {result['output']}")
    print(f"  command: {result.get('command', 'n/a')}")
else:
    print(f"  error: {result.get('error')}")
