#!/usr/bin/env python3
"""
audio-analyzer example 02_batch
Batch analyze a directory of audio files and export to CSV.
Usage: python 02_batch.py [directory] [pattern]
Example: python 02_batch.py ./samples "*.wav"
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from skills.daw_master.audio_analyzer import extract_batch

# Arguments
directory = sys.argv[1] if len(sys.argv) > 1 else "samples"
pattern = sys.argv[2] if len(sys.argv) > 2 else "*.wav"

print(f"{'='*50}")
print(f"Batch Audio Analysis")
print(f"  Directory : {directory}")
print(f"  Pattern   : {pattern}")
print(f"{'='*50}")

# Run batch extraction (CSV output)
output = extract_batch(
    directory=directory,
    pattern=pattern,
    output_format="csv",
    output_file=None  # auto-generate
)

if output:
    print(f"\nResults written to: {output}")
    # Show first few lines of CSV
    p = Path(output)
    if p.exists():
        print("\n--- CSV Preview (first 6 lines) ---")
        with p.open() as f:
            for i, line in enumerate(f):
                if i >= 6:
                    print("  ...")
                    break
                print(f"  {line.rstrip()}")
else:
    print("\nNo output generated (no matching files found).")

print(f"\n{'='*50}")
