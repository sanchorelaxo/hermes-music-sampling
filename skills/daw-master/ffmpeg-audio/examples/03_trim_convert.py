#!/usr/bin/env python3
"""
Example 3: Trim excerpt, resample, and convert to MP3.
Shows precise sample-accurate trimming and format conversion.
"""
from daw_master.ffmpeg_audio import transform

result = transform(
    input="long_recording.wav",
    pipeline=[
        {"op": "atrim", "start": 30.0, "end": 90.0},       # keep 60s from 30s mark
        {"op": "volume", "gain": "1.5dB"},                 # gentle boost
        {"op": "acompressor", "threshold": "-18dB", "ratio": 3},  # smooth compression
    ],
    output="excerpt.mp3",
    codec="libmp3lame",
    bitrate="192k"
)

print(result)
print(f"Command: {result.get('command', '')[:140]}")
