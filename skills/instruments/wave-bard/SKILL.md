---
name: "wave-bard"
description: "Use when working with the Bastl Kastle 2 Wave Bard — patchable stereo sample player with 8 samples/bank, scale quantization, resonant filter, stereo delay/chorus-flanger, pattern generator, LFO, and full CV/Gate/MIDI modulation. Firmware v1.6+."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "sampler", "kastle2", "bastl", "cv", "midi", "patchbay"]
    related_skills: ["fx-wizard", "kastle2-hardware"]
---

# Bastl Kastle 2 — Wave Bard

**Manufacturer:** [Bastl Instruments](https://bastl-instruments.com/instruments/kastle-2-wave-bard) (Czech Republic) — NOT Korg  
**Platform GitHub:** https://github.com/bastl-instruments/kastle2

Wave Bard is a patchable stereo sample player with 8 samples per bank, scale quantization, resonant filter, stereo delay/chorus-flanger, pattern generator, LFO, and full CV/Gate/MIDI modulation.

## When to Use

- Triggering and playing audio samples with CV/MIDI modulation
- Building quantized melodic sequences on a Eurorack-compatible platform
- Creating rhythmic patterns with the internal pattern generator and LFO
- Patching custom signal chains using the 3.5mm patchbay
- Loading custom samples via the web app editor

## Quick Reference

| Control | Function |
|---------|----------|
| **SHIFT** (short press) | Trigger selected sample (on button release) |
| **SHIFT + KNOB** | Secondary (silver) function |
| **BANK** | Next bank |
| **BANK + SHIFT** | Previous bank |
| **SHIFT + PITCH knob** | Output volume |
| **SHIFT + PITCH MOD knob** | Input gain |
| **SHIFT + BANK (>2s)** | Advanced settings |
| **SHIFT + BANK (>10s)** | Memory reset |
| **SHIFT + BANK (tap)** | Tap tempo |

## Main Controls (Follow the White Woodpeckers)

| Knob | Parameter | Secondary (SHIFT+) |
|------|-----------|-------------------|
| **PITCH** (top right) | Playback rate ±2 octaves | Output volume |
| **PITCH MOD** (top left) | Modulation amount of pitch CV input | Input gain |
| **SAMPLE** (middle right) | Select 1 of 8 samples in bank | Filter (LP/HP) |
| **SAMPLE MOD** (middle left) | CV modulation of sample select (PLAY or CUE mode) | Delay or Chorus/Flanger |
| **LENGTH** (center) | Decay (right) or reverse attack (left) | LENGTH input attenuversion |
| **LFO** (bottom right) | LFO speed/sync | Tempo (when SHIFT held) |
| **LFO MOD** (bottom left) | LFO modulation amount | Load preset rhythm |
| **BANK** button | Next bank | Previous bank (hold SHIFT) |

## Sample Organization

- **8 samples per bank** (adjustable 3–32 in editor)
- **6 factory banks** (Oliver Torr)
- Turn **SAMPLE knob** to browse 8 samples. **SHIFT** triggers the current sample.
- Each bank has a color. **BANK button** cycles banks.
- Samples organized as: Bank → Sample index → Sound

**Loading custom samples:** Via web app → generates .uf2 firmware file → copy to Wave Bard in boot mode (hold SHIFT + power ON).

## Pitch & Quantizer

**PITCH knob**: ±2 octaves playback rate (4 octaves total range). Not quantized by default.

**Quantized pitch**: Sample pitch aligns to musical scale when NOTE PITCH MOD input changes or when previewing scale (hold BANK + turn PITCH).

### Scale Selection

**BANK + PITCH MOD** → cycles through scales. Default scales:

| Scale | Notes (from C) |
|-------|---------------|
| Chromatic | All 12 |
| Major | C D E F G A B |
| Minor | C D Eb F G Ab Bb |
| Pentatonic | C D E G A |
| Blues | C Eb F Gb G Bb |

User-defined scales loadable via web app editor.

### Pitch Controls

| Action | Control |
|--------|---------|
| Change octave | **BANK + PITCH** (triggers sample on change) |
| Fine tune ±2 semitones | **BANK + LFO MOD** (after quantizer) |
| Set root note | **BANK + SAMPLE MOD** |
| Free (unquantized) pitch | PITCH knob directly (no scale) |
| Quantized pitch CV | NOTE PITCH MOD patch input (updates on trigger) |
| Free pitch CV | FREE patch input (continuous, unquantized) |

> **Note**: All loaded samples should be tuned to tone C for tonal accuracy with scales.

## Sample Trigger & Envelope

### Trigger
- **SHIFT** (short press): Triggers selected sample on button **release**
- **TRIG** patch input: Trigger sample playback

### Length Envelope
- **LENGTH right**: Sets decay time
- **LENGTH left**: Sets reverse attack envelope (sample plays backward, then fades in forward)
- During reverse attack: sample does **not retrigger**
- **LENGTH MOD**: CV modulation of length envelope (updates only at trigger)
- **ENV OUT**: Patchable output of the length envelope

## Sample Select Modulation (SAMPLE MOD)

| Mode | Setting | Behavior |
|------|---------|----------|
| **PLAY** | Knob left | CV directly triggers samples |
| **CUE** | Knob right | CV aims at sample, playback waits for TRIG |

**BANK input**: Patch point for bank selection CV with attenuation.

## Effects

### Delay / Chorus-Flanger (**SHIFT + SAMPLE MOD**)

| Position | Effect |
|----------|--------|
| Center | No effect |
| Left | Stereo delay (tempo-synced to 3/8th note) |
| Right | Chorus + flanger + soft-clipping distortion |

### Filter (**SHIFT + SAMPLE**)

| Position | Type |
|----------|------|
| Center | Open (no filter) |
| Left | Lowpass filter |
| Right | Highpass filter |

## Tempo Generator

Tempo source priority: **USB MIDI clock > SYNC IN > Internal clock**

- **SHIFT + LFO knob**: Set tempo (magenta = internal, cyan = external active)
- **SHIFT + tap BANK**: Tap tempo

**SYNC Jacks:**
- **SYNC IN** (left channel): External clock detection
- **SYNC OUT**: Outputs master clock; acts as **SYNC THRU** when SYNC IN is connected

## Modulation Sources

### LFO
- **LFO knob right**: Free-running (warm white light)
- **LFO knob center**: Synced to tempo (cold white light)
- **LFO outputs**: `TRI` (triangle), `PULSE` (high when triangle rises)
- **LFO inputs**: `RESET` (rising edge resets to peak), `LFO MOD` (speed modulation)

**Shaping waveforms:** Patch PULSE → LFO MOD for ramp/saw; patch TRI → LFO MOD for exp/log.

### Pattern Generator

Always tempo-synced. Sequence length is selectable via the web app (v1.6+; default 8 steps):
- **GATE**: Rhythmic sequence (75% gate length per step)
- **CV**: Stepped voltage sequence

**Patchbay inputs:**
- `PATTERN G` (left): Modifies GATE rhythm
- `PATTERN C` (right): Modifies CV sequence
- `PATTERN R` (middle): RESETS both GATE and CV on rising edge

**GATE rhythm**: **SHIFT + LFO MOD knob** → cycles through 16 preset rhythms from web app.

## Patchbay Summary

### Triple Patch Points
Three horizontal points are interconnected. Multiple outputs → single input = combined signal.

### Output vs Input
- **Outputs**: White outline, labeled inside
- **Inputs**: White text or white arrows (no outline)

### Voltage Compatibility
- Inputs: 0–5V | Outputs: 0–5V

### Bi-Directional Ports (TRS at back)
| Symbol | Description |
|--------|-------------|
| **+** | Logic high output (~5V) |
| **−** | Logic low output (~0V) |
| **⏚** | Direct ground reference |

**⚠️ When connecting multiple Kastles: connect grounds together.** Audio/sync jacks connect grounds automatically; use ⏚ → ground for explicit connection.

## Audio Input Routing

**SHIFT + PITCH MOD knob**: Adjust input gain.

**Input routing** (Advanced Settings → PITCH knob):
- Right (blue): Mix AUDIO IN with Wave Bard at output
- Left (red): Route AUDIO IN through Wave Bard effects

**Mono input mode** (Advanced Settings → PITCH MOD knob):
- Left = mono left | Center = stereo | Right = mono right

## Advanced Settings

**Enter**: **SHIFT + BANK (>2s)** | **Exit**: Power cycle or **SHIFT + BANK (>2s)**

| Setting | Control | Values |
|---------|---------|--------|
| Audio input behavior | PITCH MOD knob | Left=mono L, Center=stereo, Right=mono R |
| Input routing | PITCH knob | Left=FX through, Right=mix at output |
| Clock priority | LFO knob | Khaki=ignore MIDI, White=normal, Orange=ignore SYNC IN |
| Memory reset | SHIFT + BANK (>10s) | — |

## Patch Recipes

Full cookbook (16 recipes): [references/patch-recipes.md](mdc:references/patch-recipes.md)

## MIDI Implementation

Full CC table, note mapping, and clock sync: [references/midi-cc.md](mdc:references/midi-cc.md)

## Web App Editor (Sample Loader)

Full editor guide, upload steps, and tips: [references/web-app.md](mdc:references/web-app.md)

## Resources

| Document | Source |
|----------|--------|
| Quickstart Guide | `/home/rjodouin/Downloads/kastle2-stuff/manual-kastle2-wavebard-quickstart-web.pdf` |
| Complete Manual | `/home/rjodouin/Downloads/kastle2-stuff/manual-kastle2-wavebard-web.pdf` |
| Cookbook (recipes) | `/home/rjodouin/Downloads/kastle2-stuff/kastle2-wavebard-cookbook.pdf` |
| Patch Sheets | `/home/rjodouin/Downloads/kastle2-stuff/kastle2-wavebard-patchsheet.pdf` |
| Sample Loader Web App | [apps.bastl-instruments.com/wave-bard-sample-loader](https://apps.bastl-instruments.com/wave-bard-sample-loader/) |
| GitHub (open-source) | [github.com/bastl-instruments/kastle2](https://github.com/bastl-instruments/kastle2) |