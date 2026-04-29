"""
Ardour Automator — headless Ardour DAW control via Lua scripting.

Ardour provides several CLI entry points for automation:
  - ardour6-lua  : Lua interpreter with Ardour bindings
  - luasession   : Standalone session access tool
  - ardour --script <script.lua>  : Run script in Ardour context

This skill wraps these tools for batch/automated workflows.
"""
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------------
# Availability detection
# ---------------------------------------------------------------------------
ARDour_AVAILABLE = False
ARDour_CLI = None

for candidate in ["ardour6-lua", "luasession", "ardour"]:
    path = shutil.which(candidate)
    if path is not None:
        ARDour_AVAILABLE = True
        ARDour_CLI = candidate
        break

ARDour_VERSION = None
if ARDour_AVAILABLE:
    try:
        # Try to get version; results vary by binary
        result = subprocess.run(
            [ARDour_CLI, "--version"] if ARDour_CLI != "ardour" else [ARDour_CLI, "--help"],
            capture_output=True, text=True, timeout=5
        )
        ARDour_VERSION = result.stdout.strip().split("\n")[0] if result.returncode == 0 else None
    except Exception:
        pass  # version not critical


def _check_ardour():
    """Raise informative error if Ardour CLI is not installed."""
    if not ARDour_AVAILABLE:
        raise RuntimeError(
            "Ardour CLI tool not found. Install Ardour and ensure one of:\n"
            "  - ardour6-lua\n"
            "  - luasession\n"
            "  - ardour\n"
            "is in your PATH."
        )


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def run_script(
    script_path: str,
    session_path: Optional[str] = None,
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute a Lua automation script via Ardour's CLI.

    Parameters
    ----------
    script_path : str
        Path to the .lua automation script.
    session_path : str, optional
        Path to .ardour session directory. If provided, passed to script via
        environment variable or argument.
    dry_run : bool
        If True, build command and return without executing.
    **kwargs
        Additional options (e.g., {arg=value} passed as --key value).

    Returns
    -------
    dict
        {success, command, output?, error?}
    """
    # When actually executing, Ardour must be installed
    if not dry_run:
        _check_ardour()

    script = Path(script_path).resolve()
    if not script.exists():
        return {"success": False, "error": f"Script not found: {script_path}"}

    # Determine which CLI binary to use. For dry runs, allow a placeholder
    # when Ardour is not installed so command construction still works.
    cli = ARDour_CLI if ARDour_AVAILABLE else "ardour6-lua"

    # Build command
    cmd = [cli]

    # Ardour specifics:
    # - ardour6-lua: just run with script as arg, session via env/arg
    # - luasession: may need --session flag
    # - ardour --script: use --script flag
    if cli == "ardour6-lua":
        cmd.append(str(script))
        if session_path:
            # Lua scripts can access ARDOUR_SESSION env var or arg
            cmd.extend(["--session", str(session_path)])
    elif cli == "luasession":
        cmd.extend(["--script", str(script)])
        if session_path:
            cmd.extend(["--session", str(session_path)])
    else:  # generic ardour
        cmd.extend(["--script", str(script)])
        if session_path:
            cmd.extend(["--session", str(session_path)])

    # Merge any extra CLI args from kwargs
    for key, val in kwargs.items():
        flag = f"--{key}"
        if isinstance(val, bool) and val:
            cmd.append(flag)
        else:
            cmd.extend([flag, str(val)])

    if dry_run:
        return {"success": True, "dry_run": True, "command": " ".join(cmd)}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=kwargs.get("timeout", 300),
            cwd=session_path if session_path else script.parent
        )
        success = result.returncode == 0
        return {
            "success": success,
            "command": " ".join(cmd),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "error": None if success else result.stderr.strip() or result.stdout.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Ardour script execution timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def probe(session_path: str) -> Dict[str, Any]:
    """
    Get metadata about an Ardour session.

    Probes a .ardour session directory and returns track list, duration,
    sample rate, and other session-level info.

    Parameters
    ----------
    session_path : str
        Path to the .ardour session directory.

    Returns
    -------
    dict
        {success, tracks?, duration?, sample_rate?, error?}
    """
    session = Path(session_path)
    if not session.exists() or not session.is_dir():
        return {"success": False, "error": f"Session not found: {session_path}"}

    _check_ardour()

    # Approach: run a minimal Lua script via ardour6-lua that prints JSON
    # For now, return a stub that reads session.xml (Ardour 6+ format)
    session_xml = session / "session.xml"
    if not session_xml.exists():
        return {"success": False, "error": f"Not a valid Ardour session (no session.xml): {session_path}"}

    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(session_xml)
        root = tree.getroot()
        # Very minimal extraction
        name_el = root.find(".//name")
        name = name_el.text if name_el is not None else session.name

        # Count routes/tracks (simplified)
        routes = root.findall(".//Route")
        track_count = len(routes)

        # Get sample rate if present
        sr_el = root.find(".//sample-rate")
        sample_rate = int(sr_el.text) if sr_el is not None and sr_el.text else None

        return {
            "success": True,
            "session": name,
            "tracks": track_count,
            "sample_rate": sample_rate,
            "path": str(session),
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to parse session XML: {e}"}


def export(
    session_path: str,
    output_path: str,
    format: str = "wav",
    dry_run: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Render an Ardour session to an audio file.

    Parameters
    ----------
    session_path : str
        Path to the .ardour session directory.
    output_path : str
        Destination file path.
    format : str
        Output format (wav, flac, mp3, etc.). Default: wav
    dry_run : bool
        Preview command without executing.
    **kwargs
        Additional export options (bitrate, quality, etc.).

    Returns
    -------
    dict
        {success, command?, output?, error?}
    """
    session = Path(session_path)
    output = Path(output_path)

    if not session.exists():
        return {"success": False, "error": f"Session not found: {session_path}"}

    _check_ardour()

    # Build export command using appropriate Ardour CLI
    cmd = [ARDour_CLI]

    if ARDour_CLI == "ardour":
        cmd.extend(["--render", str(session), "--output", str(output)])
        if format:
            cmd.extend(["--format", format])
    else:
        # Use run_script approach with a built-in Lua export snippet
        # For dry-run, just show that we'd call ardour6-lua with a script
        # In real implementation, would write a temp Lua script
        cmd = [ARDour_CLI, "--export", str(output), str(session)]

    # Merge extra options
    for key, val in kwargs.items():
        flag = f"--{key}"
        if isinstance(val, bool) and val:
            cmd.append(flag)
        else:
            cmd.extend([flag, str(val)])

    if dry_run:
        return {"success": True, "dry_run": True, "command": " ".join(cmd)}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=kwargs.get("timeout", 600),
            cwd=session
        )
        success = result.returncode == 0 and output.exists()
        return {
            "success": success,
            "command": " ".join(cmd),
            "output": str(output) if success else None,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "error": None if success else result.stderr.strip() or "Export failed",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Export timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}
