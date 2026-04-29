"""
Batch Processor — orchestrates daw-master skills to process audio file directories.

Features:
- Recursive directory scanning with glob patterns
- Parallel file processing (multiprocessing)
- Progress and error aggregation
- JSON/CSV manifest output
- Resume support (overwrite control)
"""

import json
import sys
import types
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

# ---------------------------------------------------------------------------
# Paths setup
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
# Directory layout:
#   .../skills/daw-master/batch-processor/pipeline.py
_DAW_MASTER_DIR = _THIS_FILE.parents[1]      # skills/daw-master
_SKILLS_PARENT = _DAW_MASTER_DIR.parent       # skills/  (top-level skills namespace)

# ---------------------------------------------------------------------------
# Engine registry: engine -> (skill_dir_name_under_daw-master, function_name)
# Skill directory names use hyphens (e.g., sox-engine).
# ---------------------------------------------------------------------------
_ENGINE_MAP = {
    'sox':                 ('sox-engine',        'transform'),
    'sox-engine':          ('sox-engine',        'transform'),
    'ffmpeg':              ('ffmpeg-audio',      'transform'),
    'ffmpeg-audio':        ('ffmpeg-audio',      'transform'),
    'rubberband':          ('rubber-band-engine', 'transform'),
    'rubber-band-engine': ('rubber-band-engine', 'transform'),
    'dawdreamer':          ('dawdreamer',        'transform'),
}

# Cache for loaded transform functions
_TRANSFORM_CACHE: Dict[str, Any] = {}

def _ensure_skills_namespace(skill_dir: Path, skill_name: str) -> None:
    """
    Ensure the 'skills' namespace package and 'skills.<skill_name>' parent package
    exist in sys.modules, mirroring conftest.import_skill_module.
    """
    if "skills" not in sys.modules:
        skills_pkg = types.ModuleType("skills")
        skills_pkg.__path__ = [str(_SKILLS_PARENT)]
        sys.modules["skills"] = skills_pkg

    parent_pkg_name = f"skills.{skill_name}"
    if parent_pkg_name not in sys.modules:
        parent_pkg = types.ModuleType(parent_pkg_name)
        parent_pkg.__path__ = [str(skill_dir)]
        parent_pkg.__package__ = "skills"
        sys.modules[parent_pkg_name] = parent_pkg

def _resolve_skill(engine: str):
    """
    Lazily import and return the transform function for the given engine.
    Uses dynamic module loading from the skill's pipeline.py with caching.
    """
    if engine not in _ENGINE_MAP:
        raise ValueError(
            f"Unknown engine: '{engine}'. Available: {list(_ENGINE_MAP.keys())}"
        )
    if engine in _TRANSFORM_CACHE:
        return _TRANSFORM_CACHE[engine]

    skill_dir_name, func_name = _ENGINE_MAP[engine]
    # Skill lives under skills/daw-master/<skill_dir_name>
    skill_dir = _DAW_MASTER_DIR / skill_dir_name
    if not skill_dir.exists():
        raise RuntimeError(f"Skill directory not found: {skill_dir}")

    # Set up namespace packages
    _ensure_skills_namespace(skill_dir, skill_dir_name)

    module_path = skill_dir / "pipeline.py"
    module_full_name = f"skills.{skill_dir_name}.pipeline"

    spec = importlib.util.spec_from_file_location(module_full_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {module_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_full_name] = mod
    spec.loader.exec_module(mod)

    transform_func = getattr(mod, func_name, None)
    if transform_func is None:
        raise AttributeError(f"Skill '{skill_dir_name}' does not define '{func_name}'")

    _TRANSFORM_CACHE[engine] = transform_func
    return transform_func

def process_file(
    input_path: Path,
    output_path: Path,
    pipeline: List[Dict],
    engine: str = 'sox',
    dry_run: bool = False,
    overwrite: bool = False,
    **engine_kwargs
) -> Dict[str, Any]:
    """
    Process a single audio file with the given pipeline.

    Parameters
    ----------
    input_path : Path
        Source audio file.
    output_path : Path
        Destination file path.
    pipeline : list of dict
        Transformation operations.
    engine : str
        Engine name ("sox", "ffmpeg", "dawdreamer", "rubberband").
    dry_run : bool
        Validate without executing.
    overwrite : bool
        Overwrite existing output if True.
    **engine_kwargs
        Additional keyword arguments passed to the engine transform.

    Returns
    -------
    dict
        {success, input, output, error?, skipped?, dry_run?}
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        return {"success": False, "input": str(input_path), "output": str(output_path),
                "error": "Input file not found"}

    if output_path.exists() and not overwrite:
        return {"success": True, "input": str(input_path), "output": str(output_path),
                "skipped": True, "reason": "output already exists"}

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        transform_func = _resolve_skill(engine)
        result = transform_func(
            input=str(input_path),
            pipeline=pipeline,
            output=str(output_path),
            dry_run=dry_run,
            **engine_kwargs
        )
        return {"success": result.get("success", False), "input": str(input_path),
                "output": str(output_path), **result}
    except Exception as e:
        return {"success": False, "input": str(input_path), "output": str(output_path),
                "error": str(e)}

def process_directory(
    input_dir: str,
    output_dir: str,
    pipeline: List[Dict],
    engine: str = 'sox',
    pattern: str = "**/*.wav",
    dry_run: bool = False,
    overwrite: bool = False,
    max_workers: int = 4,
    manifest_path: Optional[str] = None,
    **engine_kwargs
) -> Dict[str, Any]:
    """
    Batch-process all audio files under input_dir matching the glob pattern.

    Parameters
    ----------
    input_dir : str
        Root directory to scan recursively.
    output_dir : str
        Root directory where processed files will be written (mirrored structure).
    pipeline : list of dict
        Transformation operations.
    engine : str
        daw-master engine ("sox", "ffmpeg", "dawdreamer", "rubberband").
    pattern : str
        Glob pattern relative to input_dir (default: "**/*.wav").
    dry_run : bool
        Report actions without processing.
    overwrite : bool
        Overwrite existing output files.
    max_workers : int
        Parallel workers (default 4). Set to 1 for serial execution.
    manifest_path : str, optional
        If provided, write JSON manifest of all results to this path.

    Returns
    -------
    dict
        Summary: {processed, skipped, failed, total, errors: [...]}
    """
    input_root = Path(input_dir).resolve()
    output_root = Path(output_dir).resolve()

    if not input_root.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    files = [f for f in input_root.glob(pattern) if f.is_file()]
    total = len(files)

    if total == 0:
        return {"processed": 0, "skipped": 0, "failed": 0, "total": 0, "errors": []}

    if dry_run:
        print(f"[DRY-RUN] Process {total} files with engine '{engine}'")
        print(f"  Input:  {input_root}")
        print(f"  Output: {output_root}")
        print(f"  Pattern: {pattern}")
        print(f"  Pipeline: {json.dumps(pipeline, indent=2)}")
        return {"processed": 0, "skipped": 0, "failed": 0, "total": total, "dry_run": True}

    results = []
    errors = []

    if max_workers == 1:
        for in_file in files:
            rel = in_file.relative_to(input_root)
            out_file = output_root / rel
            res = process_file(in_file, out_file, pipeline, engine, overwrite=overwrite,
                               **engine_kwargs)
            results.append(res)
            if not res["success"]:
                errors.append({"file": str(in_file), "error": res.get("error", "unknown")})
    else:
        with ProcessPoolExecutor(max_workers=max_workers) as exe:
            futures = {
                exe.submit(process_file, in_file,
                           output_root / in_file.relative_to(input_root),
                           pipeline, engine, overwrite=overwrite, **engine_kwargs): in_file
                for in_file in files
            }
            for fut in as_completed(futures):
                res = fut.result()
                results.append(res)
                if not res["success"]:
                    errors.append({"file": str(futures[fut]), "error": res.get("error", "unknown")})

    processed = sum(1 for r in results if r.get("success") and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    failed = sum(1 for r in results if not r.get("success"))

    summary = {
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "total": total,
        "errors": errors,
    }

    if manifest_path:
        manifest = {
            "engine": engine,
            "pipeline": pipeline,
            "summary": summary,
            "files": results,
        }
        Path(manifest_path).write_text(json.dumps(manifest, indent=2))

    return summary

# Convenience alias
batch_transform = process_directory
