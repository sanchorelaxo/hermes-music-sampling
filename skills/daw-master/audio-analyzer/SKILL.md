---
name: daw-master:audio-analyzer
version: 1.0.0
description: Advanced audio analysis and feature extraction using librosa with optional Vamp plugin support via sonic-annotator
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - audio
      - analysis
      - feature-extraction
      - librosa
      - vamp
      - statistics
    provides:
      - analyze
      - probe
      - extract_batch
    requires:
      - python
      - librosa
      - soundfile
      - numpy
    optional:
      - sonic-annotator
---

# daw-master:audio-analyzer

Comprehensive audio analysis skill for extracting musical features, spectral characteristics, and metadata from audio files. Integrates with the daw-master meta-skill pipeline.

## Capabilities

- **Feature extraction**: Tempo, key estimation, loudness, spectral features, MFCCs, harmonic/percussive separation
- **Batch processing**: Recursively analyze directories with progress tracking and CSV/JSON output
- **Vamp plugin support**: Optional sonic-annotator integration for advanced analysis (qM Tempotracker, NNLS Chroma, etc.)
- **Graceful degradation**: Works with librosa alone; uses sonic-annotator when available

## Operations

| Operation | Description | Parameters |
|-----------|-------------|------------|
| `analyze` | Extract comprehensive feature set from a single audio file | `file`, `features` (list, optional subset) |
| `probe` | Basic file metadata (duration, sample rate, channels, format) | `file` |
| `extract_batch` | Recursively analyze directory, write results to CSV/JSON | `directory`, `pattern`, `output_format`, `output_file` |

## Dependencies

**Required (Python)**:
```bash
pip install librosa soundfile numpy
```

**Optional (Vamp plugins)**:
```bash
sudo apt install sonic-annotator
# Install Vamp plugin packs:
#   qm-vamp-plugins: tempo tracking, chroma, onset detection
#   vamp-example-plugins: basic features
```

## Examples

```python
from skills.daw_master.audio_analyzer import analyze, probe, extract_batch

# Single file analysis
features = analyze("input.wav")
print(f"Tempo: {features['tempo']} BPM")
print(f"Key: {features['key']}")

# Batch processing
extract_batch(
    directory="./samples",
    pattern="*.wav",
    output_format="csv",
    output_file="features.csv"
)
```

## Output Format

`analyze()` returns a dictionary containing:

```json
{
  "duration": 180.5,
  "sample_rate": 44100,
  "channels": 2,
  "tempo": 128.0,
  "tempo_confidence": 0.85,
  "key": "C major",
  "key_confidence": 0.72,
  "loudness": -12.3,
  "spectral_centroid": 2450.0,
  "spectral_rolloff": 5800.0,
  "spectral_flatness": 0.15,
  "mfcc": [mean_vector, std_vector],
  "harmonic_ratio": 0.68,
  "percussive_ratio": 0.32,
  "onset_count": 240,
  "zero_crossing_rate": 0.08
}
```

## Integration with daw-master

All audio-analyzer operations are pipeable:

```python
# Chain with sox-engine for preprocessing
from skills.daw_master.sox_engine import trim, normalize
from skills.daw_master.audio_analyzer import analyze

# Normalize then analyze
normalize("raw.wav", "normalized.wav")
features = analyze("normalized.wav")
```

## Tips

- For accurate tempo/key: use high-quality, full-bandwidth audio (not MP3 128kbps)
- Batch mode: set `pattern="**/*.wav"` for recursive directory scanning
- Sonic-annotator features appear under `vamp_plugins` key in output
- Memory usage scales with file duration; process long files in chunks if needed