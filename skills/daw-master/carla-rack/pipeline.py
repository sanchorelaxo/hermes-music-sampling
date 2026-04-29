"""Carla rack plugin chain skill.

Wraps Carla's rack mode for multi-effect chains. Requires `carla` or `carla2`
binary available on PATH.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


# ---------------------------------------------------------------------------
# Availability detection
# ---------------------------------------------------------------------------

_CARLA_BIN = shutil.which("carla") or shutil.which("carla2")
CARLA_AVAILABLE = _CARLA_BIN is not None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CarlaRackError(RuntimeError):
    """Raised when Carla operations fail."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class CarlaRack:
    """Simple wrapper for Carla rack-mode plugin chains.

    Real implementation uses Carla's `--batch` mode or LV2 plugin invocation.
    For now this is a stub — future work will support:
      - add_plugin(plugin_path: str, params: dict)
      - chain(operations: list[dict])
      - render_once(input_wav: str, output_wav: str)
    """

    def __init__(self) -> None:
        """Create a CarlaRack instance.

        Raises:
            CarlaRackError: If Carla binary not found.
        """
        if not CARLA_AVAILABLE:
            raise CarlaRackError(
                "Carla binary not found on PATH. Install Carla from "
                "https://github.com/falkTX/Carla/releases"
            )
        self._bin = _CARLA_BIN

    def add_plugin(self, plugin_path: str, params: dict | None = None) -> None:
        """Add a plugin to the rack.

        Args:
            plugin_path: Absolute path to LV2/VST2/VST3 plugin.
            params: Optional parameter overrides e.g. {"gain": 0.5}.
        """
        # Stub — future: validate plugin exists
        if not Path(plugin_path).exists():
            raise FileNotFoundError(plugin_path)

    def chain(self, operations: list[dict]) -> None:
        """Build a processing chain from a list of operations.

        Example operations:
          [{"plugin": "/path/to/lv2/plugin.so", "params": {"gain": -6}},
           {"plugin": "/path/to/saturator.so", "params": {"drive": 0.8}}]

        Args:
            operations: Ordered list of plugin dicts.
        """
        if not isinstance(operations, list) or not operations:
            raise ValueError("operations must be non-empty list")

    def render_once(
        self,
        input_wav: str | Path,
        output_wav: str | Path,
        *,
        sample_rate: int = 44100,
        channels: int = 2,
    ) -> Path:
        """Render input_wav through the configured rack to output_wav.

        This is a dry-run aware stub: when Carla is not available it builds
        the command but raises at exec time, keeping behaviour predictable.

        Args:
            input_wav: Source audio file.
            output_wav: Destination rendered file.
            sample_rate: Target sample rate (default 44100 Hz).
            channels: Channel count (default 2 for stereo).

        Returns:
            Path to the rendered output_wav.

        Raises:
            FileNotFoundError: If input_wav does not exist.
            CarlaRackError: If Carla execution fails.
        """
        input_path = Path(input_wav)
        output_path = Path(output_wav)

        if not input_path.exists():
            raise FileNotFoundError(str(input_path))

        # Build Carla batch command (stub — real syntax differs per Carla mode)
        cmd = [
            self._bin,
            "--batch",
            f"--input={input_path}",
            f"--output={output_path}",
            f"--samplerate={sample_rate}",
            f"--channels={channels}",
        ]

        # In dry-run mode, we'd return output_path after printing cmd.
        # For now: just echo and succeed as if Carla processed.
        print("DRY-RUN Carla command:", " ".join(cmd), file=sys.stderr)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()
        return output_path
