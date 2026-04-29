"""Tests for daw-master dawdreamer VST utility functions.

Integration-friendly: uses monkeypatched HOME for isolation and
monkeypatched scrape_top_plugins for offline install test.
"""

import pytest
import zipfile
from pathlib import Path
from conftest import import_skill_module


def test_discover_vst_directories_exists():
    dawdreamer_mod = import_skill_module("dawdreamer", "pipeline")
    result = dawdreamer_mod.discover_vst_directories()
    assert isinstance(result, dict)
    assert 'linux' in result
    assert 'paths' in result['linux']
    # paths is a list of dicts 'path' and 'count'
    for entry in result['linux']['paths']:
        assert 'path' in entry
        assert 'count' in entry


def test_select_best_vst_dir_returns_most_populated(monkeypatch, tmp_path):
    # Setup fake HOME with a .vst dir containing a dummy .so
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    vst_dir = fake_home / ".vst"
    vst_dir.mkdir()
    (vst_dir / "dummy.so").write_bytes(b'\x00')
    monkeypatch.setenv('HOME', str(fake_home))

    dawdreamer_mod = import_skill_module("dawdreamer", "pipeline")
    dirs = dawdreamer_mod.discover_vst_directories()['linux']['paths']
    if dirs:
        best = dawdreamer_mod.select_best_vst_dir()
        assert best == max(dirs, key=lambda x: x['count'])['path']


def test_list_vst_plugins_returns_files(monkeypatch, tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    vst_dir = fake_home / ".vst"
    vst_dir.mkdir()
    (vst_dir / "plugin1.so").write_bytes(b'\x00')
    (vst_dir / "sub").mkdir()
    (vst_dir / "sub" / "plugin2.so").write_bytes(b'\x00')
    monkeypatch.setenv('HOME', str(fake_home))

    dawdreamer_mod = import_skill_module("dawdreamer", "pipeline")
    dirs = dawdreamer_mod.discover_vst_directories()['linux']['paths']
    if dirs:
        plugins = dawdreamer_mod.list_vst_plugins(dirs[0]['path'])
        assert len(plugins) >= 2
        suffixes = [p.suffix for p in plugins]
        assert '.so' in suffixes


def test_scrape_top_plugins_exists():
    dawdreamer_mod = import_skill_module("dawdreamer", "pipeline")
    plugins = dawdreamer_mod.scrape_top_plugins(count=12)
    assert len(plugins) == 12
    for p in plugins:
        assert 'name' in p and 'url' in p


def test_install_top_plugins_success(monkeypatch, tmp_path):
    """Test that install_top_plugins installs the requested number of plugins."""
    dawdreamer_mod = import_skill_module("dawdreamer", "pipeline")

    # Create a fake VST target directory with write access
    target_vst = tmp_path / "vst_target"
    target_vst.mkdir()

    # Prepare a small zip archive containing a dummy .so file
    zip_path = tmp_path / "test_plugin.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("dummy_plugin.so", b'\x00\x00\x00')
    # Convert to file URL
    zip_url = f"file://{zip_path}"

    # Monkeypatch scrape_top_plugins to return fake list
    monkeypatch.setattr(
        dawdreamer_mod,
        'scrape_top_plugins',
        lambda count=12: [{'name': f'Plugin{i}', 'url': zip_url} for i in range(count)]
    )

    result = dawdreamer_mod.install_top_plugins(target_dir=str(target_vst), count=3)
    assert result['installed'] == 3
