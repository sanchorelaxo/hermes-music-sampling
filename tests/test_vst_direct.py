import platform
import pytest

def _is_arm_architecture():
    """Return True if running on ARM architecture (Raspberry Pi, etc.)."""
    machine = platform.machine().lower()
    return machine in ('arm64', 'aarch64', 'armv7l', 'armv8l', 'arm')

try:
    import dawdreamer as dd  # noqa: F401
    DAWDREAMER_AVAILABLE = True
except ImportError:
    DAWDREAMER_AVAILABLE = False

# Skip entire module on ARM or when dawdreamer not installed
pytestmark = pytest.mark.skipif(
    _is_arm_architecture() or not DAWDREAMER_AVAILABLE,
    reason="dawdreamer not available on ARM or not installed"
)


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
