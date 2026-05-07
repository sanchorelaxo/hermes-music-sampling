---
name: "wavedrum-mini"
description: "Korg WAVEDRUM Mini — dynamic percussion synthesizer with onboard sounds, effects, rhythm patterns, and looper"
category: instruments
---

# WAVEDRUM Mini Skill

Korg WAVEDRUM Mini is a dynamic percussion synthesizer with a clip-triggered pickup, onboard sounds, effects, rhythm patterns, and phrase overdubbing.

## Device Overview

| Spec | Detail |
|------|--------|
| Trigger | Built-in contact microphone (clip sensor) |
| Sounds | 100+ built-in sounds (acoustic/electronic drums, percussion) |
| Effects | 25 effect types (reverb, delay, chorus, flanger, etc.) |
| Rhythm Patterns | 100+ built-in patterns |
| Looper | Phrase overdubbing |
| Audio | 3.5mm stereo in/out |
| Power | AC adapter or batteries |

## Sound Categories

| Category | Description |
|----------|-------------|
| **Acoustic** | Realistic acoustic drum/percussion sounds |
| **Electronic** | Synthesized drum sounds |
| **Percussion** | World percussion, shakers, etc. |
| **Extra** | Unique/experimental sounds |

## Effects

Hold `EFX` to enter effect select. Use data dial to choose.

The WAVEDRUM Mini has 10 effect types (0-9). Each effect has a type parameter (for reverb type selection) and three adjustable parameters.

| Type | Name | P1-Name | P1-Range | P2-Name | P2-Range | P3-Name | P3-Range |
|------|------|---------|----------|---------|----------|---------|----------|
| 0 | Reverb | Type (0-10): 0=Off, 1=Slap, 2=Spring1, 3=Spring2, 4=Plate, 5=Garage, 6=Chamber, 7=Canyon, 8=Room, 9=Studio, 10=Hall | 0-10 | Mix (Dry/Wet balance) | 0-99 | Depth (Reverb duration) | 0-99 |
| 1 | Multi Tap Delay | Mode: 0=Conventional echo, 1=ta ta ta (rest), 2=ta (rest) ta ta, 3=ta ta (rest) ta, 4=ta ta ta ta | 0-4 | Time (Delay time) | 0-99 | Feedback (Feedback amount) | 0-99 |
| 2 | Delay + Reverb | Time (Delay time) | 0-99 | Feedback (Delay feedback) | 0-99 | Mix (Reverb mix amount) | 0-99 |
| 3 | Reverb + Phaser | Mix (Reverb amount) | 0-99 | Depth (Phaser depth) | 0-99 | Speed (Phaser speed) | 0-99 |
| 4 | Reverb + Flanger | Mix (Reverb amount) | 0-99 | Depth (Flanger depth) | 0-99 | Speed (Flanger speed) | 0-99 |
| 5 | Pitch Shifter | Pitch (Semitone steps) | 0-48 | Tracking (Tracking characteristics) | 0-99 | Delay Time | 0-99 |
| 6 | Random Step Filter | Speed | 0-99 | Depth (Modulation depth) | 0-99 | Resonance | 0-99 |
| 7 | Sweep Modulation Delay + Flanger | Time (Sweep time) | 0-99 | Type: 0=Sweep down, 1=Sweep up | 0-1 | Mix (Flanger mix) | 0-99 |
| 8 | Tube OD + Flanger | Drive (Distortion/boost) | 0-99 | Speed (Flanger speed) | 0-99 | Mix (Flanger mix) | 0-99 |
| 9 | Random Step Filter + Delay | Speed (Random step filter speed) | 0-99 | Depth (Modulation depth) | 0-99 | Time (Delay time) | 0-99 |

## Rhythm Patterns

- 100+ preset patterns across genres
- Auto BPM detect or manual tap
- Play along with patterns as backing tracks
- Pattern categories: Rock, Jazz, Latin, Electro, etc.

## Overdubbing (Looper)

1. Select a sound
2. Press `REC` to start recording
3. Play phrases
4. Press `REC` again to stop
5. Subsequent REC presses = overdub

## Quick Reference

| Action | Control |
|--------|---------|
| Select sound | DATA DIAL (while playing or stopped) |
| Effect on/off | EFX button |
| Select effect | Hold EFX + DATA DIAL |
| Pattern on/off | PATTERN button |
| Select pattern | Hold PATTERN + DATA DIAL |
| Record/overdub | REC button |
| Tap tempo | TAP button |
| Output to headphones | 3.5mm headphone out |

## Linux Integration

```bash
# WAVEDRUM Mini = audio in/out only (no MIDI on this model)
# Connect to sound card line in

# Route audio
jack_connect system:capture_1 wavedrum:input_1
jack_connect wavedrum:output_1 system:playback_1
```

## Reference

- Manual: `~/Downloads/current_music_docs/WAVEDRUM_Mini_OM_EFGJ2.pdf`
