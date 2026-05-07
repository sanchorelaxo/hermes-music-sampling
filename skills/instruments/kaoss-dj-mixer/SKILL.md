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

## Effect Program Table

### FILTER (1–13)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 1 | Low Pass Filter | Cutoff | Resonance |
| 2 | High Pass Filter | Cutoff | Resonance |
| 3 | Band Pass Filter | Cutoff | Resonance |
| 4 | 72dB/oct LPF | Cutoff | Resonance |
| 5 | Morphing Filter | Cutoff | Resonance |
| 6 | Vowel Filter | 1st & 2nd Formant | 1st & 2nd Formant |
| 7 | Mid Cut Filter | Cutoff | Resonance |
| 8 | Isolator | Low – MidLo – MidHi – Hi | Level |
| 9 | Dist Isolator | Low – MidLo – MidHi – Hi | Distortion |
| 10 | Center Cancel | Cutoff | Resonance |
| 11 | Radio | Tone | Level |
| 12 | Telephone | Tone | Stereo – Mono |
| 13 | Reverb Filter | Cutoff | Resonance |

### MODULATION (14–25)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 14 | Vinyl Break | Stop Speed | Scratch |
| 15 | Break Reverb | Stop Speed | Scratch |
| 16 | Jet | Tone (Delay Time) | Feedback |
| 17 | Manual Phaser | Cutoff | Resonance |
| 18 | Talk Filter | 1st Formant | 2nd Formant, Feedback |
| 19 | Digi Talk | 1st Formant | 2nd Formant |
| 20 | Decimator | Cutoff | Sampling Rate & Bit Depth |
| 21 | Fuzz Distortion | Tone | Distortion |
| 22 | Bass Distortion | Distortion | Low Boost |
| 23 | Ring Mod HPF | Ring Mod Frequency | Cutoff |
| 24 | Pitch Shift HPF | Pitch | Cutoff |
| 25 | Mid Pitch Shift | Pitch | Pitch Shift Depth |

### LFO (29–45)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 29 | LFO LPF | LFO Speed | Resonance |
| 30 | LFO HPF | LFO Speed | Resonance |
| 31 | Infinite Filter | LFO Speed | LFO Depth |
| 32 | Jag Filter | LFO Speed | LFO Shape |
| 33 | Yoi Yoi | LFO Speed | Yoi Level |
| 34 | Flanger | LFO Speed | Feedback |
| 35 | Flanger Filter | LFO Speed | Cutoff |
| 36 | Infinite Flanger | LFO Speed | Feedback |
| 37 | Phaser | LFO Speed | Resonance |
| 38 | Mid Phaser | LFO Speed | Resonance |
| 39 | Step Phaser | Cutoff | Resonance |
| 40 | Auto Pan | LFO Speed | Auto Pan Depth |
| 41 | Mid Auto Pan | LFO Speed | Auto Pan Depth |
| 42 | Slicer | LFO Speed | Slicer Depth |
| 43 | Mid Slicer | LFO Speed | Slicer Depth |
| 44 | LPF Slicer | LFO Speed | Cutoff |
| 45 | HPF Slicer | LFO Speed | Cutoff |

### DELAY (46–53)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 46 | Delay | Delay Time | Feedback Level |
| 47 | One Delay | Delay Time | Delay Tone |
| 48 | Ping Pong Delay | Delay Time | Feedback Level |
| 49 | Multi Tap Delay | Delay Tone | Feedback Level |
| 50 | Modulation Delay | Delay Time | Feedback Level |
| 51 | Tape Echo | Delay Time | Feedback Level |
| 52 | Dub Echo | Delay Time | Feedback Level |
| 53 | Feedback Echo | Delay Time | Feedback Level |

### REVERB (54–62)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 54 | LPF Delay | Delay Time | Cutoff |
| 55 | HPF Delay | Delay Time | Cutoff |
| 56 | Phaser Delay | Delay Time | Resonance & Feedback |
| 57 | Flanger Delay | Delay Time | Resonance & Feedback |
| 58 | Hall Reverb | Reverb Time | Reverb Depth |
| 59 | Room Reverb | Reverb Time | Reverb Depth |
| 60 | Spring Reverb | Reverb Time | Reverb Depth |
| 61 | Pump Reverb | Reverb Tone | Pump Depth |
| 62 | Freeze Reverb | Reverb Tone | Mix Balance |

### GRAIN (63–65)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 63 | Grain Shifter | Buffer Update Interval | Duration |
| 64 | Mid Grain | Buffer Update Interval | Duration |
| 65 | Mix Grain | Duration | Mix Balance |

### LOOPER (66–86)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 66 | KP2 Looper | Loop Length | Cutoff |
| 67 | LPF Looper | Loop Length | Cutoff |
| 68 | HPF Looper | Loop Length | Cutoff |
| 69 | High Looper | Loop Length | Lo Range Balance |
| 70 | Iso Looper | Loop Length | Low – MidLo – MidHi – Hi |
| 71 | Freeze Looper | Loop Length | Cutoff |
| 72 | Phaser Looper | Loop Length | Cutoff |
| 73 | Flanger Looper | Loop Length | Flanger Tone (Delay Time) |
| 74 | Deci Looper | Loop Length | Sampling Rate & Cutoff |
| 75 | Slice Looper | Loop Length | Slice Position |
| 76 | F/R Looper | Loop Length | Reverse – Forward |
| 77 | OverDub Looper | Loop Length | Loop – Overdub |
| 78 | Break Looper | Loop Length | Stop Speed |
| 79 | KP3 RwLooper | Loop Length | Pitch |
| 80 | RwDelay Looper | Loop Length | Cutoff |
| 81 | OverDub Looper | Loop Length | Loop – Overdub |
| 82 | Break Looper | Loop Length | Stop Speed |
| 83 | KP3 RwLooper | Loop Length | Pitch |
| 84 | Pitch Looper | Loop Length | Pitch |
| 85 | Weird Looper | Loop Length | Pitch |
| 86 | Looper & Noise | Loop Length | Noise Level |

### LEAD (87–95)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 87 | Unison Saw | Note | Reverb Depth |
| 88 | KP3 Unison Saw | Note | Cutoff, Resonance |
| 89 | Unison Lead | Note | Cutoff |
| 90 | Pulse Verb | Note | Cutoff |
| 91 | Paz Square | Note | Pitch EG Time |
| 92 | 8bit Square | Note | Octave |
| 93 | Ring Flutter | Note | Mod Detune Width |
| 94 | Say Yay Synth | Note | Formant & Vibrato Depth |
| 95 | Air Spectrum | Note | Decay & Release Time |

### ACOUSTIC (96–97)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 96 | Ray EP | Note | Velocity |
| 97 | Didgeridoo | Note | LFO Speed |

### BASS (98–a4)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| 98 | Slap Bass | Note | Decay Time (Mute) |
| 99 | Unison Squ Bass | Note | Cutoff, Resonance |
| a0 | Hoover Bass | Note | Octave |
| a1 | Bad Bass | Note | LFO Depth |
| a2 | Wobble Bass | Note, LFO Speed | Cutoff |
| a3 | Fall Bass | Note | Cutoff, Drive |
| a4 | Pulse Code | Note | Cutoff, Resonance |

### CHORD (a5–a8)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| a5 | Pump Chord | Note | Chord (Min – Maj) |
| a6 | Scale Chord | Note | Reverb Depth |
| a7 | Sine Chord | Note | Octave |
| a8 | Pad Chord | Note | Filter Attack Time & EG Int. |

### SOUND EFFECT (a9–c0)

| No. | Program | X-Axis | Y-Axis |
|-----|---------|--------|--------|
| a9 | Noise Filter | Cutoff | Resonance |
| b0 | Pump Noise | Cutoff | Pump Depth |
| b1 | Bubble SFX | LFO Speed | LFO Depth |
| b2 | Resonator | Cutoff | LFO Depth & Speed |
| b3 | Itch Noiz | Note | LFO Speed & Pitch Mod Int. |
| b4 | Ring Mod SFX | Pitch | Mod LFO Intensity |
| b5 | Beam Saber | Mod Pitch | Mod Depth |
| b6 | Kaoss Drone | Cutoff | Feedback |
| b7 | Sync Random | Note | Random Pitch Width |
| b8 | Disco Siren | LFO Speed | Sound Character |
| b9 | Rise/Fall | Pitch | Rise – Fall |
| c0 | Sweep | Pitch, Pan | LFO Speed |

## Reference

- Manual: `~/Downloads/current_music_docs/KAOSS_DJ_MIXER_OM_EFG1.pdf`
