---
name: metadata:bwf
description: "Broadcast Wave Format (BWF) and ID3 metadata manager — BEXT/iXML tagging"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "metadata", "bwf", "id3", "broadcast", "tagging"]
    related_skills: ["daw-master:sox-engine", "daw-master:audio-analyzer"]
---

# Metadata Manager Skill

Wrapper for BWF MetaEdit CLI plus mutagen-based ID3 tagging — professional audio metadata management.

Supports:
- **BWF/BEXT** chunks: DESCRIPTION, ORIGINATOR, TIME_REFERENCE, DATE, CODING_HISTORY
- **iXML** chunks (pass-through via bwfmetaedit)
- **ID3v2** for MP3 (via mutagen): TIT2, TPE1, TALB, TCON, TDRC, TXXX (custom)

## Quick Status

```bash
# Check availability
bwfmetaedit --version           # should print version

# BWF MetaEdit (required for WAV/BWF)
sudo apt install bwfmetaedit     # Debian/Ubuntu
brew install bwfmetaedit          # macOS
sudo dnf install bwfmetaedit      # Fedora

# Python mutagen (optional, for MP3 ID3)
pip install mutagen
```

## Installation Notes

BWF MetaEdit v26+ (2025) is the reference implementation from MediaArea.net.

**Ubuntu / Pop!_OS 24.04**: Download the `.deb` from [mediaarea.net/BWFMetaEdit/Download/Ubuntu](https://mediaarea.net/BWFMetaEdit/Download/Ubuntu) and install locally without sudo using:
```bash
ar x bwfmetaedit_*.deb
tar xf data.tar.zst
# Binary is in extracted/usr/bin/bwfmetaedit — add to PATH or symlink to ~/.local/bin
```

**Other distros**: Use your package manager (`apt`, `dnf`, `pacman`) or Flatpak/Snap.

## Core API

```python
from daw_master.metadata import write_bwf, read_bwf, tag_mp3, extract_metadata

# Write BWF metadata
result = write_bwf(
    "sample.wav",
    description="Take 1 — studio",
    originator="Hermes Studios",
    originator_reference="HS-2025-0042",
    date="2025-04-29",
    coding_history="REC/DATE=2025-04-29"
)

# Read BWF/iXML
info = read_bwf("sample.wav")
print(info.get("metadata", {}))
# {'DESCRIPTION': 'Take 1 — studio', 'ORIGINATOR': 'Hermes Studios', ...}

# Tag MP3
tag_mp3("track.mp3", title="Song", artist="Hermes", album="Debut", tracknumber="3")

# Universal extractor (auto-detects format)
meta = extract_metadata("sample.wav")  # returns BWF fields if present
```

## API Reference

### `write_bwf(filepath, **fields) → dict`

Write or update BEXT (Broadcast Wave) metadata on a WAV file.

Parameters
- `filepath` (str): WAV file path
- `description` (str, optional): BEXT description field (commonly used for take/comment)
- `originator` (str, optional): Who produced the file
- `originator_reference` (str, optional): Unique reference ID assigned by originator
- `time_reference` (int, optional): Sample frame count since midnight (SMPTE)
- `date` (str, optional): Recording date (YYYY-MM-DD or full timestamp)
- `**extra_fields` (dict): Any other BEXT chunks (e.g. `coding_history="..."`, `umid="..."`)

Return
- `{success: bool, file: str, updated: [field_names]}`

Notes: Creates BEXT chunk if the file is plain WAV (automatically converted to BWF by bwfmetaedit). Overwrites existing fields by default.

### `read_bwf(filepath) → dict`

Read BEXT/iXML metadata from an audio file.

Parameters
- `filepath` (str): Audio file

Return
- `{success: bool, file: str, metadata: {str: str}}`

Metadata keys are uppercase BEXT field names (DESCRIPTION, ORIGINATOR, DATE, etc.). If the file has iXML chunks they appear with an `iXML:` prefix.

### `update_bwf(filepath, updates: dict) → dict`

Update many BWF fields with a single dict mapping field names (case-insensitive; underscores auto-converted to hyphens).

### `tag_mp3(filepath, **tags) → dict`

Write ID3v2.4 tags to an MP3 file.

Supported keys (case-insensitive):
- `title`, `artist`, `album`, `tracknumber`, `genre`, `date`
- `comment`, `composer`, `encoder`, `copyright`
- `TXXX:<description>` form for custom user-text frames, e.g. `TXXX:LABEL="MyLabel"`

Return: `{success, file, written: [frame_ids]}`

Requires `mutagen` (`pip install mutagen`). If not available, returns error.

### `extract_metadata(filepath) → dict`

Universal extractor. Returns a dict with:
- `format`: `"BWF"`, `"ID3"` or `"mutagen"`
- all tag fields at top-level

If the file is WAV/BWF → read via bwfmetaedit; if MP3 → via mutagen. Returns `{success: False, error: str}` if neither backend is available.

## Examples

### Example 1 — Add catalog metadata to a sample library

```python
import os
from pathlib import Path
from daw_master.metadata import write_bwf

for wav in Path("samples/").rglob("*.wav"):
    stem = wav.stem
    write_bwf(
        str(wav),
        description=f"Hermes sample library — {stem}",
        originator="Hermes Agent",
        originator_reference=f"HERM-{stem.upper()}",
        date="2025-04-29",
        UMID="0x" + os.urandom(13).hex().upper()  # unique material identifier
    )
```

### Example 2 — Verify metadata across a directory

```python
from daw_master.metadata import read_bwf
import json

manifest = {}
for wav in Path("final/").glob("*.wav"):
    info = read_bwf(str(wav))
    meta = info.get("metadata", {})
    manifest[str(wav)] = {
        "description": meta.get("DESCRIPTION", ""),
        "originator": meta.get("ORIGINATOR", ""),
    }

json.dump(manifest, open("metadata_manifest.json", "w"), indent=2)
```

### Example 3 — Tag MP3 export

```python
from daw_master.metadata import tag_mp3

tag_mp3(
    "export/beat_01.mp3",
    title="Beat 01 — Drums Only",
    artist="Hermes Beats",
    album="Drum Pack Vol 1",
    tracknumber="1",
    genre="Hip-Hop",
    date="2025",
    TXXX_CUSTOM_ID="HERM-BEAT-001"  # custom frame
)
```

## Notes

- **BWF vs regular WAV**: Regular WAV files will gain a BEXT chunk on first `write_bwf` — this is normal and makes the file a Broadcast Wave.
- **Unicode**: BEXT fields are ASCII-safe; for UTF-8 content, prefer iXML or external JSON sidecar. bwfmetaedit supports UTF-8 in recent versions.
- **Time reference**: `time_reference` is samples since midnight — rarely needed manually.
- **MP3 support**: ID3v2.4 via mutagen; does not support ID3v1 (legacy).
- **iXML**: Use `extra_fields` to pass raw iXML blocks: `write_bwf("file.wav", ixml="<xml>...</xml>")`.
- **Validation**: `bwfmetaedit --verify file.wav` can check compliance; this skill does not call verify automatically.

## Hermes Integration

```
Use skill metadata:bwf write_bwf file="sample.wav" description="..." originator="..."
Use skill metadata:bwf tag_mp3 file="track.mp3" artist="Hermes" title="..."
```

## Dependencies

| Tool | Package | Purpose |
|------|---------|---------|
| bwfmetaedit | apt/dnf/brew | BWF BEXT/iXML read/write |
| mutagen | pip | MP3 ID3 tagging (optional but recommended) |
