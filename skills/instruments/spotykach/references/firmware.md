# Spotykach — Firmware

Current installed: **v1.4.0 beta 2** (latest, adds USB file transfer).
Most recent stable: v1.3.1.

- Releases: https://github.com/Synthux-Academy/Spotykach/releases
- Firmware notes: https://tsemah.notion.site/p/Spotykach-Firmware-2396331933b880d89f04f61ecf0f58e6

A Daisy device does not expose its installed version over USB, so "confirm latest" means
flash the target version and verify the unit boots into normal (MIDI) mode. The bootloader
is fail-safe: a failed flash leaves it in DFU mode rather than bricked.

## Enter bootloader mode

Press and hold the small **RESET** button next to the USB port for 3–5 s. The LED rings
glow **white** when in bootloader mode. (If holding Reset does not work, plug in power
while holding Reset.)

In bootloader mode the device enumerates as an Electrosmith **Daisy Bootloader** (STM32
DFU, `0483:df11`).

Firmware is flashed over the **rear USB-C port on the main PCB** — not the Seed's own
onboard USB port (application firmware can only be flashed via the main PCB's USB-C).

## Flashing (Linux, headless via dfu-util)

One-time udev rule (grants userspace access to the DFU device):

```bash
# /etc/udev/rules.d/99-spotykach-dfu.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="df11", MODE="0666", TAG+="uaccess"

sudo udevadm control --reload-rules && sudo udevadm trigger
```

Flash (programs are stored on QSPI at `0x90040000`; the first 256 KB of QSPI is reserved):

```bash
dfu-util -l                                        # confirm the device is listed (0483:df11)
dfu-util -a 0 -s 0x90040000:leave -D firmware.bin  # flash, then reboot into the app
```

The `Invalid DFU suffix signature` warning is normal (Daisy `.bin` files carry no DFU
suffix). Success is `File downloaded successfully` followed by the device re-enumerating as
`Spotykach MIDI 1` (not staying in DFU / not blinking SOS).

## Verify

```bash
amidi -l      # IO  hw:2,0,0  Spotykach MIDI 1
aconnect -l   # client 'Spotykach' [type=kernel,card=2]
```

The official (non-headless) path is the **Daisy Programmer** in Google Chrome
(https://flash.daisy.audio/ → File Upload → FLASH); WebUSB only works in Chrome.

## USB file transfer (v1.4.0+)

v1.4.0 adds USB file transfer (WebUSB via the WAV.builder web app). Known open issue
([#15](https://github.com/Synthux-Academy/Spotykach/issues/15)): large transfers stall
mid-upload ("corrupted request") and the device can drop the session if a resend also
stalls. The **SD-card workflow is the reliable path** — prefer it over USB transfer for
loading samples.

## Alternative firmware — sk-engines (install / run / de-install)

[sk-engines](https://github.com/shakfu/sk-engines) (release tag `0.6.1`, version string
`0.6.1-1-g4faeddd`) replaces the stock firmware with a per-engine system. One engine
binary is flashed at a time (the app region is shared). Automated by
`scripts/sk_engines.py`; the bundle ships pinned `references/sk-engines-SHA256SUMS` and
`references/sk-engines-MANIFEST.txt` for offline, deterministic checksum verification.

### Install (flash an engine)

```bash
# put the device into DFU mode first (hold Reset ~3 s → bottom pads breathe white)
python3 scripts/sk_engines.py install delay     # download + verify + flash
python3 scripts/sk_engines.py install reverb    # any of the 18 release engines
python3 scripts/sk_engines.py list              # names + sram/qspi kind
```

Equivalent raw command (the script builds this for you):

```bash
dfu-util -a 0 -s 0x90040000:leave -D sk-delay-0.6.1-1-g4faeddd.bin -d ,0483:df11
```

Release engines: `bard chuck csound delay edrums filter glitch graincloud mosc
pstretch qdelay radio reso reverb shuttle softcut tape voice`. `granular`,
`passthrough`, `chorus`, `gigaverb` are **build-only** — `git clone --recurse-submodules`,
then `make -j8 libs && make -j8 ENGINE=granular` before flashing the resulting `.bin`.

### Run (verify the engine boots)

After `:leave`, the device resets out of the bootloader and runs the engine. The
correct headless signal that the flash succeeded *and the app booted* is that the DFU
interface left the bus — **`DFU mode: no`** — not that USB MIDI reappeared:

```bash
python3 scripts/sk_engines.py status      # expect: "DFU mode: no"
dfu-util -l                               # expect: no `0483:df11` entry
```

Do **not** expect a `Spotykach` MIDI client here: the SRAM engines ship with
`USB_MIDI=0` (the sk-engines Makefile enables it only for QSPI builds), so a running
SRAM engine presents **no USB MIDI at all** — it is audio-only. That absence is by
design, not a boot failure. USB MIDI (`0483:5740` VCP + `Spotykach MIDI 1`) is only
present on the **stock** firmware, so after `restore` you *will* see it re-enumerate.

A binary's identity can be read back without flashing it:

```bash
python3 scripts/sk_engines.py verify sk-delay-0.6.1-1-g4faeddd.bin
# → sk-engines {'version': '0.6.1-1-g4faeddd', 'engine': 'delay'} (checksum OK)
```

### De-install (restore original firmware)

Flashing the official Synthux firmware back over the app region removes the engine —
the device returns to stock. Same DFU path and address, so a failed flash merely leaves
it in DFU mode:

```bash
python3 scripts/sk_engines.py restore       # downloads + flashes spotykach_1.3.1.bin
# raw: dfu-util -a 0 -s 0x90040000:leave -D spotykach_1.3.1.bin -d ,0483:df11
```

`restore` uses the latest **stable** official release (v1.3.1,
`spotykach_1.3.1.bin`). To return to the beta line instead, download the pre-release
binary from the same [releases](https://github.com/Synthux-Academy/Spotykach/releases)
page and flash it with the same `dfu-util` command.

### Bootloader — required for SRAM engines to run

sk-engines app binaries "run under the spotykach bootloader". That is not a soft
note: the SRAM engines (the 15 default release engines, `delay` included) link against
`bootloader-spotykach-v2.bin` (`APP_TYPE = BOOT_SRAM`, `BOOT_BIN` in the Makefile) and
**do not fully boot under the stock bootloader**. Verified on hardware: flashing `delay`
at `0x90040000` over a stock unit re-enumerated nothing (no USB, since `USB_MIDI=0`)
and left only a green play LED / partial LED init — the engine was resident but never
ran. The same flash command restores the stock firmware perfectly, so the flash path is
correct; the missing piece is the bootloader.

The release notes describe bootloader installation as "a separate, device-level
procedure not covered here", and the author warns that changing it "can 'brick'
(temporarily) the device and require reinstallation of either the bootloader, the
firmware binary, or both". The bootloader (`bootloader-spotykach-v2.bin`, in-tree) also
**moves DFU to the rear USB-C port** (main PCB) instead of the Seed's own port — after
installing it, app flashing goes through the rear USB-C, not the port used for the
stock firmware.

Practically: flashing stock firmware (`restore`) is safe and reversible at any time.
Flashing an engine at `0x90040000` works mechanically (download + verified checksum +
`dfu-util` success) but only runs correctly once the sk-engines bootloader is in place —
a one-time, riskier device-level change that should be done deliberately, not as part of
routine engine swapping.

#### Installing the bootloader (one-time)

The bootloader ships in-tree (no release asset) as `bootloader-spotykach-v2.bin`. It is
flashed to its own QSPI region at **`0x90000000`** — the 256 KB bootloader region
directly below the app at `0x90040000` — *not* the STM32 ROM DFU address `0x08000000`
(a different physical entry that is a red herring). It uses the same alt-0 / `0483:df11`
interface as app flashing.

```bash
python3 scripts/sk_engines.py bootloader -o /tmp/sk-boot --yes
# raw: dfu-util -a 0 -s 0x90000000:leave -D bootloader-spotykach-v2.bin -d ,0483:df11
```

The subcommand downloads + checksum-verifies the bootloader (pinned against an in-code
`BOOTLOADER_SHA256`; it raises on mismatch before any flash) and dry-runs unless `--yes`
is passed. Like every other flash it requires the unit already be in DFU mode — entering
DFU is always a physical, human step, so the command never enters DFU or auto-flashes on
its own. Success prints `flashed bootloader …; rebooting into it`, then the still-stock
app at `0x90040000` boots normally (same `0483:5740` VCP / `Spotykach MIDI 1`). Once
this one-time step is done, SRAM engines boot cleanly (`DFU mode: no`, no USB MIDI).

### Tests

```bash
pytest tests/test_spotykach_sk_engines.py
```

Covers resolution, checksum verification against the pinned `SHA256SUMS`, binary
identity, dfu-util argument construction, and state tracking. The hardware steps
(flash / MIDI enumeration) skip cleanly when no Spotykach is in DFU mode, mirroring
sk-engines' own `make test-hw` rule.

Run these tests with bare `pytest` (resolves to `~/.local/bin/pytest`) — `python3 -m
pytest` fails because the Hermes venv Python has no pytest, and the repo's own venv may
not either. When tool output shows a bundled reference name mangled (e.g.
`sk-eng....txt` instead of `sk-engines-MANIFEST.txt`), trust `xxd`, not the mangled
text: confirm true on-disk bytes with `find references -name 'sk-*' -printf '%f\n' |
xxd` before renaming or assuming corruption — the display layer elides the `sk-engines`
substring.
