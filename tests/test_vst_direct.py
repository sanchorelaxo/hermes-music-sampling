import pytest
import dawdreamer as dd

def test_load_vst2_zamverb():
    """Test loading ZamVerb VST2 plugin directly."""
    with dd.RenderEngine(sample_rate=44100) as engine:
        plugin = engine.make_plugin_processor("zamverb", "/usr/lib/vst/ZamVerb-vst.so")
        assert plugin is not None

def test_load_vst2_zamtube():
    """Test loading ZamTube VST2 plugin directly."""
    with dd.RenderEngine(sample_rate=44100) as engine:
        plugin = engine.make_plugin_processor("zamtube", "/usr/lib/vst/ZamTube-vst.so")
        assert plugin is not None
