#!/usr/bin/env python3
"""
Example 1: Loudness normalization (broadcast quality) + light compression.
"""
from daw_master.ffmpeg_audio import transform

result = transform(
    input="input.wav",
    pipeline=[
        {"op": "highpass", "cutoff": 80},              # remove sub-bass rumble
        {"op": "acompressor", "threshold": "-22dB", "ratio": 2.5, "attack": 5, "release": 50},
        {"op": "loudnorm", "i": -16, "lra": 8, "tp": -1},  # streaming loudness
    ],
    output="output_normalized.m4a",
    codec="aac"
)

print("Transform result:")
print(f"  success: {result.get('success')}")
if result.get('success'):
    print(f"  output: {result['output']}")
    print(f"  filter: {result.get('filter_string')}")
    print(f"  command: {result.get('command', '')[:120]}...")
else:
    print(f"  error: {result.get('error')}")
