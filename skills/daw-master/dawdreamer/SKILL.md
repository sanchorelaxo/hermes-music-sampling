---
name: daw-master:dawdreamer
description: "DawDreamer Python framework wrapper - full DAW operations: effects, mixing, time/pitch, VST plugins, multi-track composition"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "daw", "python", "effects", "vst", "mixing", "time-stretch", "pitch-shift"]
    related_skills: ["daw-master:sox-engine", "daw-master:ffmpeg-audio", "daw-master:rubber-band"]
---

# DawDreamer Skill

Wraps the DawDreamer Python framework (JUCE-based) for full DAW capabilities within Hermes.

## Quick Status

```bash
# Check if DawDreamer is available
python -c "import dawdreamer; print(dawdreamer.__version__)"
```

If not installed:

```bash
# DawDreamer requires JUCE and system audio libs. Install dependencies first:
sudo apt update
sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev libcurl4-openssl-dev

# Then install via pip
pip install dawdreamer
```

**Platform note:** Pre-built wheels are only available for x86_64. On ARM (e.g., Raspberry Pi), you must build from source (`pip install --no-binary :all: dawdreamer`), which requires significant RAM and may fail on constrained devices. Consider cross-compiling on a more capable ARM machine or using an x86_64 host.

## Overview

DawDreamer provides:
- **Multi-track composition** — build graphs of audio processors
- **VST2/VST3 hosting** — load and automate plugins
- **Audio playback/recording** — file-based or real-time
- **Time-stretching & pitch-warping** — Ableton-style warping
- **Mix & render** — offline rendering to WAV/MP3/FLAC

This skill wraps those capabilities in a pipeline-friendly interface.

---

## Core Concept: The Pipeline

Transformations are sequences of operations applied to an audio file:

```python
# Conceptual example
result = dawdreamer.transform(
    input="vocals.wav",
    pipeline=[
        {"op": "normalize", "target_level": -6},
        {"op": "time_stretch", "factor": 0.88, "preserve_formants": True},
        {"op": "add_reverb", "room_size": 0.4, "wet": 0.3},
        {"op": "compressor", "threshold": -20, "ratio": 4},
        {"op": "fade", "in": 0.1, "out": 2.0},
    ],
    output="vocals_processed.wav"
)
```

---

## Operations Reference

### Audio I/O
- `load` — Load audio file into working buffer
- `save` / `render` — Write buffer to output file
- `info` — Get audio properties (duration, sample_rate, channels, peak, RMS)

### Time & Pitch
- `time_stretch` — Change tempo without affecting pitch (via Rubber Band or similar)
  - `factor`: tempo multiplier (0.5 = half speed, 2.0 = double)
  - `preserve_formants`: keep vocal character (bool)
- `pitch_shift` — Change pitch without affecting tempo
  - `semitones`: pitch shift in semitones (can be fractional)
  - `preserve_formants`: keep timbre
- `warp` — Full Ableton-style warp markers (advanced)

### Level & Dynamics
- `gain` / `volume` — Apply linear gain (dB: +6, -3, etc.)
- `normalize` — Scale to target peak (default: -0.1 dB)
- `compress` — Dynamic range compression
  - `threshold` (dB), `ratio` (4:1 = 4), `attack` (s), `release` (s)
- `limit` — Hard limiter/ceiling

### EQ & Filtering
- `equalizer` — Multi-band EQ
  - `bands`: list of {freq, gain, Q} objects
- `lowpass` / `highpass` — Simple filters
  - `cutoff` (Hz), `order` (filter steepness)
- `loudness` — Apply loudness normalization (EBU R128 target)

### Effects
- `reverb` — Convolution or algorithmic reverb
  - `room_size`, `wet`, `dry`, `decay`
- `delay` / `echo` — Time-based delay
  - `time` (seconds), `feedback`, `wet`
- `chorus` / `flanger` — Modulation effects
  - `depth`, `rate`, `mix`
- `distortion` / `overdrive` — Waveshaping

### Editing
- `trim` / `crop` — Extract segment
  - `start` (seconds), `end` (seconds or `duration`)
- `fade` / `fade_in` / `fade_out` — Fade amplitude
  - `duration` (seconds), `curve` (`linear`, `exp`, `log`)
- `reverse` — Reverse audio
- `concat` / `append` — Join audio files end-to-end
- `overlay` / `mix` — Blend two audio files (sample-accurate sync)

### Mixing
- `add_track` — Load additional audio as a new track
- `mix_tracks` — Sum all tracks with optional per-track gain/pan
- `pan` / `balance` — Stereo positioning
- `solo` / `mute` — Track enable/disable

### Analysis (Read-Only)
- `analyze` — Full feature extraction
  - Returns: duration, sample_rate, channels, peak_dB, RMS_dB, loudness_LUFS
  - Optional: `compute_mfcc`, `compute_spectral_contrast`
- `beat_track` — Estimate tempo and beats (like librosa)
- `onset_detect` — Find onset times
- `pitch_detect` — Fundamental frequency estimation

---

## Tool Use: Implementation Pattern

```python
from hermes_tools import file, execute_code, web_search

# DawDreamer skill file structure:
SKILL.md   ← this file (metadata + documentation)
dawdreamer/__init__.py   ← main implementation
dawdreamer/examples/     ← example scripts
dawdreamer/templates/    ← project templates
```

The skill registers with Hermes as `skill:daw-master:dawdreamer` (or `dawdreamer` if
the `daw-master` namespace is implicit).

---

## Example Scripts

### Simple Time-Stretch + Fade

```python
import dawdreamer

result = dawdreamer.transform(
    input="input.wav",
    pipeline=[
        {"op": "time_stretch", "factor": 0.88, "preserve_formants": True},
        {"op": "normalize", "target_level": -6},
        {"op": "fade_out", "duration": 1.5},
    ],
    output="slowed_faded.wav"
)
# result: {success: true, output: "slowed_faded.wav", duration: 45.2}
```

### Add Reverb from a DSP rack (VST)

```python
result = dawdreamer.transform(
    input="drums.wav",
    pipeline=[
        {"op": "load_vst", "path": "/usr/local/vst/ValhallaRoom.vst3"},
        {"op": "set_param", "plugin_idx": 0, "param": "RoomSize", "value": 0.75},
        {"op": "set_param", "plugin_idx": 0, "param": "Wet", "value": 0.4},
    ],
    output="drums_spacy.wav"
)
```

### Mix Two Stems Together

```python
result = dawdreamer.mix(
    tracks=[
        {"path": "vocals.wav", "gain_db": 0, "pan": 0.0},
        {"path": "instrumental.wav", "gain_db": -3, "pan": 0.3},
    ],
    output="full_mix.wav",
    normalize_final=True
)
```

### Batch Process a Directory

```python
from pathlib import Path

for wav in Path("samples/").glob("*.wav"):
    out = f"processed/{wav.stem}_proc.wav"
    dawdreamer.transform(
        input=str(wav),
        pipeline=[{"op": "normalize"}, {"op": "compress", "threshold": -20}],
        output=out
    )
```

---

## Error Handling & Safety

- **Input validation**: File existence, format support, readable
- **Dry-run mode**: `dry_run=True` describes pipeline without executing
- **Peak protection**: Clipping prevention (`clip_protection=True`)
- **Backup originals**: `backup_original=True` copies input to `.bak/` before processing
- **Timeouts**: Long renders can be bounded via `timeout_seconds`

---

## Hermes Integration

Call from Hermes via:

```
Use skill daw-master:dawdreamer transform input="file.wav" pipeline=[...] output="out.wav"
```

Or from Python:

```python
from hermes import skill

result = skill.call('daw-master:dawdreamer', 'transform', {
    'input': 'sample.wav',
    'pipeline': [...],
    'output': 'out.wav'
})
```

---

## Chaining with Other Skills

DawDreamer integrates downstream/upstream with other `daw-master` skills:

```python
# 1. Analyze with audio-analyzer
analysis = audio_analyzer.analyze("sample.wav")

# 2. Build pipeline based on analysis
pipeline = []
if analysis["loudness_lufs"] > -10:
    pipeline.append({"op": "gain", "amount_db": -3})  # bring down
if analysis["bpm"] < 80:
    pipeline.append({"op": "time_stretch", "factor": 1.15})  # speed up

# 3. Apply transformations
result = dawdreamer.transform("sample.wav", pipeline=pipeline, output="final.wav")

# 4. Tag with metadata
bwfmetaedit.write("final.wav", description="Processed via Hermes pipeline")
```

---

## Notes

- DawDreamer uses JUCE's audio engine; real-time constraints apply. For long files,
  consider chunked rendering (`chunk_size` parameter).
- VST plugin paths: Set `VST_PATH` or `VST3_PATH` environment variables, or pass
  explicit `vst_search_paths` to the skill.
- Sample rate conversion: DawDreamer resamples using high-quality algorithms; no
  manual resample step needed unless targeting specific sample rate.
- Multi-threading: Set `num_workers` for batch operations to parallelize across CPU cores.
