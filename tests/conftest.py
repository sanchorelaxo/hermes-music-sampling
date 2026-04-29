"""
Pytest configuration and shared fixtures for hermes-music-sampling tests.
"""
import subprocess
import sys
from pathlib import Path
import pytest
import tempfile
import importlib.util

# Resolve project root (two levels up from this conftest.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "daw-master"

@pytest.fixture(scope="session")
def sample_wav(tmp_path_factory):
    """Create a simple 440Hz sine wave WAV file for testing."""
    tmp_dir = tmp_path_factory.mktemp("audio")
    wav_path = tmp_dir / "test.wav"
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
         "-af",
            "volume=12dB",
            "-t", "0.5", str(wav_path)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")
    return wav_path

@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    """Provide a temporary directory for output files."""
    return tmp_path_factory.mktemp("out")

def import_skill_module(skill_name: str, module_name: str):
    """Import a skill's module from its file path.

    Sets up parent packages in sys.modules so relative imports within the
    skill (e.g. from .operations import ...) work correctly.
    """
    import types
    skill_dir = SKILLS_DIR / skill_name
    module_path = skill_dir / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"skills.{skill_name}.{module_name}", module_path)
    mod = importlib.util.module_from_spec(spec)

    # Ensure parent packages exist in sys.modules
    # Top-level: 'skills'
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [str(PROJECT_ROOT / "skills")]
        sys.modules["skills"] = skills_pkg
    # Namespace: 'skills.{skill_name}'
    parent_pkg_name = f"skills.{skill_name}"
    if parent_pkg_name not in sys.modules:
        parent_pkg = types.ModuleType(parent_pkg_name)
        parent_pkg.__path__ = [str(skill_dir)]
        parent_pkg.__package__ = "skills"
        sys.modules[parent_pkg_name] = parent_pkg

    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod
