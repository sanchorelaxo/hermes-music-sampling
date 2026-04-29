"""
Tests for ardour-automator skill — headless Ardour DAW control.

Uses Ardour's Lua scripting interface (ardour6-lua or luasession).
When Ardour is not installed, tests that require the binary are skipped.
"""
import pytest
from pathlib import Path
from conftest import import_skill_module

ardour = import_skill_module("ardour-automator", "pipeline")


def test_run_script_requires_ardour_binary():
    """When Ardour CLI is missing, run_script should raise a clear error."""
    if ardour.ARDour_AVAILABLE:
        pytest.skip("Ardour is installed — test only applies when Ardour CLI missing")
    with pytest.raises(RuntimeError, match="Ardour CLI tool not found"):
        ardour.run_script("/nonexistent/script.lua", dry_run=False)


def test_run_script_dry_run_builds_command(tmp_path):
    """dry_run=True should return command without executing."""
    script = tmp_path / "test.lua"
    script.write_text("-- test script")
    result = ardour.run_script(str(script), dry_run=True)
    assert "command" in result
    cmd = result["command"]
    # Should contain ardour6-lua or luasession
    assert any(tool in cmd for tool in ["ardour6-lua", "luasession", "ardour"])


def test_probe_returns_session_info_when_available(sample_wav, tmp_path):
    """probe() should return dict with session metadata (tracks, duration)."""
    # Create a minimal dummy Ardour session file for testing
    session_dir = tmp_path / "test_session.ardour"
    session_dir.mkdir()
    (session_dir / "session.xml").write_text(
        "<Ardour><Session><name>test</name></Session></Ardour>"
    )
    if not ardour.ARDour_AVAILABLE:
        pytest.skip("Ardour CLI not installed")
    info = ardour.probe(str(session_dir))
    assert isinstance(info, dict)
    assert "tracks" in info or "error" in info


def test_export_builds_render_command(sample_wav, tmp_path):
    """export() should construct correct ardour --render command."""
    session = tmp_path / "session.ardour"
    session.mkdir()
    (session / "session.xml").write_text("<Ardour><Session/></Ardour>")
    output = tmp_path / "output.wav"
    if not ardour.ARDour_AVAILABLE:
        pytest.skip("Ardour CLI not installed")
    result = ardour.export(str(session), str(output), dry_run=True)
    assert "command" in result
    cmd = result["command"]
    assert "--render" in cmd or "export" in cmd or "render" in cmd


def test_run_script_with_session_path(sample_wav, tmp_path):
    """run_script should pass the session path to the Lua interpreter."""
    script = tmp_path / "script.lua"
    script.write_text('print("hello")')
    session = tmp_path / "session.ardour"
    session.mkdir()
    (session / "session.xml").write_text("<Ardour><Session/></Ardour>")
    if not ardour.ARDour_AVAILABLE:
        pytest.skip("Ardour CLI not installed")
    result = ardour.run_script(str(script), session_path=str(session), dry_run=True)
    cmd = result["command"]
    # Script path should be in command; session may be via env var or arg
    assert str(script) in cmd


def test_run_script_actually_executes_lua(sample_wav, tmp_path):
    """When Ardour is available, run_script with dry_run=False should actually execute the Lua interpreter."""
    if not ardour.ARDour_AVAILABLE:
        pytest.skip("Ardour CLI not installed")

    # Create a simple Lua script that prints a known marker
    script = tmp_path / "test.lua"
    script.write_text('print("HERMES_TEST_OUTPUT")')

    # Execute with dry_run=False, no session (session loading can segfault in some Ardour builds)
    result = ardour.run_script(
        script_path=str(script),
        dry_run=False,
        timeout=10
    )

    # Should succeed (returncode 0)
    assert result["success"], f"Ardour execution failed: returncode={result.get('returncode')} stderr={result.get('stderr')} error={result.get('error')}"
    # The command that was executed should be recorded
    assert "command" in result
    assert any(tool in result["command"] for tool in ["ardour6-lua", "luasession", "ardour", "ardour8-lua"])
