"""
Batch-Processor tests.

These tests exercise the batch-processing orchestrator across
daw-master engines (sox-engine primarily, since it's always available).
"""

import subprocess
import json
import shutil
from pathlib import Path
import pytest

from conftest import import_skill_module


@pytest.fixture
def batch_mod():
    """Import the batch-processor module."""
    return import_skill_module("batch-processor", "pipeline")


def test_batch_imports_work(batch_mod):
    """Sanity: module exposes expected functions."""
    assert hasattr(batch_mod, 'process_directory')
    assert hasattr(batch_mod, 'process_file')
    assert hasattr(batch_mod, 'batch_transform')


def test_process_file_missing_input(batch_mod, tmp_path):
    """process_file returns error when input doesn't exist."""
    result = batch_mod.process_file(
        input_path=tmp_path / "nope.wav",
        output_path=tmp_path / "out.wav",
        pipeline=[{"op": "normalize"}],
        engine="sox",
    )
    assert result["success"] is False
    assert "not found" in result.get("error", "").lower()


def test_process_file_basic_success(batch_mod, sample_wav, tmp_path):
    """process_file successfully transforms a sample with sox-engine."""
    out = tmp_path / "out_basic.wav"
    result = batch_mod.process_file(
        input_path=sample_wav,
        output_path=out,
        pipeline=[{"op": "normalize", "peak": -0.1}],
        engine="sox",
    )
    assert result["success"] is True, result.get("error")
    assert out.exists()
    assert result["output"] == str(out)


def test_process_file_skips_existing(batch_mod, sample_wav, tmp_path):
    """overwrite=False causes skip when output exists."""
    out = tmp_path / "exists.wav"
    shutil.copy(sample_wav, out)  # pre-create

    result = batch_mod.process_file(
        input_path=sample_wav,
        output_path=out,
        pipeline=[{"op": "normalize"}],
        engine="sox",
        overwrite=False,
    )
    assert result.get("skipped") is True
    assert result["success"] is True


def test_process_file_overwrites(batch_mod, sample_wav, tmp_path):
    """overwrite=True overwrites existing output."""
    out = tmp_path / "exists2.wav"
    shutil.copy(sample_wav, out)
    original_size = out.stat().st_size

    # Write a different-sized file to verify overwrite
    (tmp_path / "other.wav").write_bytes(b"corrupted")

    result = batch_mod.process_file(
        input_path=sample_wav,
        output_path=out,
        pipeline=[{"op": "normalize"}],
        engine="sox",
        overwrite=True,
    )
    assert result["success"] is True
    assert out.stat().st_size != original_size  # was overwritten


def test_process_directory_basic(batch_mod, sample_wav, tmp_path):
    """process_directory processes a single file and returns correct summary."""
    # Create input dir with one file
    in_dir = tmp_path / "input"
    in_dir.mkdir()
    dest = in_dir / "tone.wav"
    shutil.copy(sample_wav, dest)

    out_dir = tmp_path / "output"
    stats = batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}],
        engine="sox",
        pattern="**/*.wav",
        max_workers=1,
    )

    assert stats["total"] == 1
    assert stats["processed"] == 1
    assert stats["skipped"] == 0
    assert stats["failed"] == 0
    assert (out_dir / "tone.wav").exists()


def test_process_directory_multiple_files(batch_mod, sample_wav, tmp_path):
    """process_directory handles multiple input files."""
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    for i in range(3):
        shutil.copy(sample_wav, in_dir / f"file{i}.wav")

    out_dir = tmp_path / "out"
    stats = batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}, {"op": "fade", "type": "out", "length": 0.2}],
        engine="sox",
        pattern="*.wav",
        max_workers=1,
    )

    assert stats["total"] == 3
    assert stats["processed"] == 3
    assert (out_dir / "file0.wav").exists()
    assert (out_dir / "file1.wav").exists()
    assert (out_dir / "file2.wav").exists()


def test_process_directory_preserves_subdirs(batch_mod, sample_wav, tmp_path):
    """Subdirectory structure is mirrored in output."""
    in_dir = tmp_path / "in"
    (in_dir / "sub1" / "sub2").mkdir(parents=True)
    shutil.copy(sample_wav, in_dir / "sub1" / "a.wav")
    shutil.copy(sample_wav, in_dir / "sub1" / "sub2" / "b.wav")

    out_dir = tmp_path / "out"
    batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}],
        engine="sox",
        pattern="**/*.wav",
        max_workers=1,
    )

    assert (out_dir / "sub1" / "a.wav").exists()
    assert (out_dir / "sub1" / "sub2" / "b.wav").exists()


def test_process_directory_skips_on_no_overwrite(batch_mod, sample_wav, tmp_path):
    """Existing output files are skipped when overwrite=False."""
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    shutil.copy(sample_wav, in_dir / "tone.wav")

    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "tone.wav").write_bytes(b"preexisting")

    stats = batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}],
        engine="sox",
        overwrite=False,
        max_workers=1,
    )

    assert stats["skipped"] == 1
    assert stats["processed"] == 0
    assert stats["failed"] == 0


def test_process_directory_dry_run(batch_mod, sample_wav, tmp_path):
    """dry_run=True reports without writing files."""
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    shutil.copy(sample_wav, in_dir / "tone.wav")

    out_dir = tmp_path / "out"
    stats = batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}],
        engine="sox",
        dry_run=True,
        max_workers=1,
    )

    assert stats.get("dry_run") is True
    assert stats["processed"] == 0
    assert not out_dir.exists()


def test_process_directory_manifest_written(batch_mod, sample_wav, tmp_path):
    """manifest_path produces a JSON file with per-file records."""
    in_dir = tmp_path / "in"
    in_dir.mkdir()
    shutil.copy(sample_wav, in_dir / "tone.wav")

    out_dir = tmp_path / "out"
    manifest = tmp_path / "manifest.json"

    stats = batch_mod.process_directory(
        input_dir=str(in_dir),
        output_dir=str(out_dir),
        pipeline=[{"op": "normalize"}],
        engine="sox",
        manifest_path=str(manifest),
        max_workers=1,
    )

    assert manifest.exists()
    data = json.loads(manifest.read_text())
    assert "files" in data
    assert len(data["files"]) == 1
    assert data["files"][0]["success"] is True
    assert data["summary"]["processed"] == 1


def test_engine_resolution_valid(batch_mod):
    """_resolve_skill returns callables for known engines."""
    from concurrent.futures import ProcessPoolExecutor  # noqa

    # Just check resolution doesn't blow up; don't exec in parallel in tests
    func = batch_mod._resolve_skill('sox')
    assert callable(func)


def test_engine_resolution_invalid(batch_mod):
    """Unknown engine raises ValueError."""
    with pytest.raises(ValueError) as ei:
        batch_mod._resolve_skill('not-an-engine')
    assert "not-an-engine" in str(ei.value).lower()
