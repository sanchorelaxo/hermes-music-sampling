"""
Pytest configuration and shared fixtures for hermes-music-sampling tests.
(Updated to include batch-processor and metadata fixtures)
"""
import subprocess
import sys
from pathlib import Path
import pytest
import tempfile
import importlib.util
import shutil
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "daw-master"

# Try locate external tools
SOX_PATH = shutil.which('sox')
FFMPEG_PATH = shutil.which('ffmpeg')
BWFMETAEDIT_PATH = shutil.which('bwfmetaedit')
MUTAGEN_AVAILABLE = False
try:
    import mutagen  # noqa
    MUTAGEN_AVAILABLE = True
except ImportError:
    pass


@pytest.fixture(scope="session")
def sample_wav(tmp_path_factory):
    """Create a simple 440Hz sine wave WAV file for testing."""
    tmp_dir = tmp_path_factory.mktemp("audio")
    wav_path = tmp_dir / "test.wav"
    result = subprocess.run(
        [ FFMPEG_PATH or "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
          "-af", "volume=12dB", "-t", "0.5", str(wav_path) ],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    return wav_path


@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    """Provide a clean temporary directory for output files."""
    return tmp_path_factory.mktemp("out")


def import_skill_module(skill_name: str, module_name: str):
    """
    Import a skill's module from its file path.

    Works for skills nested in skills/daw-master/<skill>/ and skills/<skill>/.

    Sets up sys.modules entries so relative imports inside the skill work.
    """
    import types

    # Try daw-master namespace first
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        # Try top-level skills/<skill_name>
        skill_dir = PROJECT_ROOT / "skills" / skill_name

    module_path = skill_dir / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(
        f"skills.{skill_name}.{module_name}", module_path
    )
    mod = importlib.util.module_from_spec(spec)

    # Construct parent packages: 'skills' and 'skills.<skill_name>'
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [str(PROJECT_ROOT / "skills")]
        sys.modules["skills"] = skills_pkg

    parent_pkg_name = f"skills.{skill_name}"
    if parent_pkg_name not in sys.modules:
        parent_pkg = types.ModuleType(parent_pkg_name)
        parent_pkg.__path__ = [str(skill_dir)]
        parent_pkg.__package__ = "skills"
        sys.modules[parent_pkg_name] = parent_pkg

    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def audio_test_files(sample_wav, temp_dir):
    """Yield a dict with a sample WAV and a copy in temp_dir."""
    tmp_out = temp_dir / "output.wav"
    import shutil as _shutil
    _shutil.copy(sample_wav, tmp_out)
    return {"input": sample_wav, "output": tmp_out}


@pytest.fixture(scope="session")
def metadata_pipeline(import_skill_module):
    return import_skill_module("metadata-manager", "pipeline")
