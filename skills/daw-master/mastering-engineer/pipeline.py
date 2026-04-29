"""
Mastering Engineer — audio mastering for streaming platforms using FFmpeg loudnorm
and audio-analyzer verification. No external Python deps required.
"""

import os
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np

import sys
import types
import importlib.util
from pathlib import Path as _Path

_THIS_FILE = _Path(__file__).resolve()
_DAW_MASTER_DIR = _THIS_FILE.parents[1]  # skills/daw-master
_SKILLS_PARENT = _DAW_MASTER_DIR.parent      # skills/

def _load_skill(skill_dir_name: str, func_name: str):
    """Load a function from a skill's pipeline.py, setting up the skills namespace."""
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [str(_SKILLS_PARENT)]
        sys.modules["skills"] = skills_pkg
    parent_pkg_name = f"skills.{skill_dir_name}"
    if parent_pkg_name not in sys.modules:
        parent_pkg = types.ModuleType(parent_pkg_name)
        parent_pkg.__path__ = [str(_DAW_MASTER_DIR / skill_dir_name)]
        parent_pkg.__package__ = "skills"
        sys.modules[parent_pkg_name] = parent_pkg
    module_path = _DAW_MASTER_DIR / skill_dir_name / "pipeline.py"
    full_name = f"skills.{skill_dir_name}.pipeline"
    spec = importlib.util.spec_from_file_location(full_name, module_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, func_name)

# Load granular skill functions
ffmpeg_transform = _load_skill('ffmpeg-audio', 'transform')
ffmpeg_analyze   = _load_skill('ffmpeg-audio', 'analyze')
ffmpeg_probe     = _load_skill('ffmpeg-audio', 'probe')

audio_analyze    = _load_skill('audio-analyzer', 'analyze')
audio_probe      = _load_skill('audio-analyzer', 'probe')


# ============================
# Genre Presets
# ============================

# Format: { genre: { "target_lufs": float, "highmid_cut_db": float, "eq": [ {...}, ... ] } }

GENRE_PRESETS = {
    "default": {
        "target_lufs": -14.0,
        "true_peak_dbtp": -1.0,
        "lra": 7.0,
        "highmid_cut_db": -2.0,
        "highmid_freq": 3500,
        "eq": [
            # Optional additional EQ can be added here
        ],
    },
    "hip-hop": {
        "target_lufs": -12.0,
        "highmid_cut_db": -2.5,
        "highmid_freq": 4000,
        "sub_boost_db": 2.0,
        "sub_boost_freq": 60,
        "vocal_pres_freq": 3000,
    },
    "rock": {
        "target_lufs": -13.0,
        "highmid_cut_db": -2.0,
        "highmid_freq": 3500,
        "guitar_pres_db": 1.0,
        "guitar_pres_freq": 2000,
    },
    "metal": {
        "target_lufs": -14.0,
        "highmid_cut_db": -2.5,
        "highmid_freq": 4000,
        "low_tighten_db": -1.5,  # tighten low end
        "low_tighten_freq": 120,
    },
    "edm": {
        "target_lufs": -10.0,
        "highmid_cut_db": -1.5,
        "highmid_freq": 5000,
        "sub_boost_db": 2.0,
        "sub_boost_freq": 50,
    },
    "ambient": {
        "target_lufs": -16.0,
        "highmid_cut_db": -1.0,
        "highmid_freq": 5000,
        "dynamic_preserve": True,
    },
    "jazz": {
        "target_lufs": -17.0,
        "highmid_cut_db": -1.0,
        "highmid_freq": 4000,
        "minimal_processing": True,
    },
    "folk": {
        "target_lufs": -15.0,
        "highmid_cut_db": -1.5,
        "highmid_freq": 4000,
        "warm_boost_db": 1.0,
        "warm_boost_freq": 200,
    },
    "country": {
        "target_lufs": -13.5,
        "highmid_cut_db": -1.5,
        "highmid_freq": 3500,
        "vocal_clarity_db": 1.5,
    },
    "classical": {
        "target_lufs": -18.0,
        "highmid_cut_db": -0.5,
        "highmid_freq": 6000,
        "minimal_processing": True,
    },
    "pop": {
        "target_lufs": -14.0,
        "highmid_cut_db": -2.0,
        "highmid_freq": 4000,
    },
    "reggae": {
        "target_lufs": -14.0,
        "highmid_cut_db": -1.5,
        "highmid_freq": 4000,
        "bass_presence_db": 1.5,
        "bass_presence_freq": 120,
    },
    "latin": {
        "target_lufs": -13.0,
        "highmid_cut_db": -1.5,
        "highmid_freq": 5000,
        "perc_cut_db": -1.0,
    },
    "soundtrack": {
        "target_lufs": -14.0,
        "highmid_cut_db": -1.5,
        "highmid_freq": 4000,
        "orchestral_warmth_db": 1.0,
        "orchestral_warmth_freq": 300,
    },
}

# Quality thresholds
MAX_LUFS_DEVIATION = 0.5  # ±0.5 dB target
MAX_TRUE_PEAK_DBTP = -1.0
MAX_ALBUM_LUFS_RANGE = 1.0  # max difference between loudest and quietest track


# ============================
# Helpers
# ============================

def _db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)

def _linear_to_db(lin: float) -> float:
    import numpy as np
    return 20 * np.log10(lin + 1e-12)


def _estimate_lufs_ffmpeg(wav_path: str) -> Optional[float]:
    """
    Use FFmpeg loudnorm filter to measure integrated loudness (I) in LUFS.
    Returns float or None on failure.
    """
    cmd = [
        'ffmpeg', '-y', '-i', wav_path,
        '-af', 'loudnorm=I=-14:TP=-1:LRA=7:print_format=json',
        '-f', 'null', '-'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        # Parse JSON from stderr
        for line in result.stderr.splitlines():
            try:
                data = json.loads(line)
                if 'input_i' in data:
                    return float(data['input_i'])
            except json.JSONDecodeError:
                continue
    except Exception as e:
        print(f"Warning: LUFS measurement failed for {wav_path}: {e}")
    return None


def _get_track_lufs(track_path: str) -> float:
    """Get LUFS via ffmpeg measurement, fallback to audio-analyzer RMS approximation."""
    lufs = _estimate_lufs_ffmpeg(track_path)
    if lufs is None:
        # Fallback: use audio-analyzer loudness (RMS dB) and convert to LUFS roughly
        # RMS loudness is typically ~–18 dBFS for –23 LUFS; approximate offset
        info = audio_analyze(track_path, features=['loudness'])
        rms_db = info.get('loudness', -20)
        # Rough conversion: LUFS ≈ RMS + 3 (heuristic; varies by content)
        lufs = rms_db + 3.0
    return lufs


def _build_eq_filters(genre: str, extra_cut: Optional[float] = None) -> List[Dict]:
    """
    Build EQ filter chain from genre preset.
    """
    preset = GENRE_PRESETS.get(genre, GENRE_PRESETS['default'])
    filters: List[Dict] = []

    # High-mid cut (shelf)
    cut_db = extra_cut if extra_cut is not None else preset.get('highmid_cut_db', -2.0)
    cut_freq = preset.get('highmid_freq', 3500)
    if cut_db < 0:
        filters.append({"op": "highshelve", "frequency": cut_freq, "gain": cut_db})

    # Sub-bass boost or low-end shaping
    if 'sub_boost_db' in preset:
        freq = preset.get('sub_boost_freq', 60)
        gain = preset['sub_boost_db']
        filters.append({"op": "lowshelve", "frequency": freq, "gain": gain})

    # Warmth boost (low-mid shelf)
    if 'warm_boost_db' in preset:
        freq = preset.get('warm_boost_freq', 200)
        filters.append({"op": "lowshelve", "frequency": freq, "gain": preset['warm_boost_db']})

    # Guitar presence
    if 'guitar_pres_db' in preset:
        freq = preset.get('guitar_pres_freq', 2000)
        width = 1.2
        filters.append({"op": "equalizer", "frequency": freq, "width": str(width), "gain": preset['guitar_pres_db']})

    # Vocal clarity presence
    if 'vocal_clarity_db' in preset:
        freq = preset.get('vocal_pres_freq', 3000)
        filters.append({"op": "equalizer", "frequency": freq, "width": "1.0", "gain": preset['vocal_clarity_db']})

    # Low-end tighten (highpass-style via low shelf cut)
    if 'low_tighten_db' in preset:
        freq = preset.get('low_tighten_freq', 120)
        filters.append({"op": "lowshelve", "frequency": freq, "gain": preset['low_tighten_db']})

    return filters


def _build_loudnorm_pipeline(
    target_lufs: float,
    true_peak_dbtp: float = -1.0,
    lra: float = 7.0,
) -> List[Dict]:
    """
    Create FFmpeg loudnorm filter parameters.
    """
    return [
        {
            "op": "loudnorm",
            "i": target_lufs,
            "tp": true_peak_dbtp,
            "lra": lra,
        }
    ]


# ============================
# Public API
# ============================

def analyze_audio(album_path: str, subfolder: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze all WAV files in album_path or a specific subfolder.
    """
    base = Path(album_path)
    if subfolder:
        search_dir = base / subfolder
    else:
        search_dir = base

    if not search_dir.exists():
        return {"success": False, "error": f"Directory not found: {search_dir}"}

    wav_files = sorted(search_dir.glob("*.wav"))
    if not wav_files:
        return {"success": False, "error": f"No WAV files in {search_dir}"}

    tracks = []
    lufs_values = []

    for wav in wav_files:
        lufs = _get_track_lufs(str(wav))
        info = audio_probe(str(wav))
        peak = info.get('peak_db', 0)
        tracks.append({
            "filename": wav.name,
            "path": str(wav),
            "loudness_lufs": round(lufs, 2),
            "peak_db": round(peak, 2),
            "duration": info.get('duration', 0),
            "sample_rate": info.get('sample_rate', 0),
            "channels": info.get('channels', 0),
        })
        lufs_values.append(lufs)

    album_avg = float(np.mean(lufs_values)) if lufs_values else None
    album_range = float(np.ptp(lufs_values)) if len(lufs_values) > 1 else 0.0

    return {
        "success": True,
        "tracks": tracks,
        "album_lufs_avg": round(album_avg, 2) if album_avg is not None else None,
        "album_lufs_range": round(album_range, 2),
        "directory": str(search_dir),
    }


def qc_audio(album_path: str, subfolder: Optional[str] = None) -> Dict[str, Any]:
    """
    Run technical QC checks.
    """
    base = Path(album_path)
    search_dir = base / (subfolder or "")
    if not search_dir.exists():
        return {"success": False, "error": f"Directory not found: {search_dir}"}

    wav_files = sorted(search_dir.glob("*.wav"))
    checks = []
    issues: List[Dict] = []

    for wav in wav_files:
        track_checks = {"filename": wav.name, "passed": True, "notes": []}

        # 1. Format validation
        info = audio_probe(str(wav))
        if not info.get('format'):
            track_checks["passed"] = False
            track_checks["notes"].append("Invalid WAV format")
            issues.append({"file": wav.name, "issue": "invalid_format"})
            continue

        # 2. Clipping (peak > 0 dB)
        peak = info.get('peak_db', -100)
        if peak >= 0.0:
            track_checks["passed"] = False
            track_checks["notes"].append(f"Peak {peak:.2f} dB (clipping)")
            issues.append({"file": wav.name, "issue": "clipping", "peak_db": peak})

        # 3. Mono compatibility (quick channel check)
        if info.get('channels', 2) > 2:
            track_checks["notes"].append("More than 2 channels — check for phase issues")

        # 4. Silence check (leading/trailing)
        # Use ffprobe to detect very quiet start/end; skip detailed for performance

        # 5. Spectral balance (basic: no total drop)
        # More advanced would require audio-analyzer full features

        track_checks["peaks"] = peak
        checks.append(track_checks)

    return {
        "success": True,
        "directory": str(search_dir),
        "tracks_checked": len(checks),
        "passed": all(c["passed"] for c in checks),
        "issues": issues,
        "details": checks,
    }


def master_audio(
    album_path: str,
    genre: str = "default",
    cut_highmid: Optional[float] = None,
    source_subfolder: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Master all tracks in album_path.
    """
    preset = GENRE_PRESETS.get(genre, GENRE_PRESETS['default'])
    target_lufs = preset['target_lufs']
    true_peak = preset.get('true_peak_dbtp', -1.0)
    lra = preset.get('lra', 7.0)

    # Override cut if provided
    if cut_highmid is not None:
        preset['highmid_cut_db'] = cut_highmid

    # Find source files
    base = Path(album_path)
    if source_subfolder:
        src_dir = base / source_subfolder
    else:
        # Look for raw or polished; default to raw if exists else polished else root
        if (base / "raw").exists():
            src_dir = base / "raw"
        elif (base / "polished").exists():
            src_dir = base / "polished"
        else:
            src_dir = base

    wav_files = sorted(src_dir.glob("*.wav"))
    if not wav_files:
        return {"success": False, "error": f"No WAV files found in {src_dir}"}

    mastered_dir = base / "mastered"
    mastered_dir.mkdir(exist_ok=True)

    results = []
    commands_planned = []

    for wav in wav_files:
        rel_name = wav.name
        out_wav = mastered_dir / rel_name

        # Build pipeline
        pipeline: List[Dict] = []

        # 1. Genre EQ
        eq_filters = _build_eq_filters(genre, extra_cut=cut_highmid)
        pipeline.extend(eq_filters)

        # 2. Loudness normalization
        ln = _build_loudnorm_pipeline(target_lufs, true_peak, lra)[0]
        pipeline.append(ln)

        # 3. Final normalize peak (safety)
        pipeline.append({"op": "volume", "gain": "0dB"})

        if dry_run:
            dry = ffmpeg_transform(input=str(wav), pipeline=pipeline, output=str(out_wav), dry_run=True)
            commands_planned.append(dry.get('command', ''))
            results.append({"input": str(wav), "output": str(out_wav), "pipeline": pipeline})
        else:
            res = ffmpeg_transform(input=str(wav), pipeline=pipeline, output=str(out_wav))
            results.append(res)

    return {
        "success": True,
        "tracks_mastered": len(wav_files),
        "output_dir": str(mastered_dir),
        "target_lufs": target_lufs,
        "dry_run": dry_run,
        "commands_planned": commands_planned if dry_run else [],
        "results": results,
    }


def master_with_reference(
    album_path: str,
    reference_wav: str,
    source_subfolder: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reference-based mastering: match spectral characteristics of reference track.
    """
    ref_path = Path(reference_wav)
    if not ref_path.exists():
        return {"success": False, "error": f"Reference file not found: {reference_wav}"}

    # Analyze reference
    ref_info = audio_analyze(str(ref_path), features=['spectral_centroid', 'spectral_rolloff', 'mfcc'])
    ref_centroid = ref_info.get('spectral_centroid', 2000)

    # Determine target EQ to match reference's brightness
    # Simple heuristic: if ref centroid > 3000 Hz, we may want to boost highs
    # This is rudimentary; better would be full spectral matching
    target_centroid = ref_centroid

    base = Path(album_path)
    src_dir = base / (source_subfolder or "polished" if (base / "polished").exists() else "raw")
    wav_files = sorted(src_dir.glob("*.wav"))

    mastered_dir = base / "mastered"
    mastered_dir.mkdir(exist_ok=True)

    results = []
    for wav in wav_files:
        out_wav = mastered_dir / wav.name
        # Analyze track
        track_info = audio_analyze(str(wav), features=['spectral_centroid'])
        track_centroid = track_info.get('spectral_centroid', 2000)

        # Compute EQ correction: difference in dB at presence region
        diff_db = 20 * np.log10(target_centroid / (track_centroid + 1e-9))
        # Clamp to reasonable range
        diff_db = max(-6.0, min(6.0, diff_db))

        # Build pipeline
        pipeline = [
            {"op": "equalizer", "frequency": 3000, "width": "1.0", "gain": diff_db},
            {"op": "loudnorm", "i": -14.0, "tp": -1.0, "lra": 7.0},
            {"op": "volume", "gain": "0dB"},
        ]

        res = ffmpeg_transform(input=str(wav), pipeline=pipeline, output=str(out_wav))
        results.append(res)

    return {
        "success": True,
        "reference": str(ref_path),
        "tracks_mastered": len(wav_files),
        "output_dir": str(mastered_dir),
        "results": results,
    }


def fix_dynamic_track(album_path: str, track_filename: str) -> Dict[str, Any]:
    """
    Apply additional compression + limiting to a track with excessive dynamic range.
    """
    base = Path(album_path)
    src_dir = base / "mastered"  # operate on already-mastered file
    in_wav = src_dir / track_filename
    if not in_wav.exists():
        return {"success": False, "error": f"Track not found: {in_wav}"}

    out_wav = src_dir / f"fixed_{track_filename}"

    # Additional heavy compression then re-normalize
    pipeline = [
        {"op": "acompressor", "threshold": "-18dB", "ratio": 4.0, "attack": "0.005", "release": "0.2"},
        {"op": "loudnorm", "i": -14.0, "tp": -1.0, "lra": 7.0},
    ]

    res = ffmpeg_transform(input=str(in_wav), pipeline=pipeline, output=str(out_wav))
    return {"success": res.get('success', False), "output": str(out_wav), "result": res}


def master_album(
    album_path: str,
    genre: str = "default",
    **kwargs,
) -> Dict[str, Any]:
    """
    End-to-end pipeline: analyze → pre-QC → master → verify → post-QC.
    """
    # 1. Analysis
    analysis = analyze_audio(album_path)
    if not analysis.get('success'):
        return {"success": False, "stage": "analyze", "error": analysis.get('error')}

    # 2. Pre-QC (check raw/polished source)
    qc_pre = qc_audio(album_path)
    qc_pre_passed = qc_pre.get('passed', True)

    # 3. Master
    master = master_audio(album_path, genre=genre, **kwargs)
    if not master.get('success'):
        return {"success": False, "stage": "master", "error": master.get('error')}

    # 4. Verify
    verify = analyze_audio(album_path, subfolder="mastered")
    if not verify.get('success'):
        return {"success": False, "stage": "verify", "error": verify.get('error')}

    # 5. Post-QC
    qc_post = qc_audio(album_path, subfolder="mastered")

    # 6. Consistency check
    lufs_range = verify.get('album_lufs_range', 0)
    consistent = lufs_range <= MAX_ALBUM_LUFS_RANGE

    return {
        "success": True,
        "album_path": album_path,
        "genre": genre,
        "analysis": analysis,
        "pre_qc": qc_pre,
        "master": master,
        "verify": verify,
        "post_qc": qc_post,
        "album_lufs_range": lufs_range,
        "consistency_ok": consistent,
        "output_dir": str(Path(album_path) / "mastered"),
    }