"""Tests for carla-rack DAW skill."""

import pytest
from conftest import import_skill_module


# ---------------------------------------------------------------------------
# 1. Module import & availability detection
# ---------------------------------------------------------------------------

def test_carla_rack_module_imports():
    """CarlaRack module should be importable from skills.daw-master."""
    mod = import_skill_module("carla-rack", "pipeline")
    assert hasattr(mod, "CarlaRack")
    assert hasattr(mod, "CARLA_AVAILABLE")
    assert isinstance(mod.CARLA_AVAILABLE, bool)


def test_carla_rack_exposes_expected_api():
    """CarlaRack should expose a rack of plugins and render capabilities."""
    mod = import_skill_module("carla-rack", "pipeline")
    if not mod.CARLA_AVAILABLE:
        pytest.skip("Carla binary not found on PATH")
    # Should provide rack construction and processing
    assert hasattr(mod.CarlaRack, "add_plugin")
    assert hasattr(mod.CarlaRack, "chain")
    assert hasattr(mod.CarlaRack, "render_once")
