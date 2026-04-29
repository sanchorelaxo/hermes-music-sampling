#!/usr/bin/env python3
"""
audio-analyzer example 03_vamp
Demonstrates Vamp plugin extraction via sonic-annotator.
This example only works if sonic-annotator and Vamp plugins are installed.
If not available, it falls back to showing a message.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from skills.daw_master.audio_analyzer import analyze, DEPENDENCIES

INPUT = sys.argv[1] if len(sys.argv) > 1 else "input.wav"

print(f"{'='*50}")
print(f"Vamp Plugin Analysis Demo")
print(f"  Input   : {INPUT}")
print(f"{'='*50}")

# Check availability
if not DEPENDENCIES["sonic_annotator"]:
    print("\nNOTE: sonic-annotator not found in PATH.")
    print("Install it to enable Vamp plugin analysis:")
    print("  sudo apt install sonic-annotator")
    print("  # and install Vamp plugin packs e.g., qm-vamp-plugins")
    sys.exit(0)

# Run analysis WITH vamp plugins
print(f"\nAnalyzing with Vamp plugins enabled...")
features = analyze(INPUT, features=["vamp"])

if "vamp_plugins" in features:
    vamp = features["vamp_plugins"]
    if vamp and not vamp.get("_error"):
        print(f"\nVamp plugin results:")
        print(json.dumps(vamp, indent=2, ensure_ascii=False))
    elif vamp.get("_error"):
        print(f"\nVamp error: {vamp['_error']}")
    else:
        print(f"\nNo Vamp plugin output (no matching plugins installed?)")
else:
    print(f"\nNo vamp data in results")

print(f"\n{'='*50}")
