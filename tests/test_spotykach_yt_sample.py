"""Tests for the Spotykach YouTube sample tool (yt_sample.py).

Runs real ffmpeg/ffprobe and real executable lookups — no mocks. Network is
never touched: a local audio file is passed where a URL would go, which is the
same code path minus the download step.

The contract under test:

  yt_sample.build_sample(url, start, end, is_deck_a, ...) -> SampleResult

  * times accept SS, MM:SS, HH:MM:SS
  * a segment longer than the deck's 42 s loop ceiling is refused
  * deck A installs to SK/B/1.WAV, deck B to SK/B/2.WAV
  * the installed file is byte-identical to the built segment and native format
  * an existing slot is backed up before being overwritten
"""

import os
import struct
import subprocess
import sys
from pathlib import Path

import pytest

SPOTYKACH_SCRIPTS = (
    Path(__file__).resolve().parent.parent
    / "skills" / "instruments" / "spotykach" / "scripts"
)
sys.path.insert(0, str(SPOTYKACH_SCRIPTS))

import wav_builder as wb  # noqa: E402
import yt_sample as ys  # noqa: E402


# --- helpers -------------------------------------------------------------

def _make_tone(tmp_path, seconds=60, freq=440, sr=48000, ch=2):
    """A real local audio file to stand in for a downloaded source."""
    path = tmp_path / f"source_{seconds}s_{sr}_{ch}_{freq}.wav"
    if path.exists():
        return path
    subprocess.run(
        [wb.ffmpeg(), "-y", "-f", "lavfi",
         "-i", f"sine=frequency={freq}:duration={seconds}",
         "-ar", str(sr), "-ac", str(ch), str(path)],
        capture_output=True, text=True, check=True,
    )
    return path


def _fmt_tag(path):
    with open(path, "rb") as f:
        header = f.read(22)
    return struct.unpack("<H", header[20:22])[0]


def _duration(path):
    out = subprocess.run(
        [wb.ffprobe(), "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


# --- time parsing --------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("6:40", 400.0),
    ("12:45", 765.0),
    ("0:30", 30.0),
    ("400", 400.0),
    ("1:02:03", 3723.0),
    ("00:06:40", 400.0),
])
def test_parse_time_accepts_clock_and_seconds(text, expected):
    assert ys.parse_time(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "6:xx", "::", "-5", "6:40:70"])
def test_parse_time_rejects_garbage(text):
    with pytest.raises(ValueError):
        ys.parse_time(text)


def test_parse_time_accepts_numeric_seconds():
    assert ys.parse_time(400) == 400.0
    assert ys.parse_time(400.5) == 400.5


# --- deck -> slot mapping ------------------------------------------------

def test_deck_a_maps_to_blue_track_1():
    assert ys.deck_slot(True) == ("B", 1)


def test_deck_b_maps_to_blue_track_2():
    assert ys.deck_slot(False) == ("B", 2)


# --- validation ----------------------------------------------------------

def test_rejects_end_before_start(tmp_path):
    src = _make_tone(tmp_path, 5)
    with pytest.raises(ValueError, match="end"):
        ys.build_sample(str(src), "10", "5", True, card=tmp_path)


def test_rejects_zero_length(tmp_path):
    src = _make_tone(tmp_path, 5)
    with pytest.raises(ValueError):
        ys.build_sample(str(src), "3", "3", True, card=tmp_path)


def test_rejects_segment_longer_than_loop_ceiling(tmp_path):
    src = _make_tone(tmp_path, 60)
    with pytest.raises(ValueError, match="42"):
        ys.build_sample(str(src), "0", "45", True, card=tmp_path)


def test_loop_ceiling_is_42_seconds():
    assert ys.MAX_LOOP_SECONDS == 42.0


# --- video id ------------------------------------------------------------

@pytest.mark.parametrize("url,vid", [
    ("https://www.youtube.com/watch?v=Rnltl0euaSw", "Rnltl0euaSw"),
    ("https://www.youtube.com/watch?v=Rnltl0euaSw&list=RDX&index=2", "Rnltl0euaSw"),
    ("https://youtu.be/Rnltl0euaSw", "Rnltl0euaSw"),
    ("https://youtu.be/Rnltl0euaSw?t=400", "Rnltl0euaSw"),
    ("https://www.youtube.com/shorts/Rnltl0euaSw", "Rnltl0euaSw"),
    ("https://www.youtube.com/embed/Rnltl0euaSw", "Rnltl0euaSw"),
])
def test_video_id_extraction(url, vid):
    assert ys.video_id(url) == vid


def test_video_id_returns_none_for_non_youtube():
    assert ys.video_id("/tmp/somefile.wav") is None


# --- segment extraction --------------------------------------------------

def test_extract_segment_is_native_and_exact(tmp_path):
    src = _make_tone(tmp_path, 60)
    out = ys.extract_segment(src, tmp_path / "seg.wav", 10.0, 30.0)
    assert out.exists()
    assert abs(_duration(out) - 30.0) < 1e-6
    p = wb.probe(out)
    assert p["sample_fmt"] in wb.PCM_FMT_ALIASES
    assert p["sample_rate"] == 48000
    assert p["channels"] == 2
    assert _fmt_tag(out) == 0x0003


def test_extract_segment_rejects_range_beyond_source(tmp_path):
    # a 5 s source cannot yield 10..40 — must fail loudly, not write a stub
    src = _make_tone(tmp_path, 5)
    with pytest.raises(RuntimeError, match="shorter|empty"):
        ys.extract_segment(src, tmp_path / "seg.wav", 10.0, 30.0)
    assert not (tmp_path / "seg.wav").exists()


# --- card discovery ------------------------------------------------------

def test_find_card_finds_root_with_sk(tmp_path):
    card = tmp_path / "CARD"
    (card / "SK" / "B").mkdir(parents=True)
    assert ys.find_card(roots=[card]) == card


def test_find_card_returns_none_when_absent(tmp_path):
    (tmp_path / "elsewhere").mkdir()
    assert ys.find_card(roots=[tmp_path / "elsewhere"]) is None


# --- end to end ----------------------------------------------------------

def test_build_sample_installs_to_deck_a(tmp_path):
    # 800 s mono 8 kHz source: the timecodes stay literal without a huge file
    src = _make_tone(tmp_path, 800, sr=8000, ch=1)
    card = tmp_path / "CARD"
    (card / "SK" / "B").mkdir(parents=True)

    res = ys.build_sample(str(src), "6:40", "7:10", True, card=card,
                          cache_dir=tmp_path / "cache")

    dst = card / "SK" / "B" / "1.WAV"
    assert res.installed is True
    assert res.card_path == dst
    assert dst.exists()
    assert wb.is_valid(dst)
    assert abs(_duration(dst) - 30.0) < 1e-6
    assert ys.sha256(dst) == ys.sha256(res.segment_path)


def test_build_sample_installs_to_deck_b_slot_2(tmp_path):
    src = _make_tone(tmp_path, 800, sr=8000, ch=1)
    card = tmp_path / "CARD"
    (card / "SK" / "B").mkdir(parents=True)

    res = ys.build_sample(str(src), "12:45", "13:15", False, card=card,
                          cache_dir=tmp_path / "cache")

    dst = card / "SK" / "B" / "2.WAV"
    assert res.card_path == dst
    assert dst.exists()
    assert not (card / "SK" / "B" / "1.WAV").exists()


def test_build_sample_backs_up_previous_slot(tmp_path):
    src = _make_tone(tmp_path, 60, freq=440)
    card = tmp_path / "CARD"
    slot = card / "SK" / "B" / "1.WAV"
    slot.parent.mkdir(parents=True)

    first = ys.build_sample(str(src), "0", "30", True, card=card,
                            cache_dir=tmp_path / "cache")
    original_hash = ys.sha256(slot)

    # different frequency -> different content in the same slot
    src2 = _make_tone(tmp_path, 60, freq=880)
    res = ys.build_sample(str(src2), "0", "30", True, card=card,
                          cache_dir=tmp_path / "cache2")

    assert res.backup_path is not None
    assert res.backup_path.exists()
    assert ys.sha256(res.backup_path) == original_hash
    assert ys.sha256(slot) != original_hash


def test_build_sample_without_card_raises_but_keeps_segment(tmp_path):
    src = _make_tone(tmp_path, 60)
    empty = tmp_path / "empty"
    empty.mkdir()

    with pytest.raises(ys.CardNotFound) as excinfo:
        ys.build_sample(str(src), "0", "30", True, card=None,
                        search_roots=[empty], cache_dir=tmp_path / "cache")
    # the built segment survives the failure and is named in the error
    assert str(excinfo.value).strip()
    assert list((tmp_path / "cache").rglob("*.WAV"))


# --- yt-dlp binary resolution -------------------------------------------

def _fake_ytdlp(path, version):
    path.write_text(f"#!/bin/sh\necho '{version}'\n")
    path.chmod(0o755)
    return path


def test_resolve_ytdlp_prefers_newest_version(tmp_path):
    old = _fake_ytdlp(tmp_path / "yt-dlp-old", "2026.03.17")
    new = _fake_ytdlp(tmp_path / "yt-dlp-new", "2026.10.26")
    chosen = ys.resolve_ytdlp(candidates=[old, new])
    assert Path(chosen) == new


def test_resolve_ytdlp_raises_when_none_usable(tmp_path):
    with pytest.raises(RuntimeError):
        ys.resolve_ytdlp(candidates=[tmp_path / "nope"])


# --- CLI -----------------------------------------------------------------

def test_cli_build_with_local_source(tmp_path, capsys):
    src = _make_tone(tmp_path, 800, sr=8000, ch=1)
    card = tmp_path / "CARD"
    (card / "SK" / "B").mkdir(parents=True)

    code = ys.main(["--url", str(src), "--start", "6:40", "--end", "7:10",
                    "--deck", "a", "--card", str(card),
                    "--cache-dir", str(tmp_path / "cache")])

    assert code == 0
    assert (card / "SK" / "B" / "1.WAV").exists()
    out = capsys.readouterr().out
    assert "1.WAV" in out


def test_cli_rejects_bad_time_with_clear_error(tmp_path, capsys):
    src = _make_tone(tmp_path, 60)
    code = ys.main(["--url", str(src), "--start", "abc", "--end", "7:10",
                    "--deck", "a", "--card", str(tmp_path)])
    assert code != 0
    assert "time" in capsys.readouterr().err.lower()
