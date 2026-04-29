# Linux Audio Tools Research for Hermes Music Sampling Skills

## Executive Summary

This document catalogs Linux-based audio production tools that meet the following criteria:
- Can run Python scripts or provide Python bindings
- Have a CLI and/or headless mode
- Can analyze WAV, MP3 files
- Can edit/remix sound files (preferably via CLI)

---

## Python-Native Frameworks (First-Class Candidates)

### 1. DawDreamer
- **URL**: https://github.com/DBraun/DawDreamer
- **Python Native**: Yes — pure Python module
- **CLI/Headless**: Yes — fully scriptable, no GUI required
- **Analysis Features**:
  - Audio feature extraction
  - Source separation
  - Time-stretching and pitch-warping (Ableton-style warping)
  - Spectral analysis
- **Editing/Remixing**:
  - Multi-track composition
  - VST2/VST3 plugin hosting
  - Audio routing (DAG-based)
  - Mix and render
- **File Formats**: WAV, MP3, FLAC, AIFF, plus many via VST
- **Notes**: Built on JUCE framework. Bridges gap between Python and DAW functionality. Strong for algorithmic composition and batch processing.

### 2. librosa
- **URL**: https://librosa.org/
- **Python Native**: Yes
- **CLI/Headless**: Via Python scripts
- **Analysis Features**:
  - MFCC (Mel-frequency cepstral coefficients)
  - Spectral centroid, roll-off, bandwidth
  - Chroma features
  - Onset detection
  - Beat and tempo tracking
  - Harmonic/percussive separation
- **Editing/Remixing**: None — analysis library only
- **File Formats**: WAV, MP3, OGG, FLAC (depends on soundfile/audioread backends)
- **Notes**: The standard Python library for music/audio analysis. No editing capabilities but excellent for feature extraction and MIR (Music Information Retrieval).

### 3. PyDub
- **URL**: https://github.com/jiaaro/pydub
- **Python Native**: Yes
- **CLI/Headless**: Via Python scripts
- **Analysis Features**:
  - Duration, channels, sample width, frame rate
  - Amplitude/dBFS
- **Editing/Remixing**:
  - Splitting, concatenation, overlay/mixing
  - Fade in/out, crossfade
  - Speed change, reverse
  - Volume adjustment
  - Sample rate conversion
- **File Formats**: WAV (pure Python), MP3/OGG/FLAC/AAC via ffmpeg
- **Notes**: High-level, intuitive API. Great for simple batch edits, concatenations, and format conversions. Wraps ffmpeg underneath.

---

## Command-line Audio Tools (Shell-Script Friendly)

### 4. SoX (Sound eXchange)
- **URL**: http://sox.sourceforge.net/
- **Python Native**: No
- **CLI/Headless**: Yes — designed for CLI
- **Analysis Features**:
  - `stats`: amplitude stats, RMS, peak, DC offset
  - `spectrogram`: generate spectrogram PNGs
  - `silence`: detect/trim silence
  - `fade`, `tone`, `synth`: generate test signals
- **Editing/Remixing**:
  - Trim, concatenate, merge/channel mixing
  - Normalize, fade, pad
  - Channel manipulation (split/merge, convert mono↔stereo)
  - Effects: reverb, delay, chorus, flanger, eq, compressor, phaser, tremolo
  - Sample rate and bit depth conversion
- **File Formats**: WAV, MP3, FLAC, AIFF, OGG, VOC,和各种; over 30 formats
- **Notes**: The original "Swiss Army knife" of CLI audio. Excellent for batch processing in shell scripts. Effects chain is simple but effective.

### 5. FFmpeg
- **URL**: https://ffmpeg.org/
- **Python Native**: No
- **CLI/Headless**: Yes
- **Analysis Features**:
  - `ffprobe`: detailed stream info (duration, bitrate, codec, sample rate, channels, pixel format for video)
  - Metadata extraction (title, artist, album, tags)
  - Frame-level inspection
- **Editing/Remixing**:
  - Convert between virtually any format
  - Trim (by time or sample count)
  - Concatenate
  - Stream copy (no re-encode)
  - Audio filters: volume, equalizer, bass/treble, channelsplit, join, amix, sidechaincompress, etc.
  - Normalize, loudness (ebur128 filter)
- **File Formats**: Virtually all audio/video formats
- **Notes**: Universal media processor. Audio filtergraph is extremely powerful but more complex than SoX. Best for format conversion and codec work.

### 6. Sonic Annotator
- **URL**: https://vamp-plugins.org/sonic-annotator/
- **Python Native**: No
- **CLI/Headless**: Yes
- **Analysis Features**:
  - Runs any Vamp audio plugin
  - Beat tracking, tempo estimation
  - Note transcription, melody extraction
  - Onset detection, structural segmentation
  - Tonal analysis (chord, key)
- **Editing/Remixing**: None — analysis only
- **File Formats**: WAV, MP3, FLAC, AIFF, OGG
- **Notes**: Batch feature extraction tool. Outputs to RDF, CSV, JSON, or text. Essential for music IR pipelines.

### 7. Ecasound
- **URL**: https://ecasound.seul.org/
- **Python Native**: No (but has Python bindings via PyEcasound)
- **CLI/Headless**: Yes — `ecasound` binary, plus `ecatools` suite
- **Analysis Features**: Peak/RMS metering, level detection
- **Editing/Remixing**:
  - Multi-track recording and playback
  - Real-time effects processing
  - Automation (parameter curves)
  - Mix and render
  - Bus/group routing
- **File Formats**: WAV, MP3, FLAC, SND, many via libaudiofile
- **Notes**: Mature, full-featured DAW engine. Great for batch renders and automation scripts.

### 8. Rubber Band
- **URL**: https://breakfastquay.com/rubberband/
- **Python Native**: No (but has Python bindings)
- **CLI/Headless**: Yes — `rubberband` CLI
- **Analysis Features**: None (processing only)
- **Editing/Remixing**:
  - High-quality time-stretching
  - Pitch-shifting (with formant preservation)
- **File Formats**: WAV, MP3, FLAC, others
- **Notes**: Industry-quality time-stretch algorithm. Used by many DAWs as a library. Also available as VAMP plugin.

### 9. BWF MetaEdit (CLI)
- **URL**: https://mediaarea.net/BWFMetaEdit
- **Python Native**: No
- **CLI/Headless**: Yes — `bwfmetaedit` command
- **Analysis Features**: None (metadata only)
- **Editing/Remixing**:
  - Inject/edit BEXT chunk (Broadcast Wave) metadata
  - iXML metadata
  - Validate against standards
- **File Formats**: WAV (BWF)
- **Notes**: Professional broadcast audio metadata. Essential for archiving and sample libraries.

---

## Full DAWs with Automation (High-End Options)

### 10. Ardour
- **URL**: https://ardour.org/
- **Python Native**: Via Lua scripting (primary), Python via Lua bridge possible
- **CLI/Headless**: Yes
  - `ardour6-lua`: interactive Lua interpreter + script runner
  - `luasession`: standalone tool to access Ardour sessions headlessly
  - Can run without X server for CI/automation
- **Analysis Features**: Built-in meters (peak, RMS), spectrum analyzer (plugin)
- **Editing/Remixing**:
  - Full non-destructive editing
  - Multi-track audio/MIDI
  - Unlimited undo/redo
  - Unlimited audio buses
  - Automation curves (sample-accurate)
  - LV2/VST2/VST3 plugin support
  - Mix and render entire sessions
- **File Formats**: WAV, MP3, FLAC, AIFF, OGG, BWF, and many via libsndfile
- **Notes**: The most capable open-source DAW for automation. Can write Lua scripts to create sessions, import tracks, apply plugins, and render — fully unattended.

### 11. REAPER (via Wine)
- **URL**: https://www.reaper.fm/
- **Python Native**: No native, but has ReaScript (Python/EEL/Lua)
- **CLI/Headless**: Yes (via Wine on Linux)
  - `reaper.exe -batchprojectRender project.RPP`
  - command-line project loading and rendering
- **Analysis Features**: Built-in spectrum analysis, loudness metering (ReaPlugs)
- **Editing/Remixing**:
  - Full DAW (non-destructive)
  - Multi-track, MIDI, automation
  - VST2/VST3 support (native Windows, runs via Wine)
  - JSFX (native effects)
- **File Formats**: Virtually all audio formats via project media items
- **Notes**: Extremely scriptable and lightweight. Runs well under Wine. Commercial license but very affordable. Proven for batch rendering and automated workflows.

### 12. Carla
- **URL**: https://carla.readthedocs.io/
- **Python Native**: No
- **CLI/Headless**: Yes — `carla` with `--nogui`, `--jack`, etc.
  - Can load plugin racks from command line
  - OSC and MIDI control for automation
- **Analysis Features**: Via hosted plugins (meters, analyzers)
- **Editing/Remixing**:
  - Plugin host (VST2, VST3, LV2, AU, SFZ, SF2)
  - Modular signal routing (patchbay mode)
  - Rack mode (FX chains)
  - Transport control
- **File Formats**: Hosts plugins; uses JACK/Audio for audio IO
- **Notes**: Powerful plugin host/sandbox. Great for testing plugin chains or building custom DSP workflows headlessly.

---

## Tool Comparison Matrix

| Tool              | Python | CLI/Headless | Audio Analysis | Audio Editing | Formats    | Maturity |
|-------------------|--------|-------------|---------------|--------------|------------|----------|
| DawDreamer        | Yes    | Yes         | Strong        | Full DAW     | Broad      | New      |
| librosa           | Yes    | Scripts     | Excellent     | None         | Broad      | Mature   |
| PyDub             | Yes    | Scripts     | Basic         | Good         | Broad      | Mature   |
| SoX               | No     | Yes         | Good          | Very Good    | 30+        | Ancient  |
| FFmpeg            | No     | Yes         | Good          | Good         | Universal  | Ancient  |
| Sonic Annotator   | No     | Yes         | Excellent     | None         | Broad      | Mature   |
| Ecasound          | Maybe  | Yes         | Basic         | Full DAW     | Broad      | Mature   |
| Rubber Band       | No     | Yes         | No            | Time/pitch   | Broad      | Mature   |
| BWF MetaEdit      | No     | Yes         | No            | Metadata     | WAV/BWF    | Mature   |
| Ardour            | Lua    | Yes         | Basic         | Full DAW     | Broad      | Mature   |
| REAPER (Wine)     | ReaScript | Yes     | Plugin-based  | Full DAW     | Universal  | Mature   |
| Carla             | No     | Yes         | Via plugins   | Host         | Plugin I/O | Mature   |

---

## Recommendations for Hermes Skill Integration

### Tier 1: Core CLI Tools (Shell-Script Wrappers)
These should be primary Hermes skills because they're universally available (apt/yum/pacman), fast, and scriptable:
- **SoX** — for simple edits, format conversion, batch processing, effects
- **FFmpeg** — for codec work, complex filtering, transcoding pipelines
- **Rubber Band** — for high-quality time-stretch/pitch-shift
- **Sonic Annotator** — for feature extraction (beat, melody, chords) from many files
- **BWF MetaEdit** — for professional sample library metadata management

### Tier 2: Python Libraries (Python-Skill Wrappers)
For more sophisticated analysis and editing:
- **librosa** — feature extraction, beat tracking, music analysis
- **PyDub** — simple mixing, concatenation, format conversion
- **DawDreamer** — full DAW automation in Python, VST hosting, multi-track rendering

### Tier 3: Full DAW Automation (Advanced Skills)
For complex project-based workflows:
- **Ardour** — Lua scripting (or Python via luainterpreter); can run fully headless; render entire sessions
- **REAPER + Wine** — ReaScript (Python); excellent command-line batch render; proven in production

---

## Example Workflow Ideas

1. **Sample Analysis Pipeline** — librosa + Sonic Annotator → extract BPM, key, spectral features, save to JSON for a sample library
2. **Batch Remix** — PyDub/DawDreamer → time-align multiple stems, apply effects chain, render mashup
3. **Format Migration** — FFmpeg + SoX — convert legacy sample libraries to modern codecs, normalize, tag with BWF
4. **DAW Rendering** — Ardour/REAPER CLI — render stems/mixes from template projects headlessly on a server
5. **DSP Experimentation** — DawDreamer + Python — test effect chains, generate training data for ML models

---

## Installation Notes (Debian/Ubuntu)

```bash
# Core CLI tools
sudo apt install sox ffmpeg rubberband-cli

# Python libraries
pip install librosa pydub dawdreamer

# Sonic Annotator + Vamp plugins
sudo apt install sonic-annotator vamp-examples

# BWF MetaEdit
sudo apt install bwfmetaedit  # or from upstream for latest

# Ardour (if not in repos)
# Download from ardour.org

# Ecasound (optional)
sudo apt install ecasound

# Carla (optional)
sudo apt install carla
```

---

## Next Steps for Skill Development

1. **Create wrapper skills** for SoX, FFmpeg, Sonic Annotator that provide Hermes-friendly interfaces
2. **Build a `sample_analyzer` skill** that orchestrates librosa + SoX to extract comprehensive metadata from audio files
3. **Build a `batch_processor` skill** that applies effects/normalization/conversion to directories of samples
4. **Build a `daw_renderer` skill** that drives Ardour or REAPER headlessly to render projects
5. **Create a `vst_testbench` skill** using Carla to test plugin chains on sample material
6. **Create a `sample_library` skill** that organizes, tags, and catalogs sample collections
