---
name: "minikp-v2"
description: "Korg mini kaoss pad 2s dynamic effect processor — X-Y touchpad, fnc button, Direct/Send routing, audio player, auto power-off, 100+ programs"
category: instruments
---

# miniKP V2 (mini kaoss pad 2s) Skill

Korg mini kaoss pad 2s dynamic effect processor, second generation (2011).

## Hardware

| Spec | Value |
||~~~~~~||~~~~~~-|
| Year | 2011 |
| Model | mini kaoss pad 2s |
| Dimensions | Compact, smaller than V1 |
| Weight | ~100 g |
| Power | 2x AA batteries (extended life with power conservation feature) |
| Auto power-off | After 30 minutes of no input (battery or DC) |
| Connectors | MIC IN (stereo mini), LINE IN, LINE OUT, PHONES, DC4.5V |
| Touchpad | X-Y slider-style pad |
| Display | Screen showing program, parameters |

## Programs

- **100+ programs** categorized by effect type:
  - **FLT** (Filter): Low Pass, High Pass, Band+, 72dB LPF, Morphing, Vowel, Mid Cut, Isolator, Dist Isolator, Center Cancel, Radio, Telephone, Reverb Filter, LPF Delay, HPF Delay
  - **MOD** (Modulation): Vinyl Break, Break Reverb, Jet, Manual Phaser, Talk Filter, Digi Talk, Ducking Comp, LowBoost Comp, Hard Limiter, Decimator, Fuzz Distortion, Bass Distortion, Ring Mod HPF, Pitch Shift HPF, Mid Pitch Shift
  - **LFO**: LFO LPF, LFO HPF, Infinite Filter, Jag Filter, Yoi Yoi, Flanger, Flanger Filter, Infinite Flanger, Phaser, Mid Phaser, Step Phaser, Auto Pan, Mid Auto Pan, Slicer, Mid Slicer, LPF Slicer, HPF Slicer, Grain Shifter, Mix Grain, Beat Grain
  - **DELAY**: Standard delay variants
  - **REVERB**: Reverb variants
  - Additional categories via fnc button navigation

## Controls

| Element | Function |
||~~~~~~~~~||~~~~~~~~~-|
| Touchpad | X-Y effect control |
| fx button | Access FX PARAMETER screen, FX RELEASE, and layer parameters |
| fnc (function) button | CONNECTION screen, FX RELEASE, power settings, volume |
| VALUE slider | Program selection / parameter adjustment |
| DC4.5V jack | External power |

## fnc Button Features

1. **CONNECTION screen**: Direct vs Send routing
2. **FX RELEASE**: Adjust release time of effect tails after finger leaves pad
3. **Power settings**: Auto power-off toggle, power conservation mode
4. **Volume**: MIC input volume, LINE input volume (hold fx + use slider)

### Direct vs Send Routing

- **Direct**: Connect to instrument/CD player — audio input + effect mixed together at output (wet+dry)
- **Send**: Connect to mixer's effect send/return jacks — only effect sound sent to output (wet only)

## Audio Player Mode

- Play audio files (WAV, MP3) from microSD card
- Use as backing track player during live performance
- Control audio player volume: hold fnc + use VALUE slider

## Power Conservation

- Enable via CONNECTION screen → power conservation ON
- Extends battery life significantly
- Auto power-off after 30 minutes with no input

## Hold Function

- Effect continues after finger leaves pad (BPM-synchronized tails)
- FX RELEASE time adjustable via fnc button

## Linux USB MIDI

```bash
amidi -l | grep -i kaoss
amidi -p hw:X,Y,Z -d
```

- Class-compliant USB MIDI
- X-Y pad outputs MIDI data for each axis

## Source

`~/Downloads/current_music_docs/miniKP_V2_OM_EFG1.pdf`
