"""
Metadata Manager — audio file metadata operations.

BWF MetaEdit wrapper for Broadcast Wave Format, iXML, and ID3.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Any
import re

# Try import mutagen for ID3 handling; optional dependency
try:
    from mutagen.id3 import (ID3, ID3NoHeaderError, TIT2, TPE1, TALB, TRCK,
                              TCON, TDRC, COMM, TCOM, TENC, TCOP, TXXX)
    from mutagen.mp3 import MP3
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

# BWF MetaEdit CLI availability check
try:
    subprocess.run(['bwfmetaedit', '--version'], capture_output=True, timeout=5)
    BWFMETAEDIT_AVAILABLE = True
except (FileNotFoundError, subprocess.TimeoutExpired):
    BWFMETAEDIT_AVAILABLE = False


def _check_bwfmetaedit():
    if not BWFMETAEDIT_AVAILABLE:
        raise RuntimeError(
            "bwfmetaedit is not installed or not in PATH.\n"
            "Install with:\n"
            "  sudo apt install bwfmetaedit      # Debian/Ubuntu\n"
            "  brew install bwfmetaedit          # macOS (via brew)\n"
            "  sudo dnf install bwfmetaedit      # Fedora\n"
        )


def write_bwf(
    filepath: str,
    description: Optional[str] = None,
    originator: Optional[str] = None,
    originator_reference: Optional[str] = None,
    time_reference: Optional[int] = None,
    date: Optional[str] = None,
    **extra_fields
) -> Dict[str, Any]:
    """
    Write or update BWF/BEXT metadata on a WAV file using bwfmetaedit.

    Parameters
    ----------
    filepath : str
        Path to WAV file (must be Broadcast Wave or regular WAV; will be
        converted to BWF if needed).
    description : str, optional
        BEXT `description` (often used for take/comment).
    originator : str, optional
        BEXT `originator` — who produced the file.
    originator_reference : str, optional
        BEXT `originatorReference` — unique ID from originator.
    time_reference : int, optional
        BEXT `timeReference` — sample offset since midnight (SMPTE).
    date : str, optional
        BEXT `date` — YYYY-MM-DD or full timestamp.
    **extra_fields
        Any other BEXT chunk key/value pairs. Use underscores for hyphens:
        `coding_history="..."`, `umid="..."`.

    Returns
    -------
    dict
        {success, file, updated: [field_names]}
    """
    p = Path(filepath).resolve()
    if not p.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    if not BWFMETAEDIT_AVAILABLE:
        return {"success": False, "error": "bwfmetaedit not installed"}

    # Build arguments — map to bwfmetaedit's exact flag names (case-sensitive)
    args = ['bwfmetaedit', str(p)]
    updated_fields = []   # field names for return value
    if description is not None:
        args.append(f"--Description={description}")
        updated_fields.append("DESCRIPTION")
    if originator is not None:
        args.append(f"--Originator={originator}")
        updated_fields.append("ORIGINATOR")
    if originator_reference is not None:
        args.append(f"--OriginatorReference={originator_reference}")
        updated_fields.append("ORIGINATOR_REFERENCE")
    if time_reference is not None:
        args.append(f"--Timereference={time_reference}")
        updated_fields.append("TIME_REFERENCE")
    if date is not None:
        args.append(f"--OriginationDate={date}")
        updated_fields.append("ORIGINATION_DATE")
    for key, val in extra_fields.items():
        # Convert snake_case to CamelCase flag (e.g., coding_history -> --CodingHistory=)
        flag = f"--{key.replace('_', ' ').title().replace(' ', '')}={val}"
        args.append(flag)
        # Store field name in uppercase with underscores for consistency
        field_name = key.upper()
        updated_fields.append(field_name)

    if not updated_fields:
        return {"success": False, "error": "No metadata fields provided"}

    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"success": True, "file": str(p), "updated": updated_fields}
        else:
            return {"success": False, "error": result.stderr.strip() or result.stdout.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"bwfmetaedit timed out after 30s"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_bwf(filepath: str) -> Dict[str, Any]:
    """
    Read BWF/BEXT/iXML metadata from an audio file using bwfmetaedit.

    Uses --out-xml and parses the XML output (BWF MetaEdit v26+).
    """
    p = Path(filepath).resolve()
    if not p.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    if not BWFMETAEDIT_AVAILABLE:
        return {"success": False, "error": "bwfmetaedit not installed"}

    try:
        result = subprocess.run(
            ['bwfmetaedit', '--out-xml=-', str(p)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            # Maybe unsupported format; try mutagen for MP3
            if p.suffix.lower() == '.mp3' and MUTAGEN_AVAILABLE:
                return _read_id3(str(p))
            return {"success": False, "error": result.stderr.strip() or result.stdout.strip()}

        # Parse XML output — BWF MetaEdit v26+ outputs XML to stdout with --out-xml=-
        import xml.etree.ElementTree as ET
        root = ET.fromstring(result.stdout)
        metadata = {}

        # BEXT fields are under <Core> in the output
        core = root.find('.//Core')
        if core is not None:
            for child in core:
                # Convert CamelCase XML tag to SNAKE_UPPER (e.g. OriginatorReference → ORIGINATOR_REFERENCE)
                tag = child.tag
                if tag and child.text:
                    # Transform CamelCase to SNAKE_UPPER
                    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', tag)
                    key = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
                    metadata[key] = child.text.strip()
                    # Aliases for compatibility: DATE → ORIGINATION_DATE
                    if key == 'ORIGINATION_DATE':
                        metadata['DATE'] = child.text.strip()

        # Also try to capture any INFO chunks if present under <bext> or <INFO>
        # (future extensions can be added here)
        return {"success": True, "file": str(p), "metadata": metadata}

    except ET.ParseError as e:
        return {"success": False, "error": f"XML parse error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_bwf(filepath: str, updates: Dict[str, str]) -> Dict[str, Any]:
    """
    Update multiple BWF fields at once (convenience wrapper around write_bwf).

    Parameters
    ----------
    filepath : str
        Path to WAV file.
    updates : dict
        Mapping of field_name → value. Field names are case-insensitive
        and underscores are converted to hyphens (e.g. originator_reference
        becomes ORIGINATOR-REFERENCE in BEXT).

    Returns
    -------
    dict
        write_bwf result.
    """
    return write_bwf(filepath, **updates)


def tag_mp3(filepath: str, **tags) -> Dict[str, Any]:
    """
    Write ID3v2.4 tags to an MP3 file using mutagen.

    Supported tag keys: title, artist, album, tracknumber, genre, date,
    comment, composer, encoder, copyright, language, group, subtitle.
    Any other keys go into TXXX frames (user-defined).

    Parameters
    ----------
    filepath : str
        MP3 file path.
    **tags
        Arbitrary tag values. Use `TXXX:<desc>` for custom user text frames.

    Returns
    -------
    dict
        {success, file, written: [frame_ids]}
    """
    p = Path(filepath).resolve()
    if not p.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    if not MUTAGEN_AVAILABLE:
        return {"success": False, "error": "mutagen not installed (pip install mutagen)"}

    try:
        try:
            tags_obj = ID3(p)
        except ID3NoHeaderError:
            tags_obj = ID3()
            tags_obj.add_to(p)

        written = []
        for key, val in tags.items():
            key_lower = key.lower()
            if key_lower == 'title':
                tags_obj.add(TIT2(encoding=3, text=val))
                written.append('TIT2')
            elif key_lower == 'artist':
                tags_obj.add(TPE1(encoding=3, text=val))
                written.append('TPE1')
            elif key_lower == 'album':
                tags_obj.add(TALB(encoding=3, text=val))
                written.append('TALB')
            elif key_lower in ('track', 'tracknumber'):
                tags_obj.add(TRCK(encoding=3, text=str(val)))
                written.append('TRCK')
            elif key_lower == 'genre':
                tags_obj.add(TCON(encoding=3, text=val))
                written.append('TCON')
            elif key_lower in ('date', 'year'):
                tags_obj.add(TDRC(encoding=3, text=val))
                written.append('TDRC')
            elif key_lower == 'comment':
                tags_obj.add(COMM(encoding=3, lang='eng', desc='', text=val))
                written.append('COMM')
            elif key_lower == 'composer':
                tags_obj.add(TCOM(encoding=3, text=val))
                written.append('TCOM')
            elif key_lower == 'encoder':
                tags_obj.add(TENC(encoding=3, text=val))
                written.append('TENC')
            elif key_lower == 'copyright':
                tags_obj.add(TCOP(encoding=3, text=val))
                written.append('TCOP')
            elif key_lower.startswith('txxx:'):
                # Custom user text frame: TXXX:<description>
                _, desc = key_lower.split(':', 1)
                tags_obj.add(TXXX(encoding=3, desc=desc, text=val))
                written.append(f'TXXX:{desc}')
            else:
                # Unknown: store as TXXX with raw key as description
                tags_obj.add(TXXX(encoding=3, desc=key, text=val))
                written.append(f'TXXX:{key}')

        tags_obj.save(p, v2_version=4)
        return {"success": True, "file": str(p), "written": written}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_metadata(filepath: str) -> Dict[str, Any]:
    """
    Universal metadata extractor for audio files.
    Tries BWF MetaEdit first (for WAV/BWF), then mutagen (for MP3/others).

    Parameters
    ----------
    filepath : str
        Audio file path.

    Returns
    -------
    dict
        Unified metadata dict with `format` key indicating the source.
    """
    p = Path(filepath).resolve()
    if not p.exists():
        return {"success": False, "error": f"File not found: {filepath}"}

    # Try BWF first for WAV files
    if p.suffix.lower() in ('.wav', '.bwf'):
        res = read_bwf(str(p))
        if res.get("success"):
            return {"success": True, "file": str(p), "format": "BWF", **res.get("metadata", {})}

    # Fallback to mutagen for all types
    if MUTAGEN_AVAILABLE:
        try:
            audio = MP3(p, ID3=ID3)
            meta = {
                "success": True,
                "file": str(p),
                "format": "ID3" if p.suffix.lower() == '.mp3' else "mutagen",
                "duration": audio.info.length if hasattr(audio, 'info') else None,
            }
            if audio.tags:
                for frame in audio.tags.values():
                    frame_name = frame.FrameID
                    if hasattr(frame, 'text'):
                        meta[frame_name] = str(frame.text[0]) if frame.text else ''
            return meta
        except Exception:
            pass

    return {"success": False, "error": "Unable to read metadata; install bwfmetaedit or mutagen"}


def _read_id3(filepath: str) -> Dict[str, Any]:
    """Internal: read ID3 tags from MP3 via mutagen (fallback for bwfmetaedit)."""
    try:
        audio = MP3(filepath, ID3=ID3)
        meta = {}
        if audio.tags:
            for frame in audio.tags.values():
                if hasattr(frame, 'text'):
                    meta[frame.FrameID] = str(frame.text[0]) if frame.text else ''
        return {"success": True, "metadata": meta}
    except Exception as e:
        return {"success": False, "error": str(e)}
