# Hermes Music Sampling

Aggregated music sampling skills for Hermes Agent — enabling audio production, analysis, and remixing on Linux.

## Overview

This project collects and organizes music sampling and audio processing skills for use with Hermes Agent. It provides tools and knowledge for discovering, analyzing, editing, and remixing audio files from the command line, both in pure CLI tools and Python environments.

## Research Summary

We've identified and categorized Linux-based audio production tools that meet these criteria:
- Can run Python scripts or provide Python bindings
- Have a CLI and/or headless mode
- Can analyze WAV, MP3 files
- Can edit/remix existing sound files (preferably via CLI)

See [RESEARCH.md](RESEARCH.md) for the full breakdown.

### Tier 1: Core CLI Tools (Shell-Script Friendly)

| Tool | Purpose | Notes |
|------|---------|-------|
| SoX | Audio conversion, editing, effects | The classic CLI Swiss Army knife |
| FFmpeg | Universal media processor | Best for codec work and filtering |
| Rubber Band | Time-stretch & pitch-shift | High-quality, industry-standard |
| Sonic Annotator | Feature extraction | Beat tracking, melody, chords via Vamp |
| BWF MetaEdit | Broadcast Wave metadata | Professional sample library tagging |

### Tier 2: Python Libraries

| Library | Purpose | Notes |
|---------|---------|-------|
| DawDreamer | Full DAW in Python | VST hosting, multi-track composition |
| librosa | Audio analysis | MFCC, chroma, onset, beat tracking |
| PyDub | Simple audio editing | Slicing, mixing, format conversion |

### Tier 3: Full DAWs with Automation

| DAW | Automation Method | Notes |
|-----|-------------------|-------|
| Ardour | Lua (and Python via Lua bridge) | Native Linux, full headless mode |
| REAPER | ReaScript (Python/EEL/Lua) | Runs via Wine, excellent CLI |
| Carla | MIDI/OSC/CLI | Plugin host and routing matrix |

---

## Planned Skills

Skills we plan to create for the Hermes ecosystem:

- `audio-analysis` — Extract features (BPM, key, spectral, MFCC) using librosa + Sonic Annotator
- `batch-processor` — Apply effects, normalize, convert formats using SoX/FFmpeg
- `sample-library` — Organize, tag, and catalogue audio collections
- `daw-renderer` — Drive Ardour/REAPER headlessly to render projects
- `vst-testbench` — Use Carla to test plugin chains on samples
- `time-stretch-engine` — Rubber Band-powered tempo/pitch manipulation
- `metadata-manager` — BWF/iXML tagging with BWF MetaEdit
- `mashup-builder` — Combine stems using DawDreamer/PyDub

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/sanchorelaxo/hermes-music-sampling.git
cd hermes-music-sampling

# Install core dependencies (Ubuntu/Debian)
sudo apt install sox ffmpeg rubberband-cli bwfmetaedit

# Or see RESEARCH.md for full installation across distros
```

## License

MIT
