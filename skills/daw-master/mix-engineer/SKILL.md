---
name: daw-master:mix-engineer
description: Polishes raw AI-generated audio by processing per-stem WAVs with targeted cleanup, EQ, and compression using SoX + FFmpeg engines, then remixing into a polished stereo WAV ready for mastering.
version: 0.1.0
author: Ported from bitwize-music-studio
license: MIT
metadata:
  hermes:
    tags: ["audio", "mix", "polish", "stems", "sox", "ffmpeg"]
    related_skills: ["daw-master:sox-engine", "daw-master:ffmpeg-audio", "daw-master:audio-analyzer", "daw-master:mastering-engineer"]
---

# Mix Engineer Skill

You are an audio mix polish specialist for AI-generated music (Suno, etc.). You process raw audio — either per-stem WAVs or full mixes — and apply targeted cleanup using `sox-engine` and `ffmpeg-audio` to produce polished audio ready for mastering.

**Your role**: Per-stem processing, noise reduction, frequency cleanup, dynamic control, stem remixing
**Not your role**: Creative production, lyrics, generation
**Primary tools**: `sox-engine.transform`, `ffmpeg-audio.transform`, `audio-analyzer.analyze`

## Core Principles

### Stems First
When `stems/` directory is present with track folders, process each stem independently. This allows targeted processing impossible on a full mix.

### Preserve the Performance
Mix polishing removes defects, not character. Be conservative — over-processing sounds worse than under-processing.

### Non-Destructive
All processing writes to `polished/` subfolder — originals are never modified.

### Frequency Coordination with Mastering
- Mix presence boost: ~3 kHz (clarity)
- Mastering harshness cut: ~3.5 kHz (taming)
These target different center frequencies, minimizing cancellation risk.

## Dependencies

This skill uses only the existing `daw-master` granular engines:
- `sox-engine` — single-track effects (EQ, compand, normalize, fades, highpass/lowpass/bandpass via raw effect)
- `ffmpeg-audio` — multi-track mixing, loudnorm, advanced dynamics
- `audio-analyzer` — feature extraction for analysis decisions

No external Python packages are required beyond what's already installed.

## Path Convention

Audio directories are expected under the standard layout:

```
{audio_root}/artists/[artist]/albums/[genre]/[album]/
├── stems/
│   ├── 01-track-name/
│   │   ├── 0 Lead Vocals.wav
│   │   ├── 1 Backing Vocals.wav
│   │   ├── 2 Drums.wav
│   │   ├── 3 Bass.wav
│   │   ├── 4 Guitar.wav
│   │   ├── 5 Keyboard.wav
│   │   ├── 6 Strings.wav
│   │   ├── 7 Brass.wav
│   │   ├── 8 Woodwinds.wav
│   │   ├── 9 Percussion.wav
│   │   ├── 10 Synth.wav
│   │   └── 11 FX.wav
│   └── 02-track-name/
│       └── ...
├── polished/            ← mix-engineer output
│   ├── 01-track-name.wav
│   └── ...
└── mastered/            ← mastering-engineer output
    └── ...
```

## Per-Stem Processing Chains

All processing uses SoX effects via `sox-engine.transform` with genre-specific parameter overrides.

### Common Operations

| Effect | SoX op | Parameters |
|--------|--------|------------|
| Highpass | "raw_effect": "highpass {freq}" | cutoff Hz, e.g., 30, 80 |
| Lowpass | "raw_effect": "lowpass {freq}" | cutoff Hz |
| Bandpass | "raw_effect": "bandpass {freq} {width}" | center freq, Q or width |
| Noise reduction | "raw_effect": "noisered {profile} {strength}" | profile file, strength 0–1 |
| EQ (shelf/peak) | "equalizer" | frequency, width, gain dB |
| Compression | "compand" | attack, soft_knee, threshold_in, threshold_out |
| Fade | "fade" | type (in/out/in-out), length sec |
| Normalize | "normalize" | peak dB (default -0.1) |
| Reverse | "reverse" | — |
| Trim/Pad | "trim", "pad" | start/end or silence |

> **Note**: SoX `noisered` requires a noise profile file. We auto-generate a profile from the quietest 100ms segment of each stem via `sox -n stat`. If no suitable silent region is found, noise reduction is skipped.

### Processing Chains by Stem

#### Vocals (Lead)
1. Noise reduction (strength 0.5)
2. Presence boost (+2 dB at 3 kHz, Q=1.0)
3. High tame (-2 dB shelf at 7 kHz)
4. Gentle compress: attack=0.01:0.1, soft_knee=0, in=-20dB, out=-10dB
5. Optional: fade in/out on track boundaries

#### Backing Vocals
1. Noise reduction (0.5)
2. Presence boost (+1 dB at 3 kHz)
3. High tame (-2.5 dB at 7 kHz)
4. Stereo width enhancement (via ffmpeg `pan` or `stereotools` — optional)
5. Tighter compress: attack=0.008:0.1, threshold_in=-14dB, threshold_out=-10dB

#### Drums
1. Click removal (high-amplitude transient detection; threshold 6σ)
2. Gentle compress: attack=0.005:0.1, threshold_in=-12dB, threshold_out=-10dB

#### Bass
1. Highpass (30 Hz Butterworth)
2. Mud cut: equalizer freq=200 gain=-3 width=2q
3. Gentle compress: attack=0.01:0.1, threshold_in=-15dB, threshold_out=-10dB

#### Guitar
1. Highpass (80 Hz)
2. Mud cut: eq freq=250 gain=-2.5 width=2q
3. Presence boost: eq freq=3000 gain=+1.5 width=1.2
4. High tame: highshelve freq=8000 gain=-1.5
5. Stereo width (mild)
6. Compress: attack=0.012:0.1, threshold_in=-14dB, threshold_out=-10dB

#### Keyboard
1. Highpass (40 Hz)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. Presence boost: eq freq=2500 gain=+1 width=0.8
4. High tame: highshelve freq=9000 gain=-1.5
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

#### Strings
1. Highpass (35 Hz)
2. Mud cut: eq freq=250 gain=-1.5 width=0.8
3. Presence boost: eq freq=3500 gain=+1
4. High tame: highshelve freq=9000 gain=-1
5. Wide stereo
6. Very light compress: attack=0.02:0.1, threshold_in=-18dB, threshold_out=-10dB

#### Brass
1. Highpass (60 Hz)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. Presence boost: eq freq=2000 gain=+1.5
4. High tame: highshelve freq=7000 gain=-2
5. Compress: attack=0.01:0.1, threshold_in=-14dB, threshold_out=-10dB

#### Woodwinds
1. Highpass (50 Hz)
2. Mud cut: eq freq=250 gain=-1.5 width=0.8
3. Presence boost: eq freq=2500 gain=+1
4. High tame: highshelve freq=8000 gain=-1
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

#### Percussion
1. Highpass (60 Hz)
2. Click removal (transient detection)
3. Presence boost: eq freq=4000 gain=+1
4. High tame: highshelve freq=10000 gain=-1
5. Stereo width (1.2×)
6. Compress: attack=0.008:0.1, threshold_in=-15dB, threshold_out=-10dB

#### Synth
1. Highpass (80 Hz)
2. Mid boost: eq freq=2000 gain=+1 width=0.8
3. High tame: highshelve freq=9000 gain=-1.5
4. Stereo width (1.2×)
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

#### Other (catch-all)
1. Light noise reduction (0.3)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. High tame: highshelve freq=8000 gain=-1.5

### Full-Mix Fallback
When stems aren't available, process the full stereo mix with a lighter chain:
- Noise reduction (0.3 strength, if profile available)
- Highpass 35 Hz
- Click removal (transient spike detection)
- Mud cut: eq freq=250 gain=-2
- Presence boost: eq freq=3000 gain=+1.5
- High tame: highshelve freq=7000 gain=-1.5
- Gentle compress

## Genre Presets

See [mix-presets.md](mix-presets.md) for full genre-specific settings. Key mappings:

| Genre | Vocal boost | Bass boost | Drum boost | High-mid cut |
|-------|-------------|------------|------------|--------------|
| Default | 0 dB | 0 dB | 0 dB | –2 dB @ 7 kHz |
| Hip-Hop/Rap | +1 dB | +1 dB | +0.5 dB | aggressive |
| Rock/Metal | 0 dB | 0 dB | +0.5–1 dB | –2.5 to –3 dB |
| EDM/Electronic | 0 dB | +0.5–1 dB | +0.5–1 dB | lighter |
| Folk/Country | +0.5 dB | 0 dB | +0.5 dB | –1.5 dB |
| Ambient/Lo-Fi | 0 dB | 0 dB | 0 dB | –1.5 dB; lighter NR |

## API Reference

### `analyze_mix_issues(album_path: str) -> Dict`

Scan audio directory for stems or full mix and detect potential issues.

**Returns**
```python
{
  "source_mode": "stems" | "full_mix",
  "tracks": [...],
  "issues": {
    "noisy_tracks": [{"track": "Vocals", "noise_floor": -45.2}],
    "muddy_tracks": [...],
    "harsh_tracks": [...],
    "clicky_tracks": [...],
    "sub_bass_rumble": [...]
  },
  "summary": "string"
}
```

### `polish_audio(album_path: str, genre: str = "default", dry_run: bool = False, use_stems: Optional[bool] = None) -> Dict`

Process stems or full mix with genre-appropriate settings.

**Parameters**
- `album_path`: Path to album directory containing `stems/` or WAVs
- `genre`: Genre preset name (default, hip-hop, rock, edm, ambient, folk, jazz, etc.)
- `dry_run`: If True, only return planned commands without executing
- `use_stems`: Force stems (True) or full-mix (False). If None, auto-detect.

**Returns**
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

End-to-end pipeline: analyze → polish → verify.

**Returns**
```python
{
  "analysis": {...},
  "polish": {...},
  "verification": {...},
  "output_dir": "/path/to/polished"
}
```

### `_generate_noise_profile(input_wav: str) -> str`

Generate a SoX noise profile from the quietest portion of an audio file. Returns path to temporary profile file.

### `_detect_clicks(audio_data, sr) -> List[float]`

Detect transient clicks via amplitude spike detection (> 6σ). Returns list of click timestamps (seconds).

## Quality Standards

Before handoff to mastering:
- [ ] No clipping (peak < –0.1 dBFS)
- [ ] All samples finite
- [ ] Noise floor reduced vs original (where applicable)
- [ ] No obvious processing artifacts
- [ ] Polished files written to `polished/` subfolder

## Handoff to Mastering

After polishing, invoke:
```python
from daw_master.mastering_engineer import master_audio
master_audio(album_path, source_subfolder="polished", genre=genre)
```

---

## Implementation Notes

### Noise Reduction Strategy
SoX `noisered` requires a stationary noise profile. We generate one automatically from the quietest non-silent 100ms window of the input stem using SoX's `stat` mode to find minimum RMS, then extract that segment with `sox input.wav -n trim {start} {duration} stat`. This profile is applied with strength 0.5–0.8 depending on genre.

### Click Removal Strategy
Click detection scans the waveform for amplitude spikes exceeding 6 standard deviations above the signal's median amplitude. Detected clicks are attenuated by interpolation (linear or spline) using SoX's `fade` + `trim` chaining or a custom Python-based repair if necessary.

### Highpass/Lowpass/Bandpass
SoX's `highpass`, `lowpass`, and `bandpass` effects are passed via `sox-engine`'s `raw_effect` operation to preserve parameter flexibility.

### Mix Rendering
After per-stem processing, stems are mixed to stereo using `ffmpeg-audio.mix()` with optional per-stem gain adjustments from genre preset.
