---
name: daw-master:rubber-band-engine
description: "Rubber Band library wrapper — professional-grade time-stretch and pitch-shift"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "time-stretch", "pitch-shift", "rubberband", "dsp", "formant"]
    related_skills: ["daw-master:dawdreamer", "daw-master:sox-engine", "daw-master:ffmpeg-audio"]
---

# Rubber Band Engine Skill

High-quality time-stretching and pitch-shifting via the Rubber Band library.

This skill does exactly two things, and does them exceptionally well:
- **Time-stretch** — change tempo without affecting pitch
- **Pitch-shift** — change pitch without affecting tempo

It's the same algorithm used in professional DAWs. Use this when you need clean,
artifact-free transforms on musical material (vocals, chords, polyphonic samples).

## When to Use Rubber Band vs SoX/FFmpeg

| Tool | Time-Stretch Quality | Pitch-Shift Quality | Speed |
|------|---------------------|--------------------|-------|
| `sox-engine` | Basic — works at medium lengths | Basic via `pitch` effect | Fast |
| `ffmpeg-audio` (`atempo`) | Limited 0.5–2.0 only, okay | No native (needs Rubber Band) | Fast |
| `dawdreamer` (warp) | Good — uses Rubber Band under the hood | Good | Moderate |
| **`rubber-band-engine`** | **Excellent — dedicated algorithm** | **Excellent** | Moderate–Slow (quality-dependent) |

**Use Rubber Band when:**
- You need transparent, professional-quality tempo changes on polyphonic material
- You're pitch-shifting vocals or chords and want formants preserved
- Quality matters more than processing speed

**Use SoX/FFmpeg when:**
- You need very fast approximate transforms (drafts, batch on 1000s of files)
- Simple speech-only material (SoX `speed` effect fine)
- Already in a SoX/FFmpeg pipeline and don't want to switch tools

---

## Installation

```bash
# CLI (recommended)
sudo apt install rubberband-cli        # Debian/Ubuntu
sudo dnf install rubberband            # Fedora
brew install rubberband                # macOS
pacman -S rubberband                   # Arch

# Python bindings (optional alternative to CLI)
pip install rubberband

# Verify
rubberband --version
python -c "import rubberband; print(rubberband.__version__)"
```

---

## Philosophy

- **Single-responsibility**: This skill only warps time and pitch. For everything else, delegate to `sox-engine`, `ffmpeg-audio`, or `dawdreamer`.
- **Pipeline step**: Use as one stage in a multi-skill transformation chain.
- **CLI-first, Python fallback**: Prefers binary (language-agnostic); uses Python bindings if CLI missing.
- **Quality presets**: Abstract complex tuning into `"quick" | "standard" | "high" | "ultra"`.

---

## Core API

```python
from daw_master.rubber_band_engine import transform

# Slow down 12% (preserve vocal formants)
transform("sample.wav", [{"op": "time_stretch", "factor": 0.88, "formant": True}], "out.wav")

# Pitch up 5 semitones + formant correction
transform("sample.wav", [{"op": "pitch_shift", "semitones": 5, "formant": True}], "out.wav")

# Both: speed up and pitch up together
transform("sample.wav", [
    {"op": "time_stretch", "factor": 1.15, "formant": False},
    {"op": "pitch_shift", "semitones": 3}
], "out.wav")
```

Return value: `{success: bool, output: str, command?: str, error?: str}`

---

## Operations Reference

### `time_stretch`

Change tempo while keeping pitch.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `factor` | float | **required** | Tempo multiplier. `1.0` = unchanged, `0.5` = half speed, `2.0` = double. |
| `formant` | bool | `False` | Preserve vocal formants (timbre). Set `True` for vocals/acoustic instruments. |
| `quality` | str | `"standard"` | `"quick"` (fast), `"standard"`, `"high"`, `"ultra"` (best). |
| `transients` | str | `"mixed"` | How to handle transients: `"crisp"`, `"smooth"`, `"mixed"` (auto). |
| `window_size` | int | auto | Advanced: processing window size in samples. Leave default. |
| `preserve` | bool | `True` | Preserve phase relationships (keep True). |

**Example:**
```python
{"op": "time_stretch", "factor": 0.85, "formant": True, "quality": "high"}
```

---

### `pitch_shift`

Change pitch while keeping tempo.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `semitones` | float | **required** | Pitch shift in semitones (can be fractional: `2.5`, `-1.5`). |
| `formant` | bool | `True` | Preserve formants (recommended for vocals). |
| `quality` | str | `"standard"` | `"quick"`, `"standard"`, `"high"`, `"ultra"`. |
| `transients` | str | `"mixed"` | Transient handling. |
| `window_size` | int | auto | Advanced tuning. |

**Example:**
```python
{"op": "pitch_shift", "semitones": 4.0, "formant": True, "quality": "ultra"}
```

---

## Pipeline Semantics

You can combine both ops in one pipeline — they will be applied in order.
Internally this compiles to a **single** Rubber Band call (if CLI) or sequential Python calls.

**Order matters**:
- `time_stretch` → `pitch_shift` : adjust tempo first, then transpose
- `pitch_shift` → `time_stretch` : transpose first, then adjust tempo

For most sampling workflows: adjust tempo to match target BPM, then pitch to target key.

---

## Examples

### Example 1 — Slow-down vocals (musical sampling)
```python
from daw_master.rubber_band_engine import transform

# Slow to ~82% of original tempo, keep vocal character
transform(
    input="vocal_phrase.wav",
    pipeline=[{"op": "time_stretch", "factor": 0.82, "formant": True, "quality": "high"}],
    output="vocal_slow.wav"
)
```

### Example 2 — Pitch-shift drum hit (transient-sensitive)
```python
transform(
    input="snare_hit.wav",
    pipeline=[{"op": "pitch_shift", "semitones": 4.0, "formant": False, "transients": "crisp"}],
    output="snare_hit_higher.wav"
)
```

### Example 3 — Speed up + brighten (chipmunk effect)
```python
transform(
    input="speech_sample.wav",
    pipeline=[
        {"op": "time_stretch", "factor": 1.3, "formant": False, "quality": "quick"},
        {"op": "pitch_shift", "semitones": 3.5, "formant": False}
    ],
    output="chipmunk.wav"
)
```

### Example 4 — Batch process sample directory
```python
from pathlib import Path
from daw_master.rubber_band_engine import transform

for wav in Path("raw_samples/").rglob("*.wav"):
    out = f"timed/{wav.stem}_timed.wav"
    transform(
        input=str(wav),
        pipeline=[{"op": "time_stretch", "factor": 0.95, "formant": True}],
        output=out,
        quality="high"
    )
```

---

## Quality Presets Guide

| Preset | Speed | Quality | Best For |
|--------|-------|---------|----------|
| `quick` | Fastest | Acceptable | Drafts, 1000s of files, realtime preview |
| `standard` | Balanced | Good | General use, instruments, vocals |
| `high` | Slower | Very good | Critical listening, release samples |
| `ultra` | Slowest | Near-transparent | Mastering, archiving, flagship sample libs |

Window size increases with quality; processing time roughly doubles per step.

---

## Chaining Example

```python
# Full sample preparation pipeline:
# 1. Rubber Band: tempo/pitch align to project
# 2. SoX: normalize and fade
# 3. FFmpeg: encode to final codec

rubber.transform("raw.wav",
    pipeline=[{"op": "time_stretch", "factor": 0.98, "formant": True}],
    output"step1.wav"
)
sox.transform("step1.wav",
    pipeline=[{"op": "normalize", "peak": -0.1}, {"op": "fade", "type": "out", "length": 0.5}],
    output="step2.wav"
)
ffmpeg.transform("step2.wav",
    pipeline=[],
    output="final.m4a", codec="aac", bitrate="256k"
)
```

---

## Installation Notes

### Debian/Ubuntu
```bash
sudo apt update
sudo apt install rubberband-cli
# Optional Python bindings:
pip install rubberband
```

### macOS
```bash
brew install rubberband
pip install rubberband  # optional
```

### From Source (latest)
```bash
git clone https://github.com/breakfastquay/rubberband.git
cd rubberband
./configure && make && sudo make install
```

---

## Error Handling

- `FileNotFoundError` — input missing or Rubber Band binary not installed
- `ValueError` — invalid pipeline (missing factor, factor ≤ 0)
- `subprocess.CalledProcessError` — Rubber Band CLI failed; inspect `stderr`

All exceptions caught and returned as `{success: False, error: str}`.

---

## Hermes Integration

```
Use skill daw-master:rubber-band-engine transform input="sample.wav" pipeline=[...] output="out.wav"
```

---

## References

- Rubber Band GitHub: https://github.com/breakfastquay/RubberBand
- Paper: *A Tutorial on Rubber Band Transposition* — breakfastquay.com/rubberband/RubberBandTutorial.pdf
- Used in: Ableton Live, Logic Pro, REAPER, Mixbus, Ardour

---

## Notes

- Rubber Band is most effective on **tonal/polyphonic** material. For drums-only, try `transients="crisp"`.
- For vocal processing, always set `formant=True` to avoid the chipmunk effect.
- Very short sounds (< 100 ms) may not stretch cleanly — use sparingly on one-shots.
- Maximum practical stretch factor is about 0.125–8.0. Outside that range, artifacts dominate.
- For batch work on long files (hours), consider splitting first to avoid memory pressure.