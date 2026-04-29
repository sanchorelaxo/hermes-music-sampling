"""
Tests for sox-engine skill.
"""
import pytest
from pathlib import Path

# Import the pipeline module using helper from conftest
from conftest import import_skill_module

sox = import_skill_module("sox-engine", "pipeline")

def test_transform_with_normalize(sample_wav, temp_dir):
    """Normalize should produce a valid output file."""
    output = temp_dir / "normalized.wav"
    result = sox.transform(
        input=str(sample_wav),
        pipeline=[{"op": "normalize", "peak": -0.1}],
        output=str(output),
        dry_run=False,
    )
    assert result["success"], f"transform failed: {result.get('error')}"
    assert output.exists(), "Output file not created"

def test_transform_with_fade_in(sample_wav, temp_dir):
    """Fade in should build correct command and produce output."""
    output = temp_dir / "fade_in.wav"
    result = sox.transform(
        input=str(sample_wav),
        pipeline=[{"op": "fade", "type": "in", "length": 0.5}],
        output=str(output),
        dry_run=False,
    )
    assert result["success"], f"transform failed: {result.get('error')}"
    assert output.exists()

def test_transform_with_fade_out(sample_wav, temp_dir):
    """Fade out should use valid SoX syntax: fade <shape> 0 <length>."""
    output = temp_dir / "fade_out.wav"
    # Use dry_run to capture command without executing (faster)
    result = sox.transform(
        input=str(sample_wav),
        pipeline=[{"op": "fade", "type": "out", "length": 1.5}],
        output=str(output),
        dry_run=True,
    )
    cmd = result["command"]
    # SoX fade-out syntax: fade <shape> 0 <length>
    # Default shape is 'q' (quadratic). Verify we get "fade q 0 1.5"
    assert "fade q 0 1.5" in cmd, f"Expected 'fade q 0 1.5' in command, got: {cmd}"
    # Verify structure: after 'fade' comes shape, then 0, then length
    parts = cmd.split()
    if 'fade' in parts:
        idx = parts.index('fade')
        assert idx + 3 < len(parts), "fade command should have 3 args after 'fade'"
        assert parts[idx+1] == 'q', f"shape should be 'q', got {parts[idx+1]}"
        assert parts[idx+2] == '0', f"fade-in should be 0 for fade-out, got {parts[idx+2]}"
        assert parts[idx+3] == '1.5', f"fade-out length should be 1.5, got {parts[idx+3]}"

def test_transform_with_trim(sample_wav, temp_dir):
    """Trim operation should work."""
    output = temp_dir / "trimmed.wav"
    result = sox.transform(
        input=str(sample_wav),
        pipeline=[{"op": "trim", "start": 0.1, "length": 0.2}],
        output=str(output),
        dry_run=False,
    )
    assert result["success"]
    assert output.exists()

def test_mix_two_tracks(sample_wav, temp_dir):
    """Mix two tracks into one output."""
    track1 = sample_wav
    track2 = sample_wav  # same file for simplicity
    output = temp_dir / "mix.wav"
    result = sox.mix(
        tracks=[
            {"path": str(track1), "gain": 1.0},
            {"path": str(track2), "gain": 0.7},
        ],
        output=str(output),
        dry_run=False,
    )
    assert result["success"], f"mix failed: {result.get('error')}"
    assert output.exists()

def test_analyze_returns_keys(sample_wav):
    """Analyze should return dict with expected keys."""
    info = sox.analyze(str(sample_wav))
    assert isinstance(info, dict)
    for key in ["duration", "sample_rate", "channels", "peak"]:
        assert key in info, f"Missing key {key}"

def test_probe_returns_metadata(sample_wav):
    """Probe should return basic metadata."""
    meta = sox.probe(str(sample_wav))
    assert meta["success"]
    assert meta.get("duration", 0) > 0
