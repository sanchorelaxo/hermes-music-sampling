"""Mix rendering: build and run ffmpeg acrossfade mixes from a list of files.

Port of cli-anything-mixxx exporter, with fixes:
- Handles the single-file case (no acrossfade filter needed).
- Builds a valid filter_complex even when align_bpm is off.
"""
import os
import shutil
import subprocess

try:
    from typing import List, Optional, Tuple
except ImportError:  # pragma: no cover
    pass


def _which(cmd):
    return shutil.which(cmd)


def _safe_atempo_chain(factor):
    """Return an atempo filter expression for any positive factor.

    atempo supports 0.5-2.0 per filter; chain filters for out-of-range factors.
    """
    if factor <= 0:
        return None
    parts = []
    remaining = factor
    while remaining > 2.0:
        parts.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        parts.append("atempo=0.5")
        remaining *= 2.0
    parts.append(f"atempo={remaining:.6f}")
    return ",".join(parts)


def build_ffmpeg_mix_command(
    files,
    out,
    crossfade=5.0,
    bpms=None,
    align_bpm=False,
    codec="libmp3lame",
):
    """Build (cmd, filter_complex) for an acrossfaded mix of `files`.

    If align_bpm is True and bpms provided, atempo-aligns each input to the
    first track's BPM. Handles single-input case (returns cmd without a
    filter_complex). Does not execute ffmpeg.
    """
    ffmpeg = _which("ffmpeg") or "ffmpeg"
    if not files:
        raise ValueError("no input files")

    cmd = [ffmpeg]
    for f in files:
        cmd += ["-i", f]

    labels = [f"[{i}:a]" for i in range(len(files))]
    filter_parts = []
    processed_labels = []

    # Optional BPM alignment via atempo per input
    if align_bpm and bpms and len(bpms) == len(files) and bpms[0]:
        target = bpms[0]
        for i, b in enumerate(bpms):
            lbl_in = labels[i]
            if b and b > 0:
                factor = target / b
                atempo_expr = _safe_atempo_chain(factor)
                if atempo_expr:
                    out_lbl = f"[a{i}]"
                    filter_parts.append(f"{lbl_in}{atempo_expr}{out_lbl}")
                    processed_labels.append(out_lbl)
                else:
                    processed_labels.append(lbl_in)
            else:
                processed_labels.append(lbl_in)
    else:
        processed_labels = labels

    # Single input: no crossfade possible. Map without filtergraph syntax.
    if len(processed_labels) < 2:
        final_label = "0:a"
        filter_complex = None
        cmd += ["-map", final_label, "-c:a", codec, "-y", out]
        return cmd, filter_complex

    # Chain acrossfades: [mix1], [mix2], ...
    cur_label = None
    idx = 0
    while idx < len(processed_labels) - 1:
        left = cur_label if cur_label else processed_labels[idx]
        right = processed_labels[idx + 1]
        out_label = f"[mix{idx + 1}]"
        filter_parts.append(
            f"{left}{right}acrossfade=d={crossfade}:c1=tri:c2=tri{out_label}"
        )
        cur_label = out_label
        idx += 1

    filter_complex = ";".join(filter_parts)
    final_label = cur_label if cur_label else processed_labels[0]
    cmd += ["-filter_complex", filter_complex, "-map", final_label, "-c:a", codec, "-y", out]
    return cmd, filter_complex


def create_mix_from_track_files(track_files, out, crossfade=5.0, align_bpm=False, bpms=None, codec="libmp3lame"):
    """Render a mix from a list of track files. Returns {success, message}."""
    existing = [f for f in track_files if f and os.path.exists(f)]
    if not existing:
        return {"success": False, "message": "no existing track files provided"}
    try:
        cmd, _ = build_ffmpeg_mix_command(
            existing, out, crossfade, bpms=bpms, align_bpm=align_bpm, codec=codec
        )
    except ValueError as e:
        return {"success": False, "message": str(e)}
    try:
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        return {"success": True, "message": proc.stdout, "out": out}
    except subprocess.CalledProcessError as e:
        return {"success": False, "message": e.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "ffmpeg timed out"}


def create_mix_from_playlist(playlist_id, out, crossfade=5.0, align_bpm=False, codec="libmp3lame"):
    """Render a mix from a Mixxx playlist by id. Returns {success, message, out}."""
    from . import playlists as pl

    tracks = pl.get_playlist_tracks(playlist_id)
    files = [t["file"] for t in tracks if t.get("file")]
    bpms = [t.get("bpm") for t in tracks if t.get("file")]
    return create_mix_from_track_files(files, out, crossfade, align_bpm=align_bpm, bpms=bpms, codec=codec)


__all__ = [
    "build_ffmpeg_mix_command",
    "create_mix_from_track_files",
    "create_mix_from_playlist",
]
