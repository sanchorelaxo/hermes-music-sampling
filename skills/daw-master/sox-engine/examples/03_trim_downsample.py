#!/usr/bin/env python3
"""
Example 3: Trim a section, convert to mono, and downsample.
"""
from daw_master.sox_engine import transform

result = transform(
    input="long_recording.wav",
    pipeline=[
        {"op": "trim", "start": 12.5, "length": 30.0},   # extract 30s from 12.5s
        {"op": "channels", "count": 1},                  # mono
        {"op": "rate", "sample_rate": 22050},            # downsample
        {"op": "fade", "type": "in", "length": 0.2},     # short fade in
    ],
    output="excerpt_mono_22k.wav"
)

print(result)
