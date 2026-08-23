---
name: daw-master:mixxx
description: "Use when working with Mixxx DJ software — reading the Mixxx library/playlists/cues from its SQLite DB, rendering crossfaded DJ mixes from playlists via ffmpeg, and driving the MIDI autopilot for live-set crossfades. Read-only DB access, safe against a running Mixxx."
version: 1.0.0
author: Ported from cli-anything-mixxx (Hype-Cartel)
license: MIT
metadata:
  hermes:
    tags: ["mixxx", "dj", "playlists", "library", "cues", "crossfade", "ffmpeg", "autopilot", "midi", "sqlite"]
    related_skills: ["daw-master:ffmpeg-audio", "daw-master:sox-engine", "daw-master:audio-analyzer"]
---

# Mixxx (DJ Library + Autopilot)

Programmatic access to the [Mixxx](https://mixxx.org/) DJ software: read the
track library, playlists, and cue points from its SQLite database, render
crossfaded DJ mixes from playlists with ffmpeg, and (optionally) drive live-set
crossfades over MIDI with the autopilot.

**Role**: A DJ set builder + library browser. It does **not** control the Mixxx
GUI or audio engine — it reads `mixxxdb.sqlite` read-only and uses ffmpeg to
render mixes from the underlying audio files.

**Primary tools**: `mixxx.library`, `mixxx.playlists`, `mixxx.cues`,
`mixxx.exporter`, `mixxx.autopilot`, `mixxx.decision`

## When to Use

- "List tracks in my Mixxx library" / "what playlists do I have?"
- "Render a DJ mix from playlist X" / "crossfade these tracks together"
- "Show cue points / hot cues for a track"
- Automating a live set: load a track, start playback, crossfade to the next
- Mapping natural-language suggestions ("more energy", "crossfade to 12") to
  autopilot actions

## When NOT to Use

- Simple single-file audio edits (fade/trim/normalize) — use `sox-engine` /
  `ffmpeg-audio` directly
- Beat-synced DJ transitions with perfect timing — the autopilot uses stored
  BPMs for alignment but is beat-agnostic in its default demo sequence
- Mastering or loudness normalization — use `mastering-engineer`

## Location & Data Source

```
skills/daw-master/mixxx/
├── __init__.py      # package: library, playlists, cues, exporter, decision, autopilot
├── __main__.py      # CLI entry: python skills/daw-master/mixxx/__main__.py ...
├── cli.py           # click-based CLI (REPL with no args)
├── library.py       # read-only DB layer + path resolution
├── playlists.py     # playlist listing + track resolution
├── cues.py          # cue/hotcue/loop reads
├── exporter.py      # ffmpeg acrossfade mix rendering
├── decision.py      # natural-language -> autopilot action
├── autopilot.py     # rtmidi crossfade agent (optional dep)
├── repl_skin.py     # terminal UI helpers
├── references/
│   ├── db-schema.md        # modern vs legacy Mixxx schema notes
│   └── controller-mapping.md  # MIDI CC mapping for Mixxx Preferences
└── examples/
    ├── 01_list_library.py
    ├── 02_render_playlist_mix.py
    └── 03_autopilot_dryrun.py
```

The database is auto-detected (first path that exists):

1. `~/.var/app/org.mixxx.Mixxx/.mixxx/mixxxdb.sqlite` — **flatpak** install (this machine: Mixxx 2.5.6, live)
2. `~/snap/mixxx-community/common/.mixxx/mixxxdb.sqlite` — snap install
3. `~/.mixxx/mixxxdb.sqlite` — classic install

Override with the `MIXXX_DB_PATH` env var (also used by the tests). All DB
connections are opened **read-only**, so this is safe while Mixxx is running.

## Quick Reference (CLI)

```
python skills/daw-master/mixxx/__main__.py library list --limit 20
python skills/daw-master/mixxx/__main__.py playlists list
python skills/daw-master/mixxx/__main__.py playlists show <playlist_id>
python skills/daw-master/mixxx/__main__.py cues list <track_id>
python skills/daw-master/mixxx/__main__.py mix create <playlist_id> -o out.mp3 [--crossfade 6] [--align-bpm]
python skills/daw-master/mixxx/__main__.py export -o library.json
python skills/daw-master/mixxx/__main__.py autopilot a.mp3 b.mp3 --dry-run
python skills/daw-master/mixxx/__main__.py suggest "more energy"
```

`--json` on the top level switches to machine-readable JSON output. Run with no
arguments for an interactive REPL.

## Library API

```python
import mixxx

tracks = mixxx.library.list_tracks(limit=10)      # [ {id, artist, title, duration, bpm, key, file, ...} ]
t = mixxx.library.get_track(track_id)             # single track dict or None
all_tracks = mixxx.library.export_library()       # full library (JSON-serializable)
```

Every track dict includes `file` — the **resolved absolute path** (see
`references/db-schema.md` for the modern `library.location` →
`track_locations.id` join).

## Playlists

```python
pls = mixxx.playlists.list_playlists()            # [ {id, name, track_count, hidden} ]
tracks = mixxx.playlists.get_playlist_tracks(pid) # ordered, with resolved 'file'
files = mixxx.playlists.existing_files(pid)       # only those on disk
```

## Cues

```python
cues = mixxx.cues.list_cues_for_track(track_id)
# [ {id, type, type_name, position, length, hotcue, label, color} ]
```

Cue types: `cue`, `main_cue`, `hotcue`, `loop`, `beatloop`, `intro`, `outro`,
`beatjump`, `preroll`. Positions are in frames (44100 = 1s).

## Mix Rendering

```python
from mixxx.exporter import create_mix_from_playlist, create_mix_from_track_files

res = create_mix_from_playlist(playlist_id, "out.mp3", crossfade=6.0, align_bpm=True)
res = create_mix_from_track_files(["a.mp3", "b.flac"], "out.mp3", crossfade=5.0, align_bpm=True, bpms=[120.0, 90.0])
# -> {"success": bool, "message": str, "out": str}
```

- Requires `ffmpeg` in PATH.
- Missing files are **filtered out** silently (playlist 8 on this machine has
  2 dead paths; the mix still renders from the rest).
- `align_bpm=True` atempo-stretches each track to the first track's stored BPM
  (handles factors outside atempo's 0.5–2.0 range by chaining filters).
- Codec defaults to `libmp3lame`; pass `codec="aac"` etc. for others.

## Autopilot (MIDI)

```python
from mixxx.autopilot import run_sequence

run_sequence(["a.mp3", "b.mp3"], crossfade=8.0, dry_run=True)   # print CCs only
run_sequence(["a.mp3", "b.mp3"], crossfade=8.0)                  # live (needs rtmidi + virtual MIDI port)
```

The sequence: load track A into deck 1 → play → wait `durationA − crossfade` →
load track B into deck 2 → play → ramp the crossfader across `crossfade` secs.

Requires `python-rtmidi` (optional). Without it, only `dry_run=True` works.

Full MIDI controller mapping (Mixxx Preferences → Controllers): [references/controller-mapping.md](mdc:references/controller-mapping.md)

## Decision (natural-language → action)

```python
from mixxx.decision import decide

decide("more energy")       # -> {"type": "play_next", "params": {"crossfade": 6.0}}
decide("crossfade to 12")   # -> {"type": "set_crossfade", "params": {"value": 127}}
decide("load deck 2")       # -> {"type": "load_and_play", "params": {"slot": 2}}
```

Useful for an agent loop: take a free-text suggestion, map to an autopilot
action, and run it. Ported from Hype-Cartel's autopilot decision module.

## Dependencies

- Python stdlib + `click` for the CLI (already installed on this machine).
- `ffmpeg` + `ffprobe` for mix rendering and duration probing.
- `python-rtmidi` only for live (non-dry-run) autopilot — optional.

## Testing

```
python3 -m pytest tests/test_mixxx.py -v
```

17 tests cover the synthetic modern-schema DB, exporter command construction,
decision mapping, and live integration against the flatpak DB (auto-skipped if
the DB is absent).

## Common Pitfalls

1. **Zero-byte / fake files break ffmpeg.** The unit tests create real sine
   WAV/MP3s via ffmpeg for the render test — touching empty files with
   `Path.touch()` makes ffmpeg fail with "Could not seek".
2. **`-map [0:a]` fails without a filter_complex.** When rendering a single
   file (no crossfade), the exporter maps `0:a` (no brackets). Keep it that way.
3. **The snap install may have no database.** On this machine the snap
   (`mixxx-community` 2.4.0) only has logs — the flatpak (2.5.6) owns the live
   `mixxxdb.sqlite`. Use the flatpak DB.
4. **Modern schema has no `library.filepath`.** Upstream cli-anything-mixxx
   looked for that column and would return empty playlists on Mixxx 2.4+.
   This port joins `library.location` → `track_locations.id`.
5. **Cue type 8** (`preroll`, Mixxx 2.5+) — older docs stop at type 7. The map
   includes it.
6. **BPMs of 0 / None** are treated as "unknown" and skipped by alignment.
7. **Live autopilot needs a real MIDI route.** Without a virtual port /
   `jack`-style routing, `open_virtual_port` may fail; always verify with
   `--dry-run` first.

## Verification Checklist

- [ ] `mixxx.library.list_tracks()` returns tracks with resolved `file` paths
- [ ] `playlists show <id>` lists the playlist's tracks in order
- [ ] `mix create <id> -o /tmp/mix.mp3` renders a playable file (non-silent)
- [ ] Single-file mixes render (no `[0:a]` filtergraph error)
- [ ] `autopilot ... --dry-run` prints the CC sequence
- [ ] `decide("more energy")` returns a valid action dict
- [ ] All 17 tests pass (`tests/test_mixxx.py`)
