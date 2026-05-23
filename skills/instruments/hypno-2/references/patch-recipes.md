# Hypno 2 — Patch Recipe Patterns Reference

12 preset workflows for the Hypno 2. Each assumes knowledge of the basic controls from Quick Reference.

## 1. Infinite Feedback Resampling

The core Hypno workflow — capture output and feed it back repeatedly.

1. Load a video on Ch 1 (File Browser → select → decode → left encoder tap)
2. Set Ch 1 playback mode to **Loop**
3. On Main track, set **feedback** (CC 1) to ~0.7
4. Adjust **fb zoom** (CC 4) slightly for fractal zoom effect
5. Tap **Record** (red button) — let it run 10–30 seconds — tap again to stop
6. Choose to assign recording to Ch 2
7. Now both channels play — switch Main feedback source or adjust mixer
8. Repeat: record → assign → layer indefinitely

## 2. Dual Source Crossfade Blend

Blend two video sources with independent processing.

1. Load source A on Ch 1, source B on Ch 2
2. Set both to **Loop** mode
3. On Main track: 
   - Page 1: ride **ch1 gain** (CC 0) and **ch2 gain** (CC 2) for crossfades
   - Page 2: offset each channel's feedback separately
   - Page 3: key out dark/bright areas on the combined output
4. Use Ch 1/2 parameter pages for per-channel rotation, cropping, mirroring
5. Optional: assign LFO to crossfade for auto-blending

## 3. Audio Reactive Visuals

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

## 4. Eurorack CV Integration

Patch modular synth CV to control video parameters.

1. Connect CV source (0–5 V) to CV 1–4 jacks on rear panel
2. On any parameter, open modulation → select the **CV jack badge** matching the input
3. Set **gain** (modulation depth, bipolar) and **smooth** (reduces jitter)
4. Connect triggers to Clock/Trig inputs for BPM sync
5. Open Clock/BPM → set source to CLK1 or CLK2 → use division controls
6. Verify CV levels on the scope display in modulation view

## 5. MIDI Keyboard Chromatic Playback

Play video/audio at different pitches from a keyboard.

1. Load a video with audio on Ch 1
2. Connect USB MIDI keyboard
3. Ensure MIDI Ch 1 is routed to Track A (Settings → MIDI Devices → In toggle)
4. Play notes — middle C = normal speed, higher notes = faster, lower = slower
5. Enable clock sync in Clock/BPM to preserve tempo while pitching
6. This also works for audio-only files (WAV, MP3)

## 6. LFO Auto-Animation Set

Create auto-moving visuals with no external input.

1. Load a shape shader on Ch 1 (e.g., `sin.frag`)
2. Tap **x offset** (CC 0) label → modulation menu
3. Internal LFO is default source — set **gain**, pick **func** (try Tri or Sin), set **freq**
4. Repeat for **rotation** (CC 4) with a different waveform and slower speed
5. Add LFO to Main **feedback zoom** (CC 4) for breathing effect
6. Enable **re-trig** on each LFO if using clock sync for phase-locked motion

## 7. Live Camera → Feedback Synthesis

Process live camera feed through the feedback engine.

1. Connect UVC webcam or capture card to USB port
2. Open File Browser → tap **Cameras** shortcut button
3. Select camera → left encoder tap to load onto Ch 1
4. Set Ch 1 playback to **Loop**
5. Adjust cropping/rotation/mirroring on Ch 1 parameter pages
6. Crank Main **feedback** (CC 1) for live video feedback
7. Record the output to capture processed camera footage
8. Load the recording onto Ch 2 for dual-source live + processed

## 8. Preset-Based Performance Set

Prepare a set of presets for live performance.

1. Design your visual state (shaders, parameters, modulation, playback modes)
2. Tap **Save Preset** (left sidebar) — appears as thumbnail
3. Repeat for each song/scene (up to 4 thumbnails shown, many more stored)
4. During performance: tap thumbnails to instantly recall states
5. For MIDI recall: send Note On on Ch 3–16 — short press loads, long hold saves
6. Presets store complete state including MIDI mappings and modulation

## 9. Shader Switching During Performance

Switch visual looks without stopping playback.

1. Pre-load source videos/images on Ch 1 and Ch 2
2. Use the **previous/next shader arrows** in the top bar to cycle shaders
3. Tap the channel title to open File Browser and pick a different shader
4. Combine with preset recall for instant shader + parameter changes
5. Different shaders expose different parameters — presets persist the mapping

## 10. NDI Network Send/Receive

Use Hypno 2 as a network video source or destination.

1. Ensure Hypno 2 is on the same network as target device
2. **Send:** Hypno output is automatically available as an NDI source on the network
3. Other NDI-capable devices (Resolume, OBS, TouchDesigner) can receive it
4. **Receive:** NDI sources appear automatically in the File Browser
5. Load an NDI source like any other video/camera source onto a channel
6. NDI also carries audio — use for multi-room installations

## 11. Clock-Synced Performance

Lock everything to a master BPM.

1. Set clock source in Clock/BPM:
   - **INT** for internal tempo → dial BPM with left encoder
   - **EXT** for trigger inputs (CV clock from modular)
   - **CLK** for MIDI clock from DAW/sequencer
2. Per-parameter modulation: set LFO source to **Clock**, choose **division**
3. Enable **re-trig** to reset LFO phase on each clock pulse
4. Playback modes and recording can be clock-synced
5. Use **LEN** (right encoder) to set sequence length for timed recording

## 12. Desktop Mode Shader Development

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