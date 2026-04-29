# Project Manifest: hermes-music-sampling

## Repository

https://github.com/sanchorelaxo/hermes-music-sampling

---

## Directory Structure

```
hermes-music-sampling/
├── README.md              # Project overview
├── RESEARCH.md            # Linux DAW/audio tools research
├── LICENSE                # MIT License
├── .gitignore             # Build artifacts, audio files
└── skills/
    ├── daw-master/        # ← Meta-skill (namespace)
    │   ├── SKILL.md       #    DawMaster interface spec
    │   └── dawdreamer/    #    ↓ First concrete implementation
    │       ├── SKILL.md   #       DawDreamer wrapper docs
    │       ├── __init__.py
    │       ├── pipeline.py      # transform() / mix() / analyze()
    │       ├── operations.py    # Operation builders
    │       ├── examples/
    │       │   ├── 01_time_stretch_fade.py
    │       │   ├── 02_mix_stems.py
    │       │   └── 03_vst_chain.py
    │       └── templates/
    ├── analysis/          # Reserved for audio-analyzer skill
    ├── conversion/        # Reserved for sox-engine, ffmpeg-audio
    ├── daw-integration/   # Reserved for ardour-automator, carla-rack
    ├── editing/           # Reserved for batch-processor
    └── metadata/          # Reserved for bwf-metadata, tagger
```

---

## Skill Architecture

### Meta-Skill: `daw-master`

Defines the unified interface and philosophy for all audio skills:

- **Pipeline pattern**: `transform(input, pipeline=[...], output)`
- **Composable**: Output of one skill feeds into another
- **File-based**: Arguments are file paths; results are files
- **Stateless**: No hidden session state between calls

See `skills/daw-master/SKILL.md` for full spec.

---

### Concrete Skill #1: `dawdreamer`

Wraps the DawDreamer Python framework (JUCE-based) for DAW operations:

**Core functions:**
- `transform(input, pipeline, output)` → apply effect chain
- `mix(tracks, output)` → multi-track mixing
- `analyze(filepath)` → feature extraction (duration, peak, RMS, etc.)

**Supported pipeline operations:**
`gain`, `filter` (low/high/etc), `compressor`, `reverb`, `fade_in/out`,
`overlay` (mix two files), `load_vst`, `set_param`

**Implementation:**
- `operations.py`: Each op returns a processor spec dict
- `pipeline.py`: Builds DawDreamer graph, renders, saves
- `examples/`: Three runnable demos

---

## Research Summary (from RESEARCH.md)

**Category A: Python-native frameworks**
- DawDreamer — full DAW capabilities ✅ (wrapped)
- librosa — audio analysis (feature extraction) ⏳
- PyDub — simple edits ⏳

**Category B: CLI tools (shell-friendly)**
- SoX — Swiss Army knife ⏳
- FFmpeg — universal converter ⏳
- Rubber Band CLI — time-stretch/pitch-shift ⏳
- Sonic Annotator — batch feature extraction ⏳
- BWF MetaEdit — broadcast metadata ⏳

**Category C: Full DAWs**
- Ardour (Lua/headless) — full session automation ⏳
- REAPER (Wine + ReaScript) — proven batch renderer ⏳
- Carla — plugin host, OSC/MIDI control ⏳

---

## Implementation Roadmap (Suggested Order)

### Tier 1 — Foundational CLI Wrappers (No dupes, complementary)
1. **`sox-engine`** — Core CLI toolkit (trim, normalize, concat, effects)
2. **`ffmpeg-audio`** — Codec work, filters, probe
3. **`rubber-band-engine`** — High-quality time/pitch
4. **`audio-analyzer`** — librosa + sonic-annotator for features

### Tier 2 — Advanced Integration
5. **`batch-processor`** — Directory-wide pipelines (combines above)
6. **`metadata-manager`** — BWF/iXML tagging

### Tier 3 — Full DAW Automation
7. **`ardour-automator`** — Lua script runner for Ardour
8. **`reaper-agent`** — Wine + ReaScript integration
9. **`carla-rack`** — Plugin chain sandbox

---

## Design Principles

1. **No duplicate functionality** — each tool covers its strengths:
   - `sox-engine`: ad-hoc edits, effects, quick conversions
   - `ffmpeg-audio`: complex filtering, codec gymnastics
   - `dawdreamer`: programmable signal graphs, VST hosting
   - `ardour`: existing .ardour project rendering
   - `reaper`: Windows plugin compatibility under Wine

2. **Chainable** — `dawdreamer.transform(...)` produces a file
   that becomes input to `batch-processor` etc.

3. **Expose all core parameters** — but not every obscure knob.
   Each skill doc lists the knobs that matter for sampling workflows.

4. **Headless-first** — no GUI dependencies. All tools must run
   in a terminal or script environment.

5. **Progressive disclosure** — Basic use is simple:
   ```python
   dawdreamer.transform("in.wav", [{"op": "normalize"}], "out.wav")
   ```
   Advanced: pass `vst_search_paths`, `sample_rate`, `buffer_size`,
   `dry_run=True`, etc.

---

## Getting Started (Dev)

```bash
# Clone
git clone https://github.com/sanchorelaxo/hermes-music-sampling.git
cd hermes-music-sampling

# (Optional) Install DawDreamer for testing dawdreamer skill
sudo apt install build-essential cmake libasound2-dev libjack-jackd2-dev
pip install dawdreamer

# Try examples
python skills/daw-master/dawdreamer/examples/01_time_stretch_fade.py

# Install other tools
sudo apt install sox ffmpeg rubberband-cli bwfmetaedit
pip install librosa pydub
```

---

## Notes for Next Skills

When implementing `sox-engine`, `ffmpeg-audio`, etc.:

1. Follow `dawdreamer`'s pattern:
   - `SKILL.md` with operation reference
   - `pipeline.py` or `engine.py` with main api
   - `operations.py` or `effects/` for individual ops
   - `examples/` with demos

2. Keep the `daw-master` namespace: skill name = `daw-master:sox-engine`

3. Write operations so they return spec dicts (or call helpers) —
   this enables eventual cross-tool optimization (e.g., detect if
   `ffmpeg` can do whole chain more efficiently than `sox`).

4. Add error handling that returns `{success: False, error: str}` dicts
   — consistent with `dawdreamer.transform` return format.

5. Document all operation parameters in SKILL.md — what the op does,
   parameter types, default values, typical ranges.

6. Add unit tests in a `tests/` subdir when feasible.

---

## Changes Log

| Date | Commit | Notes |
|------|--------|-------|
| 2026-04-28 | `2847efe` | Added daw-master meta-skill + dawdreamer implementation |
| 2026-04-28 | `3073a03` | Added skill category READMEs |
| 2026-04-28 | `54b8708` | Added RESEARCH.md |
| 2026-04-28 | `98b86f5` | Initial README + repo creation |
