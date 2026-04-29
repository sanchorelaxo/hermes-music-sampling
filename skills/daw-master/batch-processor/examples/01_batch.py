"""
Batch-Processor skill — apply transformation pipelines to directories of audio files.

Wraps all other daw-master skills (sox-engine, ffmpeg-audio, rubber-band-engine,
dawdreamer) and applies them to directory trees with parallel execution.

Quick check:

  python -c "import daw_master.batch_processor; print('OK')"

Example: process all WAV files in samples/ with normalize + trim
"""

from daw_master.batch_processor import process_directory

# Process a directory recursively
stats = process_directory(
    input_dir="samples/",
    output_dir="processed/",
    pipeline=[
        {"op": "normalize", "peak": -0.1},
        {"op": "trim", "start": 0, "length": 30}
    ],
    engine="sox",
    pattern="**/*.wav",
    overwrite=False,
    max_workers=4,
    manifest_path="manifest.json"
)

print(f"Processed: {stats['processed']}, Skipped: {stats['skipped']}, Failed: {stats['failed']}")
