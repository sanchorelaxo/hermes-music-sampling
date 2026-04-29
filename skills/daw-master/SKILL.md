---
name: daw-master
description: "Meta-skill for DAW operations - orchestrates audio transformations and effects pipelines"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "daw", "production", "pipeline", "transformations"]
    related_skills: ["daw-master:dawdreamer", "daw-master:batch-processor"]
---

# DAW Master

Meta-skill providing a unified interface for DAW operations and audio transformation pipelines.

## Purpose

This meta-skill defines standards and base capabilities for audio processing skills under the
`daw-master` namespace. All concrete DAW skills should:

1. **Work with files**: Accept input audio file paths, produce output file paths
2. **Be chainable**: Operations can be piped/sequenced: `sox-normalize -> pitch-shift -> fade-out`
3. **Support analysis**: Extract metadata about audio (duration, peak, RMS, BPM estimate, etc.)
4. **Expose parameters**: Each operation has clear, documented parameters
5. **Return results**: Always produce a tangible output (modified file, analysis JSON, etc.)

## Philosophy

- **CLI-first**: Skills wrap command-line tools (SoX, FFmpeg, DawDreamer, etc.) but expose
  a clean Python/Hermes interface.
- **Stateless operations**: Each skill call is independent; no hidden session state.
- **Composability**: Output of one skill feeds into another. Skills are building blocks.
- **Non-destructive by default**: Transformations write to new files; original is preserved.
- **Extensible**: New tools/backends can be added as sub-skills without breaking existing workflow.

## Skill Registry

Sub-skills under `daw-master`:

|| Skill | Tool | Purpose |
|-------|------|---------|
|| `dawdreamer` | DawDreamer (Python) | Full-featured DAW: effects, mixing, time/pitch, VST |
|| `sox-engine` | SoX | Simple edits, effects, conversions |
|| `ffmpeg-audio` | FFmpeg | Codec work, filtering, stream ops |
|| `rubber-band-engine` | Rubber Band CLI | High-quality time-stretch/pitch-shift |
|| `audio-analyzer` | librosa + sonic-annotator | Extract BPM, key, MFCC, loudness |
|| `batch-processor` | SoX/FFmpeg scripts | Apply same pipeline to many files |
|| `metadata-manager` | BWFMetaEdit + mutagen | BWF/RIFF metadata embedding |
|| `ardour-automator` | Ardour (Lua) | Headless session automation & export |

## Common Patterns

### Pipeline Pattern

```python
# Conceptual: chain skills together
input = "vocals.wav"
pipeline = [
    ("normalize", {"target_level": -6}),
    ("time_stretch", {"factor": 0.95}),  # slow down 5%
    ("reverb", {"room_size": 0.4}),
    ("fade_out", {"duration": 2.0}),
]
output = run_pipeline(input, pipeline)
```

### Discovery Pattern

```python
# Analyze first, then decide transformations
info = analyze_audio("sample.wav")
if info["bpm"] > 140:
    target = "hiphop"
    pipeline = hiphop_chain
else:
    target = "ambient"
    pipeline = ambient_chain
```

### Batch Pattern

```python
# Apply skill to directory
for file in wav_files_in("in/"):
    output = dawdreamer.transform(
        file,
        effects=[gain(-3), compressor(threshold=-20)],
        output=f"out/{stem(file)}_processed.wav"
    )
```
