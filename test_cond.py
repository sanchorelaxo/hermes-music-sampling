import sys
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path("/home/rjodouin/Documents/git/hermes-music-sampling")
SKILLS_DIR = PROJECT_ROOT / "skills" / "daw-master"

def import_skill_module(skill_name, module_name):
    """Import a Python module from a skill directory."""
    skill_dir = SKILLS_DIR / skill_name.replace('-', '_')
    module_path = skill_dir / f"{module_name.replace('-', '_')}.py"
    if not skill_dir.exists() or not module_path.exists():
        raise ImportError(f"Skill module not found: {skill_name}/{module_name}")
    spec = importlib.util.spec_from_file_location(f"skills.{skill_name}.{module_name}", str(module_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

audio_analyzer = import_skill_module("daw-master", "audio-analyzer")

sample_wav = Path("/home/rjodouin/Documents/git/hermes-music-sampling/tests/fixtures/sample.wav")

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
