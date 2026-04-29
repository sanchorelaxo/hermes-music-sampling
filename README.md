# Hermes Music Sampling

Aggregated music sampling skills for Hermes Agent — enabling audio production, analysis, and remixing on Linux.

## Overview

This project collects and organizes music sampling and audio processing skills for use with Hermes Agent. It provides tools and knowledge for discovering, analyzing, editing, and remixing audio files from the command line, both in pure CLI tools and Python environments.

**Architecture**: All skills live under the `daw-master` meta-skill namespace, which defines a unified interface: `transform(input, pipeline, output)`, `mix(tracks, output)`, and `analyze(file)`.

## Implemented Skills

| Skill | Tool | Status |
|-------|------|--------|
| [`dawdreamer`](skills/daw-master/dawdreamer/SKILL.md) | DawDreamer (Python, JUCE) | ✅ Wrapped — effect chain, VST hosting, multi-track |
| [`sox-engine`](skills/daw-master/sox-engine/SKILL.md) | SoX (CLI Swiss Army knife) | ✅ Implemented — 12+ effects, mix, analyze |

## Skills Under Development

| Skill | Tool | Expected Role |
|-------|------|--------------|
| `ffmpeg-audio` | FFmpeg | Codec work, complex filtergraphs |
| `rubber-band-engine` | Rubber Band CLI | High-quality time-stretch/pitch-shift |
| `audio-analyzer` | librosa + sonic-annotator | BPM, key, MFCC, loudness extraction |
| `batch-processor` | SoX + FFmpeg | Directory-wide pipelines, parallel |
| `metadata-manager` | BWF MetaEdit | BWF/iXML/ID3 tag management |
| `ardour-automator` | Ardour (Lua) | Headless session rendering |
| `reaper-agent` | REAPER + Wine | Batch render via ReaScript |
| `carla-rack` | Carla | Plugin chain testing |

See [RESEARCH.md](RESEARCH.md) for full tool comparison and rationale.

---

## Quick Start

```bash
# Clone
git clone https://github.com/sanchorelaxo/hermes-music-sampling.git
cd hermes-music-sampling

# Install SoX (for sox-engine — works immediately)
sudo apt install sox

# Run an example (requires input.wav in cwd)
python skills/daw-master/sox-engine/examples/01_normalize_compress_fade.py

# Optional: Install DawDreamer (requires JUCE deps)
sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev
pip install dawdreamer
```

---

## Example Usage

### Using `sox-engine` (fast, no Python deps)
```python
from daw_master.sox_engine import transform, mix, analyze

# Normalize + fade out
transform("input.wav", [
    {"op": "normalize", "peak": -0.1},
    {"op": "fade", "type": "out", "length": 2.0}
], "output.wav")

# Mix two stems
mix([
    {"path": "vocals.wav", "gain": 1.0},
    {"path": "beats.wav", "gain": 0.7}
], "full_mix.wav", normalize_final=True)

# Get stats
info = analyze("sample.wav")
print(f"Duration: {info['duration']}s, Peak: {info['peak']:.2f}")
```

### Using `dawdreamer` (full DAW in Python)
```python
from daw_master.dawdreamer import transform, mix

# Time-stretch + reverb
transform("sample.wav", [
    {"op": "time_stretch", "factor": 0.88, "preserve_formants": True},
    {"op": "reverb", "room_size": 0.5, "wet": 0.3}
], "slowed_reverb.wav")

# Multi-track mix with per-track gain/pan
mix([
    {"path": "drums.wav", "gain_db": -3, "pan": -0.2},
    {"path": "bass.wav", "gain_db": 0, "pan": 0.3},
    {"path": "synth.wav", "gain_db": -6, "pan": 0.0}
], "mixdown.wav", normalize_final=True)
```

---

## Chaining Skills

```python
# 1. sox-engine: quick trim + normalize
sox_engine.transform("raw.wav", [{"op": "trim", "start": 0, "length": 30}, {"op": "normalize"}], "trimmed.wav")

# 2. dawdreamer: add effects
dawdreamer.transform("trimmed.wav", [{"op": "compand"}, {"op": "reverb"}], "processed.wav")

# 3. audio-analyzer (when ready): extract features
# analyzer.extract("processed.wav", "tags.json")
```

---

## Project Layout

```
skills/daw-master/
├── SKILL.md           # Meta-skill specification
├── dawdreamer/        # DawDreamer wrapper (Python-JUCE DAW)
│   ├── SKILL.md
│   ├── __init__.py
│   ├── pipeline.py
│   ├── operations.py
│   └── examples/
└── sox-engine/        # SoX CLI wrapper
    ├── SKILL.md
    ├── __init__.py
    ├── pipeline.py
    └── examples/
```

More directories waiting to be filled: `analysis/`, `conversion/`, `editing/`, `metadata/`, `daw-integration/`.

---

## Research Context

See [RESEARCH.md](RESEARCH.md) for the full survey of Linux audio tools that meet these criteria:

- Can run Python scripts or provide Python bindings
- Have a CLI and/or headless mode
- Can analyze WAV, MP3 files
- Can edit/remix existing sound files (preferably via CLI)

**Top picks** per category:
- **Python-native**: DawDreamer, librosa, PyDub
- **CLI tools**: SoX, FFmpeg, Rubber Band, Sonic Annotator, BWF MetaEdit
- **Full DAWs**: Ardour (Lua), REAPER (Wine + ReaScript), Carla (plugin host)

---

## Contributing

New skills should follow the `daw-master` pattern:

1. Create `skills/daw-master/<skill-name>/`
2. Implement `transform()`, `mix()`, `analyze()` in `pipeline.py`
3. Document every operation in `SKILL.md`
4. Add 2-3 example scripts in `examples/`
5. Add a placeholder README in the relevant category directory (`analysis/`, etc.)

See `MANIFEST.md` for complete architecture notes and design principles.

---

## License

MIT