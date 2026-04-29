---
name: daw-master:ffmpeg-audio
description: "FFmpeg audio filter wrapper — codec work, complex filtergraphs, stream operations"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "ffmpeg", "filters", "codec", "stream", "multi-input"]
    related_skills: ["daw-master:sox-engine", "daw-master:dawdreamer", "daw-master:rubber-band"]
---

# FFmpeg Audio Skill

Wraps FFmpeg's audio filters (`-af`) and multi-input mixing (`-filter_complex`).

FFmpeg complements SoX by offering:
- **Codec-level control** — encode/decode any format (AAC, AC3, Opus, etc.)
- **Complex filtergraphs** — parallel processing, sidechains, splits
- **Precise sample-accurate** trimming and seeking
- **Built-in loudness normalization** (EBU R128 `loudnorm`)
- **Stream operations** — concat, overlay, merge, split

## Installation

```bash
# Debian/Ubuntu
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg

# Verify
ffmpeg -version | head -1
ffprobe -version | head -1
```

---

## Philosophy

- **Filter-first**: Each pipeline op maps to an FFmpeg audio filter
- **Single-process chains**: Most pipelines compile into one `ffmpeg -af "...filter1,filter2,..."` call
- **Multi-input ops** (overlay, mix) use `-filter_complex` when needed
- **Codec flexibility**: Output format inferred from file extension; override with `format` param
- **Probe via ffprobe**: All `analyze()` calls go to `ffprobe` (not ffmpeg)

---

## Core API

```python
from daw_master.ffmpeg_audio import transform, mix, analyze, probe, ebu_r128_analysis

# Transform with filter chain
transform(
    input="input.wav",
    pipeline=[
        {"op": "volume", "gain": 0.8},          # -80% volume
        {"op": "loudnorm", "i": -24, "lra": 11}, # EBU R128
        {"op": "fade", "type": "out", "duration": 2.0},
    ],
    output="output.m4a",                        # format inferred (AAC in MP4)
    codec="aac"                                 # explicit codec
)

# Mix multiple files (multi-input filtergraph)
mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0, "delay": 0.0},
        {"path": "beats.wav", "gain": 0.7, "delay": 0.05},  # 50ms delay
    ],
    output="mix.wav",
    normalize_final=True
)

# Analyze
info = analyze("sample.mp3")
# {'duration': 45.2, 'sample_rate': 44100, 'channels': 2, 'bit_rate': 128000, ...}
```

---

## Operations Reference

### Volume & Level

`volume {gain}`
- Apply gain multiplier or dB.
- Param `gain`: linear multiplier (0.5 = -6dB) or dB string (`"3dB"`, `"-6dB"`)
- FFmpeg: `volume=0.8` or `volume=3dB`

`loudnorm {i=-24} {lra=11} {tp=-1}`
- EBU R128 loudness normalization (two-pass or single-pass).
- Params:
  - `i` (RMS/INT): target integrated loudness, e.g. `-24` (default)
  - `lra`: target loudness range, e.g. `11`
  - `tp`: true peak ceiling, e.g. `-1` or `-2`
- This is **the proper** broadcast/advertising loudness standard.
- FFmpeg: `loudnorm=I=-24:LRA=11:TP=-1`

`dynaudnorm`
- Dynamic audio normalization (adaptive gain).
- No params (uses defaults), or `p=0.95:g=10` etc.
- FFmpeg: `dynaudnorm=p=0.95`

`acompressor` / `acompress`
- Dynamic range compression.
- Params: `threshold`, `ratio`, `attack`, `release`, `makeup` (dB), `knee`
- FFmpeg: `acompressor=threshold=-20dB:ratio=4:attack=5:release=50:makeup=6dB:knee=2`

Examples:
```
{"op": "volume", "gain": 0.5}              # -6 dB
{"op": "volume", "gain": "6dB"}             # +6 dB
{"op": "loudnorm", "i": -23, "lra": 10}    # streaming standard
{"op": "dynaudnorm"}                        # adaptive
{"op": "acompressor", "threshold": "-20dB", "ratio": 4, "attack": 5, "release": 50}
```

---

### Editing & Manipulation

`atrim start={s} end={s} duration={s}`
- Trim audio to segment.
- Params: `start` (seconds), `end` (seconds), `duration` (seconds)
- FFmpeg: `atrim=start=5:end=30`

`areverse`
- Reverse audio.
- No params.

`apad pad_duration={s}`
- Pad with silence at end.
- Params: `pad_duration` (seconds)

`adelay delays="ms|ms|..."`
- Delay channels (for stereo widening or echo simulation).
- Params: `delays` as pipe-separated ms values: `"1000|500"` for stereo
- FFmpeg: `adelay=1000|500`

Examples:
```
{"op": "atrim", "start": 10.0, "end": 45.0}
{"op": "areverse"}
{"op": "apad", "pad_duration": 2.0}
{"op": "adelay", "delays": "500|500"}     # 0.5s stereo delay
```

---

### Channels & Layout

`channelmap channels=0,1,...`
- Remap/reorder channels.
- Params: `channels` — list of source channel indices

`pan` (stereo or more)
- Pan/balance control.
- Params: `FL`/`FR`/`FC` etc strings: `"FC"` for center mono
- Example: `pan=FL|c0=0.5|c1=0.5` — mono downmix
- Simpler: `pan=mono` downmix

`channelsplit`
- Split multi-channel into separate outputs (used in filter_complex).

`join` (multi-input)
- Concatenate audio streams (not samples, but files).
- Used via `-filter_complex "[0:a][1:a]join=inputs=2[a]"`

Examples:
```
{"op": "channelmap", "channels": [0, 1]}   # reorder
{"op": "pan", "mode": "stereo", "left": 0.7, "right": 0.3}
```

---

### Filters & EQ

`lowpass cutoff={freq}`
- Low-pass filter.
- Param `cutoff`: Hz (e.g., `2000`). FFmpeg: `lowpass=f=2000`

`highpass cutoff={freq}`
- High-pass.
- Param `cutoff`: Hz (e.g., `80` to remove rumble)

`bandpass freq={center} width={Q|Hz}`
- Band-pass filter.
- Params: `freq` center Hz, `width` (Q factor or Hz bandwidth)

`equalizer` (aka `equalizer` or `bass/shelf` family)
- Multi-band parametric EQ via multiple filter clauses.
- Params:
  - `freq` — frequency to affect
  - `width_type` — `"hz"` or `"q"` or `"o"`
  - `width` — bandwidth
  - `gain` — dB adjustment
- FFmpeg: `equalizer=f=1000:width_type=o:width=2:g=3`

`bass {gain}`
- Bass shelving. FFmpeg: `bass=g=6`
- Alias: `lowshelve`

`treble {gain}`
- Treble shelving. FFmpeg: `treble=g=-3`
- Alias: `highshelve`

Examples:
```
{"op": "lowpass", "cutoff": 8000}
{"op": "highpass", "cutoff": 80}
{"op": "equalizer", "freq": 1000, "width_type": "q", "width": 1.0, "gain": 3}
{"op": "bass", "gain": 6}
{"op": "treble", "gain": -2}
```

---

### Dynamics & Effects

`compand` (same name as SoX but different syntax)
- Compressor/expander/limiter.
- Params: `attacks`, `decays`, `points` (knee points), `soft-knee`, `gain`
- Example: `compand=attacks=0.01:decays=0.1:points=-80/-80|-20/-3|0/-3`
- This is the FFmpeg equivalent of SoX's `compand` but different parameterization.

`acompressor` (preferred over compand for music)
- Simpler compressor.
- Params: `threshold`, `ratio`, `attack`, `release`, `makeup`, `knee`

`sidechaincompress`
- Sidechain compression (ducking). Needs two inputs.
- Params: `threshold`, `ratio`, `attack`, `release`, `makeup`, `knee`

`aecho`
- Echo/delay effect.
- Params: ` delays="ms|ms|..."`, `decays="0.9|0.9"`, `gain_in=0.6`, `gain_out=0.6`
- Example: `aecho=0.05:0.1:0.9:0.9` (0.05s delay, 0.1 decay, 0.9 gains)

`areverb` (simple) / `freeverb` (better)
- Reverb.
- `freeverb`: params `scale=0.5:wet=0.3:dry=0.7`
- FFmpeg doesn't have a high-quality reverb built-in; use convolution (`aconvolve`) or VST via `avfilter`?

`atempo tempo={factor}`
- Change speed without pitch change (limited 0.5–2.0 range).
- Param `tempo`: float (0.5 = half, 2.0 = double)
- For extreme stretches, chain: `atempo=0.5,atempo=0.5` = quarter speed

`asetrate` + `atempo`
- Pitch shift (via resample + tempo) but loses quality.

Examples:
```
{"op": "acompressor", "threshold": "-20dB", "ratio": 4, "attack": 5, "release": 50}
{"op": "compand", "attacks": "0.01", "decays": "0.1", "points": "-80/-80|-20/-3|0/-3"}
{"op": "aecho", "delays": "500|1000", "decays": "0.8|0.6", "gain_in": 0.6, "gain_out": 0.6}
{"op": "freeverb", "wet": 0.4, "dry": 0.6}
{"op": "atempo", "tempo": 0.88}             # slow down 12%
```

---

### Multi-Input Operations

These require `-filter_complex` and are handled specially by `transform()` when detected.

`amix inputs=2 [base_params]`
- Mix (sum) multiple audio streams.
- Params: `inputs` (count), `duration` (`longest` or `shortest`), `dropout_transition`
- Example: `amix=inputs=2:duration=longest:dropout_transition=2`

`amerge inputs=2`
- Merge channels into multi-channel layout (vs sum).
- Use when you want to preserve each input as separate channel.

`sidechaincompress` — already covered but needs two inputs.

`join` — concatenate streams sample-accurately (like `sox --combine concatenate`).

---

## Pipeline Step Format

Each step dict:
```python
{"op": "operation_name", "param1": value1, "param2": value2, ...}
```

FFmpeg-specific tuning:
- `codec`: override output codec (e.g. `"aac"`, `"mp3"`, `"flac"`, `"pcm_s16le"`)
- `format`: container format (`"mp4"`, `"wav"`, `"ogg"`) — inferred from output.ext usually
- `extra_output_args`: list of extra ffmpeg CLI flags for output stage
- `extra_global_args`: list of global flags (e.g., `["-y"]` to overwrite)

Examples:
```python
pipeline = [
    {"op": "volume", "gain": "-3dB"},          # attenuate
    {"op": "highpass", "cutoff": 80},         # remove sub-bass rumble
    {"op": "acompressor", "threshold": "-20dB", "ratio": 3, "attack": 3, "release": 50},
    {"op": "loudnorm", "i": -16, "lra": 5},   # podcast loudness
    {"op": "fade", "type": "out", "duration": 1.0},
]
```

---

## Implementation Details

### Single-Input Pipeline (most common)

Translates to:
```
ffmpeg -i input.wav -af "filter1=params,filter2=params,..." -c:a <codec> output
```

### Multi-Input Pipeline (overlay/mix)

Detected when pipeline contains `overlay` or when `mix()` is called.
Uses `-filter_complex`:

```
ffmpeg -i a.wav -i b.wav -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest[out]" -map "[out]" output
```

The `transform()` function will auto-detect and switch to `subprocess` with custom
filter_complex string construction.

---

## Examples

### Example 1 — Normalize Loudness + Fade
```python
from daw_master.ffmpeg_audio import transform

transform(
    input="podcast.wav",
    pipeline=[
        {"op": "highpass", "cutoff": 80},             # remove rumble
        {"op": "loudnorm", "i": -19, "lra": 5},      # podcast standard
        {"op": "fade", "type": "out", "duration": 0.5},
    ],
    output="podcast_normalized.m4a",
    codec="aac"
)
# Command: ffmpeg -i podcast.wav -af "highpass=f=80,loudnorm=I=-19:LRA=5,fade=t=out:st=0:d=0.5" -c:a aac output.m4a
```

### Example 2 — Trim, Resample, Convert Format
```python
transform(
    input="long_recording.wav",
    pipeline=[
        {"op": "atrim", "start": 30.0, "end": 90.0},  # keep 1 min
        {"op": "volume", "gain": "2dB"},              # +2 dB
        {"op": "aresample", "sample_rate": 22050},    # downsample
    ],
    output="excerpt_22k.mp3",
    codec="mp3",
    bitrate="128k"
)
```

### Example 3 — Simple Mix (3 tracks)
```python
from daw_master.ffmpeg_audio import mix

mix(
    tracks=[
        {"path": "vocals.wav", "gain": 1.0, "pan": "FC"},       # center
        {"path": "drums.wav", "gain": 0.8, "pan": "FL+FR"},     # stereo spread
        {"path": "bass.wav", "gain": 1.2, "pan": "FC"},         # center, louder
    ],
    output="full_mix.wav",
    normalize_final=True
)
# Uses: -filter_complex "[0:a]volume=1.0,pan=FC[a0];[1:a]volume=0.8,pan=FL+FR[a1];... [a0][a1][a2]amix=inputs=3"
```

### Example 4 — Generate Silence + Tone (synthesis)
```python
transform(
    input=None,  # no input — generate
    pipeline=[
        {"op": "sine", "freq": 440, "duration": 5.0, "volume": 0.5},
    ],
    output="A4_tone.wav",
    codec="pcm_s16le"
)
# FFmpeg: ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -c:a pcm_s16le out.wav
```

### Example 5 — Analyze File
```python
info = analyze("sample.mp3")
# {
#   'format': 'mp3', 'duration': 185.3, 'size': 2945000,
#   'bit_rate': '128k', 'sample_rate': 44100, 'channels': 2,
#   'codec': 'mp3', 'tags': {'title': '...', 'artist': '...'}
# }
```

### Example 6 — EBU R128 Loudness Analysis
```python
loudness = ebu_r128_analysis("track.wav", target=-23.0)
# {
#   'success': True,
#   'file': '/abs/path/track.wav',
#   'target': -23.0,
#   'integrated_loudness': -18.7,   # LUFS
#   'lra': 8.2,                      # Loudness Range in LU
#   'lra_low': -24.5,               # LUFS lower bound
#   'lra_high': -12.3,              # LUFS upper bound
#   'threshold': -41.2,             # LUFS integrated threshold
#   'stderr': None                  # only on error
# }
```
Measures loudness per EBU R128 standard using FFmpeg's `ebur128` filter.
Complements the `loudnorm` transform (which normalizes) by providing analysis.


---

## Chaining with Other daw-master Skills

```python
# 1. sox-engine: fast trim + normalize (simple)
sox.transform("raw.wav", [{"op": "trim", "start": 5, "length": 60}, {"op": "normalize"}], "trimmed.wav")

# 2. ffmpeg-audio: codec conversion + loudness + compression
ffmpeg.transform("trimmed.wav", [
    {"op": "loudnorm", "i": -16, "lra": 6},
    {"op": "acompressor", "threshold": "-22dB", "ratio": 3},
], "final.m4a", codec="aac")

# 3. dawdreamer: VST color
dawdreamer.transform("final.m4a", [{"op": "load_vst", "path": "tone_vst.vst3"}, ...], "mastered.wav")
```

---

## Notes

- **Filter syntax cheat sheet**: Every op generates `key=value` pairs for `-af`.
  - Booleans: `true`/`false` → `1`/`0`
  - Lists: `[0,1]` → `"0|1"` (pipe-separated for FFmpeg list params)
  - Multiple filters: comma-separated `filter1=...,filter2=...`

- **Two-pass loudnorm**: For best quality, run `loudnorm` in two passes (measure then apply). This skill uses single-pass for simplicity. Advanced use: call `analyze()` → compute loudnorm params → call `transform()` with `dual_pass=True`.

- **Sample-accurate trimming**: `atrim` uses float seconds (e.g., `start=12.54321`). Much more precise than `sox trim` which also uses float but FFmpeg can do frame-accurate if you specify in frames too.

- **Overlay operation**: Unlike SoX's `-m` summing, FFmpeg's `amix` can optionally delay one track by `duration` or `shortest`. Use for echo/dub style delays.

- **Codec selection**: If you don't specify `codec`, FFmpeg chooses based on container (file extension). To force raw PCM: `codec='pcm_s16le'` (WAV), `codec='flac'` for lossless, `codec='aac'` for AAC.

- **Quality controls**: Pass `extra_output_args=['-q:a', '2']` for variable-bitrate MP3/AAC quality (0=best, 9=worst).

---

## Hermes Integration

```
Use skill daw-master:ffmpeg-audio transform input="in.wav" pipeline=[...] output="out.m4a"
```

Or Python:
```python
from daw_master.ffmpeg_audio import transform
result = transform("in.wav", [{"op": "volume", "gain": "3dB"}], "out.wav")
```