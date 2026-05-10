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

## Factory Shader Library

The Hypno 2 ships with a foundational factory library. The core 5 shapes and 5 FX shaders from Hypno 1 are all present, plus additional shaders added for Hypno 2. Shaders are loaded per-channel from the file browser. Custom .frag shaders can be added and edited in the built-in shader editor.

### FX Shaders (Main Track / Mixer)

Loaded on the Main track. The default is `fx_feedback.frag`. All FX shaders share the same CC mapping (CC 0–8, see MIDI CC Map above).

| Shader File | Name | Description |
|-------------|------|-------------|
| `fx_feedback.frag` | Basic Feedback | Classic camera-pointed-at-screen feedback. Supports zoom, X/Y offset, rotation, and luma keying. |
| `fx_hsv_feedback.frag` | HSV Feedback | Hue-shifts the feedback frame on each iteration. Same offset/zoom/rotate controls. |
| `fx_hyperdigital_feedback.frag` | Hyperdigital Feedback | Feedback path divides back into itself (fractal division). Very sensitive — can cause flashing at high gain. Use low feedback. |
| `fx_invert_feedback.frag` | Invert Feedback | Inverts the feedback frame, creating pastel-like color shifts. Same offset/zoom/rotate controls. |
| `fx_lumakey_feedback.frag` | Luma Key Feedback | Feeds back only the surviving foreground edges after keying. Good for cutout effects on complex sources. |

### Generative Shape Shaders (Track A / Track B)

Loaded on Channels 1 and 2. These are 2D oscillator shapes that generate video from mathematical functions. They follow the CC 0–61 parameter grid (MIDI CC Map above).

| Shader File | Name | Description |
|-------------|------|-------------|
| `sin.frag` | Sine Wave Oscillator | Classic sine wave shape with scroll, rotation, polarization, aspect controls |
| `tan.frag` | Tangent Oscillator | Tangent wave shape — sharper transitions |
| `poly.frag` | Polygon | N-sided polygon shape with fractal/self-modulation |
| `circle.frag` | Circle / Oval | Circular oscillator with aspect ratio stretch |
| `noise.frag` | Fractal Noise | Perlin/simplex noise field generator |
| `sampler.frag` | Sampler | Video/image sampler for loaded media. **CCs 0–2 reserved** for loop in, framerate, loop out. Shader params start at CC 3. |

### Custom Shaders

- `.frag` files must be valid GLSL fragment shaders
- Uniform names become parameter labels in the UI (underscores become spaces)
- 5 uniforms maximum (beyond the built-in resolution/time uniforms)
- Example uniforms: `uniform float x_offset;`, `uniform float rotation;`
- Built-in editor: syntax highlighting, live preview, compile error display
- Custom shaders respect the same mod CC offset rule (mod CC = base CC + 66)

> **Shader parameter count rule:** Shaders can expose 0–5 custom uniforms. When fewer than 5 are exposed, unused CCs show `---` in the UI.

## Patch Recipe Patterns

Common workflows for the Hypno 2. Each recipe assumes you know the basic controls from Quick Reference.

### 1. Infinite Feedback Resampling

The core Hypno workflow — capture output and feed it back repeatedly.

1. Load a video on Ch 1 (File Browser → select → decode → left encoder tap)
2. Set Ch 1 playback mode to **Loop**
3. On Main track, set **feedback** (CC 1) to ~0.7
4. Adjust **fb zoom** (CC 4) slightly for fractal zoom effect
5. Tap **Record** (red button) — let it run 10–30 seconds — tap again to stop
6. Choose to assign recording to Ch 2
7. Now both channels play — switch Main feedback source or adjust mixer
8. Repeat: record → assign → layer indefinitely

### 2. Dual Source Crossfade Blend

Blend two video sources with independent processing.

1. Load source A on Ch 1, source B on Ch 2
2. Set both to **Loop** mode
3. On Main track: 
   - Page 1: ride **ch1 gain** (CC 0) and **ch2 gain** (CC 2) for crossfades
   - Page 2: offset each channel's feedback separately
   - Page 3: key out dark/bright areas on the combined output
4. Use Ch 1/2 parameter pages for per-channel rotation, cropping, mirroring
5. Optional: assign LFO to crossfade for auto-blending

### 3. Audio Reactive Visuals

Make parameters respond to sound.

1. Ensure mic (or AUX input) is active — no external source needed if using built-in mic
2. On any parameter, tap its label to open modulation
3. Select **Audio Input** badge (ear icon) — blue ring confirms selection
4. Page 1: Set **gain** for modulation depth, **smooth** to taste
5. Page 2: Isolate frequency bands — e.g., only **LOW** for bass reactivity
6. Repeat on additional parameters (feedback, rotation, hue)
7. For finer control: try **Audio Track** modulation instead (uses channel's loaded audio, not mic)

**Recommended audio-reactive targets:**
- Main feedback amount — visuals pulse with beat
- Feedback zoom — bass-synced zoom
- Ch 1/2 rotation — treble-reactive spin
- Hue (CC 63) — color shift on transients

### 4. Eurorack CV Integration

Patch modular synth CV to control video parameters.

1. Connect CV source (0–5 V) to CV 1–4 jacks on rear panel
2. On any parameter, open modulation → select the **CV jack badge** matching the input
3. Set **gain** (modulation depth, bipolar) and **smooth** (reduces jitter)
4. Connect triggers to Clock/Trig inputs for BPM sync
5. Open Clock/BPM → set source to CLK1 or CLK2 → use division controls
6. Verify CV levels on the scope display in modulation view

### 5. MIDI Keyboard Chromatic Playback

Play video/audio at different pitches from a keyboard.

1. Load a video with audio on Ch 1
2. Connect USB MIDI keyboard
3. Ensure MIDI Ch 1 is routed to Track A (Settings → MIDI Devices → In toggle)
4. Play notes — middle C = normal speed, higher notes = faster, lower = slower
5. Enable clock sync in Clock/BPM to preserve tempo while pitching
6. This also works for audio-only files (WAV, MP3)

### 6. LFO Auto-Animation Set

Create auto-moving visuals with no external input.

1. Load a shape shader on Ch 1 (e.g., `sin.frag`)
2. Tap **x offset** (CC 0) label → modulation menu
3. Internal LFO is default source — set **gain**, pick **func** (try Tri or Sin), set **freq**
4. Repeat for **rotation** (CC 4) with a different waveform and slower speed
5. Add LFO to Main **feedback zoom** (CC 4) for breathing effect
6. Enable **re-trig** on each LFO if using clock sync for phase-locked motion

### 7. Live Camera → Feedback Synthesis

Process live camera feed through the feedback engine.

1. Connect UVC webcam or capture card to USB port
2. Open File Browser → tap **Cameras** shortcut button
3. Select camera → left encoder tap to load onto Ch 1
4. Set Ch 1 playback to **Loop**
5. Adjust cropping/rotation/mirroring on Ch 1 parameter pages
6. Crank Main **feedback** (CC 1) for live video feedback
7. Record the output to capture processed camera footage
8. Load the recording onto Ch 2 for dual-source live + processed

### 8. Preset-Based Performance Set

Prepare a set of presets for live performance.

1. Design your visual state (shaders, parameters, modulation, playback modes)
2. Tap **Save Preset** (left sidebar) — appears as thumbnail
3. Repeat for each song/scene (up to 4 thumbnails shown, many more stored)
4. During performance: tap thumbnails to instantly recall states
5. For MIDI recall: send Note On on Ch 3–16 — short press loads, long hold saves
6. Presets store complete state including MIDI mappings and modulation

### 9. Shader Switching During Performance

Switch visual looks without stopping playback.

1. Pre-load source videos/images on Ch 1 and Ch 2
2. Use the **previous/next shader arrows** in the top bar to cycle shaders
3. Tap the channel title to open File Browser and pick a different shader
4. Combine with preset recall for instant shader + parameter changes
5. Different shaders expose different parameters — presets persist the mapping

### 10. NDI Network Send/Receive

Use Hypno 2 as a network video source or destination.

1. Ensure Hypno 2 is on the same network as target device
2. **Send:** Hypno output is automatically available as an NDI source on the network
3. Other NDI-capable devices (Resolume, OBS, TouchDesigner) can receive it
4. **Receive:** NDI sources appear automatically in the File Browser
5. Load an NDI source like any other video/camera source onto a channel
6. NDI also carries audio — use for multi-room installations

### 11. Clock-Synced Performance

Lock everything to a master BPM.

1. Set clock source in Clock/BPM:
   - **INT** for internal tempo → dial BPM with left encoder
   - **EXT** for trigger inputs (CV clock from modular)
   - **CLK** for MIDI clock from DAW/sequencer
2. Per-parameter modulation: set LFO source to **Clock**, choose **division**
3. Enable **re-trig** to reset LFO phase on each clock pulse
4. Playback modes and recording can be clock-synced
5. Use **LEN** (right encoder) to set sequence length for timed recording

### 12. Desktop Mode Shader Development

Write and test custom shaders on-device.

1. Settings → **Go to Desktop** — switches to Raspberry Pi OS
2. Open text editor — write or modify `.frag` files in the resources directory
3. **VIDOS** desktop shortcut returns to Hypno 2
4. In vidOS, load your new `.frag` from File Browser
5. Tap the `.frag` file to open the built-in shader editor for live tweaking
6. Compile errors display inline — fix and re-save

> **Tip:** Copy working shaders from the factory library as starting templates. The 5 classic Hypno 1 shapes (`sin.frag`, `tan.frag`, `poly.frag`, `circle.frag`, `noise.frag`) are good reference examples.

## Resources

- PDF manual: `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf`
- Online manual: https://docs.sleepycircuits.com/hypno2
- GitBook docs: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-manual
- Product page: https://sleepycircuits.com/hypno-2
- FAQ: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-faq
- Firmware: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-firmware
- Forum: https://forum.sleepycircuits.com/
- Matrix chat: #sleepycircuits:matrix.org
