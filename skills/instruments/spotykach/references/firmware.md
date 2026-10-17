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
