---
name: daw-master:mix-engineer
description: "Use when polishing AI-generated audio OR when asked about mixing craft — per-stem SoX cleanup (EQ, compression, noise/click removal) and remix into polished WAVs, plus the five-pass mix workflow, gain staging, bus routing, EQ/compression frameworks, and spatial processing mapped to SoX/FFmpeg/DawDreamer."
version: 0.2.0
author: Ported from bitwize-music-studio
license: MIT
metadata:
  hermes:
    tags: ["audio", "mix", "polish", "stems", "sox", "ffmpeg", "craft", "workflow", "gain-staging", "sidechain", "parallel-compression", "reverb"]
    related_skills: ["daw-master:sox-engine", "daw-master:ffmpeg-audio", "daw-master:audio-analyzer", "daw-master:mastering-engineer"]
---

# Mix Engineer

Polishes raw AI-generated audio (Suno, etc.) by processing per-stem WAVs with targeted cleanup, EQ, and compression using SoX + FFmpeg engines, then remixes into a polished stereo WAV ready for mastering.

**Role**: Per-stem processing, noise reduction, frequency cleanup, dynamic control, stem remixing, and mixing craft guidance (five-pass workflow, gain staging, bus routing, EQ/compression frameworks, spatial processing).
**Not role**: Creative production/songwriting, lyrics, generation, or mastering (see `mastering-engineer`).
**Primary tools**: `sox-engine.transform`, `ffmpeg-audio.transform`, `audio-analyzer.analyze`

## Core Principles

- **Stems first**: When `stems/` directory is present, process each stem independently for targeted processing impossible on a full mix.
- **Preserve performance**: Mix polishing removes defects, not character. Be conservative.
- **Non-destructive**: All processing writes to `polished/` — originals never modified.
- **Frequency coordination with mastering**: Mix presence boost at ~3 kHz (clarity); mastering harshness cut at ~3.5 kHz — different center frequencies minimize cancellation.

## Dependencies

- `sox-engine` — single-track effects (EQ, compand, normalize, fades, highpass/lowpass/bandpass)
- `ffmpeg-audio` — multi-track mixing, loudnorm, advanced dynamics
- `audio-analyzer` — feature extraction for analysis decisions

No external Python packages beyond those already installed.

## Path Convention

```
{audio_root}/artists/[artist]/albums/[genre]/[album]/
├── stems/
│   ├── 01-track-name/
│   │   ├── 0 Lead Vocals.wav
│   │   ├── 1 Backing Vocals.wav
│   │   ├── 2 Drums.wav
│   │   ├── 3 Bass.wav
│   │   └── ... (up to 12 stem types)
├── polished/    ← output
└── mastered/    ← mastering-engineer output
```

## When to Use

- Cleaning up noise from AI-generated vocals or instruments
- Applying frequency-targeted EQ (mud cuts, presence boosts, high tames)
- Compressing stems to even out dynamics
- Removing clicks or transient spikes from generated audio
- Mixing stems into a polished full stereo mix
- Applying genre-specific processing chains (hip-hop, rock, EDM, folk, ambient)
- Explaining or applying mixing craft: the five-pass workflow, gain staging,
  bus routing, the EQ decision framework, parallel/sidechain/multiband
  compression, or spatial processing (reverb/delay/width)
- Answering "how do I mix a track" / "teach me EQ, compression, reverb" questions

## When NOT to Use

- Songwriting, lyrics, or audio *generation* — this skill processes existing audio
- Mastering / loudness-normalization / platform delivery — use `mastering-engineer`
- Simple single-effect edits (a lone fade, trim, or format conversion) — use
  `sox-engine` or `ffmpeg-audio` directly

## Creative Mixing Craft

The art-layer guidance (five-pass workflow, gain staging, bus routing, EQ
decision framework + frequency cheat sheet, parallel/sidechain/multiband
compression, spatial processing, genre architecture, anti-patterns), mapped to
SoX/FFmpeg/DawDreamer/Carla tooling:

- **Full guide:** [references/mixing-craft.md](mdc:references/mixing-craft.md)

Quick reference:

| Topic | Core idea |
|-------|-----------|
| Five-pass workflow | static mix → subtractive EQ → compression → additive EQ/saturation → spatial |
| Gain staging | -18 dBFS working level; peaks < -6 dBFS/track; mix bus -6 to -3 dBFS |
| Bus routing | Drum/Bass/Vocal/Music/FX/Mix buses for macro balance |
| EQ framework | level → arrangement → masking → resonance → enhancement, in that order |
| Parallel comp | crush duplicate (10-15 dB GR) + blend under dry; for drums/vocals |
| Sidechain comp | kick→bass pump, kick→pads EDM pump, vocal→music 1-2 dB duck |
| Multiband comp | band-split only for specific problems (sox `mcompand`) |
| Spatial | 2-3 reverb sends, pre-delay 20-80 ms, short (50-120 ms) vs tempo-synced delays |

## API

### `analyze_mix_issues(album_path: str) -> Dict`

Scan for stems or full mix and detect issues.

```python
{
  "source_mode": "stems" | "full_mix",
  "tracks": [...],
  "issues": {
    "noisy_tracks": [...],
    "muddy_tracks": [...],
    "harsh_tracks": [...],
    "clicky_tracks": [...],
    "sub_bass_rumble": [...]
  }
}
```

### `polish_audio(album_path: str, genre: str = "default", dry_run: bool = False) -> Dict`

Process stems or full mix with genre-appropriate settings. Writes to `polished/`.

```python
{
  "mode": "stems" | "full_mix",
  "tracks_processed": 5,
  "output_dir": "/path/to/polished",
  "commands": [...],
  "success": bool
}
```

### `polish_album(album_path: str, genre: str = "default") -> Dict`

End-to-end: analyze → polish → verify.

### `_generate_noise_profile(input_wav: str) -> str`

Auto-generates SoX noise profile from quietest 100ms window.

### `_detect_clicks(audio_data, sr) -> List[float]`

Detects transient clicks (> 6σ amplitude spikes).

## Per-Stem Processing

Full chains for all 12 stem types (Vocals, Backing Vocals, Drums, Bass, Guitar, Keyboard, Strings, Brass, Woodwinds, Percussion, Synth, Other): [references/stems.md](mdc:references/stems.md)

Quick reference:

| Stem | Key steps |
|------|-----------|
| **Lead Vocals** | NR → +2dB @ 3kHz → -2dB @ 7kHz → compress |
| **Backing Vocals** | NR → +1dB @ 3kHz → -2.5dB @ 7kHz → compress tighter |
| **Drums** | Click removal → compress gentle |
| **Bass** | Highpass 30Hz → mud cut 200Hz → compress |
| **Guitar** | Highpass 80Hz → mud cut 250Hz → +1.5dB @ 3kHz → compress |
| **Keyboard** | Highpass 40Hz → mud cut 300Hz → +1dB @ 2.5kHz → compress |
| **Strings** | Highpass 35Hz → +1dB @ 3.5kHz → wide stereo → very light compress |
| **Brass** | Highpass 60Hz → +1.5dB @ 2kHz → compress |
| **Woodwinds** | Highpass 50Hz → +1dB @ 2.5kHz → compress |
| **Percussion** | Highpass 60Hz → click removal → +1dB @ 4kHz → stereo width |
| **Synth** | Highpass 80Hz → +1dB @ 2kHz → stereo width → compress |

## Genre Presets

| Genre | Vocal | Bass | Drums | High-mid |
|-------|-------|------|-------|----------|
| Default | 0 dB | 0 dB | 0 dB | –2 dB @ 7 kHz |
| Hip-Hop/Rap | +1 dB | +1 dB | +0.5 dB | aggressive |
| Rock/Metal | 0 dB | 0 dB | +0.5–1 dB | –2.5 to –3 dB |
| EDM/Electronic | 0 dB | +0.5–1 dB | +0.5–1 dB | lighter |
| Folk/Country | +0.5 dB | 0 dB | +0.5 dB | –1.5 dB |
| Ambient/Lo-Fi | 0 dB | 0 dB | 0 dB | –1.5 dB; lighter NR |

## Handoff to Mastering

```python
from daw_master.mastering_engineer import master_audio
master_audio(album_path, source_subfolder="polished", genre=genre)
```

## Quality Standards

Before handoff: no clipping (peak < –0.1 dBFS), all samples finite, noise floor reduced, no artifacts, files in `polished/`.