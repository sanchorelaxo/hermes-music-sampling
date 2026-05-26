---
name: "kaossilator-v2"
description: "Use when working with the Korg kaossilator 2S dynamic phrase synthesizer — X-Y touchpad, 150 programs, 50 arp patterns, loop recording, audio player, master recorder, microSD storage, and USB MIDI on Linux."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "synthesizer", "kaossilator", "korg", "midi", "loop"]
    related_skills: []
---

# Korg kaossilator 2S — Dynamic Phrase Synthesizer

## Hardware

| Spec | Value |
|------|-------|
| Dimensions | 76 × 128 × 25 mm |
| Weight | 100 g (without batteries) |
| Power | 2× AA batteries or DC 4.5V |
| Storage | microSDHC (up to 16 GB) |
| USB | Type C (charging + data) |
| Touchpad | X-Y position sensing, slider-style |
| Display | OLED (program, tempo, loop data) |
| Connectors | MIC IN (stereo 1/8"), PHONES (stereo 1/8"), DC jack |

Internal speaker — auto power-off when headphones connected.

## When to Use

- Playing phrases on an X-Y touchpad with real-time parameter modulation
- Loop recording performances via MIC IN or internal mic
- Selecting from 150 programs across 7 categories (Lead, Acoustic, Bass, Chord, SFX, Drum, Pattern)
- Using the 50-pattern arpeggiator with swing
- Playing back audio files (WAV/MP3) from microSD
- Recording a full performance to microSD as WAV (Master Recorder)
- Using built-in scales (26 total: Ionian through exotic scales) with selectable root note

## Programs

150 programs across 7 categories:

| Category | Range | Key Use |
|----------|-------|---------|
| **LEAD** | LD.001–025 | Melodic phrases, synth leads |
| **ACOUSTIC** | AC.026–035 | Pianos, Rhodes, organ, guitar |
| **BASS** | BS.036–065 | Basslines with filter/distortion |
| **CHORD** | CH.066–090 | Poly chords, pads, vox |
| **SOUND EFFECT** | SE.091–110 | Percussion hits and hits |
| **DRUM** | DR.111–125 | Full drum kits (808, 909, etc.) |
| **PATTERN** | PT.126–150 | Pre-programmed drum patterns |

Full program table with X/Y axis assignments: [references/programs.md](mdc:references/programs.md)

Shared Korg program data (all products): [korg-programs.md](mdc:../../references/korg-programs.md) — load via `skill_view(name='hermes-music-sampling', file_path='references/korg-programs.md')`

## Controls

| Element | Function |
|---------|----------|
| VALUE slider | Select program / adjust parameters |
| snd button | Recall Program Select screen |
| arp button + indicator | Toggle arpeggiator / access arp parameters |
| REC button | Loop recording |
| PLAY button | Loop playback |
| new button | Create new loop / access functions |
| Lock button | Lock controls to prevent accidental touches |
| Volume buttons | Adjust master / audio player volume |

## Loop Recording

- REC button to start/stop — records via MIC IN or internal mic
- PLAY button to play recorded loop
- Variable loop length (not limited to 8 beats like V1)
- Edit: trim, adjust start point
- Import/export WAV (16-bit 44.1 kHz / 48 kHz stereo) from/to microSD

## Scales

26 scales: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian + exotic (Arabic, Spanish, Gypsy, Egyptian, Hawaiian, Balinese Pelog, Japanese Miyakobushi, Ryuku, Chinese) + interval scales (Whole Tone, 3rd, 4th, 5th, Octave) + special (Bass Line, Combination Diminished, Melodic minor, Major/minor Pentatonic, Raga variants).

Select root note C–B across octaves.

## Audio Routing

**MIC IN:** stereo mini input for external sources. Direct monitoring: input + effect mixed at output. CLIP indicator if input too hot.

## Linux USB MIDI

Class-compliant. `amidi -l | grep -i kaossilator` to detect.

```bash
amidi -p hw:X,Y,Z -d  # monitor MIDI
```