"""
Tests for audio-analyzer skill.
"""
import pytest
from pathlib import Path
from conftest import import_skill_module
import os

aa = import_skill_module("audio-analyzer", "pipeline")

def test_analyze_returns_features(sample_wav):
    info = aa.analyze(str(sample_wav))
    assert isinstance(info, dict)
    # expected features: duration, sample_rate, tempo maybe, loudness, etc.
    for key in ["duration", "sample_rate", "frames", "tempo", "loudness", "mfcc"]:
        assert key in info, f"Missing feature {key}"

def test_probe_success(sample_wav):
    meta = aa.probe(str(sample_wav))
    assert meta["success"]
    assert meta["duration"] > 0

def test_extract_batch_creates_output_in_directory(sample_wav, temp_dir):
    """extract_batch should write output file inside the target directory, not cwd."""
    # Put a wav file in temp_dir
    (temp_dir / "test.wav").write_bytes(sample_wav.read_bytes())
    output_fmt = "csv"
    result = aa.extract_batch(str(temp_dir), pattern="*.wav", output_format=output_fmt)
    # result is path to output file as string
    assert result, "No output file returned"
    out_path = Path(result)
    # The output file should be inside temp_dir
    assert out_path.parent == temp_dir, f"Output {out_path} not in target dir {temp_dir}"
    assert out_path.suffix == f".{output_fmt}"
    assert out_path.exists()

def test_extract_batch_handles_no_matches(sample_wav, temp_dir):
    """If no files match, extract_batch should return empty string and not raise."""
    result = aa.extract_batch(str(temp_dir), pattern="*.nonexistent")
    assert result == ""  # per code

def test_extract_batch_json_format(sample_wav, temp_dir):
    (temp_dir / "tone.wav").write_bytes(sample_wav.read_bytes())
    result = aa.extract_batch(str(temp_dir), pattern="*.wav", output_format="json")
    assert result.endswith(".json")
    out_path = Path(result)
    assert out_path.exists()
    import json
    data = json.loads(out_path.read_text())
    assert isinstance(data, list)
    assert len(data) >= 1

def test_extract_batch_jsonl_format(sample_wav, temp_dir):
    (temp_dir / "tone.wav").write_bytes(sample_wav.read_bytes())
    result = aa.extract_batch(str(temp_dir), pattern="*.wav", output_format="jsonl")
    assert result.endswith(".jsonl")
    out_path = Path(result)
    assert out_path.exists()
    lines = out_path.read_text().strip().splitlines()
    assert len(lines) >= 1
