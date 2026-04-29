"""
Metadata Manager — BWF tagging and ID3 operations.

Demonstrates writing broadcast wave metadata and reading tags.
"""

from pathlib import Path
import sys

# Ensure we can import from skills.metadata
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from metadata import write_bwf, read_bwf, tag_mp3, extract_metadata

# Example 1 — Write BWF metadata to a WAV file
sample_wav = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.wav"
if sample_wav.exists():
    result = write_bwf(
        str(sample_wav),
        description="Test sample — processed via Hermes",
        originator="Hermes Agent",
        originator_reference="HERM-2025-001",
        date="2025-04-29",
        coding_history="REC/DATE=2025-04-29"
    )
    print("Write BWF:", result)

    # Read it back
    info = read_bwf(str(sample_wav))
    print("Read BWF:", info.get("metadata", {}))
else:
    print(f"Sample not found: {sample_wav}")

# Example 2 — Tag an MP3 file
sample_mp3 = Path(__file__).parent.parent / "tests" / "fixtures" / "sample.mp3"
if sample_mp3.exists():
    result = tag_mp3(
        str(sample_mp3),
        title="Example Track",
        artist="Hermes Agent",
        album="Hermes Music Sampling",
        tracknumber="1",
        genre="Electronic",
        date="2025"
    )
    print("Tag MP3:", result)
else:
    print(f"Sample MP3 not found: {sample_mp3}")

print("Metadata examples complete")
