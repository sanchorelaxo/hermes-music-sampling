# Hermes Music Sampling

Aggregated music sampling skills for Hermes Agent — enabling audio production, analysis, and remixing on Linux.

## Overview

This project collects and organizes music sampling and audio processing skills for use with Hermes Agent. It provides tools for discovering, analyzing, editing, and remixing audio files from the command line.

**Architecture**: All skills live under the `daw-master` meta-skill namespace, which defines a unified interface: `transform(input, pipeline, output)`, `mix(tracks, output)`, and `analyze(file)`.

## Implemented Skills

| Skill | Tool | Status | What It Does |
|-------|------|--------|--------------|
| [`dawdreamer`](skills/daw-master/dawdreamer/SKILL.md) | DawDreamer (Python, JUCE) | ⚙️ Scaffolded | Full DAW: VST hosting, multi-track, effect graphs |
| [`sox-engine`](skills/daw-master/sox-engine/SKILL.md) | SoX CLI | ✅ Implemented | 12+ effects: normalize, fade, trim, compand, EQ, mix |
| [`ffmpeg-audio`](skills/daw-master/ffmpeg-audio/SKILL.md) | FFmpeg filters | ✅ Implemented | Codecs, loudnorm, filtergraphs, multi-track mix |
| [`rubber-band-engine`](skills/daw-master/rubber-band-engine/SKILL.md) | Rubber Band | ✅ Implemented | Professional time-stretch & pitch-shift |

## Planned Skills

| Skill | Tool | Role |
|-------|------|------|
| `audio-analyzer` | librosa + sonic-annotator | Extract BPM, key, MFCC, loudness |
| `batch-processor` | SoX + FFmpeg scripts | Apply pipeline to directories |
| `metadata-manager` | BWF MetaEdit | BWF/iXML/ID3 tagging |
| `ardour-automator` | Ardour (Lua) | Headless session render |
| `reaper-agent` | REAPER + Wine | Batch render automation |
| `carla-rack` | Carla | Plugin chain testbench |

See [RESEARCH.md](RESEARCH.md) for full tool comparison.

---

## Quick Start

```bash
# Clone
git clone https://github.com/sanchorelaxo/hermes-music-sampling.git
cd hermes-music-sampling

# Install core tools
sudo apt install sox ffmpeg rubberband-cli   # Debian/Ubuntu
# brew install sox ffmpeg rubberband        # macOS

# Test sox-engine (requires input.wav in cwd)
python skills/daw-master/sox-engine/examples/01_normalize_compress_fade.py

# Test ffmpeg-audio
python skills/daw-master/ffmpeg-audio/examples/01_loudnorm_compress.py

# Test rubber-band-engine
python skills/daw-master/rubber-band-engine/examples/01_time_stretch_formant.py

# Optional: Install DawDreamer (requires JUCE deps)
# sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev
# pip install dawdreamer
```

---

## Example Usage

### sox-engine — Fast effect chain
```python
from daw_master.sox_engine import transform, mix, analyze

transform("raw.wav", [
    {"op": "normalize", "peak": -0.1},
    {"op": "fade", "type": "out", "length": 1.5},
    {"op": "bass", "gain": 6}
], "out.wav")

info = analyze("out.wav")
print(f"Duration: {info['duration']}s, Peak: {info['peak']:.2f}")
```

### ffmpeg-audio — Loudness normalization + codec
```python
from daw_master.ffmpeg_audio import transform

transform("raw.wav", [
    {"op": "highpass", "cutoff": 80},
    {"op": "loudnorm", "i": -16, "lra": 8},
    {"op": "acompressor", "threshold": "-20dB", "ratio": 3}
], "final.m4a", codec="aac", bitrate="192k")
```

### rubber-band-engine — Clean time/pitch
```python
from daw_master.rubber_band_engine import transform

transform("sample.wav", [
    {"op": "time_stretch", "factor": 0.94, "formant": True, "quality": "high"}
], "slowed.wav")
```

---

## Skill Comparison

| Operation | sox-engine | ffmpeg-audio | rubber-band-engine |
|-----------|-----------|--------------|-------------------|
| normalize | ✅ `norm` | ✅ `loudnorm` / `volume` | ❌ (use another skill) |
| gain | ✅ `gain` | ✅ `volume` | ❌ |
| trim | ✅ `trim` | ✅ `atrim` | ❌ |
| fade | ✅ `fade` | ✅ `afade` | ❌ |
| compress | ✅ `compand` | ✅ `acompressor` | ❌ |
| EQ | ✅ `equalizer`, `bass`, `treble` | ✅ `equalizer`, filters | ❌ |
| reverb | ✅ simple `reverb` | ⚠️ limited | ❌ |
| time-stretch | ⚠️ basic | ⚠️ `atempo` (0.5–2.0 only) | ✅ **high-quality** |
| pitch-shift | ❌ | ❌ | ✅ **high-quality** |
| mix tracks | ✅ `mix` | ✅ `amix` | ❌ |
| codec convert | ❌ (via sox but limited) | ✅ all codecs | ❌ |

Each skill covers its strengths; chain them for complex workflows.

---

## Chaining Skills

```python
# 1. Trim and normalize quickly with SoX
sox.transform("raw.wav", [{"op": "trim", "start": 0, "length": 30}, {"op": "normalize"}], "trimmed.wav")

# 2. Apply professional tempo warp with Rubber Band
rubber.transform("trimmed.wav", [{"op": "time_stretch", "factor": 0.98, "formant": True}], "timed.wav")

# 3. Final loudness + encode to AAC with FFmpeg
ffmpeg.transform("timed.wav", [{"op": "loudnorm", "i": -14}], "final.m4a", codec="aac")
```

---

## Project Layout

```
skills/daw-master/
├── SKILL.md                    # Meta-skill specification
├── dawdreamer/                 # DawDreamer wrapper (scaffolded)
├── sox-engine/                 # ✅ SoX — effects, edits, mix
├── ffmpeg-audio/               # ✅ FFmpeg — filters, codecs, loudnorm
├── rubber-band-engine/         # ✅ Rubber Band — time/pitch
├── analysis/                   # Reserved for audio-analyzer (librosa)
├── conversion/                 # Reserved for batch tools
├── daw-integration/            # Reserved for Ardour/REAPER/Carla
├── editing/                    # Reserved for batch-processor
└── metadata/                   # Reserved for BWF tagger
```

---

## Research Context

See [RESEARCH.md](RESEARCH.md) for complete Linux audio tool survey covering:
- Python frameworks (DawDreamer, librosa, PyDub)
- CLI utilities (SoX, FFmpeg, Rubber Band, Sonic Annotator, Ecasound, BWF MetaEdit)
- Full DAWs (Ardour, REAPER, Carla)

---

## License

MIT
