# Project Manifest: hermes-music-sampling

## Repository

https://github.com/sanchorelaxo/hermes-music-sampling

---

## Directory Structure (as of latest)

```
hermes-music-sampling/
├── README.md               # Project overview
├── RESEARCH.md             # Linux DAW/audio tools research
├── LICENSE                 # MIT License
├── MANIFEST.md             # This file — architecture + roadmap
├── .gitignore              # Build artifacts, audio files
└── skills/
    ├── daw-master/         # ← Meta-skill (namespace, interface spec)
    │   ├── SKILL.md
    │   ├── dawdreamer/     # ◻ Scaffolded — DawDreamer wrapper
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   ├── operations.py
    │   │   └── examples/
    │   ├── sox-engine/      # ✅ Implemented — SoX CLI effects
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   └── examples/
    │   ├── ffmpeg-audio/    # ✅ Implemented — FFmpeg filters & mixing
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   └── examples/
    │   ├── rubber-band-engine/  # ✅ Implemented — time-stretch/pitch-shift
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   └── examples/
    │   ├── audio-analyzer/  # ✅ Implemented — librosa feature extraction & Vamp
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   └── examples/
    │   └── dawdreamer/      # ⚙️ Scaffolded — full DAW VST hosting
    │       ├── SKILL.md
    │       ├── __init__.py
    │       ├── pipeline.py
    │       ├── operations.py
    │       └── examples/
```

---

## Implemented Skills Summary

| Skill | Tool | Status | Highlights |
|-------|------|--------|------------|
| `dawdreamer` | DawDreamer | ⚙️ Scaffolded | VST hosting, multi-track, effect graph (not yet tested) |
| `sox-engine` | SoX | ✅ | Normalize, fade, trim, EQ, compand, reverb, mix — 12+ ops |
| `ffmpeg-audio` | FFmpeg | ✅ | Loudnorm, acompress, atrim, amix, all codecs |
| `rubber-band-engine` | Rubber Band | ✅ | Professional time-stretch & pitch-shift with formants |

---

## Design Principles (recap)

1. No duplicate functionality per tool
2. Pipeline-first / composable
3. Explicit parameters
4. Stateless file I/O
5. Progressive disclosure (simple default, escape hatches)

---

## Quick Implementation Checklist for New Skills

- [ ] Create `skills/daw-master/<name>/` with SKILL.md and __init__.py
- [ ] Implement `transform(input, pipeline, output)` in `pipeline.py`
- [ ] Implement `mix(tracks, output)` if tool supports multi-input mixing
- [ ] Implement `analyze(file)` (can reuse ffprobe pattern)
- [ ] Document every op in SKILL.md (params, types, defaults, examples)
- [ ] Add 2-3 runnable example scripts in `examples/`
- [ ] Add category placeholder README if in new top-level category

---

## Changes Log

| Date | Commit | Notes |
|------|--------|-------|
| 2026-04-29 | `0fe240b` | Add rubber-band-engine skill (time-stretch, pitch-shift) |
| 2026-04-29 | `f272f59` | Add ffmpeg-audio skill (filtergraphs, codecs, multi-track mix) |
| 2026-04-29 | `845d352` | Add sox-engine (CLI effects) |
| 2026-04-28 | `2847efe` | Add daw-master meta-skill + dawdreamer scaffold |
