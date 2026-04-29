"""Tests for daw-master mastering-engineer skill."""

import pytest
from conftest import import_skill_module
import shutil


def test_analyze_audio(sample_wav, temp_dir):
    """Analyze an album directory containing a single WAV file."""
    eng = import_skill_module("mastering-engineer", "pipeline")
    album = temp_dir / "analyze_album"
    album.mkdir()
    shutil.copy(str(sample_wav), str(album / "track.wav"))
    report = eng.analyze_audio(str(album))
    assert report['success'] is True
    assert 'tracks' in report
    assert len(report['tracks']) == 1
    assert report['tracks'][0]['filename'] == 'track.wav'


def test_master_audio(sample_wav, temp_dir):
    """Master an album directory with a single track."""
    eng = import_skill_module("mastering-engineer", "pipeline")
    album = temp_dir / "master_album"
    album.mkdir()
    shutil.copy(str(sample_wav), str(album / "track.wav"))
    result = eng.master_audio(str(album), genre='default')
    assert result['success'] is True
    assert result['tracks_mastered'] == 1
    mastered_dir = album / 'mastered'
    assert mastered_dir.exists()
    assert (mastered_dir / 'track.wav').exists()
