---
name: "fx-wizard"
description: "Korg kastle 2 FX Wizard — patchable stereo multi-FX unit with 9 effects (Delay/Flanger/Freezer/Panner/Crusher/Slicer/Pitcher/Replayer/Shifter), pattern generator, LFO, envelope follower, and full CV/Gate/MIDI modulation. Firmware v1.5+."
category: instruments
---

# Korg kastle 2 — FX Wizard

## Device

| Spec | Detail |
|------|--------|
| Mode | FX Wizard (effects processor) — separate firmware from Wave Bard |
| Audio | Stereo in/out, 44kHz/16-bit |
| Power | USB-C (5V) or 3× AA batteries (~15–18 hours) |
| I/O | 3.5mm patch points: CV, Gate, LFO, Trigger, Sync; USB MIDI; analog sync in/out |
| Memory | 15 presets per mode |
| Dimensions | Compact portable (specific mm not published) |
| Weight | ~350g estimated |

**Battery**: Low battery → backlight turns red. Fresh alkaline: 3×1.5V=4.5V. NiMh: 3×1.2V=3.6V. Below 3V = dead.

**Audio Input**: +12dB gain max, accepts up to 6Vpp. WHILE HOLDING SHIFT: KASTLE logo light shows signal strength (orange=good, red=clipping). For Eurorack (>6Vpp): attenuate externally first.

**Audio Output**: Drives headphones up to 250 Ohm.

**⚠️ USB does NOT charge batteries.**

***

## Quick Reference

| Control | Function |
|---------|---------|
| **FX MODE** button | Cycle to next FX mode |
| **SHIFT + FX MODE** | Previous FX mode |
| **SHIFT + KNOB** | Secondary (silver) function |
| **SHIFT + TIME knob** | Output volume |
| **SHIFT + TIME MOD knob** | Input gain |
| **SHIFT + FX MODE (>2s)** | Advanced settings |
| **SHIFT + FX MODE (>15s)** | Memory reset |
| **SHIFT + LFO knob** | Set internal tempo |
| **SHIFT + FX MODE (tap)** | Tap tempo |

***

## 9 FX Modes

All modes share the same 3 main parameter knobs (white rabbits): **TIME**, **FEEDBACK**, **AMOUNT** — plus FILTER and STEREO (secondary functions).

| # | Mode | Color | TIME | FEEDBACK | AMOUNT |
|---|------|-------|------|----------|--------|
| 1 | **Delay** | blue | delay time | feedback | mix |
| 2 | **Flanger** | green | speed | feedback | depth |
| 3 | **Freezer** | blue | freeze size | feedback | mix |
| 4 | **Panner** | white | panning freq (→audio rate = ring mod) | global feedback | amplitude mod (square clip=radical pan) |
| 5 | **Crusher** | yellow | downsampling freq | distorted tonal backdrop | downsampling+XOR bitcrush |
| 6 | **Slicer** | light green | slice pattern | random trigger inversion | decay + dry/wet |
| 7 | **Pitcher** | red | shifting window/grain size | global feedback | ramp mod pitch shift + dry/wet |
| 8 | **Replayer** | orange | tape speed (±=fwd/rev) | feedback for new signal only | output+input buffer mix |
| 9 | **Shifter** | pink | pitch change (±=±semitones) | global feedback | dry/wet |

### Common Parameters (All Modes)

| Parameter | Control | Description |
|-----------|---------|-------------|
| **TIME** | White rabbit (top right) | Main time/frequency parameter |
| **TIME MOD** | Top left knob | Attenuverting modulation of TIME (center=0, right=positive, left=negative) |
| **FREE TIME MOD** | Patch input | Real-time direct modulation of TIME |
| **STEP TIME MOD** | Patch input | Tempo-stepped S&H modulation of TIME |
| **FEEDBACK** | White rabbit (middle right) | Unique per-mode; feeds incoming audio into effect |
| **FEEDBACK MOD** | Middle left knob | Attenuverting modulation of FEEDBACK |
| **AMOUNT** | Center knob | Dry/wet mix; fully left = full dry (effect off) |
| **AMOUNT MOD** | Patch input | Modulation of AMOUNT |
| **FILTER** | SHIFT + middle right knob | LP (left) / HP (right) in feedback path; center = open |
| **STEREO** | SHIFT + middle left knob | Detunes TIME for L/R channels (widens stereo image) |
| **TRIG** | Patch input | Aligns effect to tempo or triggers rhythmic events |

### Mode-Specific Details

**Delay (blue)**: Clean stereo delay. Max delay time ~1.15s (FW v1.1+). TIME = delay length, FEEDBACK = repeats, AMOUNT = mix.

**Flanger (green)**: Chorus/flanger with extremes. TIME = speed, FEEDBACK = resonance/feedback, AMOUNT = depth. STEREO = L/R channel detune.

**Freezer (blue)**: Captures and holds moments of audio. TIME = freeze buffer chunk size, FEEDBACK = density of frozen audio, AMOUNT = freeze (fully left = freeze new audio as it leaves minimum). TRIG = freeze new chunk.

**Panner (white)**: Amplitude modulation L/R inverse. TIME = panning frequency (up to audio rate = stereo ring mod), AMOUNT = modulation depth (clipping sine→square wave = extreme panning), FEEDBACK = global feedback. TRIG = reset panner direction.

**Crusher (yellow)**: Downsampling + bitcrushing. TIME = downsampling frequency, AMOUNT = downsampling intensity + XOR bitcrush (right), FEEDBACK = distorted tonal backdrop. TRIG = envelope dips sampling frequency temporarily.

**Slicer (light green)**: Internal tempo-synced rhythm triggers amplitude decay envelope. TIME = slice pattern (step), AMOUNT = decay (left=long, right=short) + dry/wet, FEEDBACK = random trigger inversion probability + global feedback. STEREO = different pattern per channel. TRIG = triggers slice envelope.

**Pitcher (red)**: RAMP modulation delay buffer for crude pitch-up shifting. TIME = shifting window/grain size (slow=rhythmic chops, fast=formant shifts), AMOUNT = ramp mod pitch shift + dry/wet, FEEDBACK = global feedback. TRIG = envelope temporarily enlarges window.

**Replayer (orange)**: Tape looper emulation. TIME = tape speed (left=backward, right=forward), AMOUNT = output level vs new input (right=lock buffer, left=add new signal), FEEDBACK = feedback for new signal only (not output). TRIG = fills buffer with new audio.

**Shifter (red/pink)**: Nuanced pitch shifting avoiding transient duplication. TIME = pitch direction (above middle=up, below=down), AMOUNT = dry/wet, FEEDBACK = global feedback. Cool noises when slight shift + input fades. TRIG = resets LFO sync.

***

## Tempo Generator

Tempo source priority: **USB MIDI clock > SYNC IN > Internal clock**

### Set Internal Tempo
- **SHIFT + LFO knob**: Set tempo (magenta metronome light = internal)
- **SHIFT + tap FX MODE**: Tap tempo

### Sync to External
- Connect analog clock to **SYNC IN** jack
- **SHIFT + LFO knob**: Select tempo divider (cyan light = external active)
- If clock missing >2s: Pattern Generator resets to step 1

### Clock Priority (Advanced Settings)
Enter: **SHIFT + FX MODE (>2s)**

| LFO Knob Position | Light | Behavior |
|-------------------|-------|----------|
| Left | Khaki | Ignore MIDI clock |
| Center | White | Normal priority |
| Right | Orange | Ignore analog SYNC IN |

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

### Envelope Follower
- `ENV OUT`: Audio envelope amplitude output
- `ENV IN`: Envelope follower input (for ducking effects — audio in → ENV → modulates AMOUNT/FEEDBACK)

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

**GATE rhythm**: **SHIFT + LFO MOD knob** → cycles through 16 patterns

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

## MIDI Implementation

### Setting MIDI Channel
**Learn mode**: Hold **BANK** ≥1s → top right light turns off → send any MIDI message → light turns orange → release BANK → light blinks channel number.

**Manual**: Hold **SHIFT + tap BANK** N times → release → light blinks N.

### Receiving MIDI Notes
Notes 0–44 (lowest 4 octaves) switch FX modes. C = mode 1 (Delay).

| Note | Mode |
|------|------|
| C (0, 12, 24, 36) | Delay |
| C# (1, 13, 25, 37) | Flanger |
| D (2, 14, 26, 38) | Freezer |
| D# (3, 15, 27, 39) | Panner |
| E (4, 16, 28, 40) | Crusher |
| F (5, 17, 29, 41) | Slicer |
| F# (6, 18, 30, 42) | Pitcher |
| G (7, 19, 31, 43) | Replayer |
| G# (8, 20, 32, 44) | Shifter |

Notes above 48 (C2) = trigger only.

### Receiving MIDI CC

| CC | Parameter | Physical Knob |
|----|-----------|---------------|
| 0 | — | — |
| 1 | FX Mode | mapped from 0–127 to mode values |
| 7 | Output Volume | SHIFT + top right knob |
| 9 | Input Gain | SHIFT + top left knob |
| 14 | TIME | top right knob |
| 15 | TIME MOD | top left knob |
| 16 | FEEDBACK | middle right knob |
| 17 | FEEDBACK MOD | middle left knob |
| 18 | AMOUNT | center knob |
| 19 | AMOUNT MOD | SHIFT + center knob |
| 20 | FILTER | SHIFT + middle right knob |
| 21 | STEREO | SHIFT + middle left knob |
| 22 | LFO | bottom right knob |
| 23 | LFO MOD | bottom left knob |
| 24 | TEMPO | SHIFT + bottom right knob |
| 25 | RHYTHM | SHIFT + bottom left knob |
| 26 | FX MODE MOD | FX Mode + center knob |
| 121 | Reset all controllers | Restore knob control |

### Sending MIDI CC
Knobs send CC 1 (FX MODE), 14–26 on the set MIDI channel when adjusted. CC1 (trigger) also sent when TRIG input fires.

### MIDI Clock Sync
FX Wizard syncs to incoming USB MIDI clock. Clock divider options (via TEMPO knob): 24 (¼ note), 12 (8th), 6 (16th), 3 (32nd), 1 (1:1).

**Transport**: MIDI Start = reset pattern gen + LFO; MIDI Stop = reset + stop; MIDI Continue = resume from current position.

**Sends MIDI clock** when NOT receiving MIDI clock (or after ignore setting).

***

## Advanced Settings

**Enter/Exit**: **SHIFT + FX MODE (>2s)**

| Setting | Control | Values |
|---------|---------|--------|
| Clock priority | LFO knob | Khaki=ignore MIDI, White=normal, Orange=ignore SYNC IN |
| Memory reset | SHIFT + FX MODE (>15s) | — |

**Test Mode**: Hold **FX MODE** + power ON. Announces firmware version via voice. Full HW test requires: USB power, loopback cables (SYNC OUT→SYNC IN, AUDIO OUT→AUDIO IN), specific patch cables.

**Firmware Update**: Power OFF → hold SHIFT → power ON → copy .uf2 to RPI-RP2 disk.

***

## Linux / USB MIDI

Class-compliant USB MIDI device. No driver needed.

```bash
# List MIDI ports
amidi -l
# Find Kastle 2

# Set MIDI channel (via alsa)
aconnect or a2jmidid for bridge

# Send CC to FX Wizard
sendmidi dev "Kastle 2 FX Wizard" cc 14 64  # TIME = 64

# Connect to DAW
# CC14 = TIME, CC16 = FEEDBACK, CC18 = AMOUNT
# Notes 0-8 = switch FX modes
```
