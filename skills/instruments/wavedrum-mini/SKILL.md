---
name: wavedrum-mini
description: Korg WAVEDRUM Mini — dynamic percussion synthesizer with onboard sounds, effects, rhythm patterns, and looper
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

| Effect | Description |
|--------|-------------|
| REVERB | Hall, room, plate reverb |
| DELAY | Tape, ping-pong delay |
| CHORUS | Stereo chorus |
| FLANGER | Modulated comb filter |
| PHASER | All-pass modulated filter |
| DIST | Clip, fuzz, overdrive |
| FILTER | LPF, HPF, BPF |

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
