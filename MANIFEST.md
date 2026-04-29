# Project Manifest: hermes-music-sampling

## Repository

https://github.com/sanchorelaxo/hermes-music-sampling

---

## Directory Structure (as of commit 845d352)

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
    │   ├── dawdreamer/     # ← Skill #1: DawDreamer framework wrapper
    │   │   ├── SKILL.md
    │   │   ├── __init__.py
    │   │   ├── pipeline.py
    │   │   ├── operations.py
    │   │   └── examples/
    │   │       ├── 01_time_stretch_fade.py
    │   │       ├── 02_mix_stems.py
    │   │       └── 03_vst_chain.py
    │   └── sox-engine/      # ← Skill #2: SoX CLI wrapper
    │       ├── SKILL.md
    │       ├── __init__.py
    │       ├── pipeline.py
    │       └── examples/
    │           ├── 01_normalize_compress_fade.py
    │           ├── 02_mix_stems.py
    │           └── 03_trim_downsample.py
    ├── analysis/            # Reserved for audio-analyzer skill (librosa)
    ├── conversion/          # Reserved for ffmpeg-audio skill
    ├── daw-integration/     # Reserved for ardour-automator, reaper-agent, carla-rack
    ├── editing/             # Reserved for batch-processor skill
    └── metadata/            # Reserved for bwf-metadata skill
```

---

## Skill Architecture

### Meta-Skill: `daw-master`

Defines the unified interface for all audio skills under this namespace:

- **Pipeline pattern**: `transform(input, pipeline=[...], output)`
- **Composable**: Output of one skill → input of another
- **File-based**: Inputs/outputs are file paths; no in-memory coupling
- **Stateless**: No hidden session state
- **Chaining**: Operations within a skill are applied in order

See `skills/daw-master/SKILL.md` for full specification.

---

### Implemented Skills

#### 1. `dawdreamer` (skills/daw-master/dawdreamer/)

**Tool**: DawDreamer (Python, JUCE-based DAW framework)

**Status**: ✅ Scaffolded — pipeline logic in place, operation builders defined

**Core API**:
- `transform(input, pipeline, output)` — effect chain
- `mix(tracks, output)` — multi-track mixdown
- `analyze(file)` — basic stats (duration, peak, RMS)

**Pipeline operations**:
`gain`, `filter` (low/high/etc), `compressor`, `reverb`, `fade_in/out`,
`overlay` (two-file mix), `load_vst`, `set_param`

**Notes**: Full DAW in Python. VST hosting, time-stretch, pitch-shift planned.
Not yet tested (requires `pip install dawdreamer` and system JUCE deps).

---

#### 2. `sox-engine` (skills/daw-master/sox-engine/)

**Tool**: SoX (Sound eXchange) — CLI audio Swiss Army knife

**Status**: ✅ Implemented — `transform()`, `mix()`, `analyze()` fully functional

**Core API**:
- `transform(input, pipeline, output)` — build one-shot sox command
- `mix(tracks, output)` — multi-track mix via `sox -m`
- `analyze(file)` — duration, sample_rate, channels, peak, RMS

**Pipeline operations**:
`gain`, `normalize`, `fade` (in/out/in-out), `trim`, `pad`, `reverse`,
`channels`, `rate` (resample), `compand`, `equalizer`, `bass`, `treble`,
`echo`, `reverb`, `raw_effect` (pass-through)

**Examples**:
```bash
# Normalize + compress + fade out
sox in.wav norm compand 0.01:0.1 -20:-10 fade q 1.5 out.wav

# Mix two tracks at different gains
sox -m -v 1.0 vocals.wav -v 0.7 instrumental.wav mix.wav

# Trim, mono, downsample
sox long.wav trim 12.5 30 channels 1 rate 22050 fade in 0.2 out.wav
```

**Advantages**: Available everywhere, no Python dependency, fast, battle-tested.

---

## Planned Skills (Roadmap)

### Tier 1 — CLI Foundations
3. **`ffmpeg-audio`** — FFmpeg filters (volume, normalize, amix, channelsplit, etc.)
4. **`rubber-band-engine`** — Dedicated high-quality time-stretch/pitch-shift
5. **`audio-analyzer`** — librosa + sonic-annotator for BPM, key, MFCC, loudness

### Tier 2 — Batch & Metadata
6. **`batch-processor`** — Apply same pipeline to directories (parallelizable)
7. **`metadata-manager`** — BWF/iXML/ID3 tag reading/writing

### Tier 3 — Full DAW Automation
8. **`ardour-automator`** — Lua script runner for headless Ardour rendering
9. **`reaper-agent`** — Wine + ReaScript (Python) batch render automation
10. **`carla-rack`** — Plugin chain testbench with Carla headless/OSC

---

## Design Principles

1. **No duplicate functionality** — Each tool covers its forte:
   - `sox-engine`: Quick edits, format conversion, simple effects
   - `ffmpeg-audio`: Complex filtergraphs, codec gymnastics, stream ops
   - `dawdreamer`: Programmable DSP graphs, VST hosting, multi-track composition
   - `rubber-band-engine`: Best-in-class time/pitch (algorithm different from SoX)
   - `ffmpeg-audio`: Handles formats SoX might not (AAC, AC3, etc.)

2. **Pipeline-first** — Skills are designed for composition:
   ```python
   input_audio -> sox-engine (trim/normalize) -> dawdreamer (FX chain) -> final
   ```

3. **Explicit parameters** — Only the meaningful knobs are exposed. Hide
   defaults that 95% of users won't touch.

4. **Stateless file I/O** — No session files, no temp state lives beyond the call
   (except transient intermediates for multi-step pipelines).

5. **Progressive disclosure** — Simple call signature for 80% cases; `extra_args`
   or `dry_run` escapes for power users.

---

## Integration Pattern

Every concrete skill:
- Namespaced under `daw-master` → called as `daw-master:<skill>`
- Exposes: `transform()`, `mix()`, `analyze()` (maybe more)
- Returns dict: `{success: bool, output: str, error?: str, ...}`
- Accepts `dry_run=True` to preview without executing
- Logs exact CLI/API call for reproducibility

Each skill directory:
```
<skill>/
├── SKILL.md         ← full reference + examples + installation
├── __init__.py      ← public exports
├── pipeline.py      ← implementation (transform/mix/analyze)
├── operations.py    ← operation builders (if applicable)
├── examples/        ← 2-3 runnable demo scripts
└── templates/       ← optional project templates
```

---

## Getting Started

```bash
# Clone
git clone https://github.com/sanchorelaxo/hermes-music-sampling.git
cd hermes-music-sampling

# Install SoX (sox-engine)
sudo apt install sox           # Debian/Ubuntu
# brew install sox             # macOS

# Test sox-engine (requires a WAV file named input.wav in cwd)
python skills/daw-master/sox-engine/examples/01_normalize_compress_fade.py

# Install DawDreamer (dawdreamer skill — optional)
sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev
pip install dawdreamer
```

---

## Quick Reference: Operation Matrix

| Operation | sox-engine | dawdreamer | ffmpeg-audio (planned) |
|-----------|-----------|------------|------------------------|
| normalize | ✅ `norm` | ✅ peak scaling | ✅ `loudnorm` filter |
| gain      | ✅ `gain` | ✅ gain processor | ✅ `volume` filter |
| trim      | ✅ `trim` | ✅ trim op | ✅ `trim` filter |
| fade      | ✅ `fade` | ✅ fade processor | ❌ manual envelope |
| filter    | ✅ EQ/filter | ✅ FilterProcessor | ✅ `equalizer`, `highpass`, etc |
| compress  | ✅ `compand` | ✅ CompressorProcessor | ✅ `acompress` |
| reverb    | ✅ simple reverb | ✅ ReverbProcessor | ❌ (needs convolver) |
| overlay   | ❌ (use `mix`) | ✅ overlay op | ✅ `amix` filter |
| time-stretch | ⚠️ via `rubber-band` separate | ✅ PlaybackWarp | ❌ (atempo only, limited) |
| pitch-shift | ⚠️ via `rubber-band` | ✅ warping | ❌ |
| VST       | ❌ | ✅ plugin host | ❌ |

---

## Changes Log

| Date | Commit | Notes |
|------|--------|-------|
| 2026-04-28 | `845d352` | Added sox-engine (transform/mix/analyze with 12+ effects) |
| 2026-04-28 | `2847efe` | Added daw-master meta-skill and dawdreamer scaffold |
| 2026-04-28 | `93e6795` | Added MANIFEST.md, pushed LICENSE |
| 2026-04-28 | `3073a03` | Created skill category READMEs |
| 2026-04-28 | `54b8708` | Added RESEARCH.md (Linux audio tools survey) |
| 2026-04-28 | `98b86f5` | Initial README + repo creation |

---

## Notes for Skill Maintainers

- Keep each skill's `pipeline.py` self-contained. Expose a clean `transform()` function
  that can be called directly by Hermes or by other skills.
- When implementing the next skill (`ffmpeg-audio`), copy the sox-engine template
  but translate operations to FFmpeg filtergraphs. Don't duplicate operations —
  SoX handles effects, FFmpeg handles codecs and complex filters; they complement.
- **Test locally**: Each examples/ script should run with a dummy WAV file.
  Add `tests/` directories when the skill matures.
- **Document**: SKILL.md must list every operation, parameters, types, defaults, ranges.
- **Error handling**: Always return `{success, error?}` dict; never raise uncaught.
- **Dry-run**: Implement `dry_run=True` that returns `{success: True, dry_run: True, command: "..."}`
  without executing. This helps users debug pipelines.
- **Logging**: On error, include the exact SoX/FFmpeg command and stderr snippet in the
  result dict's `error` and `stderr` fields.