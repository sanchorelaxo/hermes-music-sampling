# Wave Bard — MIDI CC Reference

## Setting MIDI Channel

**Learn mode:** Hold **BANK** ≥1s → top right light turns off → send any MIDI message → light turns orange → release BANK → light blinks channel number.

**Manual:** Hold **SHIFT + tap BANK** N times → release → light blinks N.

## Receiving MIDI Notes

Notes 0–48 (lowest 4 octaves): switch and trigger samples in current bank. Note C = first sample in bank. Only first 12 samples can be triggered.

| Octave Range | Pitch Behavior |
|-------------|----------------|
| 0–23 | Original pitch |
| 24–47 | Original pitch |
| 0–11, 12–23 | Original pitch (same) |

Notes above 48 = trigger only (no pitch info).

## Receiving MIDI CC

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

## Sending MIDI

Wave Bard acts as MIDI controller/sequencer. Sends notes, CC, pitch bend, clock.

## MIDI Clock Sync

Same as FX Wizard: syncs to incoming USB MIDI clock. Clock divider options (via TEMPO): 24 (¼), 12 (8th), 6 (16th), 3 (32nd), 1 (1:1).

**Transport:** MIDI Start = reset pattern gen; MIDI Stop = reset + stop; MIDI Continue = resume from position.

**Sends MIDI clock** when NOT receiving MIDI clock (or after ignore setting).

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