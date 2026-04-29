"""Tests for daw-master mix-engineer skill."""

import pytest
from conftest import import_skill_module


def test_mix_and_render_single_stem(sample_wav, temp_dir):
    mix_mod = import_skill_module("mix-engineer", "pipeline")
    out = temp_dir / "mix.wav"
    result = mix_mod.mix_and_render(
        stems=[{"path": str(sample_wav), "gain": 0.9}],
        output=str(out),
        normalize_final=False,
    )
    assert result['success'] is True
    assert out.exists()


def test_transform_pipeline(sample_wav, temp_dir):
    mix_mod = import_skill_module("mix-engineer", "pipeline")
    out = temp_dir / "polished.wav"
    result = mix_mod.transform(
        input=str(sample_wav),
        pipeline=[{"op": "normalize", "peak": -0.1}],
        output=str(out),
        dry_run=False,
    )
    assert result['success'] is True
    assert out.exists()
