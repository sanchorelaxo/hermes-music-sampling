---
name: "minikp-v1"
description: "Korg KAOSS PAD miniKP dynamic effect processor (2006 model) — X-Y touchpad FX, 100 programs, PROGRAM/BPM knob, LINE IN/OUT RCA, USB MIDI on Linux"
category: instruments
---

# miniKP V1 Skill

Korg KAOSS PAD miniKP dynamic effect processor, first generation (2006).

## Hardware

| Spec | Value |
||~~~~~~||~~~~~~-|
| Year | 2006 |
| Dimensions | Compact (see PDF) |
| Weight | Compact |
| Power | 4x AA batteries or optional AC adapter (DC4.5V) |
| Connectors | LINE IN (RCA L/R), LINE OUT (RCA L/R), PHONES (stereo mini), DC jack |
| Touchpad | X-Y position sensing |
| Controls | PROGRAM/BPM knob, Effect depth knob, ON/STANDBY switch |
| Display | LED/segment display for program number and BPM |

## Programs

- **100 effect programs** (00-99)
- Programs include: filters, delays, reverbs, flangers, phasers, distortions, grain shifters, loopers, synth sounds
- Categories visible in program list: Slicer, Delay, Reverb, Looper, Synth, etc.
- X axis and Y axis control different parameters per program

## Effect Types (V1 Program List)

- **Filters**: LPF, HPF, BPF+, Comb filter
- **Delays**: Standard, Smooth, Low Cut, Ping Pong, LCR, 3-band, Multi Tap, Reverse
- **Reverbs**: Standard, Spring, Gate, Reverse Gate, 3-band variants
- **Modulation**: Flanger, Phaser, Chorus, Tremolo
- **Distortion**: Fuzz, Bit Crush, Decimator
- **Grain Shifter**: Multiple variants including Mid Grain
- **Loopers**: Forward/Reverse, Vinyl, Rewind, with LPF/HPF/Flanger/Pitch Shift
- **Synth**: Unison Saw/Square Bass, Metalic Synth, Siren, LFO variants, Noise
- **EQ/Isolator**: 3-band EQ, Isolator

## Controls

| Element | Function |
||~~~~~~~~~||~~~~~~~~~-|
| PROGRAM/BPM knob | Select program 00-99 / adjust BPM |
| Effect depth knob | Set effect wet/dry mix |
| ON/STANDBY switch | Power on/off |
| PEAK indicator | Input level clipping warning |

## Key Features

- **Hold function**: effect continues playing after finger leaves pad (BPM-synchronized delay tails)
- **BPM tap**: tap PROGRAM/BPM knob to set tempo from external source
- **Memory store**: save current program + effect depth + BPM to a memory location (A button)
- **Memory recall**: recall stored memories (B button)
- **Effect send/return**: can be used with mixer's effect send/return loop

## Input/Output Routing

- LINE IN from CD player, mixer, or other audio source
- LINE OUT to mixer, headphones, or recorder
- Input level attenuator to prevent clipping
- Effect and dry signal can be mixed at output

## Auto Return

- Returns to program selection automatically if no operation for ~15 seconds (BPM mode)
- Returns after ~3 seconds in memory/other modes

## Linux USB MIDI

```bash
# Detect device
amidi -l | grep -i miniKP

# Monitor MIDI
amidi -p hw:X,Y,Z -d
```

- Class-compliant — no driver needed
- X-Y pad sends MIDI data for real-time control

## Source

`~/Downloads/current_music_docs/miniKP_OM_EFG1.pdf`
