#!/usr/bin/env python3
"""
Example 3: Autopilot dry-run — print the MIDI CC crossfade sequence.

Safe to run anywhere (no MIDI, no Mixxx needed). For a live run, remove
dry_run=True and configure the controller mapping first (see
references/controller-mapping.md).

Run from repo root:
    python skills/daw-master/mixxx/examples/03_autopilot_dryrun.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import mixxx  # noqa: E402


def main():
    # Pull two real files from playlists (more likely to be on disk than the
    # first library rows, which may be stale). Fall back to scanning the library.
    files = []
    for p in mixxx.playlists.list_playlists():
        files += mixxx.playlists.existing_files(p["id"])
        if len(files) >= 2:
            break
    files = files[:2]
    if len(files) < 2:
        tracks = mixxx.library.list_tracks(limit=50)
        files = [t["file"] for t in tracks if t.get("file") and os.path.exists(t["file"])][:2]

    if len(files) < 2:
        print("Need at least 2 existing files in the library; found:",
              [f for f in files])
        return

    print("Autopilot dry-run for:", [os.path.basename(f) for f in files])
    mixxx.autopilot.run_sequence(files, crossfade=8.0, dry_run=True)

    print("\nSuggestion mapping demo:")
    for s in ["more energy", "calm", "crossfade to 12", "play next"]:
        print(f"  {s!r:20} -> {mixxx.decision.decide(s)}")


if __name__ == "__main__":
    main()
