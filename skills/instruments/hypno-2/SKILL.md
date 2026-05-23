---
name: "hypno-2"
description: "Use when working with the Sleepy Circuits Hypno 2 video synthesizer/resampler — 2-channel video mixer/looper, shader engine, MIDI CC mapping, CV/modulation, sampler. Firmware v0.0.163+."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "video", "synthesizer", "hypno2", "shader", "midi", "cv", "eurorack"]
    related_skills: ["hypno-2:shader-dev"]
---

# Hypno 2

Sleepy Circuits Hypno 2 hardware video synthesizer and re-sampler. Built on Raspberry Pi 5 running vidOS. Re-samples 2 channels of video infinitely with mixer, feedback FX, shader engine, and per-parameter modulation.

**Manufacturer:** [Sleepy Circuits](https://sleepycircuits.com/hypno-2)  
**Docs:** [docs.sleepycircuits.com/hypno2](https://docs.sleepycircuits.com/hypno2)  
**PDF manual:** `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf` (V0.100, firmware v0.0.163)

## When to Use

- Video feedback resampling and fractal effects
- Real-time shader-based video mixing and effects
- Audio-reactive visuals (mic, AUX, or channel audio)
- Eurorack CV control of video parameters
- MIDI-driven video playback and preset switching
- NDI network video routing
- Custom GLSL shader development

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

## Specs Summary

- **Processor:** Raspberry Pi 5 (active cooler), 250 GB M.2 SSD
- **Display:** 800×480 capacitive touchscreen
- **Video I/O:** 2× micro HDMI out (1080p, 1 active), USB UVC in, NDI
- **Audio I/O:** Built-in mic, AUX 3.5mm, HDMI audio, USB, NDI
- **CV:** 4× 0–5 V unipolar Eurorack inputs
- **Clock:** 2× trigger inputs (64 ppqn BPM readout)
- **USB:** 3× USB-A (drives, MIDI, cameras, capture cards)
- **Networking:** Ethernet, Wi-Fi, Bluetooth (BLE MIDI)
- **Price:** $1,499 USD

Full hardware specs, rear panel I/O, settings pages, desktop mode keyboard mapping: [references/hardware.md](mdc:references/hardware.md)

## MIDI CC Map (Summary)

**Main / Master (MIDI Ch 16):** CC 0–8 = ch1 gain, feedback, ch2 gain, fb x/y/zoom/rotate, low/hi key.

**Track A/B (MIDI Ch 1/2):** CC 0–61 = x/y offset, frequency, rotation, crop, aspect, mirror, luma, hue/chrominance/lightness. CC 66–127 = mod CC for each parameter.

Full CC table + MIDI note mapping: [references/midi-cc.md](mdc:references/midi-cc.md)

## Modulation Sources

Each parameter (tap label) offers: **Internal LFO** (14 waveforms), **Audio Input** (mic/AUX with 3-band), **CV Input** (4 jacks), **MIDI CC**, **Clock/BPM Sync**, **Audio Track**.

Full modulation detail: [references/modulation.md](mdc:references/modulation.md)

## Factory Shader Library

**FX Shaders (Main track):** `fx_feedback.frag` (default), `fx_hsv_feedback`, `fx_hyperdigital_feedback`, `fx_invert_feedback`, `fx_lumakey_feedback`. All share CC 0–8.

**Shape Shaders (Ch A/B):** `sin`, `tan`, `poly`, `circle`, `noise`, `sampler` (CC 0–2 reserved for loop/framerate).

**Custom shaders:** `.frag` GLSL, max 5 uniforms, live editor with compile errors.

Full shader reference: [references/shaders.md](mdc:references/shaders.md)

## Patch Recipes (Cookbook)

12 workflows: Infinite Feedback, Dual Source Crossfade, Audio Reactive, Eurorack CV, MIDI Keyboard Chromatic, LFO Auto-Animation, Live Camera Feedback, Preset Performance, Shader Switching, NDI Network, Clock-Synced, Desktop Shader Dev.

Full recipes: [references/patch-recipes.md](mdc:references/patch-recipes.md)

## Resources

- PDF manual: `/home/rjodouin/Downloads/current_music_docs/Hypno 2 Manual (V0.100).pdf`
- Online: https://docs.sleepycircuits.com/hypno2
- GitHub docs (community): https://github.com/teafella/sleepy-docs/tree/main/hypno2
- GitHub binaries (h2ctl): https://github.com/teafella/sleepy_binaries/tree/main/h2/h2ctl
- GitBook: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-manual
- FAQ: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-faq
- Firmware: https://sleepycircuits.gitbook.io/sleepy-circuits/hypno2/hypno-2-firmware
- Forum: https://forum.sleepycircuits.com/
- Matrix: #sleepycircuits:matrix.org
- Shader dev guides: [shader-dev/techniques/](shader-dev/techniques/) — noise, SDF, voronoi, domain warping, blend modes, edge detection, audio-reactive
- Shader templates: [shader-dev/templates/](shader-dev/templates/) — bare-minimum.frag, generative-shape.frag, video-effect.frag, audio-reactive.frag