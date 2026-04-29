"""
Mastering Engineer — loudness optimization and quality control for streaming platforms.

Exposes: analyze_audio, qc_audio, master_audio, master_with_reference, fix_dynamic_track, master_album
"""

from .pipeline import (
    analyze_audio,
    qc_audio,
    master_audio,
    master_with_reference,
    fix_dynamic_track,
    master_album,
)

__all__ = [
    'analyze_audio',
    'qc_audio',
    'master_audio',
    'master_with_reference',
    'fix_dynamic_track',
    'master_album',
]
