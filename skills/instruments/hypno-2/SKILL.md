---
name: "hypno-2"
description: "Sleepy Circuits Hypno 2 video synthesizer/resampler — 2-channel video mixer/looper, shader engine, MIDI CC mapping, CV/modulation, sampler"
category: instruments
---

# Hypno 2

Sleepy Circuits Hypno 2 hardware video synthesizer and re-sampler. Built on Raspberry Pi 5 running vidOS. Re-samples 2 channels of video infinitely with mixer, feedback FX, shader engine, and per-parameter modulation.

Manufacturer: [Sleepy Circuits](https://sleepycircuits.com/hypno-2)
Docs: [docs.sleepycircuits.com/hypno2](https://docs.sleepycircuits.com/hypno2)
PDF manual: `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf`
Manual version: V0.100 (firmware v0.0.163)

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

## Quick Reference

| Operation | How |
|-----------|-----|
| **New session** | Tap NEW on startup popup (or RESTORE STATE to resume) |
| **Channel select** | Center button = Main, side buttons = Ch A / Ch B |
| **Change shader** | Tap channel title or previous/next shader arrows in top bar |
| **Open file browser** | Tap channel A or B program title |
| **Load video/camera/shader** | File Browser → select file → decode video if needed → tap left encoder |
| **Start/stop playback** | Transport button (bottom right, per channel) |
| **Record output** | Red record button (right sidebar) → press again to stop |
| **Save preset** | Save button (left sidebar) → saves .json to `VIDOS-Resources/Presets` |
| **Load recent preset** | Tap one of 4 thumbnail slots in left sidebar |
| **Reset parameter** | Tap encoder → tap again at zero to randomize |
| **Open modulation** | Tap any parameter name label |
| **Fullscreen toggle** | Tap background (hide UI) → tap again to return |
| **Undo/Redo** | Arrow buttons in right sidebar (tracks 100 actions) |
| **Desktop mode** | Settings → "Go to Desktop" → VIDOS shortcut to return |
| **Firmware update** | Settings → tap version number when update available |

## MIDI CC Map

### Main / Master (MIDI Ch 16)

| CC | Parameter | Description |
|----|-----------|-------------|
| 0 | ch1 gain | Track A video level |
| 1 | feedback | Frame-to-frame feedback amount |
| 2 | ch2 gain | Track B video level |
| 3 | fb x | Feedback horizontal offset |
| 4 | fb zoom | Feedback zoom/scale |
| 5 | fb y | Feedback vertical offset |
| 6 | fb rotate | Feedback rotation angle |
| 7 | low key | Luminance keying low threshold (darker pixels keyed out) |
| 8 | hi key | Luminance keying high threshold (brighter pixels keyed out) |

### Track A (MIDI Ch 1) & Track B (MIDI Ch 2)

Parameters vary by loaded shader. Common defaults:

| CC | Parameter | Description |
|----|-----------|-------------|
| 0 | x offset | Horizontal position |
| 1 | frequency | Animation speed |
| 2 | y offset | Vertical position |
| 3 | x crop min / fold axis | Horizontal crop left (shader-dependent) |
| 4 | rotation | Rotation angle |
| 5 | x crop max / fold shape | Horizontal crop right (shader-dependent) |
| 6 | y crop min / aspect x | Vertical crop top (shader-dependent) |
| 7 | polarization | Polarization amount (shader-dependent) |
| 8 | y crop max / aspect y | Vertical crop bottom (shader-dependent) |
| 9 | aspect x / luma min | Horizontal stretch (shader-dependent) |
| 10 | --- | Unassigned (shader-dependent) |
| 11 | aspect y / luma max | Vertical stretch (shader-dependent) |
| 12 | mirror amt | Mirror effect intensity |
| 13 | mirror rot | Mirror axis rotation |
| 14 | --- | Unassigned |
| 15 | luma min | Luminance low threshold |
| 16 | polarization | Polarization amount |
| 17 | luma max | Luminance high threshold |
| 18–59 | (shader-dependent) | Additional shader parameters |
| 60 | --- | Unassigned |
| 61 | cross mod | Cross-channel modulation amount |
| 62 | fb mod amt | Feedback modulation depth |
| 63 | hue | OKLab hue shift |
| 64 | chrominance | OKLab color saturation |
| 65 | lightness | OKLab brightness |
| 66–127 | mod CC 0–61 | Modulation LFO control (mod CC = base CC + 66) |

> **Sampler shader note:** When a Sampler shader is loaded with multi-frame video, CCs 0–2 are reserved for loop in, framerate, and loop out. Shader parameters start at CC 3.

### MIDI Notes

| MIDI Channel | Note Function |
|-------------|---------------|
| Ch 1–2 | Chromatic video playback — each note shifts pitch/speed (middle C = normal) |
| Ch 3–16 | Preset save/load — short press loads, long hold saves to note slot |

## Modulation Sources

Each parameter has a modulation page (tap parameter label). Available sources:

### Internal LFO

| Control | Encoder | Description |
|---------|---------|-------------|
| gain | Left | Modulation amplitude (bipolar) |
| func | Center | Waveform selector |
| freq | Right | LFO speed |

**14 waveforms:** Sin, Cos, Tri, Ramp, Tan, Rnd, Pulse, Exp, Log, StpRnd, Bounce, Chaos, Heart, Pend

### Audio Input (AUX / Mic)

| Page | Controls |
|------|----------|
| Page 1 | gain (depth, bipolar), smooth (slew rate, 0–1) |
| Page 2 | LOW band gain, MID band gain, HIGH band gain |

Built-in mic used when no jack in AUX input.

### CV Input (4 jacks)

| Control | Description |
|---------|-------------|
| gain | Modulation depth from selected CV jack |
| smooth | Input smoothing (noise/jitter reduction) |
| CV 1–4 | Select by tapping CV badge — 0–5 V unipolar Eurorack |

### MIDI CC

| Control | Description |
|---------|-------------|
| gain | Modulation depth (bipolar) |
| smooth | Input smoothing (0–1) |
| cc# | Remap CC number (0–127), independent of default |

### Clock / BPM Sync

| Control | Description |
|---------|-------------|
| source | OFF, BPM (internal), CLK1 (trigger 1), CLK2 (trigger 2) |
| division | 1/32, 1/16, 1/8, 1/4, 1/2, 1/1, 2×, 4×, 8×, 16× |
| re-trig | ON/OFF — resets LFO phase on each clock pulse |

### Audio Track (uses channel audio as modulation)

| Page | Controls |
|------|----------|
| Page 1 | gain (depth), smooth (slew) |
| Page 2 | LOW band, MID band, HIGH band gain |

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

## File Format Support

| Type | Formats | Notes |
|------|---------|-------|
| Image | JPEG, PNG (transparency), BMP, GIF, SVG | SVG cached at multiple scales |
| Video | MP4 (H.264/H.265), MOV, WebM | Must be decoded before use in channels |
| Audio | WAV, MP3, OGG, FLAC | WAV primary for mixing |
| Shader | .frag (GLSL fragment shaders) | Live editing in built-in editor; symbol names from uniforms |
| Preset | .json | Full system state (params, modulation, MIDI) |

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

## Resources

- PDF manual: `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf`
- Online manual: https://docs.sleepycircuits.com/hypno2
- GitBook docs: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-manual
- Product page: https://sleepycircuits.com/hypno-2
- FAQ: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-faq
- Firmware: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-firmware
- Forum: https://forum.sleepycircuits.com/
- Matrix chat: #sleepycircuits:matrix.org
