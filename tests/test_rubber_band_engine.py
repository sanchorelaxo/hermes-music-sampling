"""
Tests for rubber-band-engine skill.
"""
import pytest
from pathlib import Path
from conftest import import_skill_module

rb = import_skill_module("rubber-band-engine", "pipeline")

def test_time_stretch(sample_wav, temp_dir):
    out = temp_dir / "stretched.wav"
    result = rb.transform(
        input=str(sample_wav),
        pipeline=[{"op": "time_stretch", "factor": 0.88, "formant": True}],
        output=str(out),
        dry_run=False,
    )
    assert result["success"], result.get("error")
    assert out.exists()

def test_pitch_shift(sample_wav, temp_dir):
    out = temp_dir / "pitch.wav"
    result = rb.transform(
        input=str(sample_wav),
        pipeline=[{"op": "pitch_shift", "semitones": 2.0}],
        output=str(out),
        dry_run=False,
    )
    assert result["success"]
    assert out.exists()

def test_combined_time_and_pitch(sample_wav, temp_dir):
    out = temp_dir / "combo.wav"
    result = rb.transform(
        input=str(sample_wav),
        pipeline=[
            {"op": "time_stretch", "factor": 0.9},
            {"op": "pitch_shift", "semitones": 1.0},
        ],
        output=str(out),
        dry_run=False,
    )
    assert result["success"]
    assert out.exists()

def test_analyze_returns_basic(sample_wav):
    info = rb.analyze(str(sample_wav))
    assert info["success"]
    assert info.get("duration", 0) > 0
