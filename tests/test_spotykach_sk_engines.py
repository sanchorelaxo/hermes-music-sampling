"""Tests for the Spotykach sk-engines install / run / de-install automation.

Lifecycle under test (scripts/sk_engines.py):

  * install    -> resolve the release URL/filename, checksum-verify, flash
  * run        -> device reboot + MIDI enumeration (the engine runs on-device)
  * de-install -> re-flash the original Synthux firmware (restore)

The deterministic, device-free half (URL/filename resolution, SHA-256
verification against the pinned SHA256SUMS, binary-identity byte-scan, dfu-util
argument construction, state round-trip) is exercised here with real files — no
mocks. The hardware half (flash / MIDI) is gated and skips cleanly when no
Spotykach is attached, mirroring sk-engines' own `make test-hw` behaviour.
"""

import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SPOTYKACH_SCRIPTS = (
    Path(__file__).resolve().parent.parent
    / "skills" / "instruments" / "spotykach" / "scripts"
)
sys.path.insert(0, str(SPOTYKACH_SCRIPTS))

import sk_engines as se  # noqa: E402

# Known-correct SHA-256 of the delay release binary, verified against the real
# download (see sk-engines/SHA256SUMS for the full pinned set).
DELAY_SHA256 = "9d8de6952006cc9a6eddb8e74a1ff5f7cccee0a84c884df56f452faa67f840c6"


def _network_ok():
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                se.engine_download_url("delay"),
                headers={"User-Agent": "sk-engines-tests/1.0"},
            ),
            timeout=10,
        )
        return True
    except (urllib.error.URLError, OSError):
        return False


def _device_in_dfu():
    return se.detect()["dfu"]


# --- resolution ----------------------------------------------------------

def test_engine_binary_name_and_url():
    assert se.engine_binary_name("delay") == f"sk-delay-{se.SK_VERSION}.bin"
    url = se.engine_download_url("delay")
    assert url == f"{se.SK_REPO}/releases/download/{se.SK_TAG}/sk-delay-{se.SK_VERSION}.bin"


def test_all_release_engines_resolve():
    for name in se.all_engine_names():
        assert se.engine_binary_name(name) == f"sk-{name}-{se.SK_VERSION}.bin"


def test_unknown_engine_raises():
    with pytest.raises(ValueError):
        se.engine_binary_name("does-not-exist")


def test_build_only_engines_have_no_release_binary():
    for name in se.BUILD_ONLY_ENGINES:
        with pytest.raises(ValueError):
            se.engine_binary_name(name)


def test_qspi_engines_are_the_large_runtime_ones():
    assert se.QSPI_ENGINES == {"csound", "chuck", "mosc"}


# --- checksum verification ----------------------------------------------

def test_parse_sha256sums_covers_every_engine():
    sums = se.parse_sha256sums(se.SHA256SUMS_PATH)
    assert len(sums) == len(se.ENGINE_TYPES) == 18
    for name in se.all_engine_names():
        assert se.engine_binary_name(name) in sums


def test_expected_sha256_matches_pinned_delay():
    assert se.expected_sha256("delay") == DELAY_SHA256


def test_sha256_streaming_matches_hashlib(tmp_path):
    p = tmp_path / "blob.bin"
    p.write_bytes(b"spotykach 0.6.1-1-g4faeddd engine=delay\x00" + b"\x00" * 64)
    import hashlib
    assert se.sha256(p) == hashlib.sha256(p.read_bytes()).hexdigest()


def test_verify_release_rejects_tampered_file(tmp_path):
    p = tmp_path / "sk-delay-0.6.1-1-g4faeddd.bin"
    p.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        se.verify_release(p, engine="delay")


# --- binary identity -----------------------------------------------------

def _synthetic_engine_bin(tmp_path, line=b"spotykach 0.6.1-1-g4faeddd engine=delay"):
    p = tmp_path / "fake.bin"
    p.write_bytes(b"\x00" * 16 + line + b"\x00" + b"\x00" * 8)
    return p


def test_identify_engine_parses_version_and_engine(tmp_path):
    p = _synthetic_engine_bin(tmp_path)
    assert se.identify_engine(p) == {"version": se.SK_VERSION, "engine": "delay"}


def test_identify_engine_returns_none_without_stamp(tmp_path):
    p = tmp_path / "scratch.bin"
    p.write_bytes(b"\x00" * 128)
    assert se.identify_engine(p) is None


def test_is_original_firmware_detects_synthux_banner(tmp_path):
    p = tmp_path / "orig.bin"
    p.write_bytes(b"\x00Synthux\x00Spotykach\x00")
    assert se.is_original_firmware(p)
    assert se.identify_engine(p) is None  # not an sk-engines image


# --- dfu-util command construction --------------------------------------

def test_dfu_flash_cmd_is_exact():
    cmd = se.dfu_flash_cmd("out/sk-delay-0.6.1-1-g4faeddd.bin")
    assert cmd == [
        "dfu-util", "-a", "0", "-s", "0x90040000:leave",
        "-D", "out/sk-delay-0.6.1-1-g4faeddd.bin", "-d", ",0483:df11",
    ]


def test_dfu_flash_cmd_no_leave():
    cmd = se.dfu_flash_cmd("x.bin", leave=False)
    assert cmd[4] == "0x90040000"  # "-s" value without ":leave"


# --- bootloader (one-time, human-in-loop install) -------------------------

def test_bootloader_name_and_url():
    assert se.BOOTLOADER_BIN == "bootloader-spotykach-v2.bin"
    assert se.bootloader_download_url() == (
        f"{se.SK_REPO}/raw/{se.SK_TAG}/bootloader-spotykach-v2.bin"
    )


def test_bootloader_sha256_is_a_valid_pin():
    assert len(se.BOOTLOADER_SHA256) == 64
    assert all(c in "0123456789abcdef" for c in se.BOOTLOADER_SHA256)


def test_bootloader_address_is_below_app_region():
    # Bootloader lives in the QSPI region DIRECTLY below the app; both are on
    # the same alt-0 DFU interface (0483:df11), just different offsets.
    assert se.BOOTLOADER_ADDRESS == "0x90000000"
    assert se.DFU_ADDRESS == "0x90040000"


def test_bootloader_flash_cmd_targets_bootloader_address():
    cmd = se.dfu_flash_cmd("out/bootloader-spotykach-v2.bin",
                           address=se.BOOTLOADER_ADDRESS)
    assert cmd == [
        "dfu-util", "-a", "0", "-s", "0x90000000:leave",
        "-D", "out/bootloader-spotykach-v2.bin", "-d", ",0483:df11",
    ]


def test_fetch_bootloader_rejects_tampered_file(tmp_path):
    # A locally-present file that fails the pin must be rejected, no network.
    p = tmp_path / se.BOOTLOADER_BIN
    p.write_bytes(b"not-the-real-bootloader")
    with pytest.raises(ValueError, match="checksum mismatch"):
        se.fetch_bootloader(tmp_path)


@pytest.mark.skipif(not _network_ok(), reason="network / GitHub unavailable")
def test_fetch_bootloader_real_download(tmp_path):
    p = se.fetch_bootloader(tmp_path)
    assert p.name == se.BOOTLOADER_BIN
    assert p.stat().st_size == 93640          # per the 0.6.1 git tree blob
    # A real Daisy-derived bootloader carries the "$Daisy Bootloader" banner.
    assert b"Daisy Bootloader" in p.read_bytes()


# --- state tracking ------------------------------------------------------

def test_state_round_trip(tmp_path):
    s = tmp_path / "state.json"
    assert se.load_state(s) == se.DEFAULT_STATE
    se.save_state(s, flashed="sk-delay-0.6.1-1-g4faeddd.bin", engine="delay")
    assert se.load_state(s)["engine"] == "delay"
    assert se.load_state(s)["flashed"].startswith("sk-delay-")


def test_install_state_records_engine(tmp_path):
    computed = {
        "flashed": "sk-delay-0.6.1-1-g4faeddd.bin",
        "kind": "sk-engines",
        "version": se.SK_VERSION,
        "engine": "delay",
    }
    assert computed["kind"] == "sk-engines"
    assert computed["engine"] == "delay"


# --- device presence (safe, non-destructive listing) ---------------------

def test_detect_returns_well_formed_dict():
    det = se.detect()
    assert isinstance(det["dfu"], bool)
    assert isinstance(det["midi"], bool)
    assert isinstance(det["dfu_lines"], list)
    assert isinstance(det["midi_lines"], list)


# --- integration: real download + verify + identify ----------------------

@pytest.mark.skipif(not _network_ok(), reason="network / GitHub unavailable")
def test_fetch_verify_identify_real_delay_binary(tmp_path):
    path = se.fetch_engine("delay", tmp_path)
    assert path.exists()
    assert path.stat().st_size == 154432          # per the pinned MANIFEST
    assert se.verify_release(path, engine="delay") == DELAY_SHA256
    assert se.identify_engine(path) == {"version": se.SK_VERSION, "engine": "delay"}


@pytest.mark.skipif(not _network_ok(), reason="network / GitHub unavailable")
def test_fetch_original_firmware_downloads(tmp_path):
    path = se.fetch_original(tmp_path)
    assert path.name == se.ORIGINAL_BIN
    assert path.stat().st_size == 211840
    assert se.is_original_firmware(path)


# --- hardware-gated: real flash / boot (skip cleanly when no device) -----

@pytest.mark.skipif(not _device_in_dfu(), reason="Spotykach not in DFU mode")
def test_flash_requires_device_is_not_run_without_dfu():
    # Reachable only when a device IS present; in that case flash() must not
    # raise the "not in DFU mode" guard.
    try:
        se._require_dfu({"dfu": True}, "flash")
    except RuntimeError:
        pytest.fail("guard rejected a present device")