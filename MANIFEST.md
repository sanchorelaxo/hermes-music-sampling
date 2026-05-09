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
    ├── daw-master/         # Meta-skill (namespace, interface spec)
    │   ├── SKILL.md
    │   ├── sox-engine/     # ✅ SoX — effects, edits, mix
    │   ├── ffmpeg-audio/   # ✅ FFmpeg — filters, codecs, loudnorm
    │   ├── rubber-band-engine/  # ✅ Rubber Band — time/pitch
    │   ├── audio-analyzer/ # ✅ librosa — feature extraction, Vamp
    │   ├── batch-processor/    # ✅ SoX/FFmpeg batch pipelines
    │   ├── metadata-manager/   # ✅ BWF/iXML/ID3 tagging
    │   ├── ardour-automator/  # ✅ Ardour headless automation
    │   ├── carla-rack/     # ✅ Carla plugin chain rack
    │   ├── mastering-engineer/ # ✅ Multi-band compression/limiting
    │   ├── mix-engineer/   # ✅ Multi-track mixing
    │   └── dawdreamer/     # ⚙️ Scaffolded — VST hosting
    │
    instruments/             # Hardware instrument reference skills
    │   ├── SKILL.md        # Category index
    │   ├── sp404-mk2/      # Roland SP-404 MK2 — 16-pad sampler + sequencer
    │   ├── kaossilator-v1/ # Korg KAOSSILATOR (2007) — X-Y pad synth, 100 programs
    │   ├── kaossilator-v2/ # Korg kaossilator 2S (2011) — audio player, microSD
    │   ├── fx-wizard/       # Korg Kastle 2 (FX Wizard) — 9-mode patchable multi-FX
    │   ├── wave-bard/       # Korg Kastle 2 (Wave Bard) — 8-sample player + quantizer
    │   ├── wavedrum-mini/  # Roland WAVEDRUM Mini — dynamic percussion synth
    │   ├── minikp-v1/      # Korg miniKP (2006) — X-Y touchpad FX
    │   ├── minikp-v2/      # Korg mini kaoss pad 2s (2011) — audio player, fnc
    │   ├── qunexus/        # KMI QuNexus — 25-key USB MIDI keyboard
    │   ├── kaoss-dj-mixer/ # Korg KAOSS DJ MIXER — USB DJ controller
    │   └── op-1/           # Teenage Engineering OP-1 — 13 synth engines
    └── quneo/           # QuNeo 3D multi-touch MIDI controller (Keith McMillen)
        ├── SKILL.md        # Category index
        ├── quneo-controller/    # SysEx preset loading, Linux MIDI, reload
        ├── quneo-led-mapping/  # CC vs Note On LED control
        └── quneo-osc-integration/  # OSC LED control, pyliblo, QuNeOSC Bridge
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
| 2026-05-05 | — | Split kaossilator (v1/v2), minikp (v1/v2); add op-1, quneo namespace (controller/led-mapping/osc-integration) |
| 2026-05-05 | — | Add instruments category: sp404-mk2, kaossilator, kastle2, wavedrum-mini, minikp, qunexus, kaoss-dj-mixer |
| 2026-04-29 | `0fe240b` | Add rubber-band-engine skill (time-stretch, pitch-shift) |
| 2026-04-29 | `f272f59` | Add ffmpeg-audio skill (filtergraphs, codecs, multi-track mix) |
| 2026-04-29 | `845d352` | Add sox-engine (CLI effects) |
| 2026-04-28 | `2847efe` | Add daw-master meta-skill + dawdreamer scaffold |
