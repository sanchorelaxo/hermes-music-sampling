#!/usr/bin/env python3
"""
audio-analyzer example 01_basic
Demonstrates single-file analysis with all core features.
Place an input.wav in the same directory before running, or pass path as argument.
"""

import sys
import json
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from skills.daw_master.audio_analyzer import analyze, probe

INPUT = sys.argv[1] if len(sys.argv) > 1 else "input.wav"

print(f"{'='*50}")
print(f"Analyzing: {INPUT}")
print(f"{'='*50}")

# Quick probe first
meta = probe(INPUT)
print(f"\n[Metadata]")
print(f"  Duration    : {meta.get('duration', 'n/a'):.2f}s")
print(f"  Sample rate : {meta.get('sample_rate', 'n/a')} Hz")
print(f"  Channels    : {meta.get('channels', 'n/a')}")
print(f"  Format      : {meta.get('format', 'unknown')}")

# Full analysis
print(f"\n[Feature Extraction]")
features = analyze(INPUT)

# Print in a clean table
key_features = [
    ("Tempo", "tempo", "%.1f BPM"),
    ("Tempo conf.", "tempo_confidence", "%.2f"),
    ("Key", "key", "%s"),
    ("Key conf.", "key_confidence", "%.2f"),
    ("Loudness", "loudness", "%.1f dB"),
    ("Spectral cent.", "spectral_centroid", "%.0f Hz"),
    ("Spectral rolloff", "spectral_rolloff", "%.0f Hz"),
    ("Flatness", "spectral_flatness", "%.3f"),
    ("Harmonic ratio", "harmonic_ratio", "%.3f"),
    ("Percussive ratio", "percussive_ratio", "%.3f"),
    ("Onset count", "onset_count", "%d"),
    ("Zero-crossing rate", "zero_crossing_rate", "%.4f"),
]

for label, key, fmt in key_features:
    if key in features:
        print(f"  {label:<20}: {fmt % features[key]}")

# MFCC summary (first 5 coefficients)
if "mfcc" in features:
    mfcc_mean = features["mfcc"]["mean"]
    print(f"\n  MFCC (first 5 mean):")
    for i, v in enumerate(mfcc_mean[:5]):
        print(f"    MFCC-{i+1}: {v:.2f}")

# Vamp plugins (if available)
if "vamp_plugins" in features and features["vamp_plugins"]:
    print(f"\n[Vamp Plugins]")
    for plugin, data in features["vamp_plugins"].items():
        if plugin.startswith("_"):
            continue
        print(f"  {plugin}: count={data.get('count', 0)}, mean={data.get('mean', 'n/a')}")

print(f"\n{'='*50}")
print("Done. Full JSON printed above for piping.")
print(f"{'='*50}")

# Also print raw JSON for downstream consumption
print("\n--- JSON OUTPUT ---")
print(json.dumps(features, indent=2, ensure_ascii=False))
