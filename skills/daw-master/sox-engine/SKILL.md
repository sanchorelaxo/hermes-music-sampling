---
name: daw-master:sox-engine
description: "Use when doing CLI audio processing with SoX — normalize, fade, trim, EQ, compression, reverb, format conversion, or analysis. Wraps SoX for pipeline-based audio transforms."
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "sox", "cli", "batch", "effects", "conversion"]
    related_skills: ["daw-master:dawdreamer", "daw-master:ffmpeg-audio", "daw-master:rubber-band"]
---

# SoX Engine

Wraps SoX (Sound eXchange) — the classic CLI audio processor. Available on virtually every Linux/macOS system.

## Installation

```bash
sudo apt install sox      # Debian/Ubuntu
brew install sox           # macOS
sudo dnf install sox       # Fedora
sox --version
```

## When to Use

- Normalizing, fading, trimming audio files
- Applying EQ, compression, bass/treble boosts
- Converting between audio formats (WAV, MP3, FLAC, OGG, etc.)
- Converting sample rate or channel count
- Applying reverb, echo, or phaser/flanger effects
- Analyzing audio properties (RMS, peak, duration)
- Mixing multiple tracks with per-track gain

## Core API

```python
from daw_master.sox_engine import transform, mix, analyze

# Pipeline transform
result = transform(
    input="input.wav",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "fade", "in": 0.5, "out": 1.0},
        {"op": "compand", "attack": 0.01, "decay": 0.1, "threshold": -20},
    ],
    output="output.wav"
)

# Mix multiple tracks
result = mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0},
        {"path": "beats.wav", "gain": 0.7},
    ],
    output="mix.wav",
    normalize=True
)

# Analyze
info = analyze("sample.wav")
# {duration, sample_rate, channels, peak, rms, bit_depth, ...}
```

## Operations

Full reference: [references/operations.md](mdc:references/operations.md)

### Gain & Level
- `gain` / `volume` — linear or dB adjustment
- `normalize` — peak normalization

### Editing
- `trim` — extract segment by start/end time
- `fade` — fade in/out (type: in/out/in-out)
- `pad` — prepend silence
- `reverse` — reverse audio

### Channels/Sample Rate
- `channels` — convert to mono/stereo
- `rate` — resample to target rate

### Effects
- `compand` — compressor/expander
- `equalizer` — parametric EQ
- `bass` / `treble` — boost/cut
- `echo` — echo/delay
- `reverb` — algorithmic reverb

### Analysis (read-only)
- `stats` — RMS, peak, min/max, etc.
- `spectrogram` — generate PNG spectrogram

### Raw Effects
Pass any raw SoX effect: `highpass`, `lowpass`, `bandpass`, `noisered`, `phaser`, `flanger`, etc.

```python
{"op": "raw_effect", "effect": "highpass 80"}
{"op": "raw_effect", "effect": "phaser"}
```

## Examples

**Normalize + fade out:**
```python
transform(input="sample.wav",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "fade", "type": "out", "length": 1.5},
    ],
    output="sample_faded.wav")
```

**Trim, mono, downsample:**
```python
transform(input="recording.wav",
    pipeline=[
        {"op": "trim", "start": 5.0, "end": 35.0},
        {"op": "channels", "count": 1},
        {"op": "rate", "sample_rate": 22050},
    ],
    output="clip_mono_22k.wav")
```

**Bass boost + compression:**
```python
transform(input="drums.wav",
    pipeline=[
        {"op": "bass", "gain": 8},
        {"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10},
    ],
    output="drums_punchy.wav")
```

**Mix two files:**
```python
mix(tracks=[
    {"path": "vocals.wav", "gain": 1.0},
    {"path": "instrumental.wav", "gain": 0.7},
], output="full_mix.wav")
```

**Batch process directory:**
```python
from pathlib import Path
for wav in Path("samples/").rglob("*.wav"):
    transform(input=str(wav),
        pipeline=[
            {"op": "normalize", "peak": -0.1},
            {"op": "fade", "type": "in", "length": 0.1},
            {"op": "fade", "type": "out", "length": 0.5},
        ],
        output=f"processed/{wav.stem}_proc.wav")
```

## Implementation

Single `sox <input> [effects] <output>` subprocess per pipeline. Only multi-file ops need temp files or multiple invocations. Dry-run mode available.

## Error Handling

- Non-zero SoX exit codes returned as `{success: False, error: str}`
- Temp files preserved on failure for inspection
- Input must exist; output directory must be writable