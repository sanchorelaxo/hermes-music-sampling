"""Mixxx CLI — library, playlists, cues, mix rendering, and autopilot.

Usage (from this repo):
    python -m skills.daw_master.mixxx.cli library list --limit 20
    python -m skills.daw_master.mixxx.cli playlists list
    python -m skills.daw_master.mixxx.cli playlists show <id>
    python -m skills.daw_master.mixxx.cli cues list <track_id>
    python -m skills.daw_master.mixxx.cli mix create <playlist_id> -o out.mp3 [--crossfade 6] [--align-bpm]
    python -m skills.daw_master.mixxx.cli export -o library.json
    python -m skills.daw_master.mixxx.cli autopilot <file1> <file2> --crossfade 8 --dry-run
    python -m skills.daw_master.mixxx.cli suggest "more energy"

Requires `click` (and `ffmpeg` for mix rendering, `python-rtmidi` for live
autopilot). Run with no args for a REPL.
"""
import json

import click

from . import library as lib
from . import playlists as pl
from . import cues as cues_mod
from . import decision as decision_mod
from . import autopilot as autopilot_mod
from .repl_skin import ReplSkin


@click.group(invoke_without_command=True)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output JSON")
@click.pass_context
def main(ctx, as_json):
    """Mixxx CLI harness. Run without args for REPL."""
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if ctx.invoked_subcommand is None:
        _repl(ctx)
        return


def _emit(ctx, data):
    if ctx.obj.get("as_json"):
        print(json.dumps(data, default=str))
    else:
        print(data)


def _table(ctx, headers, rows):
    if ctx.obj.get("as_json"):
        print(json.dumps(rows, default=str))
        return
    skin = ReplSkin("mixxx")
    skin.table(headers, [[r.get(h) for h in headers] for r in rows])


def _repl(ctx):
    skin = ReplSkin("mixxx", version="0.3.0")
    skin.print_banner()
    while True:
        try:
            line = skin.get_input()
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break
        if not line.strip():
            continue
        parts = line.strip().split()
        cmd = parts[0]
        if cmd in ("exit", "quit"):
            skin.print_goodbye()
            break
        if cmd == "library" and len(parts) > 1 and parts[1] == "list":
            limit = 10
            if len(parts) > 2:
                try:
                    limit = int(parts[2])
                except ValueError:
                    pass
            _table(ctx, ["id", "artist", "title", "duration"],
                   [{"id": r["id"], "artist": r.get("artist"), "title": r.get("title"),
                     "duration": r.get("duration")} for r in lib.list_tracks(limit=limit)])
            continue
        if cmd == "playlists" and len(parts) > 1 and parts[1] == "list":
            _table(ctx, ["id", "name", "track_count"],
                   [{"id": r["id"], "name": r["name"], "track_count": r["track_count"]}
                    for r in pl.list_playlists()])
            continue
        skin.info(f"Unknown command: {line}")


@main.group()
def library():
    """Library commands"""


@library.command("list")
@click.option("--limit", default=10, help="Limit number of tracks")
@click.pass_context
def list_cmd(ctx, limit):
    """List tracks from the Mixxx library"""
    rows = lib.list_tracks(limit=limit)
    _table(ctx, ["id", "artist", "title", "duration"], rows)


@main.group()
def playlists():
    """Playlist commands"""


@playlists.command("list")
@click.pass_context
def playlists_list(ctx):
    """List playlists"""
    rows = pl.list_playlists()
    _table(ctx, ["id", "name", "track_count"], rows)


@playlists.command("show")
@click.argument("playlist_id", type=int)
@click.pass_context
def playlists_show(ctx, playlist_id):
    """Show tracks in a playlist (id, artist, title, file)"""
    rows = pl.get_playlist_tracks(playlist_id)
    _table(ctx, ["id", "artist", "title", "file"],
           [{"id": r["id"], "artist": r.get("artist"), "title": r.get("title"), "file": r.get("file")}
            for r in rows])


@main.group()
def cues():
    """Cue commands"""


@cues.command("list")
@click.argument("track_id", type=int)
@click.pass_context
def cues_list(ctx, track_id):
    """List cues for a track"""
    rows = cues_mod.list_cues_for_track(track_id)
    _table(ctx, ["id", "type", "type_name", "position", "label"],
           [{"id": r["id"], "type": r.get("type"), "type_name": r.get("type_name"),
             "position": r.get("position"), "label": r.get("label")} for r in rows])


@main.command("export")
@click.option("--out", "-o", required=True, help="Output JSON file")
@click.pass_context
def export_library(ctx, out):
    """Export the library to a JSON file"""
    rows = lib.export_library()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, default=str, ensure_ascii=False, indent=2)
    print(f"Wrote {len(rows)} tracks to {out}")


@main.group()
def mix():
    """Mix creation commands"""


@mix.command("create")
@click.argument("playlist_id", type=int)
@click.option("--out", "-o", required=True, help="Output audio file")
@click.option("--crossfade", default=5.0, help="Crossfade duration in seconds")
@click.option("--align-bpm", is_flag=True, default=False, help="Align BPMs to first track")
@click.option("--codec", default="libmp3lame", help="ffmpeg audio codec")
@click.pass_context
def mix_create(ctx, playlist_id, out, crossfade, align_bpm, codec):
    """Create a mix from a playlist by rendering crossfaded tracks"""
    from . import exporter
    res = exporter.create_mix_from_playlist(
        playlist_id, out, crossfade=crossfade, align_bpm=align_bpm, codec=codec
    )
    if res.get("success"):
        print("Mix created:", out)
    else:
        print("Error creating mix:", res.get("message"))
        ctx.exit(1)


@main.command("autopilot")
@click.argument("input", nargs=-1, required=True)
@click.option("--crossfade", type=float, default=8.0)
@click.option("--port", help="MIDI port name to connect to (optional)")
@click.option("--autoplay/--no-autoplay", "autoplay", is_flag=True, default=True,
              help="Send play CC after loading (default on; disable with --no-autoplay)")
@click.option("--dry-run", is_flag=True, default=False, help="Print CCs without MIDI")
def autopilot_cmd(input, crossfade, port, autoplay, dry_run):
    """Run the MIDI autopilot crossfade sequence over the given files"""
    autopilot_mod.run_sequence(
        list(input), crossfade=crossfade, port_name=port,
        autoplay=not autoplay, dry_run=dry_run,
    )


@main.command("suggest")
@click.argument("text")
def suggest(text):
    """Map a natural-language suggestion to an autopilot action"""
    action = decision_mod.decide(text)
    print(json.dumps(action, indent=2))


if __name__ == "__main__":
    main()
