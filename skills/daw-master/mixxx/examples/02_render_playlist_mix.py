#!/usr/bin/env python3
"""
Example 2: Render a crossfaded DJ mix from a Mixxx playlist.

Picks the playlist with the most on-disk files and renders it to /tmp.

Run from repo root:
    python skills/daw-master/mixxx/examples/02_render_playlist_mix.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import mixxx  # noqa: E402


def main():
    # Find the playlist with the most existing files.
    best, best_hits = None, 0
    for p in mixxx.playlists.list_playlists():
        if p["track_count"] == 0:
            continue
        files = mixxx.playlists.existing_files(p["id"])
        if len(files) > best_hits:
            best, best_hits = p, len(files)
    if best is None:
        print("No populated playlists with existing files.")
        return

    out = f"/tmp/mixxx_mix_pl{best['id']}.mp3"
    print(f"Rendering playlist #{best['id']} '{best['name']}' "
          f"({best_hits} tracks) -> {out}")

    res = mixxx.exporter.create_mix_from_playlist(best["id"], out, crossfade=6.0)
    if res["success"]:
        size = os.path.getsize(out) / 1e6
        print(f"OK: {out} ({size:.1f} MB)")
    else:
        print("FAILED:", res["message"][-500:])


if __name__ == "__main__":
    main()
