---
name: daw-master:sox-engine
description: "SoX (Sound eXchange) wrapper — the Swiss Army knife of CLI audio processing"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "sox", "cli", "batch", "effects", "conversion"]
    related_skills: ["daw-master:dawdreamer", "daw-master:ffmpeg-audio", "daw-master:rubber-band"]
---

# SoX Engine Skill

Wraps SoX (Sound eXchange) — the classic command-line audio processing tool.

SoX is available on virtually every Linux/macOS system, making this skill the most portable
audio manipulation tool in the `daw-master` suite.

## Installation

```bash
# Debian/Ubuntu
sudo apt install sox

# macOS
brew install sox

# Fedora
sudo dnf install sox

# Arch
sudo pacman -S sox

# Verify
sox --version
```

Many distributions also ship `sox` with optional format support via `sox-plugin` packages.

---

## Philosophy

- **One operation per pipeline step** — each op maps to a SoX effect or command
- **Stateless** — every call spawns a fresh SoX process
- **File-based** — input and output are file paths; intermediate stages are temp files
- **Composable** — pipeline steps are applied in order, each writing to a temp file
- **Transparent** — the exact SoX command is logged for debugging

---

## Core API

```python
from daw_master.sox_engine import transform, mix, analyze

# Transform a file through a pipeline
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

# Analyze audio properties
info = analyze("sample.wav")
# {duration, sample_rate, channels, peak, rms, bit_depth, ...}
```

---

## Operations Reference

### Gain & Level

`gain {amount}`
- Apply linear gain multiplier or dB adjustment.
- Param `amount`: float (e.g., `0.5` for half, `2.0` for +6dB, `-3` for -3dB)
- **Aliases**: `volume`

`norm [-p peak] [{dc}]`
- Normalize to peak level.
- Param `peak`: target peak in dBFS (default `-0.1`). Use `-1` for true 0 dB.
- Param `dc`: if true, remove DC offset first (`--norm-dc`)

Examples:
```
{"op": "gain", "amount": 0.8}          # attenuate 20%
{"op": "gain", "amount": 3.0}          # +9.5 dB approx
{"op": "normalize", "peak": -0.1}
```

---

### Editing & Manipulation

`trim {start} [length]`
- Extract segment.
- Param `start`: start time in seconds (floating-point)
- Param `length` or `end`: duration or end time in seconds

`fade {type} {length}`
- Fade in/out.
- Param `type`: `"in"`, `"out"`, `"in-out"` (both)
- Param `length`: fade duration in seconds

`pad {silence}`
- Pad audio with silence (prepend).
- Param `silence`: seconds to add at beginning

`reverse`
- Reverse audio entirely.
- No parameters.

Examples:
```
{"op": "trim", "start": 10.5, "end": 45.0}
{"op": "fade", "type": "in", "length": 0.3}
{"op": "fade", "type": "out", "length": 2.0}
{"op": "pad", "silence": 1.5}
{"op": "reverse"}
```

---

### Channels & Sample Rate

`channels {count}`
- Convert to mono (1), stereo (2), etc.
- Param `count`: integer channel count

`rate {sample_rate}`
- Resample to given sample rate.
- Param `sample_rate`: e.g. `44100`, `48000`, `22050`

`remix -m {gain} ...`
- Remix channels (mix down or reorder).
- Param `mixing`: boolean, for downmixing to mono

Examples:
```
{"op": "channels", "count": 1}        # mono
{"op": "channels", "count": 2}        # stereo (no-op if already)
{"op": "rate", "sample_rate": 44100}
```

---

### Effects

`compand attack1:decay1{,attack2:decay2} [soft-knee-dB:]in-dB[,out-dB]`
- Compressor/expander.
- Params:
  - `attack`, `decay`: times in seconds as `"0.01:0.1"`
  - `threshold_in`: input threshold dB
  - `threshold_out`: output threshold dB
  - `soft_knee`: soft-knee width dB

`equalizer frequency[{=|+|-|/}width[k|o|q]] [gain[dB]]`
- Parametric EQ.
- Params: `frequency` (Hz), `width` (Hz or `q` factor), `gain` (dB)

`bass {gain}`
- Boost/cut bass.
- Param `gain`: dB (e.g., `10` or `-5`)

`treble {gain}`
- Boost/cut treble.
- Param `gain`: dB

`echo gain-out:in-gain [delay]`
- Simple echo/delay.
- Params: `gain_in`, `gain_out`, `delay` (seconds)

`reverb {wet}`
- Simple algorithmic reverb.
- Param `wet`: wet/dry mix (0.0–1.0, typically 0.3)

`vol {gain}`
- Alias for `gain`.

Examples:
```
{"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10}
{"op": "equalizer", "frequency": 1000, "width": "2q", "gain": 3}
{"op": "bass", "gain": 6}
{"op": "treble", "gain": -2}
{"op": "echo", "wet": 0.4, "delay": 0.3}
{"op": "reverb", "wet": 0.3}
```

---

### Analysis & Info

**These are read-only ops that produce metadata, not audio.**

`stats`
- Print sample statistics to stdout.
- Returns: `min`, `max`, `mid`, `rms`, `rms_peak`, `rms_trough`

`stat -freq {Hz}`
- Get amplitude at a specific frequency.

`spectrogram`
- Generate a spectrogram PNG (not part of pipeline — use `analyze` mode).

---

## Pipeline Step Format

Each pipeline step dict has:
- `op` (required): operation name
- operation-specific parameters

SoX-specific: For operations that map directly to SoX effects,
we pass parameters as key-value pairs that will be rendered to SoX CLI flags.

Example:
```python
pipeline = [
    {"op": "normalize", "peak": -0.1},
    {"op": "fade", "type": "out", "length": 2.0},
    {"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10},
]
```

---

## Implementation: How It Works

```
input.wav
   ↓
[ build SoX command from pipeline ]
   ↓
sox input.wav [effect1] [effect2] ... output.wav
   ↓
output.wav
```

**Strategy:**
1. Take first and last filenames in the pipeline.
2. Build intermediate FLAG list by translating each pipeline op to SoX effects/flags.
3. Call `sox <input> <flags> <output>` in one subprocess.
4. If any step requires intermediate processing (e.g., stats-only), handle separately.

Because SoX applies effects in order, we can do a **single process call** for most pipelines.
Only multi-file operations (overlay, concatenate) need	temp files or multiple invocations.

---

## Examples

### Example 1 — Normalize and Fade Out
```python
from daw_master.sox_engine import transform

result = transform(
    input="sample.wav",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "fade", "type": "out", "length": 1.5},
    ],
    output="sample_faded.wav"
)
print(result)
# {'success': True, 'output': 'sample_faded.wav', 'command': 'sox sample.wav -t wavpcm ...'}
```

### Example 2 — Trim, Convert to Mono, and Downsample
```python
transform(
    input="recording.wav",
    pipeline=[
        {"op": "trim", "start": 5.0, "end": 35.0},  # keep seconds 5–35
        {"op": "channels", "count": 1},            # mono
        {"op": "rate", "sample_rate": 22050},      # downsample
    ],
    output="clip_mono_22k.wav"
)
```

### Example 3 — Apply Bass Boost and Light Compression
```python
transform(
    input="drums.wav",
    pipeline=[
        {"op": "bass", "gain": 8},  # low-end boost
        {"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10},
    ],
    output="drums_punchy.wav"
)
```

### Example 4 — Mix Two Files with Different Gains
```python
from daw_master.sox_engine import mix

mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0, "pan": None},
        {"path": "instrumental.wav", "gain": 0.7, "pan": None},
    ],
    output="full_mix.wav",
    # Internally calls: sox -m vocal.wav -v 1.0 instrumental.wav -v 0.7 output.wav
)
```

### Example 5 — Analyze File
```python
from daw_master.sox_engine import analyze

stats = analyze("sample.wav")
print(stats)
# {'duration': 45.2, 'sample_rate': 44100, 'channels': 2, 'peak': 0.92, 'rms': 0.35, ...}
```

### Example 6 — Batch Process a Directory
```python
from pathlib import Path
from daw_master.sox_engine import transform

for wav in Path("samples/").rglob("*.wav"):
    out = f"processed/{wav.stem}_proc.wav"
    transform(
        input=str(wav),
        pipeline=[
            {"op": "normalize", "peak": -0.1},
            {"op": "fade", "type": "in", "length": 0.1},
            {"op": "fade", "type": "out", "length": 0.5},
        ],
        output=out
    )
```

---

## Chaining with Other daw-master Skills

```python
# 1. Analyze with dawdreamer to get loudness → adjust
analysis = dawdreamer.analyze("sample.wav")
if analysis["rms_db"] < -20:
    pipeline = [{"op": "gain", "amount": 2.0}, {"op": "normalize", "peak": -0.5}]
else:
    pipeline = [{"op": "normalize"}]

# 2. Use sox-engine for simple, fast operations
sox_engine.transform("sample.wav", pipeline, "sample_balanced.wav")

# 3. Follow with dawdreamer for VST effects
dawdreamer.transform(
    "sample_balanced.wav",
    pipeline=[{"op": "load_vst", "path": "/path/to/comp.vst3"}, {"op": "set_param", "param": "Ratio", "value": 4}],
    output="final.wav"
)
```

---

## Error Handling & Safety

- **Command safety**: The built SoX command is logged; set `dry_run=True` to print only.
- **File checks**: Input must exist; output directory must be writable.
- **Temp files**: Intermediate files use `tempfile.NamedTemporaryFile(delete=False)` so
  you can inspect them if a step fails.
- **Exit codes**: Non-zero SoX exit codes are caught and returned as `{success: False, error: str}`.

---

## Advanced: Custom SoX Effects

SoX has dozens of built-in effects. This skill defines a core set,
but you can pass raw SoX effect strings via `raw_effect`:

```python
transform(
    input="in.wav",
    pipeline=[
        {"op": "raw_effect", "effect": "phaser"},
        {"op": "raw_effect", "effect": "flanger 75 5"},
    ],
    output="out.wav"
)
```

This exposes full SoX power without writing a wrapper per effect.

---

## Notes

- SoX operates on the entire file per process. Very long files may need chunking if
  memory is constrained; SoX streams internally so this is rarely an issue.
- SoX's `compand` effect uses non-standard syntax; this skill provides helpers for
  common presets (fast attack/decay for leveling).
- For sample-accurate trimming, use `trim` with floating-point times; SoX supports
  sample-precise times (e.g., `10.045921` seconds).
- When mixing (`mix` tracks), SoX's `-m` mode sums inputs; we handle per-track gain
  by inserting `-v` volume flags before each input file.

---

## Hermes Integration

Call from Hermes:
```
Use skill daw-master:sox-engine transform input="a.wav" pipeline=[...] output="b.wav"
```

Or from Python:
```python
from daw_master.sox_engine import transform
result = transform("in.wav", [{"op": "normalize"}], "out.wav")
```