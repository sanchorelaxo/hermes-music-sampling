"""Tests for the Mixxx DAW skill (skills/daw-master/mixxx).

Covers: library/playlist/cue reads against a synthetic modern-schema DB,
exporter command building, decision mapping, and live-DB integration when the
flatpak Mixxx database is present (skipped otherwise).
"""
import os
import sqlite3
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "skills" / "daw-master" / "mixxx"
sys.path.insert(0, str(SKILL_DIR.parent))  # make `import mixxx` work

import mixxx  # noqa: E402


@pytest.fixture()
def fake_db(tmp_path):
    """Create a modern-schema Mixxx DB (library.location -> track_locations.id)
    with a few tracks, a playlist, and cues. Returns the db path."""
    db = tmp_path / "mixxxdb.sqlite"
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE track_locations (
            id INTEGER PRIMARY KEY,
            location TEXT
        );
        CREATE TABLE library (
            id INTEGER PRIMARY KEY,
            artist TEXT,
            title TEXT,
            album TEXT,
            duration REAL,
            bpm REAL,
            key TEXT,
            location INTEGER,
            mixxx_deleted INTEGER DEFAULT 0
        );
        CREATE TABLE Playlists (
            id INTEGER PRIMARY KEY,
            name TEXT,
            hidden INTEGER DEFAULT 0
        );
        CREATE TABLE PlaylistTracks (
            id INTEGER PRIMARY KEY,
            playlist_id INTEGER,
            track_id INTEGER,
            position INTEGER
        );
        CREATE TABLE cues (
            id INTEGER PRIMARY KEY,
            track_id INTEGER,
            type INTEGER,
            position INTEGER,
            length INTEGER,
            hotcue INTEGER,
            label TEXT,
            color TEXT
        );
        """
    )
    # Track locations
    loc1 = str(tmp_path / "song1.mp3")
    loc2 = str(tmp_path / "song2.mp3")
    loc3 = str(tmp_path / "song3.flac")
    Path(loc1).touch()
    Path(loc2).touch()
    cur.execute("INSERT INTO track_locations VALUES (1, ?)", (loc1,))
    cur.execute("INSERT INTO track_locations VALUES (2, ?)", (loc2,))
    cur.execute("INSERT INTO track_locations VALUES (3, ?)", (loc3,))
    # Library tracks
    cur.execute(
        "INSERT INTO library (id,artist,title,album,duration,bpm,key,location,mixxx_deleted) "
        "VALUES (1,'Artist A','Track One','Album 1',240,120.0,'8A',1,0)"
    )
    cur.execute(
        "INSERT INTO library (id,artist,title,album,duration,bpm,key,location,mixxx_deleted) "
        "VALUES (2,'Artist B','Track Two','Album 2',200,90.0,'2A',2,0)"
    )
    cur.execute(
        "INSERT INTO library (id,artist,title,album,duration,bpm,key,location,mixxx_deleted) "
        "VALUES (3,'Artist C','Track Three','Album 3',180,140.0,'5B',3,1)"  # deleted
    )
    # Playlists
    cur.execute("INSERT INTO Playlists VALUES (1, 'Test Mix', 0)")
    cur.execute("INSERT INTO Playlists VALUES (2, 'Empty', 0)")
    cur.execute("INSERT INTO PlaylistTracks VALUES (1,1,1,0)")
    cur.execute("INSERT INTO PlaylistTracks VALUES (2,1,2,1)")
    # Cues
    cur.execute(
        "INSERT INTO cues VALUES (1,1,2,1000,0,1,'Drop','#ff0000')"   # hotcue
    )
    cur.execute(
        "INSERT INTO cues VALUES (2,1,3,2000,800,0,'','#00ff00')"     # loop
    )
    conn.commit()
    conn.close()
    return db


def test_list_tracks_resolves_paths(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    rows = mixxx.library.list_tracks(limit=10)
    assert len(rows) == 2  # deleted track excluded
    by_id = {r["id"]: r for r in rows}
    assert by_id[1]["file"] == str(fake_db.parent / "song1.mp3")
    assert by_id[2]["title"] == "Track Two"


def test_list_tracks_include_deleted(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    rows = mixxx.library.list_tracks(limit=10, include_deleted=True)
    assert len(rows) == 3


def test_get_track(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    t = mixxx.library.get_track(2)
    assert t["artist"] == "Artist B"
    assert t["file"] == str(fake_db.parent / "song2.mp3")
    assert mixxx.library.get_track(999) is None


def test_export_library(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    rows = mixxx.library.export_library()
    assert len(rows) == 2
    assert all(r.get("file") for r in rows)


def test_playlists(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    pls = mixxx.playlists.list_playlists()
    by_id = {p["id"]: p for p in pls}
    assert by_id[1]["track_count"] == 2
    assert by_id[2]["track_count"] == 0
    tracks = mixxx.playlists.get_playlist_tracks(1)
    assert [t["title"] for t in tracks] == ["Track One", "Track Two"]
    assert tracks[0]["file"].endswith("song1.mp3")
    assert mixxx.playlists.get_playlist_tracks(99) == []


def test_cues(fake_db, monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    cues = mixxx.cues.list_cues_for_track(1)
    by_id = {c["id"]: c for c in cues}
    assert by_id[1]["type_name"] == "hotcue"
    assert by_id[1]["label"] == "Drop"
    assert by_id[2]["type_name"] == "loop"
    assert by_id[2]["length"] == 800
    assert mixxx.cues.list_cues_for_track(99) == []


def test_cue_type_names_cover_known():
    for t in range(0, 9):
        assert mixxx.cues.CUE_TYPE_NAMES[t]
    assert mixxx.cues.CUE_TYPE_NAMES[8] == "preroll"


def test_missing_db_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("MIXXX_DB_PATH", str(tmp_path / "nope.sqlite"))
    assert mixxx.library.list_tracks() == []
    assert mixxx.playlists.list_playlists() == []
    assert mixxx.cues.list_cues_for_track(1) == []


def test_build_single_file_no_filter():
    cmd, fc = mixxx.exporter.build_ffmpeg_mix_command(["/a.mp3"], "/out.mp3")
    assert fc is None
    assert "-map" in cmd


def test_build_two_file_crossfade():
    cmd, fc = mixxx.exporter.build_ffmpeg_mix_command(
        ["/a.mp3", "/b.mp3"], "/out.mp3", crossfade=5.0
    )
    assert "acrossfade=d=5.0" in fc
    assert fc.count("acrossfade") == 1


def test_build_three_file_chains():
    cmd, fc = mixxx.exporter.build_ffmpeg_mix_command(
        ["/a.mp3", "/b.mp3", "/c.mp3"], "/out.mp3", crossfade=3.0
    )
    assert fc.count("acrossfade") == 2


def test_build_align_bpm():
    cmd, fc = mixxx.exporter.build_ffmpeg_mix_command(
        ["/a.mp3", "/b.mp3"], "/out.mp3", crossfade=4.0,
        align_bpm=True, bpms=[120.0, 90.0],
    )
    assert "atempo=1.333333" in fc  # 120/90
    assert "atempo=1.000000" in fc  # first track unchanged


def test_build_atempo_chain_out_of_range():
    # factor 3.0 -> two chained atempo=2.0 then 1.5
    from mixxx.exporter import _safe_atempo_chain
    expr = _safe_atempo_chain(3.0)
    assert expr.count("atempo") == 2
    assert "atempo=2.0" in expr


def test_build_empty_files_raises():
    with pytest.raises(ValueError):
        mixxx.exporter.build_ffmpeg_mix_command([], "/out.mp3")


def test_create_mix_filters_missing(fake_db, monkeypatch):
    """A playlist pointing at a missing file should still render (filter it)."""
    monkeypatch.setenv("MIXXX_DB_PATH", str(fake_db))
    # Build real tiny audio files so ffmpeg can actually render.
    song1 = fake_db.parent / "song1.mp3"
    song2 = fake_db.parent / "song2.mp3"
    import subprocess
    for f, freq in ((song1, 440), (song2, 660)):
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency={freq}:duration=1",
             "-c:a", "libmp3lame", "-q:a", "9", str(f)],
            capture_output=True, check=True, timeout=30,
        )
    missing = str(fake_db.parent / "missing.mp3")  # never created
    conn = sqlite3.connect(fake_db)
    conn.execute("INSERT INTO track_locations VALUES (10, ?)", (missing,))
    conn.execute("UPDATE library SET location=10 WHERE id=2")
    conn.commit()
    conn.close()
    res = mixxx.exporter.create_mix_from_playlist(1, str(fake_db.parent / "out.mp3"))
    assert res["success"] is True, res.get("message")
    assert (fake_db.parent / "out.mp3").exists()


# --- Live integration: real flatpak Mixxx DB (skipped when absent) ---
LIVE_DB = os.path.expanduser("~/.var/app/org.mixxx.Mixxx/.mixxx/mixxxdb.sqlite")


@pytest.mark.skipif(not os.path.exists(LIVE_DB), reason="flatpak Mixxx DB not found")
def test_live_db_reads(monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", LIVE_DB)
    rows = mixxx.library.list_tracks(limit=5)
    assert len(rows) >= 1
    assert all("file" in r for r in rows)
    pls = mixxx.playlists.list_playlists()
    assert len(pls) >= 1


@pytest.mark.skipif(not os.path.exists(LIVE_DB), reason="flatpak Mixxx DB not found")
def test_live_db_playlist_resolves_existing_files(monkeypatch):
    monkeypatch.setenv("MIXXX_DB_PATH", LIVE_DB)
    pls = [p for p in mixxx.playlists.list_playlists() if p["track_count"] > 0]
    assert pls, "no populated playlists in live DB"
    # Pick the playlist with the most on-disk files so the assertion is stable.
    best = None
    best_hits = 0
    for p in pls:
        tracks = mixxx.playlists.get_playlist_tracks(p["id"])
        hits = sum(1 for t in tracks if t.get("file") and os.path.exists(t["file"]))
        if hits > best_hits:
            best, best_hits = p, hits
    assert best is not None and best_hits > 0, "no playlist has existing files"
    tracks = mixxx.playlists.get_playlist_tracks(best["id"])
    assert tracks
    existing = [t for t in tracks if t.get("file") and os.path.exists(t["file"])]
    assert len(existing) == best_hits
