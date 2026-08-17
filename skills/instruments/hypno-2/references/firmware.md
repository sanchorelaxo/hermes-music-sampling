# Hypno 2 / Mezzz — Firmware Internals (reverse-engineered)

Reverse engineering of the Mezzz controller firmware image
`hypno2-binary-Latest.bin` (3,134,448 bytes, sha256
`bf7f116b549eab54a37ecd487146ba5166d6cf0fd738a06713fb5e962bd3594d`).
Project work lives in `/home/rjodouin/Documents/git/hypno2-firmware-re/`
(`INTERFACE.md`, `UML-diagrams.html`).
For the Mezzz's *user-facing* controls (knobs, center/L/R buttons, trigger
pages, Hypno Emulation UI), see [mezzz-controller.md](mezzz-controller.md) —
this file covers its internal MCU firmware.

> **Confirmation (read-only, live unit):** the file is **byte-identical** to
> `Latest.bin` shipped at `/opt/vidos/VIDOS-release/os/h2ctl/Latest.bin` on the
> Hypno 2 (hostname `hypno2` @ 192.168.1.54, Raspberry Pi 5 / vidOS). The Mezzz
> enumerates on the Pi as `usb-Sleepy_Circuits_Mezzz_10:20:ba:0e:f8:a0` →
> `/dev/ttyACM0`, and vidOS `main.out` talks to it over that USB ACM serial port.

## What the firmware is

- **Device:** Sleepy Circuits **Mezzz** handheld wireless controller for the
  Hypno 2. In the Sleepy/teafella repos it is called **"H2ctl"** (Hypno 2
  controller). Project name string `Mezzz` at image offset 0x11568.
- **SoC/board:** **ESP32-S3** on an **Adafruit Feather ESP32-S3 TFT revA**
  (4 MB flash, QIO 80 MHz, Xtensa LX7).
- **Build:** Arduino-ESP32 (`loopTask`) on **ESP-IDF v4.4.5**
  (`ac5d805d0e`), xtensa-esp32s3-elf toolchain, **NimBLE** host stack.
- **USB identity:** Arduino CDC serial / WebUSB; Windows
  `DeviceInterfaceGUIDs {975F44D9-0D08-43FD-8B3E-127CA8AFFF9D}`.
- **Not** the Pi-5 vidOS firmware — that runs on ARM64 (vidOS). This is the
  controller MCU. The two talk over USB serial.

## Flash layout (merged full-flash image)

| Offset    | Partition  | Size     | Note |
|-----------|-----------|----------|------|
| 0x00000   | bootloader |          | entry 0x403b6328 |
| 0x08000   | partition table |   | 32-byte entries |
| 0x09000   | `nvs`     | 20 KB    | calibration / presets |
| 0x0e000   | `otadata` | 8 KB     | OTA slot selector |
| 0x10000   | `ota_0`   | 1.375 MB | active app, entry 0x40377a0c, rodata 0x42000020 |
| 0x170000  | `ota_1`   | 1.375 MB | OTA standby app |

## BLE interface

- Advertises **`Mezzz`** normally, **`Sleepy Hypno2`** in Hypno Emulation mode.
- **Fully custom 128-bit GATT UUIDs** — no standard BLE-MIDI service, no
  Bluetooth base-UUID tail. UUIDs are stored as binary bytes in the NimBLE
  registration tables; extract by disassembling `ble_gatts_count_cfg` /
  `ble_gatts_add_svcs` and reading the `ble_uuid128_t` arrays.

## MIDI CC map (confirmed from firmware strings)

- **Main/Master → MIDI ch 16**, **Track A → ch 1**, **Track B → ch 2**.
- Boot/probe strings: `APPLYING HYPNO MIDI MAP to channel`,
  `Probing for Hypno`, `Sending Mod Reset For CC:`, `On Hypno Channel`,
  `Hypno mode reset combo`.
- Encoders drive CC 0–61 per channel; mod CC 66–127; IMU gestures map onto mod.

## Presets / modes / combos

- **Presets:** `LOADING MAGENTA USER PRESET` (user 1) / `LOADING TEAL USER
  PRESET` (user 2); center button latches/unlatches a preset page
  (`Unlatched Preset via Center`).
- **Center button:** channel select (Main / A / B) + preset latch.
- **Combos:** `A→B`, `B→A`, `A→Master`, `B→Master`, and Hypno-mode reset.
- **IMU:** LSM6DS (accel+gyro) + LIS3MDL (magnetometer).

## Hardware I/O (drivers)

- **Display:** ST7789V 240×135 TFT (SPI).
- **Input:** 8× haptic encoders (`Initialized Encoder`), center button.
- **Haptics:** haptic motor.
- **DMX:** DMX-512 output driver (`dmx_write_slot`, `dmx_write_offset`).
- **Sensors/peripherals:** ADC1/ADC2, I2C, SPI (flash + TFT), RMT, USB CDC.

## Host integration (vidOS on the Pi 5)

| vidOS layer | Role vs. Mezzz |
|-------------|----------------|
| `main.out`  | Host app; opens `/dev/ttyACM0`, drives the Mezzz over USB serial (replaces upstream `mpv`). |
| `os/esptool/` | Flashes the ESP32-S3 Mezzz over `/dev/ttyACM0`. |
| `os/h2ctl/` | Ships controller firmware: `Latest.bin`, `H2ctl 5-30-2025.bin`. |
| `CheckForFirmwareUpdates.sh` | Git-pulls `os/sleepy_binaries` (teafella) → esptool → OTA. |
| NDI | `main.out` also emits NDI (`_ndi._tcp`, `hypno2-32f0`). |

vidOS itself is the Sleepy Circuits fork of sen-h/VidOS
(<https://codeberg.org/sen-h/VidOS>) — a buildroot minimal Linux; the Hypno 2
fork replaces the upstream `mpv --playlist` core with `main.out`.
Boot files: `config.txt` (`kernel=Image`, `initramfs rootfs.cpio.lz4`,
`arm_64bit=1`, `gpu_mem=256`, `vc4-kms-v3d`); playback via
`mpv --hwdec=v4l2m2m --drm-* --vo=gpu`.

## Open items (disassembly needed)

1. Custom 128-bit GATT service/characteristic UUIDs (NimBLE registration).
2. USB CDC serial command grammar (is there an Rx parser/command table?).
3. Numeric MIDI CC↔parameter tables.
4. DMX universe / start-address / encoder mapping.
5. IMU gesture → CC mapping.
