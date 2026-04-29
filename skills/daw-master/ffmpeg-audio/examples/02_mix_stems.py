#!/usr/bin/env python3
"""
Example 2: Mix 3 stems with different levels, panning, and a per-track highpass.

Mixes vocals (center), drums (stereo spread), bass (center, louder).
"""
from daw_master.ffmpeg_audio import mix

result = mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0, "pan": "FC"},       # front-center mono
        {"path": "drums.wav", "gain": 0.7, "pan": "FL+FR",      # stereo wide
         "filters": ["highpass=f=80"]},
        {"path": "bass.wav", "gain": 1.2, "pan": "FC"},         # center, boost
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
