#!/usr/bin/env python3
"""
Example 1: List tracks and playlists from the Mixxx library.

Shows the read-only DB layer resolving real file paths.

Run from repo root:
    python skills/daw-master/mixxx/examples/01_list_library.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import mixxx  # noqa: E402


def main():
    print("=== Mixxx library (first 5) ===")
    for t in mixxx.library.list_tracks(limit=5):
        print(f"  #{t['id']}  {(t.get('artist') or '?')} - {(t.get('title') or '?')}"
              f"  [{t.get('bpm')} BPM] -> {t.get('file')}")

    print("\n=== Playlists ===")
    for p in mixxx.playlists.list_playlists():
        print(f"  #{p['id']}  {p['name']}  ({p['track_count']} tracks)")


if __name__ == "__main__":
    main()
