#!/usr/bin/env python3
"""
daw-master:audio-analyzer
Advanced audio analysis and feature extraction using librosa with optional Vamp plugin support via sonic-annotator.

Operations:
  - analyze(file, features=None) -> dict
  - probe(file) -> dict
  - extract_batch(dir, pattern, output_format='csv', output_file=None) -> None
"""

import json
import csv
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Check dependencies at module load time for graceful degradation
DEPENDENCIES = {
    "librosa": False,
    "soundfile": False,
    "numpy": False,
    "sonic_annotator": False,
}

try:
    import librosa
    DEPENDENCIES["librosa"] = True
except ImportError:
    pass

try:
    import soundfile as sf
    DEPENDENCIES["soundfile"] = True
except ImportError:
    pass

try:
    import numpy as np
    DEPENDENCIES["numpy"] = True
except ImportError:
    pass

# Check for sonic-annotator binary
if subprocess.run(["which", "sonic-annotator"], capture_output=True).returncode == 0:
    DEPENDENCIES["sonic_annotator"] = True


class DependencyError(RuntimeError):
    """Raised when a required dependency is missing."""
    pass


def _check_core_dependencies() -> None:
    """Ensure core Python dependencies are available."""
    missing = [name for name, ok in DEPENDENCIES.items()
               if name in ("librosa", "soundfile", "numpy") and not ok]
    if missing:
        raise DependencyError(
            f"Missing required packages: {', '.join(missing)}. "
            f"Install with: pip install librosa soundfile numpy"
        )


def _estimate_key(y: np.ndarray, sr: int) -> Tuple[str, float]:
    """
    Estimate musical key using a simple chroma-based approach.
    Returns (key_name, confidence).
    """
    # Use chroma features
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, bins_per_octave=36, n_octaves=7)
    chroma_avg = np.mean(chroma, axis=1)

    # Krumhansl-Schmuckler key profiles (major/minor weights)
    majors = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                       2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minors = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                       2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    # Score correlation with each key profile
    major_scores = np.array([np.corrcoef(chroma_avg, np.roll(majors, k))[0, 1] for k in range(12)])
    minor_scores = np.array([np.corrcoef(chroma_avg, np.roll(minors, k))[0, 1] for k in range(12)])

    best_major_idx = np.argmax(major_scores)
    best_minor_idx = np.argmax(minor_scores)

    if major_scores[best_major_idx] > minor_scores[best_minor_idx]:
        return f"{keys[best_major_idx]} major", float(major_scores[best_major_idx])
    else:
        return f"{keys[best_minor_idx]} minor", float(minor_scores[best_minor_idx])


def probe(file_path: str) -> Dict[str, Any]:
    """
    Return basic audio file metadata without full analysis.
    Uses soundfile if available, falls back to librosa.

    Parameters
    ----------
    file_path : str
        Path to audio file

    Returns
    -------
    dict with keys: duration, sample_rate, channels, format, frames
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    info: Dict[str, Any] = {"file": file_path}

    # Try soundfile first (fast, full metadata)
    if DEPENDENCIES["soundfile"]:
        try:
            with sf.SoundFile(file_path) as f:
                info["duration"] = f.duration if hasattr(f, "duration") else len(f) / f.samplerate
                info["sample_rate"] = f.samplerate
                info["channels"] = f.channels
                info["format"] = f.format
                info["subtype"] = f.subtype
                info["frames"] = len(f)
            return info
        except Exception as e:
            pass

    # Fallback: use librosa (loads entire file, slower)
    if DEPENDENCIES["librosa"]:
        try:
            y, sr = librosa.load(file_path, sr=None, mono=False)
            if y.ndim == 1:
                channels = 1
            else:
                channels = y.shape[0] if y.shape[0] <= 2 else 1  # librosa may mix to mono
            info["duration"] = librosa.get_duration(y=y, sr=sr)
            info["sample_rate"] = sr
            info["channels"] = channels
            info["format"] = "unknown (librosa fallback)"
            return info
        except Exception as e:
            pass

    # Last resort: try ffprobe
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:stream=sample_rate,channels", "-of", "default=noprint_wrappers=1:nokey=1",
             file_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                info["duration"] = float(lines[0]) if lines[0] else None
                info["sample_rate"] = int(lines[1]) if lines[1] else None
                info["channels"] = int(lines[2]) if lines[2] else None
                info["format"] = "ffprobe"
                return info
    except Exception:
        pass

    raise DependencyError(
        "No audio backend available. Install librosa+soundfile or ensure ffprobe is in PATH."
    )


def analyze(file_path: str,
            features: Optional[List[str]] = None,
            n_mfcc: int = 20,
            hop_length: int = 512) -> Dict[str, Any]:
    """
    Perform comprehensive audio analysis on a single file.

    Parameters
    ----------
    file_path : str
        Path to audio file
    features : list of str, optional
        Subset of features to compute. If None, computes all.
        Common names: 'tempo', 'key', 'loudness', 'spectral_centroid',
        'spectral_rolloff', 'spectral_flatness', 'mfcc', 'harmonic_ratio',
        'onset_count', 'zcr', 'vamp'
    n_mfcc : int, default 20
        Number of MFCC coefficients to extract
    hop_length : int, default 512
        Hop length for frame-based features

    Returns
    -------
    dict
        All extracted features and metadata
    """
    _check_core_dependencies()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    # First, get basic metadata
    info = probe(file_path)
    result: Dict[str, Any] = dict(info)

    # Load audio (mono for most feature extraction)
    y, sr = librosa.load(file_path, sr=None, mono=True, dtype=np.float32)
    result["sample_rate"] = int(sr)
    result["frames"] = len(y)
    result["duration"] = float(librosa.get_duration(y=y, sr=sr))

    # Determine which features to compute
    all_features = {
        "tempo", "key", "loudness", "spectral_centroid",
        "spectral_rolloff", "spectral_flatness", "mfcc",
        "harmonic_ratio", "onset_count", "zcr", "vamp"
    }
    if features is None:
        compute_features = all_features
    else:
        compute_features = set(features) & all_features

    # 1. Tempo (beat tracking)
    if "tempo" in compute_features:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)
        result["tempo"] = float(tempo)
        result["tempo_confidence"] = float(np.mean(onset_env[beats]) if len(beats) > 0 else 0.0)
        result["beat_count"] = int(len(beats))

    # 2. Key estimation
    if "key" in compute_features:
        key, conf = _estimate_key(y, sr)
        result["key"] = key
        result["key_confidence"] = conf

    # 3. Loudness (RMS-based)
    if "loudness" in compute_features:
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        result["loudness"] = float(20 * np.log10(np.mean(rms) + 1e-10))
        result["loudness_std"] = float(np.std(rms))

    # 4. Spectral features
    if "spectral_centroid" in compute_features:
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
        result["spectral_centroid"] = float(np.mean(cent))
        result["spectral_centroid_std"] = float(np.std(cent))

    if "spectral_rolloff" in compute_features:
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]
        result["spectral_rolloff"] = float(np.mean(rolloff))

    if "spectral_flatness" in compute_features:
        flat = librosa.feature.spectral_flatness(y=y, hop_length=hop_length)[0]
        result["spectral_flatness"] = float(np.mean(flat))

    # 5. MFCCs
    if "mfcc" in compute_features:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
        result["mfcc"] = {
            "mean": mfcc.mean(axis=1).tolist(),
            "std": mfcc.std(axis=1).tolist()
        }

    # 6. Harmonic / Percussive separation ratio
    if "harmonic_ratio" in compute_features or "percussive_ratio" in compute_features:
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        harm_energy = np.sum(y_harmonic ** 2)
        perc_energy = np.sum(y_percussive ** 2)
        total = harm_energy + perc_energy + 1e-10
        result["harmonic_ratio"] = float(harm_energy / total)
        result["percussive_ratio"] = float(perc_energy / total)

    # 7. Onset count (rhythmic activity)
    if "onset_count" in compute_features:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        peaks = librosa.util.peak_pick(onset_env, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
        result["onset_count"] = int(len(peaks))

    # 8. Zero-crossing rate (rough brightness / noise estimate)
    if "zcr" in compute_features:
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
        result["zero_crossing_rate"] = float(np.mean(zcr))

    # 9. Vamp plugins via sonic-annotator (optional)
    if "vamp" in compute_features and DEPENDENCIES["sonic_annotator"]:
        result["vamp_plugins"] = _run_sonic_annotator(file_path)

    return result


def _run_sonic_annotator(file_path: str) -> Dict[str, Any]:
    """
    Run sonic-annotator with common Vamp plugins.
    Returns a dict with plugin outputs.
    """
    plugins_to_try = [
        "qm-vamp-plugins:qm-tempotracker",
        "qm-vamp-plugins:qm-chroma",
        "qm-vamp-plugins:qm-onsetdetector",
        "vamp-example-plugins:amplitude-follower",
    ]

    results: Dict[str, Any] = {}
    tmp_csv = None

    try:
        for plugin in plugins_to_try:
            # Try each plugin; sonic-annotator outputs to stdout by default
            cmd = [
                "sonic-annotator", "-d", plugin,
                "-w", "csv", "--csv-stderr",
                file_path
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0 and proc.stdout.strip():
                # Parse CSV output: timestamp, value
                lines = proc.stdout.strip().split('\n')
                values = []
                for line in lines:
                    if line.strip():
                        parts = line.split(',')
                        if len(parts) >= 2:
                            try:
                                values.append(float(parts[1]))
                            except ValueError:
                                pass
                if values:
                    results[plugin] = {
                        "count": len(values),
                        "mean": float(np.mean(values)) if len(values) else None,
                        "values": values[:100]  # cap size
                    }
    except Exception as e:
        results["_error"] = str(e)

    return results


def extract_batch(
    directory: str,
    pattern: str = "*.wav",
    output_format: str = "csv",
    output_file: Optional[str] = None,
    features: Optional[List[str]] = None
) -> str:
    """
    Recursively analyze all audio files in a directory and write results.

    Parameters
    ----------
    directory : str
        Root directory to scan
    pattern : str, default "*.wav"
        Glob pattern for file matching (relative to directory). Use "**/*.wav" for recursive.
    output_format : {'csv', 'json', 'jsonl'}, default 'csv'
        Output file format
    output_file : str, optional
        Output path. If None, writes to directory name_timestamp.ext
    features : list of str, optional
        Passed to analyze() to limit feature set

    Returns
    -------
    str
        Path to written output file
    """
    from pathlib import Path

    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    # Discover files
    files = list(root.glob(pattern))
    # Also support recursive pattern
    if "**" in pattern:
        files = list(root.rglob(pattern.replace("**/", "")))

    if not files:
        print(f"No files matching {pattern} in {directory}")
        return ""

    # Analyze each
    records = []
    print(f"Analyzing {len(files)} files...")
    for i, filepath in enumerate(files, 1):
        try:
            rel = filepath.relative_to(root)
            print(f"[{i}/{len(files)}] {rel}")
            features_dict = analyze(str(filepath), features=features)
            record = {"file": str(rel), **features_dict}
            records.append(record)
        except Exception as e:
            print(f"  ERROR: {e}")
            records.append({"file": str(rel), "_error": str(e)})

    # Write output
    if output_file is None:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{root.name}_analysis_{ts}.{output_format}"

    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "csv":
        # Flatten nested dicts (mfcc, vamp_plugins) as JSON strings
        fieldnames = set()
        flattened = []
        for rec in records:
            flat = {"file": rec["file"]}
            for k, v in rec.items():
                if k == "file":
                    continue
                if isinstance(v, dict):
                    flat[k] = json.dumps(v, ensure_ascii=False)
                else:
                    flat[k] = v
                fieldnames.add(k)
            flattened.append(flat)

        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(flattened)

    elif output_format == "json":
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    elif output_format == "jsonl":
        with out_path.open("w", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    else:
        raise ValueError(f"Unsupported output_format: {output_format}")

    print(f"Wrote {len(records)} records to {out_path}")
    return str(out_path)


# Public interface
__all__ = ["analyze", "probe", "extract_batch"]
