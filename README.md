# Hermes Music Sampling

Aggregated music sampling skills for Hermes Agent — enabling audio production, analysis, and remixing on Linux.

## Overview

This project collects and organizes music sampling and audio processing skills for use with Hermes Agent. It provides tools for discovering, analyzing, editing, and remixing audio files from the command line.

**Architecture**: All skills live under the `daw-master` meta-skill namespace, which defines a unified interface: `transform(input, pipeline, output)`, `mix(tracks, output)`, and `analyze(file)`.

## Implemented Skills

| Skill | Tool | Status | What It Does |
|-------|------|--------|--------------|
|| [`sox-engine`](skills/daw-master/sox-engine/SKILL.md) | SoX CLI | ✅ Implemented | 12+ effects: normalize, fade, trim, compand, EQ, mix |
|| [`ffmpeg-audio`](skills/daw-master/ffmpeg-audio/SKILL.md) | FFmpeg filters | ✅ Implemented | Codecs, loudnorm, filtergraphs, multi-track mix |
|| [`rubber-band-engine`](skills/daw-master/rubber-band-engine/SKILL.md) | Rubber Band | ✅ Implemented | Professional time-stretch & pitch-shift |
|| [`audio-analyzer`](skills/daw-master/audio-analyzer/SKILL.md) | librosa + Vamp | ✅ Implemented | BPM, key, MFCC, loudness, spectral features |
|| [`dawdreamer`](skills/daw-master/dawdreamer/SKILL.md) | DawDreamer (Python, JUCE) | ⚙️ Scaffolded | Full DAW: VST hosting, multi-track, effect graphs |

## Planned Skills

| Skill | Tool | Role |
|-------|------|------|
|| `batch-processor` | SoX + FFmpeg scripts | Apply pipeline to directories |
|| [`metadata-manager`](skills/metadata-manager/SKILL.md) | BWF MetaEdit | ✅ Implemented | BWF/iXML/ID3 tagging |
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

Our skills chain in one of two modes:

- **Sequential processing** — each skill consumes an input file and produces an output, the next skill reads that output (e.g. `sox → ffmpeg → rubber-band`). Each step sees the fully-realized audio file.

- **Rack (plugin graph) processing** — a set of plugins is configured as a graph; the DAW loads the input once, routes audio through all plugin instances in the configured order, then renders a single output. `carla-rack` and `dawdreamer`'s VST chain mode work this way.

Both patterns are valid. Use sequential when you want clear, modular steps you can inspect individually. Use rack mode when you want a single consistent plugin state throughout a track, avoiding repeated disk I/O and ensuring latency compensation is handled by the host.

```python
# Example 1: Trim and normalize quickly with SoX (simple 2-step)
sox.transform("raw.wav",
    [{"op": "trim", "start": 0, "length": 30}, {"op": "normalize"}],
    "trimmed.wav")

# Example 2: Apply professional tempo warp with Rubber Band (preserve formants)
rubber.transform("trimmed.wav",
    [{"op": "time_stretch", "factor": 0.98, "formant": True}],
    "timed.wav")

# Example 3: Final loudness + encode to AAC with FFmpeg (codec delivery)
ffmpeg.transform("timed.wav",
    [{"op": "loudnorm", "i": -14}],
    "final.m4a", codec="aac")

# Example 4: Analyze first, then conditionally process based on features (discover → act)
from daw_master.audio_analyzer import analyze
features = analyze("sample.wav")
pipeline = []
# audio-analyzer returns 'loudness' (RMS dB), not 'loudness_lufs'
if features["loudness"] > -10:
    pipeline.append({"op": "gain", "amount_db": -3})   # bring down hot audio
if features["tempo"] < 80:
    pipeline.append({"op": "time_stretch", "factor": 1.15})  # speed up slow track
if pipeline:
    dawdreamer.transform("sample.wav", pipeline=pipeline, output="processed.wav")

# Example 5: Build a full mix from three stems with per-track processing (multi-track)
from daw_master.dawdreamer import mix
result = mix(
    tracks=[
        {"path": "vocals.wav",   "gain_db": 0,  "pan": 0.0,  "effects": [
            {"op": "compressor", "threshold": -20, "ratio": 3},
            {"op": "reverb",     "room_size": 0.3, "wet": 0.2}
        ]},
        {"path": "guitar.wav",   "gain_db": -3, "pan": 0.3,  "effects": [
            {"op": "eq", "low_gain": 4}
        ]},
        {"path": "drums.wav",    "gain_db": -6, "pan": -0.2, "effects": [
            {"op": "compress", "threshold": -18, "ratio": 4}
        ]},
    ],
    output="full_mix.wav",
    normalize_final=True,
    master_bus_chain=[
        {"op": "limiter", "threshold": -0.5},
        {"op": "normalize", "target_level": -1.0}
    ]
)

# Example 6: VST plugin chain applied to a vocal stem (VST-heavy production)
vst_chain = [
    {"op": "load_vst", "path": "/usr/local/vst/ValhallaRoom.vst3"},
    {"op": "set_param", "plugin_idx": 0, "param": "RoomSize", "value": 0.75},
    {"op": "set_param", "plugin_idx": 0, "param": "Wet",       "value": 0.4},
    {"op": "load_vst", "path": "/usr/local/vst/SoftubeTubeSaturator.vst3"},
    {"op": "set_param", "plugin_idx": 1, "param": "Drive",     "value": 0.25},
]
dawdreamer.transform("vocals_dry.wav", pipeline=vst_chain, output="vocals_spacy.wav")

# Example 7: Smart loudness normalization with FFmpeg EBU R128 (broadcast-safe)
ffmpeg.transform("raw.wav",
    [{"op": "highpass", "cutoff": 80},
     {"op": "loudnorm", "i": -16, "lra": 11, "tp": -1.5},
     {"op": "acompressor", "threshold": "-20dB", "ratio": 2, "attack": "200ms"}],
    "broadcast_ready.wav")

# Example 8: Fade-out → time-stretch → pitch-shift chain (creative effect)
dawdreamer.transform("pad.wav",
    [{"op": "fade_out",  "duration": 4.0, "curve": "exp"},
     {"op": "time_stretch", "factor": 1.12, "preserve_formants": False},
     {"op": "pitch_shift", "semitones": 5}],
    "ethereal_pad.wav")

# Example 9: Analyze-batch → export CSV report (batch discovery)
from daw_master.audio_analyzer import extract_batch
extract_batch(
    directory="./samples",
    pattern="**/*.wav",
    output_format="csv",
    output_file="sample_features.csv"
)

# Example 9: Build a Carla rack and render once (plugin-graph mode)
from daw_master.carla_rack import CarlaRack

rack = CarlaRack()
# Parallel signal chain — all plugins together on one pass
rack.add_plugin("/usr/lib/lv2/calf-compressor.lv2", {"threshold": -24, "ratio": 2})
rack.add_plugin("/usr/lib/lv2/calf-reverb.lv2",     {"room_size": 0.4, "wet": 0.25})
rack.add_plugin("/usr/lib/lv2/calf-limiter.lv2",    {"threshold": -0.5})
# Single render — one disk I/O, all plugins applied together
rack.render_once("dry.wav", "wet.wav")
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
├── audio-analyzer/             # ✅ librosa — feature extraction, Vamp support
├── dawdreamer/                 # ⚙️ Scaffolded — full DAW VST hosting
├── batch-processor/            # ✅ Implemented — SoX/FFmpeg batch pipelines
├── metadata-manager/           # ✅ Implemented — BWF/iXML/ID3 tagging
├── ardour-automator/           # ✅ Implemented — Ardour headless automation & export
├── carla-rack/                 # Reserved — Carla plugin chain
└── reaper-agent/               # Reserved — REAPER automation
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
