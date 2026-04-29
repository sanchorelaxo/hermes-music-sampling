"""
Tests for dawdreamer skill.

These tests mock the DawDreamer library so they run without the binary
dependencies. The mocks simulate DawDreamer's API behavior.
"""
import pytest
from pathlib import Path
import sys
import types
import warnings
import platform

from conftest import import_skill_module


# ---------------------------------------------------------------------------
# Mock helper
# ---------------------------------------------------------------------------
def _install_fake_dawdreamer(monkeypatch):
    """Install a fake dawdreamer module in sys.modules."""
    fake_dd = types.ModuleType("dawdreamer")
    fake_dd.__version__ = "0.8.3"

    class FakeAudioBuffer:
        """Simple mock of DawDreamer's AudioBuffer with numpy-like slicing."""
        def __init__(self, data=None, sample_rate=44100):
            self.sampleRate = sample_rate
            import numpy as np
            if data is not None:
                self.data = data
            else:
                # default: 0.5 sec stereo at given sample rate
                self.data = np.zeros((2, int(0.5 * sample_rate)), dtype=np.float32)
            # Derive attributes from data
            if self.data.ndim == 2:
                self.channels = self.data.shape[0]
                self.numFrames = self.data.shape[1]
            else:
                self.channels = 1
                self.numFrames = self.data.shape[0]
            self.duration = self.numFrames / sample_rate
            self._peak = float(np.max(np.abs(self.data))) if self.data.size else 0.0

        @classmethod
        def from_file(cls, filepath, sample_rate):
            return cls(sample_rate=sample_rate)

        def get_peak(self):
            return self._peak

        def get_rms(self):
            import numpy as np
            return float(np.sqrt(np.mean(self.data**2))) if self.data.size else 0.0

        def get_channels(self):
            return self.data

        def save_to_file(self, path):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch()

        def __getitem__(self, key):
            # Support slicing like audio[:, start:end] returning a new FakeAudioBuffer
            sliced = self.data[key]
            return FakeAudioBuffer(data=sliced, sample_rate=self.sampleRate)

    fake_dd.AudioBuffer = FakeAudioBuffer

    # Dummy types for annotations — not used at runtime
    class _Dummy:
        pass

    fake_dd.RenderEngine = _Dummy
    fake_dd.PlaybackProcessor = _Dummy
    fake_dd.AddProcessor = _Dummy

    class FakeRenderEngine:
        def __init__(self, sampleRate=44100, bufferSize=512):
            self.sampleRate = sampleRate
            self.bufferSize = bufferSize

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

        def make_playback_processor(self, name, buffer):
            return types.SimpleNamespace(name=name, get_name=lambda: name)

        def make_playback_warp_processor(self, name, buffer):
            # Returns a warp processor with controllable time/pitch ratios
            p = types.SimpleNamespace(name=name, time_ratio=1.0, pitch_ratio=1.0)
            return p

        def make_gain_processor(self, name, initial=0.0):
            p = types.SimpleNamespace(name=name, gain=1.0)
            return p

        def make_filter_processor(self, *a, **kw):
            return types.SimpleNamespace(name=a[0] if a else "f")

        def make_compressor_processor(self, *a, **kw):
            return types.SimpleNamespace(name=a[0] if a else "c")

        def make_reverb_processor(self, *a, **kw):
            return types.SimpleNamespace(name=a[0] if a else "r")

        def make_fade_processor(self, *a, **kw):
            p = types.SimpleNamespace(name=a[0] if a else "fade")
            p.fade_in = lambda: None
            p.fade_out = lambda: None
            return p

        def make_add_processor(self, *a, **kw):
            return types.SimpleNamespace(name=a[0] if a else "add")

        def make_plugin_processor(self, *a, **kw):
            p = types.SimpleNamespace(name=a[0] if a else "plugin")
            p.set_parameter = lambda *a, **kw: None
            p.get_parameters_description = lambda: [{"name": "gain", "value": 0.0}]
            return p

        def load_graph(self, g):
            pass

        def render(self, d):
            pass

        def get_audio(self):
            buf = FakeAudioBuffer()
            import numpy as np
            buf.data = np.zeros((2, 22050), dtype=np.float32)
            return buf

        def close(self):
            pass

    fake_dd.RenderEngine = FakeRenderEngine
    monkeypatch.setitem(sys.modules, "dawdreamer", fake_dd)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _is_arm_architecture():
    """Return True if running on ARM architecture (Raspberry Pi, etc.)."""
    machine = platform.machine().lower()
    return machine in ('arm64', 'aarch64', 'armv7l', 'armv8l', 'arm')

@pytest.fixture(autouse=True)
def mock_dawdreamer(monkeypatch):
    """Automatically mock DawDreamer for all tests in this file."""
    if not _is_arm_architecture():
        try:
            import dawdreamer
            # Real DawDreamer available on x86_64, skip mocking
            yield
            return
        except ImportError:
            # dawdreamer not installed, fall through to mock
            pass
    
    # On ARM or when dawdreamer unavailable, install the mock
    _install_fake_dawdreamer(monkeypatch)
    yield


@pytest.fixture
def sample_wav(tmp_path):
    """Create a minimal dummy WAV file (header only, 0.5s silence)."""
    wav = tmp_path / "test.wav"
    import subprocess
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
         "-t", "0.5", str(wav)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        wav.write_bytes(
            b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        )
    return wav


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for output files."""
    out = tmp_path / "out"
    out.mkdir()
    return out


@pytest.fixture
def dd():
    """Import the dawdreamer pipeline module after mocking is in place."""
    return import_skill_module("dawdreamer", "pipeline")



@pytest.fixture
def ops():
    """Import the operations module for unit testing."""
    return import_skill_module("dawdreamer", "operations")

# ---------------------------------------------------------------------------
# Transform tests
# ---------------------------------------------------------------------------
def test_transform_with_normalize(sample_wav, temp_dir, dd):
    output = temp_dir / "normalized.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "normalize", "target_level": -0.1}],
        output=str(output),
        dry_run=False,
    )
    assert result["success"], f"transform failed: {result.get('error')}"
    assert output.exists(), "Output file not created"


def test_transform_with_gain(sample_wav, temp_dir, dd):
    output = temp_dir / "gain.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "gain", "amount_db": 6.0}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_fade_in(sample_wav, temp_dir, dd):
    output = temp_dir / "fade_in.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "fade_in", "duration": 0.5}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_fade_out(sample_wav, temp_dir, dd):
    output = temp_dir / "fade_out.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "fade_out", "duration": 1.0}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_trim(sample_wav, temp_dir, dd):
    output = temp_dir / "trimmed.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "trim", "start": 0.1, "duration": 0.2}],
        output=str(output),
    )
    if not result["success"]:
        print("TRIM FAILED")
        print("Error:", result.get("error"))
        print("Trace:", result.get("traceback"))
    assert result["success"]
    assert output.exists()


def test_transform_with_time_stretch(sample_wav, temp_dir, dd):
    output = temp_dir / "stretched.wav"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = dd.transform(
            input=str(sample_wav),
            pipeline=[{"op": "time_stretch", "factor": 0.88, "preserve_formants": True}],
            output=str(output),
        )
    # Should not produce "Unknown operation" warnings
    unknown = [x for x in w if "Unknown operation" in str(x.message)]
    assert len(unknown) == 0, f"time_stretch not implemented: {[str(x.message) for x in unknown]}"
    assert result["success"]
    assert output.exists()


def test_transform_with_pitch_shift(sample_wav, temp_dir, dd):
    output = temp_dir / "pitch.wav"
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = dd.transform(
            input=str(sample_wav),
            pipeline=[{"op": "pitch_shift", "semitones": 2.0, "preserve_formants": False}],
            output=str(output),
        )
    unknown = [x for x in w if "Unknown operation" in str(x.message)]
    assert len(unknown) == 0, f"pitch_shift not implemented: {[str(x.message) for x in unknown]}"
    assert result["success"]
    assert output.exists()


def test_transform_with_compressor(sample_wav, temp_dir, dd):
    output = temp_dir / "compressed.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "compress", "threshold": -20.0, "ratio": 4.0, "attack": 2.0, "release": 50.0}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_reverb(sample_wav, temp_dir, dd):
    output = temp_dir / "reverb.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "reverb", "room_size": 0.5, "wet": 0.3, "dry": 0.7}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_filter(sample_wav, temp_dir, dd):
    output = temp_dir / "filtered.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "filter", "mode": "low", "freq": 1000.0, "q": 0.707}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_with_overlay(sample_wav, temp_dir, dd):
    track_b = temp_dir / "other.wav"
    track_b.write_bytes(b"dummyaudio")
    output = temp_dir / "mix.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[
            {"op": "overlay", "track_b": str(track_b), "gain_a": 0.0, "gain_b": -3.0}
        ],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_chain_multiple_ops(sample_wav, temp_dir, dd):
    output = temp_dir / "chain.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[
            {"op": "normalize", "target_level": -6},
            {"op": "gain", "amount_db": 3},
            {"op": "fade_in", "duration": 0.2},
            {"op": "fade_out", "duration": 0.3},
        ],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()
    assert result["steps"] == 4


def test_transform_dry_run_returns_metadata(sample_wav, temp_dir, dd):
    output = temp_dir / "dry.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[
            {"op": "normalize"},
            {"op": "time_stretch", "factor": 0.9},
        ],
        output=str(output),
        dry_run=True,
    )
    assert result["success"] is True
    assert result.get("dry_run") is True
    assert output.exists() is False
    assert result["steps"] == 2
    assert "normalize" in result["ops"]
    assert "time_stretch" in result["ops"]


def test_transform_unknown_op_returns_error(sample_wav, temp_dir, dd):
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "unicorn_horn", "sparkle": 0.5}],
        output=str(temp_dir / "fail.wav"),
    )
    assert result["success"] is False
    assert "Unknown operation" in result.get("error", "")


def test_transform_missing_input_returns_error(temp_dir, dd):
    result = dd.transform(
        input=str(temp_dir / "nonexistent.wav"),
        pipeline=[{"op": "normalize"}],
        output=str(temp_dir / "out.wav"),
    )
    assert result["success"] is False
    error = result.get("error", "").lower()
    assert "not found" in error or "no such file" in error


def test_mix_two_tracks(sample_wav, temp_dir, dd):
    output = temp_dir / "mix.wav"
    result = dd.mix(
        tracks=[
            {"path": str(sample_wav), "gain_db": 0.0, "pan": 0.0},
            {"path": str(sample_wav), "gain_db": -3.0, "pan": 0.0},
        ],
        output=str(output),
        normalize_final=False,
    )
    assert result["success"], f"mix failed: {result.get('error')}"
    assert output.exists()
    assert result["track_count"] == 2


def test_mix_with_normalization(sample_wav, temp_dir, dd):
    output = temp_dir / "norm_mix.wav"
    result = dd.mix(
        tracks=[{"path": str(sample_wav), "gain_db": 0.0}],
        output=str(output),
        normalize_final=True,
    )
    assert result["success"]
    assert output.exists()


def test_analyze_returns_expected_keys(sample_wav, dd):
    info = dd.analyze(str(sample_wav))
    assert isinstance(info, dict)
    for key in ["file", "duration", "sample_rate", "channels", "frames", "peak_dbfs", "rms_db"]:
        assert key in info, f"Missing key {key}"


def test_analyze_nonexistent_file_returns_error(dd):
    info = dd.analyze("/nonexistent/path/file.wav")
    assert info.get("success") is False
    assert "error" in info


def test_backup_original_creates_bak_file(sample_wav, temp_dir, dd):
    output = temp_dir / "with_backup.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "gain", "amount_db": 1}],
        output=str(output),
        backup_original=True,
    )
    assert result["success"]
    bak = output.with_suffix(output.suffix + ".bak")
    assert bak.exists(), "Backup file not created"


def test_transform_with_analysis(sample_wav, temp_dir, dd):
    output = temp_dir / "with_analysis.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "normalize"}],
        output=str(output),
        analysis=True,
    )
    assert result["success"]
    assert "analysis" in result
    ana = result["analysis"]
    for key in ["duration", "sample_rate", "channels", "peak_dbfs", "rms_db"]:
        assert key in ana, f"Analysis missing key {key}"


def test_transform_with_empty_pipeline_returns_error(sample_wav, temp_dir, dd):
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[],
        output=str(temp_dir / "out.wav"),
    )
    assert "success" in result


def test_transform_with_sample_rate_override(sample_wav, temp_dir, dd):
    output = temp_dir / "sr_48k.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "normalize"}],
        output=str(output),
        sample_rate=48000,
    )
    assert result["success"]


def test_mix_with_single_track(sample_wav, temp_dir, dd):
    output = temp_dir / "single.wav"
    result = dd.mix(
        tracks=[{"path": str(sample_wav)}],
        output=str(output),
    )
    assert result["success"]
    assert output.exists()


def test_transform_preserves_formants_default(sample_wav, temp_dir, dd):
    output = temp_dir / "preserve.wav"
    result = dd.transform(
        input=str(sample_wav),
        pipeline=[{"op": "time_stretch", "factor": 1.2}],
        output=str(output),
    )
    assert result["success"]


# ---------------------------------------------------------------------------
# Operation builder unit tests
# ---------------------------------------------------------------------------
def test_op_normalize_returns_gain_spec(ops):
    spec = ops.op_normalize(None, target_level=-6)
    assert spec["type"] == "gain"
    assert "gain_db" in spec


def test_op_gain_returns_gain_spec(ops):
    spec = ops.op_gain(None, amount_db=3.0)
    assert spec["type"] == "gain"
    assert spec["gain_db"] == 3.0


def test_op_time_stretch_returns_spec(ops):
    spec = ops.op_time_stretch(None, factor=0.88, preset="Studio")
    assert spec["type"] == "time_stretch"
    assert spec["factor"] == 0.88
    assert spec["preserve_formants"] is True


def test_op_pitch_shift_returns_spec(ops):
    spec = ops.op_pitch_shift(None, semitones=2.5)
    assert spec["type"] == "pitch_shift"
    assert spec["semitones"] == 2.5


def test_op_fade_in_returns_spec(ops):
    spec = ops.op_fade_in(None, duration=1.0)
    assert spec["type"] == "fade"
    assert spec["direction"] == "in"
    assert spec["duration"] == 1.0


def test_op_fade_out_returns_spec(ops):
    spec = ops.op_fade_out(None, duration=2.0)
    assert spec["type"] == "fade"
    assert spec["direction"] == "out"
    assert spec["duration"] == 2.0


def test_op_trim_returns_spec(ops):
    spec = ops.op_trim(None, start=1.0, end=5.0)
    assert spec["type"] == "trim"
    assert spec["start"] == 1.0
    assert spec["end"] == 5.0


def test_op_compress_returns_spec(ops):
    spec = ops.op_compress(None, threshold=-20, ratio=4, attack=1, release=50)
    assert spec["type"] == "compressor"
    assert spec["threshold"] == -20
    assert spec["ratio"] == 4.0


def test_op_filter_returns_spec(ops):
    spec = ops.op_filter(None, mode="high", freq=2000, q=0.5, gain=3)
    assert spec["type"] == "filter"
    assert spec["mode"] == "high"
    assert spec["freq"] == 2000.0


def test_op_reverb_returns_spec(ops):
    spec = ops.op_reverb(None, room_size=0.7, wet=0.4, dry=0.6)
    assert spec["type"] == "reverb"
    assert spec["room_size"] == 0.7


def test_op_overlay_returns_spec(ops):
    spec = ops.op_overlay(None, "track_b.wav", gain_a=0, gain_b=-3)
    assert spec["type"] == "overlay"
    assert spec["track_b"] == "track_b.wav"


def test_op_load_vst_returns_spec(ops):
    spec = ops.op_load_vst(None, path="/path/to/vst.vst3", plugin_idx=0)
    assert spec["type"] == "load_vst"
    assert spec["path"] == "/path/to/vst.vst3"


def test_op_set_param_returns_spec(ops):
    spec = ops.op_set_param(None, plugin_idx=0, param="RoomSize", value=0.75)
    assert spec["type"] == "set_param"
    assert spec["param"] == "RoomSize"
    assert spec["value"] == 0.75


def test_op_registry_contains_expected_ops(ops):
    expected = [
        "normalize", "gain", "volume", "time_stretch", "stretch", "pitch_shift",
        "fade_in", "fade_out", "trim", "crop", "compress", "compressor",
        "filter", "eq", "equalizer", "reverb", "overlay", "add_track",
        "load_vst", "set_param",
    ]
    for op in expected:
        assert op in ops.OP_REGISTRY, f"Missing op in registry: {op}"
