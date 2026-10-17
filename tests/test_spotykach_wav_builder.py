"""Tests for the Spotykach WAV.builder headless pipeline.

These run real ffmpeg/ffprobe (no mocks) and assert the output matches the
Spotykach firmware's native format and SD-card layout exactly:

  * 32-bit float, 48 kHz, stereo PCM WAV
  * SK/{B,G,P,R,T,Y}/{1..6}.WAV folder tree
  * SK/config.txt  (setting name line, then numeric value line)
"""

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


def _make_input(tmp_path, freq=440, sr=44100, ch=1):
    """Create a deliberately non-native WAV (44.1 kHz mono) as conversion input."""
    path = tmp_path / f"input_{freq}.wav"
    subprocess.run(
        [
            wb.ffmpeg(), "-y", "-f", "lavfi",
            "-i", f"sine=frequency={freq}:duration=0.5",
            "-ar", str(sr), "-ac", str(ch), str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return path


def _wav_format_tag(path):
    """Return the WAV fmt chunk's format tag (bytes 20-21, little-endian)."""
    with open(path, "rb") as f:
        header = f.read(22)
    assert header[0:4] == b"RIFF"
    assert header[8:12] == b"WAVE"
    return struct.unpack("<H", header[20:22])[0]


def test_convert_produces_native_format(tmp_path):
    src = _make_input(tmp_path)
    dst = wb.convert(src, tmp_path / "out" / "converted.WAV")
    assert dst.exists()
    p = wb.probe(dst)
    assert p["sample_fmt"] in wb.PCM_FMT_ALIASES
    assert p["sample_rate"] == 48000
    assert p["channels"] == 2


def test_convert_writes_plain_ieee_float_not_extensible(tmp_path):
    # The Spotykach firmware (libDaisy) recognizes format tag 0x0003 (IEEE
    # float) but not ffmpeg's default 0xFFFE (WAVE_FORMAT_EXTENSIBLE) header.
    src = _make_input(tmp_path)
    dst = wb.convert(src, tmp_path / "plain.WAV")
    assert _wav_format_tag(dst) == 0x0003


def test_is_valid_rejects_non_native_input(tmp_path):
    src = _make_input(tmp_path)
    assert not wb.is_valid(src)  # 44.1 kHz mono is not native
    dst = wb.convert(src, tmp_path / "valid.WAV")
    assert wb.is_valid(dst)


def test_build_card_creates_all_six_tapes(tmp_path):
    sk = wb.build_card_root(tmp_path / "card")
    assert sk.name == "SK"
    for letter in "BGPRTY":
        assert (sk / letter).is_dir()


def test_place_file_names_and_converts(tmp_path):
    src = _make_input(tmp_path, freq=880)
    sk = wb.build_card_root(tmp_path / "card")
    dst = wb.place_file(src, sk, "B", 1)
    assert dst == sk / "B" / "1.WAV"
    assert wb.is_valid(dst)


def test_place_file_rejects_bad_tape_and_track(tmp_path):
    src = _make_input(tmp_path)
    sk = wb.build_card_root(tmp_path / "card")
    with pytest.raises(ValueError):
        wb.place_file(src, sk, "Z", 1)
    with pytest.raises(ValueError):
        wb.place_file(src, sk, "B", 7)


def test_write_config_format(tmp_path):
    sk = wb.build_card_root(tmp_path / "card")
    wb.write_config({"mid_ch_b": 5, "mid_ps_a": 1}, sk)
    text = (sk / "config.txt").read_text()
    # name line immediately followed by its value line
    assert "mid_ch_b\n5\n" in text
    assert "mid_ps_a\n1\n" in text


def test_write_config_rejects_unknown_and_out_of_range(tmp_path):
    sk = wb.build_card_root(tmp_path / "card")
    with pytest.raises(ValueError):
        wb.write_config({"bogus": 1}, sk)
    with pytest.raises(ValueError):
        wb.write_config({"mid_ch_a": 99}, sk)
    with pytest.raises(ValueError):
        wb.write_config({"pre_load": 2}, sk)
