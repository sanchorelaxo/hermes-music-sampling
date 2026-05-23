# FX Wizard — MIDI CC Reference

## Setting MIDI Channel

**Learn mode:** Hold **BANK** ≥1s → top right light turns off → send any MIDI message → light turns orange → release BANK → light blinks channel number.

**Manual:** Hold **SHIFT + tap BANK** N times → release → light blinks N.

## Receiving MIDI Notes

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

## Receiving MIDI CC

| CC | Parameter | Physical Knob |
|----|-----------|---------------|
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

## Sending MIDI

Knobs send CC 1 (FX MODE), 14–26 on the set MIDI channel when adjusted. CC1 (trigger) also sent when TRIG input fires.

## MIDI Clock Sync

FX Wizard syncs to incoming USB MIDI clock. Clock divider options (via TEMPO knob): 24 (¼ note), 12 (8th), 6 (16th), 3 (32nd), 1 (1:1).

**Transport:** MIDI Start = reset pattern gen + LFO; MIDI Stop = reset + stop; MIDI Continue = resume from current position.

**Sends MIDI clock** when NOT receiving MIDI clock (or after ignore setting).

## Linux / USB MIDI

Class-compliant USB MIDI device. No driver needed.

```bash
# List MIDI ports
amidi -l

# Find Kastle 2
# "Kastle 2 FX Wizard" appears as a MIDI device

# Send CC to FX Wizard
sendmidi dev "Kastle 2 FX Wizard" cc 14 64  # TIME = 64

# Connect to DAW
# CC14 = TIME, CC16 = FEEDBACK, CC18 = AMOUNT
# Notes 0-8 = switch FX modes
```