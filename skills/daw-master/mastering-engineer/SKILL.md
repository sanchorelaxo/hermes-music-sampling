---
name: daw-master:mastering-engineer
description: Guides audio mastering for streaming platforms including loudness optimization and tonal balance, using FFmpeg loudnorm and audio-analyzer verification.
version: 0.1.0
author: Ported from bitwize-music-studio
license: MIT
metadata:
  hermes:
    tags: ["audio", "mastering", "loudness", "loudnorm", "streaming"]
    related_skills: ["daw-master:ffmpeg-audio", "daw-master:audio-analyzer", "daw-master:mix-engineer"]
---

# Mastering Engineer Skill

You are an audio mastering specialist for AI-generated music. You guide loudness optimization, platform delivery standards, and final audio preparation using `ffmpeg-audio`'s `loudnorm` filter and `audio-analyzer`'s LUFS measurement.

**Your role**: Mastering guidance, quality control, platform optimization
**Not your role**: Audio editing (trimming, fades), mixing, creative production
**Primary tools**: `ffmpeg-audio.transform` (loudnorm), `audio-analyzer.analyze`, `audio-analyzer.probe`

## Core Principles

### Loudness is Not Volume
- **LUFS** measures perceived loudness (ITU-R BS.1770)
- Streaming platforms normalize to target LUFS
- Too loud = squashed dynamics, fatiguing
- Too quiet = listener turns up volume, loses impact

### Universal Streaming Target
**Master to –14 LUFS integrated, –1.0 dBTP** = works everywhere

### Genre Informs Targets
- Classical/Jazz: –16 to –18 LUFS (high dynamic range)
- Rock/Pop: –12 to –14 LUFS (moderate dynamics)
- EDM/Hip-Hop: –8 to –12 LUFS (compressed, loud)
- For streaming: –14 LUFS works across all genres

See [genre-presets.md](genre-presets.md) for detailed genre settings.

## Dependencies

This skill uses only existing `daw-master` granular engines:
- `ffmpeg-audio.transform` with `loudnorm` filter for loudness normalization
- `audio-analyzer.analyze` for LUFS measurement (RMS-based approximation)
- `audio-analyzer.probe` for peak and format validation

No external Python packages (matchering, pyloudnorm) are required. FFmpeg's `loudnorm` filter performs EBU R128 / ITU-R BS.1770 compliant loudness measurement and normalization.

## Path Convention

Before mastering, the audio directory is resolved (passed as `album_path` argument). Expected layout:

```
{album_path}/
├── stems/            (optional)
├── polished/         ← mix-engineer output (source_subfolder="polished")
├── raw/              (original Suno WAVs)
└── mastered/         ← your output
    └── track-name.wav
```

## Mastering Workflow

### Step 1: Pre-Flight Check

Verify:
1. Audio folder exists and contains WAV files
2. If no WAVs: "No WAV files found. Download tracks from Suno as WAV (highest quality) first."
3. If only MP3s: warn user to re-download as WAV

### Step 2: Analyze Tracks

```python
from daw_master.audio_analyzer import analyze
result = analyze(track_wav)
```

**Check**: LUFS (integrated), peak dBFS, dynamic range, spectral balance.

**Red flags**:
- Tracks vary by >2 dB LUFS (inconsistent album)
- Peak > 0.0 dBTP (clipping)
- LUFS < –20 or > –8 (too quiet/too loud)

### Step 3: Choose Genre Preset

Use `genre-presets.md` to select target LUFS and EQ settings.

### Step 4: Master Each Track

```python
from daw_master.ffmpeg_audio import transform

pipeline = [
  {"op": "equalizer", "frequency": 200, "gain": -2.0, "width": "2q"},   # genre-specific cut
  {"op": "loudnorm", "i": -14.0, "tp": -1.0, "lra": 7.0}  # loudness normalize
]
transform(input=track_in, pipeline=pipeline, output=track_out)
```

**loudnorm parameters** (FFmpeg):
- `i`: Integrated loudness target (default –14)
- `tp`: True peak limit (default –1.0)
- `lra`: Target loudness range (default 7.0 LU)

### Step 5: Verify Output

```python
result = analyze(mastered_wav)
assert abs(result['loudness_lufs'] - target_lufs) < 0.5
assert result['peak_db'] < -1.0
```

### Step 6: Album Consistency

If tracks span >1 dB LUFS range, apply per-track loudness correction to align:
```python
# Compute required gain offset per track
offset = target_lufs - track_lufs
pipeline = [{"op": "volume", "gain": f"{offset}dB"}, {"op": "loudnorm", ...}]
```

### One-Call Pipeline

```python
master_album(album_path, genre="default")
```

Runs: analyze → pre-QC → master all tracks → verify → post-QC.

## API Reference

### `analyze_audio(album_path: str, subfolder: Optional[str] = None) -> Dict`

Analyze all WAV files in `album_path`. If `subfolder` provided (e.g., "mastered"), analyze that subfolder instead.

**Returns**
```python
{
  "tracks": [
    {"filename": "01-track.wav", "loudness_lufs": -14.2, "peak_db": -1.5, "lra": 6.5, ...}
  ],
  "album_lufs_avg": -14.1,
  "album_lufs_range": 0.8,
  "issues": [...]
}
```

### `qc_audio(album_path: str, subfolder: Optional[str] = None) -> Dict`

Run technical QC checks (mono compatibility, phase correlation, clipping, clicks, silence, format validation). Returns pass/fail with warnings.

### `master_audio(album_path: str, genre: str = "default", cut_highmid: float = -2.0, source_subfolder: Optional[str] = None, dry_run: bool = False) -> Dict`

Master all tracks in `album_path` using genre preset.

**Parameters**
- `album_path`: Base audio directory
- `genre`: Genre preset name
- `cut_highmid`: High-mid shelf cut amount (dB, negative = cut)
- `source_subfolder`: Read from this subfolder instead of raw (e.g., "polished")
- `dry_run`: Preview commands without writing

**Returns**
```python
{
  "tracks_mastered": 10,
  "output_dir": "/.../mastered",
  "target_lufs": -14.0,
  "commands": [...],
  "success": bool
}
```

### `master_with_reference(album_path: str, reference_wav: str) -> Dict`

Reference-based mastering: match loudness and tonal balance to a reference track using `audio-analyzer` feature comparison and FFmpeg EQ correction.

### `fix_dynamic_track(album_path: str, track_filename: str) -> Dict`

Apply additional compression + limiting to tracks with excessive dynamic range that resist reaching target LUFS.

### `master_album(album_path: str, genre: str = "default", **kwargs) -> Dict`

Full pipeline: analyze → QC → master → verify. Returns comprehensive report.

## Genre Presets

Full presets are in [genre-presets.md](genre-presets.md). Summary:

| Genre | Target LUFS | EQ priorities |
|-------|-------------|---------------|
| Hip-Hop/Rap | –12 to –14 | Sub-bass presence (40–60 Hz), vocal clarity (2–4 kHz) |
| Rock/Alternative | –12 to –14 | Guitar body (800 Hz–3 kHz), avoid harsh highs |
| EDM | –10 to –12 | Massive sub-bass (30–50 Hz), high-end sparkle (10+ kHz) |
| Jazz/Classical | –16 to –18 | Natural balance, minimal processing |
| Ambient/Lo-Fi | –15 to –16 | Warmth, preserve reverb tails |

## Quality Standards

Before distribution:
- [ ] All tracks analyzed
- [ ] Integrated LUFS: –14.0 ± 0.5 dB
- [ ] True peak: < –1.0 dBTP
- [ ] No clipping or distortion
- [ ] Album consistency: <1 dB LUFS range

## Multi-System Check

Test on:
- Studio headphones
- Laptop speakers
- Phone speaker
- Car stereo (if possible)

## Technical QC (qc_audio)

Checks performed:
1. **Mono compatibility**: phase correlation > –0.5
2. **Phase issues**: correlation not near ±1 (out-of-phase)
3. **Clipping**: true peak > 0.0 dB
4. **Clicks/pops**: transient spike detection
5. **Silence gaps**: leading/trailing silence > 2 sec
6. **Format**: valid WAV, correct sample rate/bit depth
7. **Spectral balance**: no major holes (energy dip > 20 dB in any octave)

## Reference-Based Mastering

`master_with_reference` does NOT use matchering library. Instead:

1. Analyze reference track: `audio-analyzer.analyze(ref_wav)`
2. Extract spectral fingerprint (mel spectrum statistics, centroid, rolloff)
3. Analyze each program track
4. Compute EQ correction curve to match reference's spectral shape
5. Apply via FFmpeg equalizer filters

## Handoff to Release

After mastering:

```markdown
## Mastering Complete - Ready for Release

**Album**: [Name]
**Mastered Files**: [path to mastered/]
**Track Count**: [N]
**Average LUFS**: –14.0 ± 0.3 dB

**QC Results**:
- [ ] LUFS within spec
- [ ] No clipping
- [ ] Album consistency < 1 dB
- [ ] No phase issues

**Next**: Upload to distribution platform.
```

---

## Differences from Remote Skill

This skill diverges from the upstream `bitwize-music-skills` version to avoid external dependencies:

| Feature | Upstream | This port |
|---------|----------|-----------|
| Loudness measurement | pyloudnorm | ffmpeg-audio loudnorm + audio-analyzer |
| Reference matching | matchering | spectral-feature EQ matching |
| Noise profiling | noisereduce library | SoX `noisered` with auto-generated profile |
| Click removal | custom spectral algorithm | amplitude-threshold detection (simplified) |
| MCP tools | bitwize-music-mcp | direct Python function calls |

The functional interface remains compatible in spirit: `master_audio(album_path, genre="rock")` produces a mastered `mastered/` folder with normalized, EQ'd WAV files.
