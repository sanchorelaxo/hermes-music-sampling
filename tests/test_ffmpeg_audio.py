"""
Tests for ffmpeg-audio skill.
"""
import pytest
from pathlib import Path
from conftest import import_skill_module

ffmpeg = import_skill_module("ffmpeg-audio", "pipeline")

def test_transform_volume(sample_wav, temp_dir):
    out = temp_dir / "volume.wav"
    result = ffmpeg.transform(
        input=str(sample_wav),
        pipeline=[{"op": "volume", "gain": "-3dB"}],
        output=str(out),
        dry_run=False,
    )
    assert result["success"], result.get("error")
    assert out.exists()

def test_transform_highpass(sample_wav, temp_dir):
    out = temp_dir / "highpass.wav"
    result = ffmpeg.transform(
        input=str(sample_wav),
        pipeline=[{"op": "highpass", "cutoff": 80}],
        output=str(out),
        dry_run=False,
    )
    assert result["success"]
    assert out.exists()

def test_transform_loudnorm(sample_wav, temp_dir):
    out = temp_dir / "loudnorm.wav"
    result = ffmpeg.transform(
        input=str(sample_wav),
        pipeline=[{"op": "loudnorm", "i": -16, "lra": 8, "tp": -1}],
        output=str(out),
        dry_run=False,
    )
    assert result["success"]
    assert out.exists()

def test_mix_filter_complex_syntax(sample_wav, temp_dir):
    """Mix two tracks with per-track filters: resulting command should be valid FFmpeg syntax (no stray 'a' filter)."""
    out = temp_dir / "mix.wav"
    tracks = [
        {"path": str(sample_wav), "gain": 1.0},
        {"path": str(sample_wav), "gain": 0.7, "delay": 100},
    ]
    # dry_run to get command without executing
    result = ffmpeg.mix(tracks=tracks, output=str(out), dry_run=True)
    cmd = result["command"]
    filter_str = result.get("filter_string", "")
    # Ensure filter_complex does not contain ',a' (invalid filter name)
    assert ",a" not in filter_str, f"Filter string contains invalid ',a': {filter_str}"
    # Also ensure no standalone 'a' filter segments; should not have 'a[' but 'a' only as pass-through label?
    # Our corrected code should produce labels like [out0] directly without extra 'a'
    assert "[out0]" in filter_str or "[out" in filter_str, "Filter should label outputs"

def test_transform_multiple_ops(sample_wav, temp_dir):
    out = temp_dir / "multi.wav"
    result = ffmpeg.transform(
        input=str(sample_wav),
        pipeline=[
            {"op": "highpass", "cutoff": 80},
            {"op": "acompressor", "threshold": "-22dB", "ratio": 2.5},
            {"op": "loudnorm", "i": -16},
        ],
        output=str(out),
        dry_run=False,
    )
    assert result["success"]
    assert out.exists()

def test_analyze_returns_metadata(sample_wav):
    info = ffmpeg.analyze(str(sample_wav))
    assert info["success"]
    assert info.get("duration", 0) > 0
