"""
Mix Engineer — polishes raw AI-generated audio using granular daw-master skills.

Orchestrates sox-engine (single-track effects), ffmpeg-audio (stem mixing), and
audio-analyzer (feature extraction for analysis) to produce a polished stereo
mix ready for mastering.
"""

import os
import subprocess
import tempfile
import json
import re
import shlex
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Dynamic loader for granular daw-master skills (aligned with batch-processor pattern)
import sys
import types
import importlib.util
from pathlib import Path as _Path

_THIS_FILE = _Path(__file__).resolve()
_DAW_MASTER_DIR = _THIS_FILE.parents[1]  # skills/daw-master
_SKILLS_PARENT = _DAW_MASTER_DIR.parent      # skills/

def _load_skill(skill_dir_name: str, func_name: str):
    """Load a function from a skill's pipeline.py, setting up the skills namespace."""
    # Ensure top-level 'skills' package exists
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

# Load required granular skill functions
_sox_engine_transform = _load_skill('sox-engine', 'transform')
sox_mix              = _load_skill('sox-engine', 'mix')
sox_analyze          = _load_skill('sox-engine', 'analyze')

ffmpeg_transform     = _load_skill('ffmpeg-audio', 'transform')
ffmpeg_mix           = _load_skill('ffmpeg-audio', 'mix')   # used in mix_and_render
ffmpeg_analyze       = _load_skill('ffmpeg-audio', 'analyze')
ffmpeg_probe         = _load_skill('ffmpeg-audio', 'probe')

audio_analyze        = _load_skill('audio-analyzer', 'analyze')
audio_probe          = _load_skill('audio-analyzer', 'probe')
audio_extract_batch  = _load_skill('audio-analyzer', 'extract_batch')
# Backwards compatibility alias
sox_transform = _sox_engine_transform


# ============================
# Configuration & Presets
# ============================

STEM_NAMES = {
    0: "Lead Vocals",
    1: "Backing Vocals",
    2: "Drums",
    3: "Bass",
    4: "Guitar",
    5: "Keyboard",
    6: "Strings",
    7: "Brass",
    8: "Woodwinds",
    9: "Percussion",
    10: "Synth",
    11: "FX",
}

# Default per-stem processing parameters (no genre override)
DEFAULT_STEM_SETTINGS = {
    "Lead Vocals": {
        "noise_reduction_strength": 0.5,
        "presence_boost_db": 2.0,
        "presence_freq": 3000,
        "high_tame_db": -2.0,
        "high_tame_freq": 7000,
        "comp_thresh_in": -20,
        "comp_thresh_out": -10,
        "highpass_cutoff": 80,
    },
    "Backing Vocals": {
        "noise_reduction_strength": 0.5,
        "presence_boost_db": 1.0,
        "presence_freq": 3000,
        "high_tame_db": -2.5,
        "high_tame_freq": 7000,
        "comp_thresh_in": -14,
        "comp_thresh_out": -10,
        "highpass_cutoff": 80,
        "stereo_width": 1.3,
    },
    "Drums": {
        "click_removal": True,
        "comp_thresh_in": -12,
        "comp_thresh_out": -10,
        "comp_attack": "0.005:0.1",
        "highpass_cutoff": 50,
    },
    "Bass": {
        "highpass_cutoff": 30,
        "mud_cut_db": -3.0,
        "mud_cut_freq": 200,
        "comp_thresh_in": -15,
        "comp_thresh_out": -10,
    },
    "Guitar": {
        "highpass_cutoff": 80,
        "mud_cut_db": -2.5,
        "mud_cut_freq": 250,
        "presence_boost_db": 1.5,
        "presence_freq": 3000,
        "high_tame_db": -1.5,
        "high_tame_freq": 8000,
        "stereo_width": 1.15,
        "comp_thresh_in": -14,
        "comp_thresh_out": -10,
    },
    "Keyboard": {
        "highpass_cutoff": 40,
        "mud_cut_db": -2.0,
        "mud_cut_freq": 300,
        "presence_boost_db": 1.0,
        "presence_freq": 2500,
        "high_tame_db": -1.5,
        "high_tame_freq": 9000,
        "stereo_width": 1.1,
        "comp_thresh_in": -16,
        "comp_thresh_out": -10,
    },
    "Strings": {
        "highpass_cutoff": 35,
        "mud_cut_db": -1.5,
        "mud_cut_freq": 250,
        "presence_boost_db": 1.0,
        "presence_freq": 3500,
        "high_tame_db": -1.0,
        "high_tame_freq": 9000,
        "stereo_width": 1.25,
        "comp_thresh_in": -18,
        "comp_thresh_out": -10,
    },
    "Brass": {
        "highpass_cutoff": 60,
        "mud_cut_db": -2.0,
        "mud_cut_freq": 300,
        "presence_boost_db": 1.5,
        "presence_freq": 2000,
        "high_tame_db": -2.0,
        "high_tame_freq": 7000,
        "comp_thresh_in": -14,
        "comp_thresh_out": -10,
    },
    "Woodwinds": {
        "highpass_cutoff": 50,
        "mud_cut_db": -1.5,
        "mud_cut_freq": 250,
        "presence_boost_db": 1.0,
        "presence_freq": 2500,
        "high_tame_db": -1.0,
        "high_tame_freq": 8000,
        "comp_thresh_in": -16,
        "comp_thresh_out": -10,
    },
    "Percussion": {
        "highpass_cutoff": 60,
        "click_removal": True,
        "presence_boost_db": 1.0,
        "presence_freq": 4000,
        "high_tame_db": -1.0,
        "high_tame_freq": 10000,
        "stereo_width": 1.2,
        "comp_thresh_in": -15,
        "comp_thresh_out": -10,
    },
    "Synth": {
        "highpass_cutoff": 80,
        "mid_boost_db": 1.0,
        "mid_boost_freq": 2000,
        "high_tame_db": -1.5,
        "high_tame_freq": 9000,
        "stereo_width": 1.2,
        "comp_thresh_in": -16,
        "comp_thresh_out": -10,
    },
    "FX": {
        "noise_reduction_strength": 0.3,
        "mud_cut_db": -2.0,
        "mud_cut_freq": 300,
        "high_tame_db": -1.5,
        "high_tame_freq": 8000,
    },
}

# Genre preset modifications (subset)
GENRE_PRESETS = {
    "hip-hop": {
        "Lead Vocals": {"presence_boost_db": 2.5, "gain_in_mix_db": 1.0},
        "Bass": {"gain_in_mix_db": 1.0, "highpass_cutoff": 25},
        "Drums": {"gain_in_mix_db": 0.5},
        "Guitar": {"presence_boost_db": 1.5, "mud_cut_db": -3.0},
        "Synth": {"gain_in_mix_db": -0.5},
    },
    "rock": {
        "Drums": {"gain_in_mix_db": 0.7},
        "Guitar": {
            "gain_in_mix_db": 0.5,
            "presence_boost_db": 1.5,
            "mud_cut_db": -3.0,
            "high_tame_db": -2.5,
        },
        "Bass": {"comp_thresh_in": -14},
        "Lead Vocals": {"high_tame_db": -2.5},
    },
    "edm": {
        "Bass": {"gain_in_mix_db": 1.0, "highpass_cutoff": 25},
        "Drums": {"gain_in_mix_db": 0.7},
        "Synth": {"gain_in_mix_db": 0.5, "high_tame_db": -1.0},
        "Lead Vocals": {"presence_boost_db": 2.0},
    },
    "ambient": {
        "Lead Vocals": {"noise_reduction_strength": 0.2, "presence_boost_db": 1.0, "comp_thresh_in": -16, "comp_ratio": 1.5},
        "Guitar": {"comp_thresh_in": -16},
        "Bass": {"comp_thresh_in": -16},
    },
    "folk": {
        "Lead Vocals": {"gain_in_mix_db": 0.5},
        "Guitar": {"gain_in_mix_db": 0, "presence_boost_db": 2.0, "stereo_width": 1.0},
        "Strings": {"comp_thresh_in": -16},
    },
    "jazz": {
        "Strings": {"comp_thresh_in": -16, "comp_ratio": 1.0},
        "Brass": {"saturation_amount": 0.1},
        "Woodwinds": {"saturation_amount": 0.1},
        "Guitar": {"saturation_amount": 0.1},
        "Keyboard": {"saturation_amount": 0.1},
    },
    # Genres can be extended
}

# Mix balance gains (linear multiplier, applied at mix stage)
MIX_GAIN_DB = {
    "hip-hop": {"Lead Vocals": 1.0, "Bass": 1.0, "Drums": 0.5, "Backing Vocals": 1.0, "Percussion": 0.5, "Synth": 0.7},
    "rock": {"Drums": 1.2, "Guitar": 1.15, "Bass": 1.0},
    "edm": {"Drums": 1.2, "Bass": 1.3, "Synth": 1.15},
    "folk": {"Lead Vocals": 1.15, "Guitar": 1.0, "Strings": 0.9},
    "ambient": {},
    "jazz": {},
}
DEFAULT_MIX_GAIN = 1.0


# ============================
# Helper Functions
# ============================

def _db_to_linear(db: float) -> float:
    return 10 ** (db / 20.0)

def _linear_to_db(lin: float) -> float:
    return 20 * np.log10(lin + 1e-12)

def _generate_noise_profile(wav_path: str, duration: float = 0.1) -> Optional[str]:
    """
    Generate a SoX noise profile from the quietest segment of the audio.
    Returns path to profile file or None on failure.
    """
    try:
        # Get duration
        info = subprocess.run(['sox', '--i', '-D', wav_path], capture_output=True, text=True, timeout=10)
        total = float(info.stdout.strip())

        # Scan in 100ms windows to find quietest
        best_rms = float('inf')
        best_start = 0.0
        window = min(duration, total * 0.1)
        step = window * 0.5

        for start in np.arange(0, total - window, step):
            # Use sox to extract segment and get RMS via stat
            cmd = ['sox', wav_path, '-n', 'trim', str(start), str(window), 'stat']
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            # Parse RMS from output
            rms_match = re.search(r'RMS lev.*?(-?\d+\.?\d*)', r.stdout)
            if rms_match:
                rms = float(rms_match.group(1))
                if rms < best_rms:
                    best_rms = rms
                    best_start = start

        if best_rms < 0:
            profile = tempfile.NamedTemporaryFile(delete=False, suffix='.nrp')
            # Generate noise profile from that segment using sox noiseprof
            subprocess.run(['sox', wav_path, '-n', 'noiseprof', profile.name,
                            'trim', str(best_start), str(window)], check=True, timeout=10)
            return profile.name
    except Exception as e:
        print(f"Warning: noise profile generation failed: {e}")
    return None


def _detect_clicks(wav_path: str, threshold_sigma: float = 6.0) -> List[float]:
    """
    Detect clicks via amplitude spike detection using audio-analyzer.
    Returns list of timestamps (seconds).
    """
    try:
        # Load audio for simple peak detection
        import soundfile as sf
        y, sr = sf.read(wav_path)
        if y.ndim > 1:
            y = y.mean(axis=1)  # convert to mono
        # Compute RMS and median amplitude
        amps = np.abs(y)
        median_amp = np.median(amps)
        std_amp = np.std(amps)
        threshold = median_amp + threshold_sigma * std_amp
        # Find indices exceeding threshold
        clicks = np.where(amps > threshold)[0]
        timestamps = clicks.astype(float) / sr
        return timestamps.tolist()
    except Exception as e:
        print(f"Warning: click detection failed: {e}")
        return []


def _analyze_stem_issues(wav_path: str, stem_type: str) -> Dict[str, Any]:
    """
    Run audio-analyzer and detect issue flags: noise, mud, harsh, clicks, rumble.
    """
    result = audio_analyze(wav_path, features=['loudness', 'spectral_centroid', 'spectral_rolloff', 'zcr'])
    issues = {}

    # Noise floor: RMS loudness in dB (lower = quieter = potentially more noise relative)
    loudness = result.get('loudness', -60)  # dB
    # Very quiet audio may have elevated noise floor
    issues['noise_floor_db'] = loudness

    # Muddiness: energy in low-mids (150–400 Hz). Compute via librosa spectral bands?
    # Use spectral centroid: lower centroid = more low-end / mud
    centroid = result.get('spectral_centroid', 1000)
    issues['centroid_hz'] = centroid
    issues['muddy'] = centroid < 600  # heuristic

    # Harshness: high centroid + high zero-crossing rate
    zcr = result.get('zcr', 0.1)
    issues['harsh'] = (centroid > 3000) and (zcr > 0.2)

    # Click detection (transient spikes)
    clicks = _detect_clicks(wav_path, threshold_sigma=6.0)
    issues['click_count'] = len(clicks)
    issues['clicks'] = clicks

    # Sub-bass rumble: analyze very low frequencies (<30 Hz)
    # Use spectral rolloff at 0.85 to infer low end
    rolloff = result.get('spectral_rolloff', 500)
    issues['sub_bass_energy'] = rolloff < 100  # strong low end

    return issues


def _stem_type_from_filename(fname: str) -> str:
    """Infer stem type from filename pattern like '0 Lead Vocals'."""
    stem = STEM_NAMES.get(int(fname.split(' ')[0])) if fname and fname[0].isdigit() else None
    return stem or "Other"


def _build_stem_pipeline(
    stem_type: str,
    issues: Dict[str, Any],
    genre: str,
    mix_gain_db: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Construct a SoX pipeline (list of op dicts) for a single stem.
    """
    settings = DEFAULT_STEM_SETTINGS.get(stem_type, DEFAULT_STEM_SETTINGS["FX"]).copy()
    # Genre overrides
    genre_overrides = GENRE_PRESETS.get(genre, {}).get(stem_type, {})
    settings.update(genre_overrides)

    pipeline: List[Dict[str, Any]] = []

    # 1. Highpass (via raw_effect to use SoX highpass directly)
    hp = settings.get("highpass_cutoff")
    if hp and hp > 0:
        pipeline.append({"op": "raw_effect", "effect": f"highpass {hp}"})

    # 2. Noise reduction (noisered) — generate profile on-demand
    nr_strength = settings.get("noise_reduction_strength", 0.0)
    if nr_strength > 0 and stem_type in ["Lead Vocals", "Backing Vocals", "FX"]:
        # We'll handle profile later in transform wrapper
        pipeline.append({"op": "noisered", "strength": nr_strength})

    # 3. Clicks — to be handled by custom repair (clip-and-interpolate)
    if settings.get("click_removal") and issues.get("click_count", 0) > 0:
        pipeline.append({"op": "repair_clicks", "threshold_sigma": 6.0})

    # 4. EQ: Mud cut
    mud_db = settings.get("mud_cut_db", 0.0)
    mud_freq = settings.get("mud_cut_freq", 200)
    if mud_db < 0:
        pipeline.append({"op": "equalizer", "frequency": mud_freq, "width": "2q", "gain": mud_db})

    # 5. Presence boost
    pres_db = settings.get("presence_boost_db", 0.0)
    pres_freq = settings.get("presence_freq", 3000)
    if pres_db > 0:
        pipeline.append({"op": "equalizer", "frequency": pres_freq, "width": "1.0", "gain": pres_db})

    # 6. High tame (high shelf cut)
    ht_db = settings.get("high_tame_db", 0.0)
    ht_freq = settings.get("high_tame_freq", 7000)
    if ht_db < 0:
        pipeline.append({"op": "highshelve", "frequency": ht_freq, "gain": ht_db})

    # 7. Compression (compand)
    comp_thresh_in = settings.get("comp_thresh_in", -20)
    comp_thresh_out = settings.get("comp_thresh_out", -10)
    comp_attack = settings.get("comp_attack", "0.01:0.1")
    comp_ratio = settings.get("comp_ratio", 2.0)
    # compand syntax: attack1:decay1 [soft-knee-dB:]in-dB[,out-dB]
    # Build simplified compand string
    soft_knee = 0
    compand_str = f"{comp_attack} {soft_knee}:{comp_thresh_in},{comp_thresh_out}"
    pipeline.append({"op": "compand", "compand_str": compand_str, "gain": 1.0})

    # 8. Normalize peak to -0.1 dB
    pipeline.append({"op": "normalize", "peak": -0.1})

    # Store mix gain for later
    if mix_gain_db != 0.0:
        settings["gain_in_mix_db"] = mix_gain_db

    return pipeline


def _detect_source_mode(album_path: str) -> Tuple[str, List[str]]:
    """
    Determine whether to process stems or full mix.
    Returns: ("stems", [list of stem wav paths]) or ("full_mix", [list of top-level wavs])
    """
    stems_dir = Path(album_path) / "stems"
    if stems_dir.exists():
        track_dirs = sorted([d for d in stems_dir.iterdir() if d.is_dir() and d.name[0].isdigit()])
        if track_dirs:
            stem_files = []
            for td in track_dirs:
                # Find WAV files with numeric prefixes
                wavs = sorted(td.glob("*.wav"))
                stem_files.extend([str(p) for p in wavs])
            if stem_files:
                return "stems", stem_files
    # Fall back to top-level WAVs
    wavs = sorted(Path(album_path).glob("*.wav"))
    wav_paths = [str(p) for p in wavs]
    return "full_mix", wav_paths


# ============================
# Public API
# ============================

def analyze_mix_issues(album_path: str) -> Dict[str, Any]:
    """
    Scan audio for noise, muddiness, harshness, clicks, sub-bass rumble.
    """
    source_mode, tracks = _detect_source_mode(album_path)
    if not tracks:
        return {
            "source_mode": source_mode,
            "tracks": [],
            "issues": {},
            "summary": "No audio files found in album directory.",
        }

    track_infos = []
    issues_summary = {
        "noisy_tracks": [],
        "muddy_tracks": [],
        "harsh_tracks": [],
        "clicky_tracks": [],
        "sub_bass_tracks": [],
    }

    for wav in tracks:
        # infer stem type
        stem_type = _stem_type_from_filename(Path(wav).stem)
        issues = _analyze_stem_issues(wav, stem_type)

        track_info = {
            "path": wav,
            "stem_type": stem_type,
            "issues": dict(issues),
        }
        track_infos.append(track_info)

        # Categorize
        if issues.get('noise_floor_db', -60) > -50:  # noise floor high (less negative)
            issues_summary["noisy_tracks"].append({"track": stem_type, "path": wav, "noise_floor": issues.get('noise_floor_db')})
        if issues.get('muddy'):
            issues_summary["muddy_tracks"].append({"track": stem_type, "path": wav, "centroid": issues.get('centroid_hz')})
        if issues.get('harsh'):
            issues_summary["harsh_tracks"].append({"track": stem_type, "path": wav, "zcr": issues.get('zcr')})
        if issues.get('click_count', 0) > 10:
            issues_summary["clicky_tracks"].append({"track": stem_type, "path": wav, "clicks": issues.get('click_count')})
        if issues.get('sub_bass_energy'):
            issues_summary["sub_bass_tracks"].append({"track": stem_type, "path": wav})

    # Build plain-English summary
    summary_lines = [f"Source mode: {source_mode} ({len(track_infos)} tracks)"]
    if issues_summary["noisy_tracks"]:
        summary_lines.append(f"  Noise floor elevated on: {[t['track'] for t in issues_summary['noisy_tracks'][:5]]}")
    if issues_summary["muddy_tracks"]:
        summary_lines.append(f"  Muddy low-mids on: {[t['track'] for t in issues_summary['muddy_tracks'][:5]]}")
    if issues_summary["harsh_tracks"]:
        summary_lines.append(f"  Harsh high-mids on: {[t['track'] for t in issues_summary['harsh_tracks'][:5]]}")
    if issues_summary["clicky_tracks"]:
        summary_lines.append(f"  Click artifacts on: {[t['track'] for t in issues_summary['clicky_tracks'][:5]]}")
    if issues_summary["sub_bass_tracks"]:
        summary_lines.append(f"  Sub-bass rumble on: {[t['track'] for t in issues_summary['sub_bass_tracks'][:5]]}")

    return {
        "source_mode": source_mode,
        "tracks": track_infos,
        "issues": issues_summary,
        "summary": "\n".join(summary_lines) if summary_lines else "No significant issues detected.",
    }


def polish_audio(
    album_path: str,
    genre: str = "default",
    dry_run: bool = False,
    use_stems: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Process stems or full mix with appropriate settings.
    If use_stems is None, auto-detect via stems/ directory.
    """
    album_path = os.path.abspath(album_path)
    polished_dir = Path(album_path) / "polished"
    polished_dir.mkdir(exist_ok=True)

    # Determine source mode
    detected_mode, all_tracks = _detect_source_mode(album_path)
    if use_stems is None:
        source_mode = detected_mode
    else:
        source_mode = "stems" if use_stems else "full_mix"
        if source_mode == "stems" and detected_mode != "stems":
            return {"success": False, "error": "Stems requested but no stems/ directory found."}

    if not all_tracks:
        return {"success": False, "error": "No audio files found."}

    # Pre-analysis for mix gains and per-stem settings
    analysis = analyze_mix_issues(album_path)
    mix_gains_db = MIX_GAIN_DB.get(genre, {})

    # Build per-stem (or full-mix) pipeline
    results = []
    commands_planned = []

    if source_mode == "stems":
        # Process each stem individually
        for wav in all_tracks:
            stem_type = _stem_type_from_filename(Path(wav).stem)
            # Find issues for this stem
            stem_issues = next((t['issues'] for t in analysis['tracks'] if t['path'] == wav), {})
            mix_gain_db = mix_gains_db.get(stem_type, 0.0)
            pipeline = _build_stem_pipeline(stem_type, stem_issues, genre, mix_gain_db)

            out_name = Path(wav).name
            out_path = polished_dir / out_name

            if dry_run:
                dry = transform(input=wav, pipeline=pipeline, output=str(out_path), dry_run=True)
                commands_planned.append(dry.get('command', ''))
                results.append({"input": wav, "output": str(out_path), "pipeline": pipeline, "dry_run": True})
            else:
                res = transform(input=wav, pipeline=pipeline, output=str(out_path))
                results.append(res)
        # After stems, mix them
        # Build ffmpeg mix command from polished stems
        stem_outputs = [str(polished_dir / Path(w).name) for w in all_tracks]
        # Compute per-track gains from pipeline settings (linear)
        track_gains = []
        for wav in all_tracks:
            stem_type = _stem_type_from_filename(Path(wav).stem)
            gain_db = mix_gains_db.get(stem_type, DEFAULT_MIX_GAIN)
            # Additional gain from EQ? For simplicity, just use genre mix gain
            track_gains.append({"path": str(polished_dir / Path(wav).name), "gain": _db_to_linear(gain_db)})

        mix_out = polished_dir / "mix.wav"
        if dry_run:
            dry = ffmpeg_mix(tracks=track_gains, output=str(mix_out), dry_run=True)
            commands_planned.append(dry.get('command', ''))
        else:
            ffmpeg_mix(tracks=track_gains, output=str(mix_out))
        results.append({"mix_output": str(mix_out), "track_count": len(all_tracks)})

    else:
        # Full mix fallback: single file processing
        wav = all_tracks[0]  # assume one file
        # Build simpler pipeline
        full_pipeline = [
            {"op": "raw_effect", "effect": "noisered"},  # will auto-generate profile
            {"op": "highpass", "cutoff": 35},
            {"op": "equalizer", "frequency": 250, "width": "2q", "gain": -2.0},
            {"op": "equalizer", "frequency": 3000, "width": "1.0", "gain": 1.5},
            {"op": "highshelve", "frequency": 7000, "gain": -1.5},
            {"op": "compand", "compand_str": "0.01:0.1 0:-20,-10", "gain": 1.0},
            {"op": "normalize", "peak": -0.1},
        ]
        out_path = polished_dir / "polished_mix.wav"
        if dry_run:
            dry = transform(input=wav, pipeline=full_pipeline, output=str(out_path), dry_run=True)
            commands_planned.append(dry.get('command', ''))
            results = [{"input": wav, "output": str(out_path), "pipeline": full_pipeline, "dry_run": True}]
        else:
            results = [transform(input=wav, pipeline=full_pipeline, output=str(out_path))]

    return {
        "success": True,
        "mode": source_mode,
        "tracks_processed": len(all_tracks),
        "output_dir": str(polished_dir),
        "dry_run": dry_run,
        "commands_planned": commands_planned if dry_run else [],
        "results": results,
    }


def polish_album(album_path: str, genre: str = "default") -> Dict[str, Any]:
    """End-to-end: analyze → polish → verify."""
    analysis = analyze_mix_issues(album_path)
    polish = polish_audio(album_path, genre=genre, dry_run=False)

    # Verification: check polished files
    polished_dir = Path(album_path) / "polished"
    verification = {"clipping": [], "nans": [], "reduced_noise": []}
    for wav_path in polished_dir.glob("*.wav"):
        info = audio_probe(str(wav_path))
        peak = info.get('peak_db', 0)
        if peak > -0.1:
            verification["clipping"].append(str(wav_path))
        # Check for NaNs using ffprobe (would need deeper inspection)
        # For now, just ensure file size > 0
        if wav_path.stat().st_size == 0:
            verification["nans"].append(str(wav_path))

    return {
        "analysis": analysis,
        "polish": polish,
        "verification": verification,
        "output_dir": str(polished_dir),
    }


# ============================
# Custom SoX Effects Extensions
# ============================

def _build_custom_sox_args(pipeline: List[Dict], input_file: str, output_file: str) -> List[str]:
    """
    Extended SoX builder that handles our custom ops (noisered, repair_clicks, highshelve).
    """
    args = []
    # Use temp dir for noise profiles
    temp_profile = None

    for step in pipeline:
        op = step.get('op')

        if op == 'noisered':
            strength = step.get('strength', 0.5)
            if not temp_profile:
                temp_profile = _generate_noise_profile(input_file)
            if temp_profile and os.path.exists(temp_profile):
                args.append('noisered')
                args.append(temp_profile)
                args.append(str(strength))
            else:
                # Skip if profile generation failed
                pass

        elif op == 'repair_clicks':
            # For now we flag clicks; actual repair could be done via Python scipy interpolation
            # Alternatively pass through to a custom script. We'll skip actual repair for now
            # but log warning
            pass

        elif op == 'highshelve':
            freq = step.get('frequency', 8000)
            gain = step.get('gain', 0)
            # SoX highshelve: `highshelve frequency gain`
            args.append('highshelve')
            args.append(str(freq))
            args.append(str(gain))

        elif op in ('highpass', 'lowpass', 'bandpass'):
            # These are passed raw; sox-engine will handle raw_effect
            effect = step.get('effect', op)
            args.append(effect)

        else:
            # Let sox-engine._build_sox_args handle standard ops by temporarily
            # falling through; but our wrapper rebuilds directly here.
            # For simplicity, delegate to sox-engine's internal builder for known ops.
            raise ValueError(f"Unsupported custom op in mix-engineer: {op}")

    return args


# Wrapper that intercepts some custom ops, then delegates to sox-engine
def _transform_with_custom_ops(
    input: str,
    pipeline: List[Dict],
    output: str,
    dry_run: bool = False,
) -> Dict:
    """Transform using SoX, but intercept custom ops before calling sox-engine."""
    in_path = Path(input).resolve()
    out_path = Path(output).resolve()

    if not in_path.exists():
        return {"success": False, "error": f"Input not found: {input}"}

    try:
        # Build SoX command: sox input output [effects...]
        cmd = ['sox', str(in_path), str(out_path)]
        effect_args: List[str] = []
        temp_files = []
        temp_profile = None

        for step in pipeline:
            op = step.get('op')

            if op == 'noisered':
                strength = step.get('strength', 0.5)
                if temp_profile is None:
                    temp_profile = _generate_noise_profile(str(in_path))
                    if temp_profile:
                        temp_files.append(temp_profile)
                if temp_profile:
                    effect_args.append('noisered')
                    effect_args.append(temp_profile)
                    effect_args.append(str(strength))

            elif op == 'highpass':
                cutoff = step.get('cutoff', step.get('frequency', 80))
                effect_args.append('highpass')
                effect_args.append(str(cutoff))

            elif op == 'lowpass':
                cutoff = step.get('cutoff', step.get('frequency', 8000))
                effect_args.append('lowpass')
                effect_args.append(str(cutoff))

            elif op == 'bandpass':
                freq = step.get('frequency', 1000)
                width = step.get('width', '2q')
                effect_args.append('bandpass')
                effect_args.append(str(freq))
                effect_args.append(str(width))

            elif op == 'highshelve':
                freq = step.get('frequency', 7000)
                gain = step.get('gain', 0)
                effect_args.append('highshelve')
                effect_args.append(str(freq))
                effect_args.append(str(gain))

            elif op == 'repair_clicks':
                pass

            elif op == 'compand':
                comp_str = step.get('compand_str', '0.01:0.1 0:-20,-10')
                effect_args.append('compand')
                effect_args.append(comp_str)

            elif op == 'equalizer':
                freq = step.get('frequency', 1000)
                width = step.get('width', '2q')
                gain = step.get('gain', 0)
                effect_args.append('equalizer')
                effect_args.append(f"{freq} {width} {gain}")

            elif op == 'normalize':
                peak = step.get('peak', -0.1)
                effect_args.append('norm')
                if peak != -0.1:
                    effect_args.extend(['-p', str(peak)])

            elif op == 'fade':
                ftype = step.get('type', 'out')
                length = step.get('length', 1.0)
                if ftype == 'in':
                    effect_args.extend(['fade', 'in', str(length)])
                elif ftype == 'out':
                    effect_args.extend(['fade', 'out', str(length)])
                elif ftype == 'in-out':
                    fade_in = step.get('fade_in', length)
                    fade_out = step.get('fade_out', length)
                    effect_args.extend(['fade', 'in-out', str(fade_in), str(fade_out)])

            elif op == 'raw_effect':
                effect = step.get('effect', '')
                parts = effect.split()
                effect_args.extend(parts)

            else:
                return {"success": False, "error": f"Unknown op: {op}"}

        cmd.extend(effect_args)

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "steps": len(pipeline),
            }

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Cleanup temp profile
        if temp_profile and os.path.exists(temp_profile):
            try:
                os.unlink(temp_profile)
            except:
                pass

        if result.returncode == 0:
            return {"success": True, "output": str(out_path), "command": " ".join(cmd), "steps": len(pipeline)}
        else:
            return {"success": False, "error": result.stderr.strip() or result.stdout.strip(), "command": " ".join(cmd)}

    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        for tf in temp_files:
            try:
                if os.path.exists(tf):
                    os.unlink(tf)
            except:
                pass

# Override sox_transform with our custom wrapper that handles extra ops
_original_sox_transform = sox_transform

def transform(input: str, pipeline: List[Dict], output: str, dry_run: bool = False, **kwargs) -> Dict:
    """
    Enhanced transform that supports mix-engineer specific ops.
    """
    return _transform_with_custom_ops(input, pipeline, output, dry_run=dry_run)


# ============================
# Mix Helper (uses ffmpeg-audio mix)
# ============================

def mix_and_render(stems: List[Dict[str, Any]], output: str, normalize_final: bool = False) -> Dict:
    """
    Mix processed stems using ffmpeg-audio.mix.

    stems: [{"path": str, "gain": float (linear)}, ...]
    """
    return ffmpeg_mix(tracks=stems, output=output, normalize_final=normalize_final)