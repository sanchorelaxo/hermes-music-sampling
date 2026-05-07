---
name: "kaoss-dj-mixer"
description: "Korg KAOSS DJ — USB DJ controller with X-Y touchpad, Serato DJ Intro integration, KAOSS effects, EQ, crossfader, and MIDI on Linux"
category: instruments
---

# KAOSS DJ MIXER Skill

Korg KAOSS DJ is a USB DJ controller that integrates with Serato DJ Intro. Features an X-Y touchpad for real-time effect control and full DJ mixer functionality.

## Device Overview

| Spec | Detail |
|------|--------|
| Touchpad | X-Y pad (KAOSS Effect mode) |
| Channels | 2-deck control (A/B) |
| Crossfader | Built-in crossfader curve-adjustable |
| EQ | 3-band EQ per deck (Hi/Mid/Lo) |
| Effects | KAOSS effects via touchpad |
| MIDI | USB MIDI (class-compliant) |
| Software | Serato DJ Intro (included/downloadable) |

## Touchpad Modes

Press `TOUCHPAD MODE` to cycle between:

| Mode | Function |
|------|----------|
| **Controller** | Controls Serato DJ software |
| **KAOSS Effect** | X-Y touchpad controls KAOSS effect |
| **Sampler** | Controls Serato DJ sampler |

### KAOSS Effect Mode (X-Y)
- **X-axis** = effect parameter 1 (e.g., time, rate)
- **Y-axis** = effect parameter 2 (e.g., depth, feedback)
- **Touch and drag** = real-time effect control

## Mixer Controls

| Control | Function |
|---------|----------|
| `GAIN` knob | Input gain per channel |
| `HI/MID/LO` knobs | 3-band EQ per deck |
| `HEADPHONE` knob | Headphone volume |
| `HEADPHONE BALANCE` | Cue/main mix blend |
| `MASTER` knob | Master output volume |
| `CROSSFADER` | Deck A/B blend |

## Effect Control (in KAOSS Effect mode)

| Control | Function |
|---------|----------|
| `PROGRAM` knob | Select effect type |
| `VALUE` knob | Adjust effect parameter |
| `FX` button | Assign effect to selected deck |
| `TAP` button | Tap tempo / auto BPM |

## MIDI on Linux

The KAOSS DJ is class-compliant USB MIDI. It also provides HID control for the DAW integration.

```bash
# List MIDI ports
amidi -l  # KAOSS DJ appears as raw MIDI device

# MIDI channel: per-preset (check manual for defaults)
# Notes = pad triggers
# CC = knob/fader positions
# Pitchbend = not used
```

### Sample MIDI Mapping
| Control | CC |
|---------|----|
| Deck A Gain | CC 14 |
| Deck A Hi EQ | CC 15 |
| Deck A Mid EQ | CC 16 |
| Deck A Lo EQ | CC 17 |
| Crossfader | CC 7 |
| Touchpad X | CC 20 |
| Touchpad Y | CC 21 |

## Software Workflow

The KAOSS DJ is designed for Serato DJ Intro, but the MIDI and audio I/O are standard:
1. Connect via USB
2. ALSA/JACK audio routing for analog output
3. MIDI routes to/from Serato
4. KAOSS touchpad works standalone for effect control

On Linux without Serato, use the MIDI data to control any DAW (Ardour, Mixxx, etc.) via MIDI learn.

## Quick Reference

| Action | Control |
|--------|---------|
| Switch touchpad mode | `TOUCHPAD MODE` button |
| Assign effect to deck | `FX` + deck button |
| Load track to deck | `LOAD` + deck button |
| Set cue point | `CUE` button |
| Loop | Touchpad + touch slider |
| Tap tempo | `TAP` button |

## Reference

- Manual: `~/Downloads/current_music_docs/KAOSS_DJ_MIXER_OM_EFG1.pdf`
