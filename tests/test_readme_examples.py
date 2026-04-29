"""Integration tests for README Chaining Skills examples.

Each test reproduces exactly the code from the corresponding README example
and verifies it produces the expected output file.

Tests are skipped if required dependencies are missing.
"""
import subprocess
import sys
from pathlib import Path

import pytest

# import_skill_module is defined in conftest.py and automatically available
# as a fixture/helper in the same test package
import sys
from pathlib import Path
import importlib.util

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "daw-master"

def import_skill_module(skill_name: str, module_name: str):
    """Import a skill module by name."""
    skill_dir = SKILLS_DIR / skill_name
    module_path = skill_dir / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"skills.{skill_name}.{module_name}", module_path)
    mod = importlib.util.module_from_spec(spec)
    # Ensure parent packages with proper __path__ for relative imports
    import types
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [str(PROJECT_ROOT / "skills")]
        sys.modules["skills"] = skills_pkg
    parent = f"skills.{skill_name}"
    if parent not in sys.modules:
        parent_pkg = types.ModuleType(parent)
        parent_pkg.__path__ = [str(skill_dir)]
        parent_pkg.__package__ = "skills"
        sys.modules[parent] = parent_pkg
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod

# ---------------------------------------------------------------------------
# Helper: check CLI availability
# ---------------------------------------------------------------------------
def sox_available():
    try:
        r = subprocess.run(['sox', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def rubberband_available():
    try:
        r = subprocess.run(['rubberband', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ffmpeg_available():
    try:
        r = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def librosa_available():
    try:
        import librosa  # noqa: F401
        return True
    except ImportError:
        return False


def dawdreamer_available():
    try:
        import dawdreamer  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_wav(tmp_path):
    """Create a simple 440Hz sine wave WAV file for testing."""
    wav_path = tmp_path / "sample.wav"
    r = subprocess.run(
        ['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5',
         '-af', 'volume=12dB',
         '-t', '0.5', str(wav_path)],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0:
        pytest.skip(f"ffmpeg failed to generate test audio: {r.stderr.strip()}")
    return wav_path


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for output files."""
    out = tmp_path / "out"
    out.mkdir()
    return out


# ---------------------------------------------------------------------------
# README Examples
# ---------------------------------------------------------------------------

# Example 1: sox-engine — trim and normalize
def test_example_1_sox_trim_normalize(sample_wav, temp_dir):
    """README Example 1: Trim and normalize with SoX."""
    if not sox_available():
        pytest.skip("sox not installed")
    sox_mod = import_skill_module('sox-engine', 'pipeline')
    output = temp_dir / "trimmed.wav"
    sox_mod.transform(
        str(sample_wav),
        [{"op": "trim", "start": 0, "length": 0.2}, {"op": "normalize"}],
        str(output)
    )
    assert output.exists(), "Output file not created"


# Example 2: rubber-band-engine — time stretch with formants
def test_example_2_rubber_time_stretch(sample_wav, temp_dir):
    """README Example 2: Time-stretch with formant preservation."""
    if not rubberband_available():
        pytest.skip("rubberband not installed")
    rubber_mod = import_skill_module('rubber-band-engine', 'pipeline')
    output = temp_dir / "timed.wav"
    rubber_mod.transform(
        str(sample_wav),
        [{"op": "time_stretch", "factor": 0.98, "formant": True}],
        str(output)
    )
    assert output.exists()


# Example 3: ffmpeg-audio — loudnorm + AAC encode
def test_example_3_ffmpeg_loudnorm_aac(sample_wav, temp_dir):
    """README Example 3: Loudnorm + AAC encode."""
    if not ffmpeg_available():
        pytest.skip("ffmpeg not installed")
    ffmpeg_mod = import_skill_module('ffmpeg-audio', 'pipeline')
    output = temp_dir / "final.m4a"
    ffmpeg_mod.transform(
        str(sample_wav),
        [{"op": "loudnorm", "i": -14}],
        str(output),
        codec="aac"
    )
    assert output.exists()


# Example 4: Analyze first, then conditionally process (discover → act)
def test_example_4_conditional_processing(sample_wav, temp_dir):
    """README Example 4: Analyze features, conditionally apply dawdreamer transform."""
    if not librosa_available() or not dawdreamer_available():
        pytest.skip("librosa or dawdreamer not available")
    audio_analyzer_mod = import_skill_module('audio-analyzer', 'pipeline')
    dd_mod = import_skill_module('dawdreamer', 'pipeline')

    features = audio_analyzer_mod.analyze(str(sample_wav))

    # NOTE: audio_analyzer returns 'loudness' (RMS dB), not 'loudness_lufs'.
    # The README originally contained a typo; we use the correct key.
    loud_val = features.get("loudness", -20)

    pipeline = []
    if loud_val > -10:
        pipeline.append({"op": "gain", "amount_db": -3})
    if features.get("tempo", 120) < 80:
        pipeline.append({"op": "time_stretch", "factor": 1.15})

    if pipeline:
        output = temp_dir / "processed.wav"
        result = dd_mod.transform(str(sample_wav), pipeline=pipeline, output=str(output))
        assert result["success"], f"Transform failed: {result.get('error')}"
        assert output.exists()
    else:
        pytest.skip("Conditions not met for processing")


# Example 5: Full multi-track mix with per-track effects and master bus
def test_example_5_multitrack_mix(sample_wav, temp_dir):
    """README Example 5: Multi-track mix with per-track effects and master bus chain."""
    if not dawdreamer_available():
        pytest.skip("dawdreamer not installed")
    dd_mod = import_skill_module('dawdreamer', 'pipeline')

    # Create three stem files (use same sample for test)
    vocals = temp_dir / "vocals.wav"
    guitar = temp_dir / "guitar.wav"
    drums = temp_dir / "drums.wav"
    for dst in (vocals, guitar, drums):
        subprocess.run(['cp', str(sample_wav), str(dst)], check=True, capture_output=True)

    output = temp_dir / "full_mix.wav"
    result = dd_mod.mix(
        tracks=[
            {"path": str(vocals), "gain_db": 0, "pan": 0.0, "effects": [
                {"op": "compress", "threshold": -20, "ratio": 3},
                {"op": "reverb", "room_size": 0.3, "wet": 0.2}
            ]},
            {"path": str(guitar), "gain_db": -3, "pan": 0.3, "effects": [
                {"op": "eq", "low_gain": 4}
            ]},
            {"path": str(drums), "gain_db": -6, "pan": -0.2, "effects": [
                {"op": "compress", "threshold": -18, "ratio": 4}
            ]},
        ],
        output=str(output),
        normalize_final=True,
        master_bus_chain=[
            {"op": "limiter", "threshold": -0.5},
            {"op": "normalize", "target_level": -1.0}
        ]
    )
    assert result["success"], f"Mix failed: {result.get('error')}"
    assert output.exists()


# Example 6: VST plugin chain
def test_example_6_vst_chain(sample_wav, temp_dir):
    """README Example 6: VST plugin chain on vocal stem."""
    if not dawdreamer_available():
        pytest.skip("dawdreamer not installed")
    dd_mod = import_skill_module('dawdreamer', 'pipeline')

    output = temp_dir / "vocals_spacy.wav"
    # Use available system VST2 plugins (Zam plugins) for reliable loading
    vst_chain = [
        {"op": "load_vst", "path": "/usr/lib/vst/ZamVerb-vst.so"},
        {"op": "set_param", "plugin_idx": 0, "param": "RoomSize", "value": 0.75},
        {"op": "set_param", "plugin_idx": 0, "param": "Wet", "value": 0.4},
        {"op": "load_vst", "path": "/usr/lib/vst/ZamTube-vst.so"},
        {"op": "set_param", "plugin_idx": 1, "param": "Drive", "value": 0.25},
    ]
    result = dd_mod.transform(str(sample_wav), pipeline=vst_chain, output=str(output))
    assert result["success"], f"VST chain transform failed: {result.get('error')}"
    assert output.exists()


# Example 7: EBU R128 broadcast normalization
def test_example_7_ebu_r128(sample_wav, temp_dir):
    """README Example 7: EBU R128 loudness normalization with FFmpeg."""
    if not ffmpeg_available():
        pytest.skip("ffmpeg not installed")
    ffmpeg_mod = import_skill_module('ffmpeg-audio', 'pipeline')
    output = temp_dir / "broadcast_ready.wav"
    ffmpeg_mod.transform(
        str(sample_wav),
        [
            {"op": "highpass", "cutoff": 80},
            {"op": "loudnorm", "i": -16, "lra": 11, "tp": -1.5},
            {"op": "acompressor", "threshold": "-20dB", "ratio": 2, "attack": "200ms"}
        ],
        str(output)
    )
    assert output.exists()


# Example 8: Creative effect chain (fade → warp → pitch)
def test_example_8_creative_chain(sample_wav, temp_dir):
    """README Example 8: Creative effect chain (fade-out, time-stretch, pitch-shift)."""
    if not dawdreamer_available():
        pytest.skip("dawdreamer not installed")
    dd_mod = import_skill_module('dawdreamer', 'pipeline')
    output = temp_dir / "ethereal_pad.wav"
    result = dd_mod.transform(
        str(sample_wav),
        [
            {"op": "fade_out", "duration": 0.5, "curve": "exp"},
            {"op": "time_stretch", "factor": 1.12, "preserve_formants": False},
            {"op": "pitch_shift", "semitones": 5}
        ],
        output=str(output)
    )
    assert result["success"], f"Creative chain failed: {result.get('error')}"
    assert output.exists()


# Example 9: Batch analysis → CSV report
def test_example_9_batch_csv(temp_dir):
    """README Example 9: Batch analyze directory → CSV report."""
    if not librosa_available():
        pytest.skip("librosa not installed")
    audio_analyzer_mod = import_skill_module('audio-analyzer', 'pipeline')

    samples_dir = temp_dir / "samples"
    samples_dir.mkdir()
    wav1 = samples_dir / "a.wav"
    wav2 = samples_dir / "b.wav"
    for wav in (wav1, wav2):
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.3',
                        '-t', '0.3', str(wav)], check=True, capture_output=True)

    output_csv = temp_dir / "sample_features.csv"
    audio_analyzer_mod.extract_batch(
        directory=str(samples_dir),
        pattern="**/*.wav",
        output_format="csv",
        output_file=str(output_csv)
    )
    assert output_csv.exists(), "CSV not created"
    import csv
    with open(output_csv) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) >= 2, f"Expected >=2 rows, got {len(rows)}"
    expected_cols = {'file', 'duration', 'sample_rate'}
    assert expected_cols.issubset(set(rows[0].keys()))


# ---------------------------------------------------------------------------
# Helper: Carla availability
# ---------------------------------------------------------------------------
def carla_available():
    try:
        r = subprocess.run(['carla', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            r2 = subprocess.run(['carla2', '--version'], capture_output=True, timeout=5)
            return r2.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False


# Example 10: Build a Carla rack and render once (plugin-graph mode)
def test_example_10_carla_rack(sample_wav, temp_dir):
    """README Example 10: Carla rack plugin chain — single-pass multi-effect render."""
    if not carla_available():
        pytest.skip("carla not installed")
    carla_mod = import_skill_module('carla-rack', 'pipeline')

    output = temp_dir / "wet.wav"
    rack = carla_mod.CarlaRack()
    rack.add_plugin("/usr/lib/lv2/calf-compressor.lv2", {"threshold": -24, "ratio": 2})
    rack.add_plugin("/usr/lib/lv2/calf-reverb.lv2", {"room_size": 0.4, "wet": 0.25})
    rack.add_plugin("/usr/lib/lv2/calf-limiter.lv2", {"threshold": -0.5})
    result = rack.render_once(str(sample_wav), str(output))
    assert output.exists(), f"Carla render failed: output not created: {result}"
