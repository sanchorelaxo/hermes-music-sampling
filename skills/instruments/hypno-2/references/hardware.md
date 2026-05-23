# Hypno 2 — Hardware & Spec Reference

## Spec Table

| Spec | Value |
|------|-------|
| Year | 2024 |
| Model | Hypno 2 (2nd generation) |
| Dimensions | 4.5" × 4.5" × 2" (114.3 × 114.3 × 50.8 mm) |
| Processor | Raspberry Pi 5 (active cooler) |
| Display | 800×480 capacitive touchscreen (internal UI only) |
| Storage | 250 GB M.2 SSD (user-upgradeable to 1 TB+) |
| Power | USB-C (use official Pi5 PSU) |
| Video Out | 2× micro HDMI (only 1 active at a time, 1080p) |
| Video In | USB UVC (webcams, capture cards), NDI network video |
| Audio In | Built-in mic, AUX line-level (3.5 mm), USB audio devices |
| Audio Out | HDMI audio, USB audio interfaces, NDI |
| CV Inputs | 4× 0–5 V unipolar (Eurorack compatible) |
| Clock Inputs | 2× trigger inputs (64 ppqn BPM readout) |
| USB Host | 3× USB-A (drives, MIDI controllers, cameras, capture cards) |
| Networking | Ethernet, Wi-Fi, Bluetooth (BLE MIDI Central + Peripheral) |
| Price | $1,499 USD |

## Patchbay (Rear Panel)

| Jack | Type | Notes |
|------|------|-------|
| USB-C Power | Power in | Use official Pi5 adapter |
| micro HDMI 0/1 | Video out | Only 1 active at a time, 1080p |
| CV 1–4 | 3.5 mm TS | 0–5 V unipolar Eurorack input |
| Clock/Trig 1–2 | 3.5 mm TS | 64 ppqn BPM readout |
| AUX | 3.5 mm TRS | Line-level audio input |
| Ethernet | RJ45 | Network (updates, NDI, SMB) |
| USB-A × 3 | USB host | Drives, MIDI, cameras, capture cards |

## Desktop Mode

Settings → "Go to Desktop" switches to Raspberry Pi OS. Return via VIDOS desktop shortcut.

### Hardware Keyboard/Mouse Remapping

| Control | Action |
|---------|--------|
| Left encoder (turn) | Mouse X |
| Center encoder (turn) | Mouse scroll wheel |
| Right encoder (turn) | Mouse Y |
| Left encoder (tap) | Right click |
| Center encoder (tap) | Middle click |
| Right encoder (tap) | Left click |
| Left button | ESC |
| Center button | SPACE |
| Right button | ENTER |
| Left + Right buttons | F11 (fullscreen toggle) |

## Settings Pages

| Tab | Key Controls |
|-----|-------------|
| System | Firmware version, date/time, storage usage, "Go to Desktop", "Expand Filesystem" |
| Video | HDMI output resolution (detected from display) |
| Audio | Output device enable/disable per HDMI port and USB device |
| Network | Wi-Fi ON/OFF, scan, connect with on-screen keyboard |
| Bluetooth | ON/OFF, pair MIDI controllers |
| MIDI Devices | Per-device In/Out toggles, sync enable, Bluetooth Peripheral auto-connects |
| Storage | Samba ON/OFF (smb://hypno2.local), USB drive list |

## Clock / BPM (Global)

Access by tapping BPM value in top-right corner.

| Encoder | Parameter | Values |
|---------|-----------|--------|
| Left | BPM | Internal tempo |
| Center | SRC (source) | OFF, AUTO, INT, EXT, CLK (MIDI clock) |
| Right | LEN (length) | Sequence length for clock-synced recording |

When Channel 1 or 2 is selected: Left encoder sets that channel's BPM.

## File Format Support

| Type | Formats | Notes |
|------|---------|-------|
| Image | JPEG, PNG (transparency), BMP, GIF, SVG | SVG cached at multiple scales |
| Video | MP4 (H.264/H.265), MOV, WebM | Must be decoded before use in channels |
| Audio | WAV, MP3, OGG, FLAC | WAV primary for mixing |
| Shader | .frag (GLSL fragment shaders) | Live editing in built-in editor |
| Preset | .json | Full system state (params, modulation, MIDI) |

## Playback Modes

| Mode | Behavior |
|------|----------|
| Loop | Continuous repeat |
| One-Shot | Play once, stop on final frame |
| Bounce | Alternate forward/reverse |
| Random | Select next video randomly from directory |
| Next/Previous | Linear advance |
| Walk | Randomly pick next or previous |
| Shuffle | Randomize full directory order |

Each channel has independent playback mode. Change via mode button on home screen.