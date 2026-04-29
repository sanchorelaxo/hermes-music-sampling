import sys
from pathlib import Path
import importlib.util
import subprocess
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "daw-master"

def import_skill_module(skill_name, module_name):
    """Import a Python module from a skill directory."""
    import types
    skill_dir = SKILLS_DIR / skill_name
    module_path = skill_dir / f"{module_name}.py"
    if not skill_dir.exists() or not module_path.exists():
        raise ImportError(f"Skill module not found: {skill_name}/{module_name}")
    spec = importlib.util.spec_from_file_location(f"skills.{skill_name}.{module_name}", module_path)
    mod = importlib.util.module_from_spec(spec)

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

audio_analyzer = import_skill_module("audio-analyzer", "pipeline")

# Generate a temporary 440Hz sine wave for demo (same as pytest fixture)
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
    sample_wav = Path(tmp.name)

result = subprocess.run(
    ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
     "-af", "volume=12dB", "-t", "0.5", str(sample_wav)],
    capture_output=True, text=True, timeout=30
)
if result.returncode != 0:
    print(f"ffmpeg failed: {result.stderr}", file=sys.stderr)
    sys.exit(1)

features = audio_analyzer.analyze(str(sample_wav))
print("Features keys:", list(features.keys()))
print("Loudness:", features.get("loudness"))
print("Tempo:", features.get("tempo"))

# Check condition
if features.get("loudness", -20) > -10:
    print("Condition: loudness > -10 => TRUE (would add gain)")
else:
    print("Condition: loudness > -10 => FALSE")
if features.get("tempo", 120) < 80:
    print("Condition: tempo < 80 => TRUE (would time-stretch)")
else:
    print("Condition: tempo < 80 => FALSE")

# Cleanup
sample_wav.unlink(missing_ok=True)
