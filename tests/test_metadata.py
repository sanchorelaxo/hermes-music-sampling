"""
Metadata Manager tests (BWF + ID3).

Requires:
- bwfmetaedit binary (apt/dnf/brew install bwfmetaedit) for BWF tests
- mutagen (pip install mutagen) for MP3 ID3 tests
"""

import subprocess
import json
from pathlib import Path
import pytest

from conftest import import_skill_module, BWFMETAEDIT_PATH, MUTAGEN_AVAILABLE


@pytest.fixture
def metadata_pipeline():
    """Import the metadata pipeline module."""
    return import_skill_module("metadata-manager", "pipeline")


@pytest.fixture
def sample_wav_with_bwf(sample_wav, metadata_pipeline, tmp_path):
    """Create a WAV file with BWF metadata written."""
    # Write BWF metadata onto sample_wav (in-place)
    res = metadata_pipeline.write_bwf(
        str(sample_wav),
        description="Test description",
        originator="Hermes Test",
        originator_reference="TEST-001",
        date="2025-04-29"
    )
    assert res.get("success") is True, f"write_bwf failed: {res.get('error')}"
    return sample_wav


@pytest.mark.skipif(not BWFMETAEDIT_PATH, reason="bwfmetaedit not installed")
def test_write_bwf_success(metadata_pipeline, sample_wav):
    """write_bwf writes DESCRIPTION and ORIGINATOR."""
    res = metadata_pipeline.write_bwf(
        str(sample_wav),
        description="Hello world",
        originator="Tester"
    )
    assert res["success"] is True
    assert "DESCRIPTION" in res["updated"]
    assert "ORIGINATOR" in res["updated"]


@pytest.mark.skipif(not BWFMETAEDIT_PATH, reason="bwfmetaedit not installed")
def test_read_bwf_returns_metadata(metadata_pipeline, sample_wav_with_bwf):
    """read_bwf retrieves written BEXT fields."""
    info = metadata_pipeline.read_bwf(str(sample_wav_with_bwf))
    assert info["success"] is True
    meta = info["metadata"]
    assert meta.get("DESCRIPTION") == "Test description"
    assert meta.get("ORIGINATOR") == "Hermes Test"
    assert meta.get("ORIGINATOR_REFERENCE") == "TEST-001"
    assert meta.get("DATE") == "2025-04-29"


@pytest.mark.skipif(not BWFMETAEDIT_PATH, reason="bwfmetaedit not installed")
def test_update_bwf_multiple_fields(metadata_pipeline, sample_wav):
    """update_bwf writes multiple fields at once."""
    res = metadata_pipeline.update_bwf(
        str(sample_wav),
        {
            "description": "Batch update",
            "originator": "BatchWriter",
            "date": "2025-01-01",
        }
    )
    assert res["success"] is True

    info = metadata_pipeline.read_bwf(str(sample_wav))
    meta = info["metadata"]
    assert meta["DESCRIPTION"] == "Batch update"


@pytest.mark.skipif(not BWFMETAEDIT_PATH, reason="bwfmetaedit not installed")
def test_extract_metadata_bwf(metadata_pipeline, sample_wav_with_bwf):
    """extract_metadata detects format and returns BWF fields."""
    meta = metadata_pipeline.extract_metadata(str(sample_wav_with_bwf))
    assert meta["success"] is True
    assert meta.get("format") == "BWF"
    # Top-level keys from BEXT appear
    assert "DESCRIPTION" in meta


# ─────────────────────────────────────────
# MP3 / ID3 tests (skip gracefully if mutagen missing)
# ─────────────────────────────────────────
def create_dummy_mp3(tmp_path, duration=0.5):
    """Create a tiny valid MP3 file using ffmpeg."""
    mp3 = tmp_path / "test.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
         "-c:a", "libmp3lame", "-b:a", "128k", str(mp3)],
        capture_output=True, timeout=30
    )
    if not mp3.exists():
        pytest.skip("ffmpeg not available to create test MP3")
    return mp3


@pytest.mark.skipif(not MUTAGEN_AVAILABLE, reason="mutagen not installed")
def test_tag_mp3_success(metadata_pipeline, tmp_path):
    """tag_mp3 writes basic ID3 frames."""
    mp3 = create_dummy_mp3(tmp_path)
    res = metadata_pipeline.tag_mp3(
        str(mp3),
        title="Test Song",
        artist="Hermes Tester",
        album="Test Album",
        tracknumber="7",
        genre="Electronic",
        date="2025"
    )
    assert res["success"] is True
    written = set(res["written"])
    assert "TIT2" in written  # title
    assert "TPE1" in written  # artist
    assert "TALB" in written  # album

    # Verify via mutagen read-back
    from mutagen.id3 import ID3
    tags = ID3(str(mp3))
    assert tags.get("TIT2").text[0] == "Test Song"
    assert tags.get("TPE1").text[0] == "Hermes Tester"


@pytest.mark.skipif(not MUTAGEN_AVAILABLE, reason="mutagen not installed")
def test_tag_mp3_custom_txxx(metadata_pipeline, tmp_path):
    """Custom TXXX frames are written correctly."""
    mp3 = create_dummy_mp3(tmp_path)
    res = metadata_pipeline.tag_mp3(str(mp3), TXXX_CUSTOM_ID="HERM-001")
    assert res["success"] is True
    assert any(f.startswith("TXXX:") for f in res["written"])


def test_extract_metadata_mp3(metadata_pipeline, tmp_path):
    """extract_metadata returns ID3 tags when present."""
    if not MUTAGEN_AVAILABLE:
        pytest.skip("mutagen missing")

    mp3 = create_dummy_mp3(tmp_path)
    metadata_pipeline.tag_mp3(str(mp3), title="EP Title", artist="Band")
    meta = metadata_pipeline.extract_metadata(str(mp3))
    assert meta["success"] is True
    assert meta["format"] in ("ID3", "mutagen")
    # Frame IDs appear as keys (e.g. TIT2)
    assert "TIT2" in meta or "title" in meta


def test_read_bwf_missing_tool(metadata_pipeline, sample_wav, monkeypatch):
    """If bwfmetaedit missing, read_bwf returns clear error."""
    monkeypatch.setattr(metadata_pipeline, "BWFMETAEDIT_AVAILABLE", False)
    res = metadata_pipeline.read_bwf(str(sample_wav))
    assert res["success"] is False
    assert "not installed" in res.get("error", "").lower()


def test_write_bwf_missing_tool(metadata_pipeline, sample_wav, monkeypatch):
    """If bwfmetaedit missing, write_bwf returns clear error."""
    monkeypatch.setattr(metadata_pipeline, "BWFMETAEDIT_AVAILABLE", False)
    res = metadata_pipeline.write_bwf(str(sample_wav), description="test")
    assert res["success"] is False
    assert "not installed" in res.get("error", "").lower()


def test_metadata_extract_file_not_found(metadata_pipeline, tmp_path):
    """extract_metadata handles missing file."""
    res = metadata_pipeline.extract_metadata(str(tmp_path / "nope.wav"))
    assert res["success"] is False
    assert "not found" in res.get("error", "").lower()
