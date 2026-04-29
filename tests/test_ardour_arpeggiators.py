"""
Tests for ardour-automator.arpeggiators subskill.

Test coverage:
  • Render tests — always run, verify Lua script generation (structure, parameters)
  • Wrapper unit tests — use mocks to verify run_*_arp() calls pipeline.run_script correctly
  • Integration tests — SKIPPED (require full Ardour session + MIDI processing; out of scope)

Real Ardour execution of Lua scripts is covered separately in test_ardour_automator.py.
"""
import sys
import re
import pytest
from unittest.mock import MagicMock

from conftest import import_skill_module

# Pre-load modules so sys.modules contains their spec handles
_ = import_skill_module("ardour-automator", "arpeggiators")
_ = import_skill_module("ardour-automator", "pipeline")


def _pipeline_mod():
    return sys.modules['skills.ardour-automator.pipeline']


# ============================================================================
# RENDER TESTS — always run, verify Lua generation
# ============================================================================

@pytest.fixture(scope="session")
def arp():
    return import_skill_module("ardour-automator", "arpeggiators")


class TestRenderSimpleArp:
    """Structure and parameter rendering for simple_arp."""

    def test_contains_core_elements(self, arp):
        script = arp.render_simple_arp(pattern=3, division=2, latch=1)
        assert 'ardour {' in script
        assert 'Division' in script
        assert 'Latch' in script
        assert 'Pattern' in script
        assert '["3 exclusive"] = 3' in script
        assert 'dsp_run' in script
        assert 'midiout' in script
        assert 'Temporal.TempoMap.read()' in script
        assert script.count('function') >= 3

    def test_custom_name(self, arp):
        script = arp.render_simple_arp(name="MyArp")
        assert 'MyArp' in script
        assert re.search(r'name\s*=\s*"MyArp"', script)

    def test_presets_exist(self, arp):
        script = arp.render_simple_arp()
        assert '"0 default"' in script
        assert '"1 latch"' in script
        assert '"2 latch+sync"' in script

    def test_parameter_values_appear(self, arp):
        script = arp.render_simple_arp(division=4, octave_up=2, vel1=110)
        assert re.search(r'Division\s*=\s*4', script)


class TestRenderBarlowArp:
    """Structure and indispensability logic for barlow_arp."""

    def test_includes_indispensability(self, arp):
        script = arp.render_barlow_arp(division=3, min_filter=0.2, max_filter=0.8)
        assert 'barlow' in script
        assert 'indisp' in script
        assert 'Min Filter' in script
        assert 'Max Filter' in script
        assert 'compute_indisp' in script
        assert 'w_norm' in script

    def test_debug_level(self, arp):
        script = arp.render_barlow_arp(debug=2)
        assert 'debug = 2' in script


class TestRenderRaptorArp:
    """Structure and advanced filters for raptor_arp."""

    def test_includes_filters(self, arp):
        script = arp.render_raptor_arp(pref=0.8, hmin=0.1, hmax=0.9)
        assert 'raptor' in script.lower()
        assert 'hmin' in script and 'hmax' in script
        assert 'pref' in script
        assert 'smin' in script and 'smax' in script

    def test_mode_strings(self, arp):
        for mode, name in [(0, 'random'), (1, 'up'), (2, 'down'), (3, 'up-down'), (4, 'down-up'), (5, 'outside-in')]:
            script = arp.render_raptor_arp(mode=mode)
            assert name in script.lower(), f"mode {mode} ({name}) should appear in script"


# ============================================================================
# WRAPPER UNIT TESTS — mocks; always run
# ============================================================================

class TestConvenienceWrappers:
    """run_*_arp() wrappers should call pipeline.run_script with correct flags."""

    def test_run_simple_arp_calls_pipeline(self, arp, monkeypatch):
        mock = MagicMock(return_value={'success': True, 'command': 'ardour6-lua /tmp/x.lua'})
        monkeypatch.setattr(_pipeline_mod(), 'run_script', mock)

        result = arp.run_simple_arp(pattern=1, division=2, latch=True, dry_run=True)

        assert result['success'] is True
        mock.assert_called_once()
        _, kwargs = mock.call_args
        assert kwargs['dry_run'] is True
        assert kwargs.get('cleanup', False) is False

    def test_run_barlow_arp(self, arp, monkeypatch):
        mock = MagicMock(return_value={'success': True})
        monkeypatch.setattr(_pipeline_mod(), 'run_script', mock)

        result = arp.run_barlow_arp(division=3, min_filter=0.2, dry_run=False)
        assert result['success']

    def test_run_raptor_arp(self, arp, monkeypatch):
        mock = MagicMock(return_value={'success': True})
        monkeypatch.setattr(_pipeline_mod(), 'run_script', mock)

        result = arp.run_raptor_arp(mode=5, nmax=3, pref=0.5)
        assert result['success']

    def test_cleanup_flag_respected(self, arp, monkeypatch):
        mock = MagicMock(return_value={'success': True})
        monkeypatch.setattr(_pipeline_mod(), 'run_script', mock)

        arp.run_simple_arp(cleanup=True)
        _, kwargs = mock.call_args
        assert kwargs.get('cleanup') is True


# ============================================================================
# INTEGRATION NOTE
# ============================================================================

def test_integration_requires_full_ardour_session():
    """
    Note: Actual execution of DSP arpeggiators inside a running Ardour session
    (with MIDI I/O and real-time processing) requires:
      - An .ardour session on disk
      - A track with the arpeggiator plugin instantiated
      - MIDI input feeding the plugin
      - Rendering or real-time capture

    That full E2E workflow is out of scope for unit tests here.  The existing
    test_ardour_automator.py::test_run_script_actually_executes_lua already validates
    that Ardour's Lua interpreter runs and returns exit-code 0 on a trivial script.

    If you want to add a full integration test, create a fixture that:
      1. Creates a minimal Ardour session with one MIDI track
      2. Loads the generated arpeggiator Lua as a plugin
      3. Feeds a test MIDI clip
      4. Renders output and verifies note generation
    """
    pass  # marker test — documentation only
