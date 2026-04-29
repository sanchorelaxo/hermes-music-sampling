"""
Metadata Manager — audio file tagging and metadata extraction.

Wraps BWF MetaEdit (bwfmetaedit) CLI for BWF/BEXT/iXML operations,
and supports basic ID3 tagging for MP3 via mutagen.

Quick start:

  from daw_master.metadata import write_bwf, read_bwf, tag_mp3

  # Write Broadcast Wave metadata
  write_bwf("sample.wav", description=" dialogue", originator="Hermes")

  # Read BEXT chunk
  info = read_bwf("sample.wav")
  print(info)

  # Tag MP3
  tag_mp3("track.mp3", artist="Hermes", title="Test")
"""

from .pipeline import write_bwf, read_bwf, update_bwf, tag_mp3, extract_metadata

__all__ = ['write_bwf', 'read_bwf', 'update_bwf', 'tag_mp3', 'extract_metadata']
