import platform
import pytest
import sys
import types
from pathlib import Path

def _is_arm_architecture():
    """Return True if running on ARM architecture (Raspberry Pi, etc.)."""
    machine = platform.machine().lower()
    return machine in ('arm64', 'aarch64', 'armv7l', 'armv8l', 'arm')

# Check DawDreamer availability and set up skills package for imports
try:
    # Set up skills namespace package for direct imports
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    skills_pkg_path = str(PROJECT_ROOT / "skills")
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [skills_pkg_path]
        sys.modules["skills"] = skills_pkg
    # Ensure skills.dawdreamer namespace exists
    if "skills.dawdreamer" not in sys.modules:
        skills_dawdreamer = types.ModuleType("skills.dawdreamer")
        skills_dawdreamer.__path__ = [str(PROJECT_ROOT / "skills" / "daw-master" / "dawdreamer")]
        sys.modules["skills.dawdreamer"] = skills_dawdreamer

    import dawdreamer as dd  # noqa: F401
    from skills.dawdreamer.pipeline import DawDreamerEngine
    DAWDREAMER_AVAILABLE = True
except ImportError:
    DAWDREAMER_AVAILABLE = False
    DawDreamerEngine = None

# Skip entire module on ARM or when dawdreamer not installed
pytestmark = pytest.mark.skipif(
    _is_arm_architecture() or not DAWDREAMER_AVAILABLE,
    reason="dawdreamer not available on ARM or not installed"
)


def test_load_vst2_zamverb():
    """Test loading ZamVerb VST2 plugin directly."""
    with DawDreamerEngine(sample_rate=44100, buffer_size=512) as engine:
        plugin = engine.make_plugin_processor("zamverb", "/usr/lib/vst/ZamVerb-vst.so")
        assert plugin is not None


def test_load_vst2_zamtube():
    """Test loading ZamTube VST2 plugin directly."""
    with DawDreamerEngine(sample_rate=44100, buffer_size=512) as engine:
        plugin = engine.make_plugin_processor("zamtube", "/usr/lib/vst/ZamTube-vst.so")
        assert plugin is not None
