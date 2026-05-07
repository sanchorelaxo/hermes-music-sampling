---
name: "wave-bard"
description: "Korg Kastle 2 Wave Bard — patchable stereo sample player with 8 samples/bank, scale quantization, resonant filter, stereo delay/chorus-flanger, pattern generator, LFO, and full CV/Gate/MIDI modulation. Firmware v1.5+."
category: instruments
---

# Korg Kastle 2 — Wave Bard

## Device

| Spec | Detail |
|------|--------|
| Mode | Wave Bard (sample player) — separate firmware from FX Wizard |
| Samples | 8 samples per bank (3–32 adjustable in editor), 6 factory banks |
| Sample Time | 89s mono / 44s stereo at 44kHz (or combination); more time at lower sample rates |
| Memory | 7.5 MiB; banks: 1–32; all banks must have same sample count |
| Audio | Stereo in/out, 44kHz/16-bit |
| Power | USB-C (5V) or 3× AA batteries (~15–18 hours) |
| I/O | 3.5mm patch points: CV, Gate, LFO, Trigger, Sync; USB MIDI; analog sync in/out |
| MIDI | Sends/receives: notes, CC, pitch bend, clock |
| Weight | ~350g estimated |

**Factory banks**: 6 pre-loaded banks by Oliver Torr.

**⚠️ USB does NOT charge batteries.**

***

## Quick Reference

| Control | Function |
|---------|---------|
| **SHIFT** (short press) | Trigger selected sample (on button release) |
| **SHIFT + KNOB** | Secondary (silver) function |
| **BANK** | Next bank |
| **BANK + SHIFT** | Previous bank |
| **SHIFT + PITCH knob** | Output volume |
| **SHIFT + PITCH MOD knob** | Input gain |
| **SHIFT + BANK (>2s)** | Advanced settings |
| **SHIFT + BANK (>10s)** | Memory reset |
| **SHIFT + BANK (tap)** | Tap tempo |

***

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

***

## Sample Organization

- **8 samples per bank** (adjustable 3–32 in editor)
- **6 factory banks** (Oliver Torr)
- Turn **SAMPLE knob** to browse 8 samples. **SHIFT** triggers the current sample.
- Each bank has a color. **BANK button** cycles banks.
- Samples organized as: Bank → Sample index → Sound

**Loading custom samples**: Via web app → generates .uf2 firmware file → copy to Wave Bard in boot mode (hold SHIFT + power ON).

***

## Pitch & Quantizer

**PITCH knob**: ±2 octaves playback rate (4 octaves total range). Not quantized by default — works in free mode.

**Quantized pitch**: Sample pitch aligns to musical scale when NOTE PITCH MOD input changes or when previewing scale (hold BANK + turn PITCH).

### Scale Selection
**BANK + PITCH MOD** → cycles through scales. Default scales available (with ROOT=C):

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

***

## Sample Trigger & Envelope

### Trigger
- **SHIFT** (short press): Triggers selected sample on button **release**
- **TRIG** patch input: Trigger sample playback

### Length Envelope
- **LENGTH right**: Sets decay time
- **LENGTH left**: Sets reverse attack envelope (sample plays backward, then fades in forward — attack from reversed)
- During reverse attack: sample does **not retrigger** (held note plays through reversal before forward starts)
- **LENGTH MOD**: CV modulation of length envelope (updates only at trigger)
- **ENV OUT**: Patchable output of the length envelope

***

## Sample Select Modulation (SAMPLE MOD)

Controls CV modulation of sample selection.

| Mode | Setting | Behavior |
|------|---------|----------|
| **PLAY** | Knob left | CV directly triggers samples |
| **CUE** | Knob right | CV aims at sample, playback waits for TRIG |

**BANK input**: Patch point for bank selection CV with attenuation.

***

## Effects

### Delay / Chorus-Flanger
**SHIFT + SAMPLE MOD** knob:

| Position | Effect |
|----------|--------|
| Center | No effect |
| Left | Stereo delay (tempo-synced to 3/8th note) |
| Right | Chorus + flanger + soft-clipping distortion (further right = more flanging resonance) |

### Filter
**SHIFT + SAMPLE** knob:

| Position | Type |
|----------|------|
| Center | Open (no filter) |
| Left | Lowpass filter |
| Right | Highpass filter |

***

## Tempo Generator

Tempo source priority: **USB MIDI clock > SYNC IN > Internal clock**

### Set Internal Tempo
- **SHIFT + LFO knob**: Set tempo (magenta metronome light = internal)
- **SHIFT + tap BANK**: Tap tempo

### Sync to External
- Connect analog clock to **SYNC IN** jack
- **SHIFT + LFO knob**: Select tempo divider (cyan light = external active)
- If clock missing >2s: Pattern Generator resets to step 1

### Clock Priority (Advanced Settings)
Enter: **SHIFT + BANK (>2s)**

| LFO Knob Position | Light | Behavior |
|-------------------|-------|----------|
| Left (khaki) | Ignore MIDI clock |
| Center (white) | Normal priority |
| Right (orange) | Ignore analog SYNC IN |

### SYNC Jacks
- **SYNC IN** (left channel): External clock detection. Right channel → `SYNC IN R` patch point.
- **SYNC OUT**: Outputs master clock. Acts as **SYNC THRU** when SYNC IN is connected.
- SYNC OUT R patch point for non-clock use.

***

## Modulation Sources

### LFO
- **LFO knob right section**: Free-running, speed increases as knob turns right (warm white light)
- **LFO knob center**: Synced to tempo, knob sets divider (cold white light)
- **LFO outputs**: `TRI` (triangle), `PULSE` (high when triangle rises)
- **LFO inputs**: `RESET` (rising edge resets to triangle peak), `LFO MOD` (attenuverting modulation of speed)

**Shaping LFO waveforms**:
- Ramp/Saw: Patch PULSE → LFO MOD, adjust LFO MOD
- Exp/Log: Patch TRI → LFO MOD, adjust LFO MOD
- Saw wave: Patch PULSE → LFO RESET
- Hybrid: Patch TRI → LFO RESET

### Pattern Generator
Always tempo-synced. Produces two signals:
- **GATE**: Rhythmic (75% gate length per step), 8-step sequence
- **CV**: Stepped voltage sequence, 8-step

**Patchbay inputs for Pattern Generator**:
| Input | Function |
|-------|----------|
| PATTERN G (left pin) | Modifies GATE rhythm (patch + = randomize, patch − = invert steps) |
| PATTERN C (right pin) | Modifies CV sequence (patch + = randomize level, patch − = invert around 2.5V) |
| PATTERN R (middle pin) | RESETS both GATE and CV sequences on rising edge |

**GATE rhythm**: **SHIFT + LFO MOD knob** → cycles through 16 preset rhythms loaded from web app.

***

## Patchbay

### Triple Patch Points
Three horizontal points are interconnected. Multiple outputs → single input = combined signal (safe to combine).

### Output vs Input
- **Outputs**: White outline, labeled inside outline
- **Inputs**: White text or white arrows pointing toward destination (no outline)

### Voltage Compatibility
- Inputs: 0–5V
- Outputs: 0–5V (or less, depending on power source)

### Bi-Directional Ports (TRS at back)
| Symbol | Description |
|--------|-------------|
| **+** | Logic high output (~5V) |
| **−** | Logic low output (~0V) |
| **⏚** | Direct ground reference |

Patching + and − together → ~2.5V (resistor protected).

**⚠️ When connecting multiple Kastles or devices: must connect grounds together. Audio/sync jacks connect grounds automatically. Use ⏚ → ground or − patch point for explicit ground connection.**

***

## Audio Input Routing

**SHIFT + PITCH MOD knob**: Adjust input gain.

**Input routing** (Advanced Settings → PITCH knob):

| Knob Position | Light | Routing |
|---------------|-------|---------|
| Right | Blue | Mix AUDIO IN with Wave Bard at output |
| Left | Red | Route AUDIO IN through Wave Bard effects |

**Mono input mode** (Advanced Settings → PITCH MOD knob):
- Left = mono left channel only
- Center = stereo
- Right = mono right channel only

Useful for: clock on right channel + audio on left (e.g., TE-PO sync), or mono-only devices.

***

## MIDI Implementation

### Setting MIDI Channel
**Learn mode**: Hold **BANK** ≥1s → top right light turns off → send any MIDI message → light turns orange → release BANK → light blinks channel number.

**Manual**: Hold **SHIFT + tap BANK** N times → release → light blinks N.

### Receiving MIDI Notes
Notes 0–48 (lowest 4 octaves): switch and trigger samples in current bank. Note C = first sample in bank. Only first 12 samples can be triggered.

| Octave Range | Pitch Behavior |
|-------------|---------------|
| 0–23 | Original pitch |
| 24–47 | Original pitch |
| 0–11, 12–23 | Original pitch (same) |

Notes above 48 = trigger only (no pitch info).

### Receiving MIDI CC

| CC | Parameter | Physical Knob |
|----|-----------|---------------|
| 1 | GATE trigger | TRIG input |
| 7 | Output Volume | SHIFT + PITCH |
| 9 | Input Gain | SHIFT + PITCH MOD |
| 14 | PITCH | PITCH knob |
| 15 | PITCH MOD | PITCH MOD knob |
| 16 | SAMPLE | SAMPLE knob |
| 17 | SAMPLE MOD | SAMPLE MOD knob |
| 18 | LENGTH | LENGTH knob |
| 19 | LENGTH MOD | SHIFT + LENGTH |
| 20 | FILTER | SHIFT + SAMPLE |
| 21 | FX (delay/chorus) | SHIFT + SAMPLE MOD |
| 22 | LFO | LFO knob |
| 23 | LFO MOD | LFO MOD knob |
| 24 | TEMPO | SHIFT + LFO |
| 25 | RHYTHM | SHIFT + LFO MOD |
| 74 | BANK | BANK button |

### Sending MIDI
Wave Bard acts as MIDI controller/sequencer. Sends notes, CC, pitch bend, clock.

### MIDI Clock Sync
Same as FX Wizard: syncs to incoming USB MIDI clock. Clock divider options (via TEMPO): 24 (¼), 12 (8th), 6 (16th), 3 (32nd), 1 (1:1).

**Transport**: MIDI Start = reset pattern gen; MIDI Stop = reset + stop; MIDI Continue = resume from position.

**Sends MIDI clock** when NOT receiving MIDI clock (or after ignore setting).

***

## Web App Editor (Sample Loader)

Access: Chrome/Edge/Firefox desktop (not Safari). PWA-installable.

**Features**:
- Load WAV, MP3, OGG, AAC, M4A, AIFF
- Organize samples into banks (3–32 per bank)
- Edit scales (3–32 custom scales)
- Edit rhythms (3–32 patterns)
- Preview samples
- Generate .uf2 firmware file

**To upload**:
1. Go to web app
2. Add/organize samples
3. Click **GENERATE FIRMWARE FILE**
4. Power off → hold SHIFT → power on (connected to USB)
5. Copy .uf2 to RPI-RP2 disk
6. Wait 2–5 minutes

**Tips**:
- Samples should be tuned to C for scale accuracy
- Remove silence from samples to save memory
- All banks must have same number of samples
- Draft saves allow re-editing before generating .uf2

***

## Advanced Settings

**Enter**: **SHIFT + BANK (>2s)**

| Setting | Control | Values |
|---------|---------|--------|
| Audio input behavior | PITCH MOD knob | Left=mono L, Center=stereo, Right=mono R |
| Input routing | PITCH knob | Left=FX through, Right=mix at output |
| Clock priority | LFO knob | Khaki=ignore MIDI, White=normal, Orange=ignore SYNC IN |
| Memory reset | SHIFT + BANK (>10s) | — |

**Exit**: Power cycle (settings auto-save) or **SHIFT + BANK (>2s)**.

***

## Linux / USB MIDI

Class-compliant USB MIDI + audio device.

```bash
# List MIDI ports
amidi -l

# Connect to DAW
aconnect or a2jmidid for bridge

# Send MIDI to Wave Bard
sendmidi dev "Kastle 2 Wave Bard" cc 14 64  # PITCH = 64

# Note CC example
sendmidi dev "Kastle 2 Wave Bard" note 60 127 1  # C4, velocity 127, channel 1
```

***

## Reference

- FX Wizard manual: `~/Downloads/current_music_docs/manual-kastle2-fxwizard-web.pdf`
- Wave Bard manual: `~/Downloads/current_music_docs/manual-kastle2-wave-bard-web.pdf`
