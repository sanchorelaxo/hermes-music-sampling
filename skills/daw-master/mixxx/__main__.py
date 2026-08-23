"""Runnable entry for the Mixxx skill CLI.

Usage:
    python skills/daw-master/mixxx/__main__.py playlists list
    python skills/daw-master/mixxx/__main__.py library list --limit 20
    python skills/daw-master/mixxx/__main__.py mix create 8 -o /tmp/mix.mp3 --crossfade 6
    python skills/daw-master/mixxx/__main__.py autopilot a.mp3 b.mp3 --dry-run
"""
import os
import sys

# Make the daw-master parent importable so `import mixxx` resolves to this dir.
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_THIS_DIR)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from mixxx.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
