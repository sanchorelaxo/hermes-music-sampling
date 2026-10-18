#!/usr/bin/env python3
"""Spotykach sk-engines — install / run / de-install automation.

Manages the full lifecycle of the community firmware project
https://github.com/shakfu/sk-engines on a Synthux Spotykach:

  * install   download a release engine image (checksum-verified) and flash it
  * run       the device leaves DFU and boots the engine; verify success as
              "DFU mode: no" — SRAM engines ship USB_MIDI=0, so MIDI is NOT a
              valid "running" signal for them (see references/firmware.md)
  * de-install  restore the original Synthux firmware (install / restore cmd)
  * bootloader  flash the sk-engines bootloader (one-time, risky, human-in-loop)

Lifecycle summary:

    flash       <- place one engine binary onto the device (install)
    boot        <- device leaves DFU (run; "DFU mode: no" == booted)
    bootloader  <- one-time bootloader install (required for engines to run)
    restore     <- re-flash the original Synthux firmware (de-install)

The deterministic, device-free logic (URL/filename resolution, checksum
verification, binary identity, dfu-util argument construction, state tracking)
is fully testable headlessly. The steps that touch hardware (flash / boot /
MIDI) are gated on device presence and skip cleanly in tests when no device is
attached — mirroring sk-engines' own `make test-hw` "skip when no device" rule.

    python sk_engines.py list
    python sk_engines.py download delay -o out/
    python sk_engines.py verify out/sk-delay-0.6.1-1-g4faeddd.bin
    python sk_engines.py install delay
    python sk_engines.py bootloader --yes   # one-time (device in DFU mode)
    python sk_engines.py restore
    python sk_engines.py status

Parallel to scripts/wav_builder.py (the SD-card pipeline); both are headless
CLI automations of Spotykach workflows and are covered by unit tests.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

# --- sk-engines release constants (pinned to the latest tagged release) ---
SK_REPO = "https://github.com/shakfu/sk-engines"
SK_TAG = "0.6.1"
# Version string the build stamps into each binary ("spotykach <ver> engine=<n>").
SK_VERSION = "0.6.1-1-g4faeddd"
SK_RELEASE_BASE = f"{SK_REPO}/releases/download/{SK_TAG}"

# Engines published as release binaries, with their execution model. QSPI apps
# (csound / chuck / mosc) execute in place from QSPI flash because their
# language runtimes exceed the SRAM budget; everything else is BOOT_SRAM.
ENGINE_TYPES = {
    "bard": "sram", "chuck": "qspi", "csound": "qspi", "delay": "sram",
    "edrums": "sram", "filter": "sram", "glitch": "sram",
    "graincloud": "sram", "mosc": "qspi", "pstretch": "sram",
    "qdelay": "sram", "radio": "sram", "reso": "sram", "reverb": "sram",
    "shuttle": "sram", "softcut": "sram", "tape": "sram", "voice": "sram",
}
QSPI_ENGINES = {name for name, kind in ENGINE_TYPES.items() if kind == "qspi"}

# Engine targets that exist in the Makefile but are NOT shipped as a release
# binary (they must be built from source with `make -j8 ENGINE=<name>`). The
# default `granular` looper is the most notable: no release image exists.
BUILD_ONLY_ENGINES = {"granular", "passthrough", "chorus", "gigaverb"}

# Original Synthux firmware — the de-install / restore target.
ORIGINAL_REPO = "https://github.com/Synthux-Academy/Spotykach"
ORIGINAL_TAG = "v1.3.1"          # latest stable official release
ORIGINAL_BIN = "spotykach_1.3.1.bin"

# DFU flash parameters (same for sk-engines and official firmware).
DFU_ADDRESS = "0x90040000"       # QSPI application region (first 256 KB reserved)
DFU_VIDPID = ",0483:df11"        # Electrosmith Daisy STM32 DFU device

# sk-engines custom bootloader — one-time, risky install that every engine needs
# to actually run (see the "Bootloader caveat" in references/firmware.md). It is
# shipped *in-tree* (not as a release asset), so its checksum is pinned here.
BOOTLOADER_BIN = "bootloader-spotykach-v2.bin"
BOOTLOADER_SHA256 = "aed25c888b7676bf0bc37a87c743ca9cbb40257b8ab4ed318addcfa122377e56"
BOOTLOADER_ADDRESS = "0x90000000"  # QSPI bootloader region (256 KB, below the app)

# Bundled, pinned release metadata (shipped alongside this script so checksum
# verification is deterministic and offline; see references/).
_HERE = Path(__file__).resolve().parent.parent          # .../spotykach/
REF_DIR = _HERE / "references"
MANIFEST_PATH = REF_DIR / "sk-engines-MANIFEST.txt"
SHA256SUMS_PATH = REF_DIR / "sk-engines-SHA256SUMS"


# --- resolution (device-free) -------------------------------------------

def engine_binary_name(engine):
    """Release filename for an engine, e.g. 'sk-delay-0.6.1-1-g4faeddd.bin'."""
    if engine in BUILD_ONLY_ENGINES:
        raise ValueError(
            f"engine {engine!r} is build-only (no release binary); "
            f"build from source with `make -j8 ENGINE={engine}`"
        )
    if engine not in ENGINE_TYPES:
        raise ValueError(
            f"unknown engine {engine!r}; choose {sorted(ENGINE_TYPES)}"
        )
    return f"sk-{engine}-{SK_VERSION}.bin"


def engine_download_url(engine, tag=SK_TAG):
    """Full release download URL for an engine binary."""
    return f"{SK_REPO}/releases/download/{tag}/{engine_binary_name(engine)}"


def original_download_url(tag=ORIGINAL_TAG):
    """Download URL for the original Synthux firmware (de-install target)."""
    return f"{ORIGINAL_REPO}/releases/download/{tag}/{ORIGINAL_BIN}"


def all_engine_names():
    return sorted(ENGINE_TYPES)


# --- checksum verification (device-free) --------------------------------

def sha256(path):
    """Hex SHA-256 digest of a file, read in a streaming fashion."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sha256sums(path):
    """Parse a SHA256SUMS file into {filename: hexdigest} (drops GNU ``*`` form)."""
    sums = {}
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        digest, _, name = line.partition(" ")
        name = name.strip().lstrip("*")
        if name:
            sums[name] = digest.strip()
    return sums


def expected_sha256(engine):
    """Look up the pinned release checksum for an engine, or None if absent."""
    sums = parse_sha256sums(SHA256SUMS_PATH)
    return sums.get(engine_binary_name(engine))


def verify_release(bin_path, engine=None):
    """Verify ``bin_path`` against the pinned SHA256SUMS.

    When ``engine`` is given, the expected digest is looked up directly;
    otherwise the file's basename is matched. Returns the actual hex digest.
    Raises ``ValueError`` when the file does not match.
    """
    path = Path(bin_path)
    name = engine_binary_name(engine) if engine else path.name
    sums = parse_sha256sums(SHA256SUMS_PATH)
    expected = sums.get(name)
    if expected is None:
        raise ValueError(f"{name} is not in the pinned SHA256SUMS")
    actual = sha256(path)
    if actual != expected:
        raise ValueError(
            f"checksum mismatch for {name}:\n  expected {expected}\n  actual   {actual}"
        )
    return actual


# --- binary identity (device-free, byte-scan only) -----------------------

_IDENTITY_NEEDLE = b"spotykach "  # sk-engines stamps "spotykach <ver> engine=<n>"
_ORIGINAL_NEEDLE = b"Synthux"     # official firmware carries the Synthux banner


def _scan_ascii(path, needle):
    """Return the decoded string starting at the first byte match of ``needle``.

    Scans raw bytes (no host `strings`/toolchain required) so the check is
    deterministic across environments. Returns b"" when absent.
    """
    data = Path(path).read_bytes()
    idx = data.find(needle)
    if idx == -1:
        return ""
    end = data.find(b"\x00", idx)
    stop = end if end != -1 else min(idx + 128, len(data))
    return data[idx:stop].decode("ascii", errors="replace")


def identify_engine(path):
    """Parse an sk-engines binary's identity string.

    Returns ``{"version": ..., "engine": ...}`` or ``None`` if the file does not
    carry a ``spotykach <ver> engine=<name>`` stamp.
    """
    line = _scan_ascii(path, _IDENTITY_NEEDLE)
    if not line.startswith("spotykach "):
        return None
    parts = line.split()
    # expected: ["spotykach", "<version>", "engine=<name>"]
    if len(parts) < 3 or not parts[2].startswith("engine="):
        return None
    return {"version": parts[1], "engine": parts[2].split("=", 1)[1]}


def is_original_firmware(path):
    """True when the binary carries the official Synthux banner."""
    return bool(_scan_ascii(path, _ORIGINAL_NEEDLE))


# --- DFU command construction (device-free) ------------------------------

def dfu_flash_cmd(bin_path, address=DFU_ADDRESS, vidpid=DFU_VIDPID, leave=True):
    """Build the dfu-util argument list for flashing a Daisy app binary."""
    suffix = f"{address}:leave" if leave else address
    return [
        "dfu-util", "-a", "0", "-s", suffix, "-D", str(bin_path), "-d", vidpid,
    ]


def dfu_util():
    return shutil.which("dfu-util") or "dfu-util"


# --- device detection (non-destructive) ----------------------------------

def detect(dfu=dfu_util()):
    """Report device presence without changing anything.

    Returns ``{"dfu": bool, "midi": bool, "dfu_lines": [...], "midi_lines": [...]}``.
    """
    dfu_lines, midi_lines = [], []
    dfu_present = False
    try:
        res = subprocess.run([dfu, "-l"], capture_output=True, text=True, timeout=15)
        out = res.stdout + res.stderr
        dfu_present = ("0483:df11" in out) or ("Found DFU" in out)
        dfu_lines = [ln for ln in out.splitlines() if ln.strip()]
    except (FileNotFoundError, subprocess.SubprocessError):
        dfu_lines = []
    midi_present = False
    amidi = shutil.which("amidi")
    if amidi:
        try:
            res = subprocess.run([amidi, "-l"], capture_output=True, text=True, timeout=15)
            out = res.stdout + res.stderr
            midi_present = "spotykach" in out.lower() or "spotykach" in out
            midi_lines = [ln for ln in out.splitlines() if ln.strip()]
        except (FileNotFoundError, subprocess.SubprocessError):
            midi_lines = []
    return {
        "dfu": dfu_present,
        "midi": midi_present,
        "dfu_lines": dfu_lines,
        "midi_lines": midi_lines,
    }


# --- state tracking (device-free) ----------------------------------------

DEFAULT_STATE = {"flashed": None, "kind": None, "version": None, "engine": None}


def load_state(path):
    """Load the JSON state file, or return defaults when absent/invalid."""
    path = Path(path)
    if path.exists():
        try:
            return {**DEFAULT_STATE, **json.loads(path.read_text())}
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_STATE)


def save_state(path, **fields):
    """Merge ``fields`` into the state file and write it back."""
    state = load_state(path)
    state.update(fields)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(state, indent=2) + "\n")
    return state


# --- downloads (device-free, network-gated) ------------------------------

_USER_AGENT = "sk-engines-manager/1.0"


def download(url, dest):
    """Download ``url`` to ``dest`` (follows redirects; raises on HTTP error)."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest, "wb") as f:
        f.write(resp.read())
    return dest


def fetch_engine(engine, dest_dir):
    """Download + checksum-verify an engine binary; return its path."""
    name = engine_binary_name(engine)
    url = engine_download_url(engine)
    dest = Path(dest_dir) / name
    if not dest.exists():
        download(url, dest)
    verify_release(dest, engine=engine)
    return dest


def fetch_original(dest_dir):
    """Download the original Synthux firmware (de-install target)."""
    url = original_download_url()
    dest = Path(dest_dir) / ORIGINAL_BIN
    if not dest.exists():
        download(url, dest)
    return dest


def bootloader_download_url(tag=SK_TAG):
    """Raw in-tree URL for the sk-engines bootloader (not a release asset)."""
    return f"{SK_REPO}/raw/{tag}/{BOOTLOADER_BIN}"


def fetch_bootloader(dest_dir):
    """Download + checksum-verify the sk-engines bootloader; return its path."""
    dest = Path(dest_dir) / BOOTLOADER_BIN
    if not dest.exists():
        download(bootloader_download_url(), dest)
    actual = sha256(dest)
    if actual != BOOTLOADER_SHA256:
        raise ValueError(
            f"checksum mismatch for {BOOTLOADER_BIN}:\n"
            f"  expected {BOOTLOADER_SHA256}\n  actual   {actual}"
        )
    return dest


# --- hardware-gated lifecycle --------------------------------------------

def _require_dfu(det, action):
    """Raise a clear error unless the device is actually in DFU mode."""
    if not det["dfu"]:
        raise RuntimeError(
            f"cannot {action}: Spotykach not in DFU mode. Hold Reset ~3 s until "
            f"the bottom pad LEDs breathe white, then retry. (dfu-util -l saw "
            f"no DfuSe/STSP inject:0483:df11 device)"
        )


def flash(bin_path, address=DFU_ADDRESS, leave=True, dfu=dfu_util()):
    """Flash a binary and reboot into it. Raises RuntimeError on any failure.

    Keying on dfu-util's exit code alone is wrong: the ``:leave`` reset step
    prints a *benign* ``get_status`` error for QSPI images (the flash itself
    succeeded — see the sk-engines Makefile's ``-``-prefixed ``program-dfu``),
    so we key on the download-complete marker instead.
    """
    det = detect(dfu=dfu)
    _require_dfu(det, "flash")
    cmd = dfu_flash_cmd(bin_path, address=address, leave=leave)
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = (res.stdout or "") + (res.stderr or "")
    if "File downloaded successfully" not in out:
        raise RuntimeError(
            f"dfu-util flash failed (exit {res.returncode}); no "
            f"download-complete marker in output:\n{out.strip()}"
        )
    return res


def install(engine, dest_dir, state_path=None, dfu=dfu_util()):
    """Full install: download + verify + flash one engine. Returns state dict."""
    path = fetch_engine(engine, dest_dir)
    flash(path, dfu=dfu)
    state = {"flashed": path.name, "kind": "sk-engines", "version": SK_VERSION,
             "engine": engine}
    if state_path:
        save_state(state_path, **state)
    return state


def restore(dest_dir, state_path=None, dfu=dfu_util()):
    """De-install: re-flash the original Synthux firmware. Returns state dict."""
    path = fetch_original(dest_dir)
    flash(path, dfu=dfu)
    state = {"flashed": path.name, "kind": "original", "version": ORIGINAL_TAG,
             "engine": None}
    if state_path:
        save_state(state_path, **state)
    return state


# --- CLI ----------------------------------------------------------------

def _main(argv=None):
    p = argparse.ArgumentParser(
        prog="sk_engines.py",
        description="Spotykach sk-engines install / run / de-install automation.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list available release engines")

    d = sub.add_parser("download", help="download + verify an engine binary")
    d.add_argument("engine", choices=sorted(ENGINE_TYPES))
    d.add_argument("-o", "--output", default=".")

    v = sub.add_parser("verify", help="checksum-verify and identify a binary")
    v.add_argument("file")
    v.add_argument("--engine", help="optional engine name for checksum lookup")

    i = sub.add_parser("install", help="download + verify + flash one engine")
    i.add_argument("engine", choices=sorted(ENGINE_TYPES))
    i.add_argument("-o", "--output", default=".", help="download dir")
    i.add_argument("--state", default=None, help="state JSON path")
    i.add_argument("--dry-run", action="store_true",
                   help="download/verify only, skip flashing")

    r = sub.add_parser("restore", help="de-install: re-flash original firmware")
    r.add_argument("-o", "--output", default=".", help="download dir")
    r.add_argument("--state", default=None)
    r.add_argument("--dry-run", action="store_true")

    b = sub.add_parser("bootloader",
                       help="flash the sk-engines bootloader (one-time, risky)")
    b.add_argument("-o", "--output", default=".", help="download dir")
    b.add_argument("--yes", action="store_true",
                   help="actually flash (device must already be in DFU mode — "
                        "a human/physical step)")

    s = sub.add_parser("status", help="detect device + show lifecycle state")
    s.add_argument("--state", default=None)

    args = p.parse_args(argv)

    if args.cmd == "list":
        for name in all_engine_names():
            kind = ENGINE_TYPES[name]
            print(f"{name:<12} {kind}")
        print("\nbuild-only (no release binary):", ", ".join(sorted(BUILD_ONLY_ENGINES)))

    elif args.cmd == "download":
        path = fetch_engine(args.engine, args.output)
        ident = identify_engine(path)
        print(f"downloaded {path}")
        print(f"identity: {ident}")

    elif args.cmd == "verify":
        ident = identify_engine(args.file)
        is_orig = is_original_firmware(args.file)
        if ident:
            try:
                if args.engine:
                    verify_release(args.file, engine=args.engine)
                elif ident["engine"] in ENGINE_TYPES:
                    verify_release(args.file, engine=ident["engine"])
                else:
                    raise ValueError("checksum target unknown for this build-only engine")
                print(f"{args.file}: sk-engines {ident} (checksum OK)")
            except ValueError as exc:
                print(f"{args.file}: CHECKSUM FAILED — {exc}")
                sys.exit(1)
        elif is_orig:
            print(f"{args.file}: original Synthux firmware (no pinned checksum)")
        else:
            print(f"{args.file}: unrecognized firmware image")
            sys.exit(1)

    elif args.cmd == "install":
        if args.dry_run:
            path = fetch_engine(args.engine, args.output)
            print(f"dry-run: ready to flash {path}")
            print(f"dfu-util: {' '.join(dfu_flash_cmd(path))}")
        else:
            install(args.engine, args.output, state_path=args.state)
            print(f"installed engine {args.engine!r}; rebooted into app")

    elif args.cmd == "restore":
        if args.dry_run:
            path = fetch_original(args.output)
            print(f"dry-run: ready to flash {path} (original firmware)")
            print(f"dfu-util: {' '.join(dfu_flash_cmd(path))}")
        else:
            restore(args.output, state_path=args.state)
            print(f"restored original firmware {ORIGINAL_TAG}; rebooted into app")

    elif args.cmd == "bootloader":
        # One-time, risky step: replaces the stock bootloader. Entering DFU is a
        # physical/human act, so this never auto-flashes — it dry-runs unless the
        # human has already put the device in DFU mode AND passed --yes.
        path = fetch_bootloader(args.output)
        cmd = dfu_flash_cmd(path, address=BOOTLOADER_ADDRESS)
        if not args.yes:
            print(f"dry-run: ready to flash {path} (bootloader, one-time)")
            print(f"dfu-util: {' '.join(cmd)}")
            print()
            print("WARNING: this replaces the stock bootloader with the sk-engines")
            print("bootloader. It can temporarily brick the unit if interrupted,")
            print("moves DFU to the rear USB-C port, and is required for engines")
            print("to actually run. Re-run with --yes once the device is in DFU")
            print("mode (hold RESET ~3s until the pads breathe).")
        else:
            flash(path, address=BOOTLOADER_ADDRESS)
            print(f"flashed bootloader {BOOTLOADER_BIN}; rebooting into it")
            print("note: DFU now lives on the rear USB-C port for later flashes")

    elif args.cmd == "status":
        det = detect()
        print("DFU mode:", "yes" if det["dfu"] else "no")
        for ln in det["dfu_lines"]:
            print("  ", ln)
        print("MIDI device:", "yes" if det["midi"] else "no")
        for ln in det["midi_lines"]:
            print("  ", ln)
        if not det["dfu"] and not det["midi"]:
            print("interpretation: app running with no USB MIDI "
                  "(normal for sk-engines SRAM engines, which are audio-only; "
                  "stock firmware would enumerate 'Spotykach MIDI 1' here)")
        if args.state:
            print("state:", json.dumps(load_state(args.state)))


if __name__ == "__main__":
    _main()