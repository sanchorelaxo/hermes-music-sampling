---
name: daw-master:batch-processor
description: "Batch audio processor — apply daw-master pipelines to directories of files"
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["audio", "batch", "parallel", "orchestration", "pipeline"]
    related_skills: ["daw-master:sox-engine", "daw-master:ffmpeg-audio", "daw-master:dawdreamer", "daw-master:rubber-band-engine"]
---

# Batch Processor Skill

Orchestrates daw-master skill engines to process entire directories of audio files.

This skill provides the "batch" layer on top of individual transform skills, handling:
- Recursive file discovery with glob patterns (e.g., `**/*.wav`, `**/*.mp3`)
- Parallel processing via multiprocessing (configurable workers)
- Error aggregation and resumable manifests
- Mirroring directory structure from input to output

## Quick Start

```bash
# Check
python -c "import daw_master.batch_processor; print('OK')"
```

## Installation

No extra installation — it uses the installed daw-master skills. Ensure at least one engine is available:

```bash
# Recommended: install SoX (fast, always available)
sudo apt install sox

# Or for advanced processing
pip install dawdreamer
```

## Core API

```python
from daw_master.batch_processor import process_directory

# Process all WAV files under samples/ with a normalize + trim pipeline
stats = process_directory(
    input_dir="samples/",
    output_dir="processed/",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "trim", "start": 0, "length": 30}
    ],
    engine="sox",           # sox | ffmpeg | dawdreamer | rubberband
    pattern="**/*.wav",     # glob pattern relative to input_dir
    overwrite=False,        # skip existing outputs
    max_workers=4,          # parallel jobs (1 = serial)
    manifest_path="batch_manifest.json"  # optional per-file report
)

print(f"Processed {stats['processed']}/{stats['total']}, "
      f"skipped {stats['skipped']}, failed {stats['failed']}")
```

## Parameters

**`process_directory`**
- `input_dir` – directory tree to scan
- `output_dir` – where to write processed files (mirrors input structure)
- `pipeline` – list of op dicts, exactly as passed to the underlying transform skill
- `engine` – which daw-master engine to use. Choices:
  - `"sox"` or `"sox-engine"` — fastest, most portable
  - `"ffmpeg"` or `"ffmpeg-audio"` — codec support, EBU R128
  - `"dawdreamer"` — VST plugins, multi-track, high-quality effects
  - `"rubberband"` or `"rubberband-engine"` — pristine time-stretch & pitch-shift
- `pattern` – glob for which files to process; default `"**/*.wav"` matches recursively
- `dry_run` – if True, log what would happen without touching files
- `overwrite` – if False, skip files where output already exists
- `max_workers` – number of parallel processes; default 4. Increase for I/O-bound workloads on SSDs, decrease on HDDs
- `manifest_path` – write a JSON manifest recording per-file results and errors

**`process_file`** (lower-level): Process a single file; returns dict `{success, input, output, error?, skipped?}`.

## Return Value

Success summary:
```python
{
  "processed": 42,   # successfully written
  "skipped": 5,     # already existed when overwrite=False
  "failed": 2,      # errors encountered
  "total": 49,      # matched by glob
  "errors": [        # only present if failed > 0
    {"file": "path/to/bad.wav", "error": "..."},
    ...
  ]
}
```

If `manifest_path` is set, an additional JSON file is written with full per-file records.

## Examples

### Example 1 — Normalize all samples in a library

```python
from daw_master.batch_processor import process_directory

stats = process_directory(
    input_dir="~/sample-library/",
    output_dir="~/sample-library-normalized/",
    pipeline=[{"op": "normalize", "peak": -0.1}],
    engine="sox",
    pattern="**/*.wav",
    max_workers=8
)
print(f"Done: {stats}")
```

### Example 2 — Apply vintage VST chain to vocal stems

```python
from daw_master.batch_processor import process_directory

stats = process_directory(
    input_dir="stems/vocals_raw/",
    output_dir="stems/vocals_processed/",
    pipeline=[
        {"op": "load_vst", "path": "/usr/local/vst/ValhallaRoom.vst3"},
        {"op": "set_param", "plugin_idx": 0, "param": "RoomSize", "value": 0.7},
        {"op": "set_param", "plugin_idx": 0, "param": "Wet", "value": 0.4},
        {"op": "normalize"},
    ],
    engine="dawdreamer",
    pattern="**/*.wav",
    overwrite=False
)
```

### Example 3 — RPM analysis pipeline (filter → time-stretch → normalize)

```python
stats = process_directory(
    input_dir="raw_recordings/",
    output_dir="cleaned/",
    pipeline=[
        {"op": "highpass", "cutoff": 80},           # remove rumble
        {"op": "time_stretch", "factor": 1.0},      # placeholder — adjust per file after analysis
        {"op": "normalize", "peak": -0.5},
    ],
    engine="ffmpeg-audio",
    pattern="**/*.flac"
)
```

### Example 4 — Skip already-processed files with a manifest

```python
stats = process_directory(
    input_dir="samples/",
    output_dir="out/",
    pipeline=[{"op": "gain", "amount_db": 3}],
    engine="sox",
    manifest_path="out/manifest.json"
)

# Later: inspect which files succeeded/failed
import json
m = json.load(open("out/manifest.json"))
for rec in m["files"]:
    if not rec["success"]:
        print(f"FAILED: {rec['input']} → {rec.get('error')}")
```

## Dry-Run Mode

```python
stats = process_directory(
    input_dir="big_library/",
    output_dir="out/",
    pipeline=[{"op": "normalize"}],
    engine="sox",
    pattern="**/*.wav",
    dry_run=True  # prints plan, no files written
)
```

Output:
```
[DRY-RUN] Process 1247 files with engine 'sox'
  Input:  /path/big_library
  Output: /path/out
  Pattern: **/*.wav
  Pipeline: [
    {"op": "normalize", "peak": -0.1}
  ]
```

## Parallel vs Serial

- `max_workers=1` — serial (simpler debugging, predictable ordering)
- `max_workers=4` (default) — balanced parallelism
- `max_workers=multiprocessing.cpu_count()` — CPU-bound engines like dawdreamer

Parallel execution uses `concurrent.futures.ProcessPoolExecutor`. Each worker process gets its own engine instance, which is safe for SoX/FFmpeg/DawDreamer (all spawn external processes).

## Error Handling

Failed files are collected in the `errors` list; processing continues for all files. A non-zero `failed` count does not raise an exception — check `stats["failed"]` after the call. Per-file error messages include the underlying skill's error string.

To fail fast on first error, inspect immediately and raise:

```python
stats = process_directory(...)
if stats["failed"] > 0:
    raise RuntimeError(f"Batch failed: {stats['failed']} files had errors")
```

## Safety

- **No overwrites by default**: `overwrite=False` means already-existing outputs are skipped.
- **Read-only input**: The skill never modifies input files.
- **Directory creation**: `output_dir` and any subdirectories are created automatically.

## Hermes Integration

```
Use skill daw-master:batch-processor process_directory
  input_dir="samples/"
  output_dir="processed/"
  pipeline=[{"op": "normalize"}]
  engine="sox"
```

Or from Python:
```python
from daw_master.batch_processor import process_directory
process_directory(...)
```

## Chaining with Other Skills

This skill is the batch execution layer. Compose it upstream with analysis:

```python
# 1. Analyze directory to decide pipeline
from daw_master.audio_analyzer import extract_batch
features = extract_batch("samples/", output_format="json")

# 2. Build conditional pipeline per file
# (see example 4 in the docstring of pipeline.py for full pattern)

# 3. Apply to entire directory
process_directory(
    input_dir="samples/",
    output_dir="normalized/",
    pipeline=[{"op": "normalize"}],
    engine="sox"
)
```

## Notes

- DawDreamer uses significant RAM; limit `max_workers` to 1–2 when using the `dawdreamer` engine.
- SoX and FFmpeg are lightweight; higher worker counts (4–8) are fine.
- Manifest files are JSON; they can be loaded and re-fed to `process_directory` by setting `overwrite=False` to resume interrupted batches.
- Pipeline definitions are JSON-serializable; store them in `.json` files for reproducible workflows.
