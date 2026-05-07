---
name: "kaossilator-v2"
description: "Korg kaossilator 2S dynamic phrase synthesizer — X-Y touchpad, internal speaker, audio player, master recorder, 50 arp patterns, microSD, USB MIDI on Linux"
category: instruments
---

# KAOSSILATOR V2 (kaossilator 2S) Skill

Korg kaossilator 2S dynamic phrase synthesizer, second generation (2011).

## Hardware

| Spec | Value |
|------|-------|
| Year | 2011 |
| Model name | kaossilator 2S |
| Dimensions | 76 x 128 x 25 mm |
| Weight | 100 g (without batteries) |
| Power | 2x AA batteries (alkaline or nickel-metal hydride) |
| Battery life | Extended with optional power conservation feature |
| Connectors | MIC IN (stereo 1/8" mini), PHONES (stereo 1/8" mini), DC4.5V jack |
| Internal speaker | Built-in (auto power-off when headphones connected) |
| Storage | microSDHC slot (up to 16 GB); 512 MB - 2 GB microSD also supported |
| USB | Type C (charging + data) |
| Touchpad | X-Y position sensing, slider-style (not original circular pad) |
| Display | OLED (shows program, tempo, loop data) |

## Programs

- **100 programs** (00-99) with categorized structure
- Selected via **VALUE slider** (front-facing, not top knob)
- X/Y axis control effect parameters per program
- OLED shows program number + name simultaneously

## Controls

| Element | Function |
|---------|----------|
| VALUE slider | Select program / adjust parameters |
| snd button | Recall Program Select screen |
| arp button + indicator | Toggle arpeggiator / access arp parameters |
| ● (REC) button | Loop recording |
| ► (PLAY) button | Loop playback |
| new button | Create new loop / access functions |
| Lock button | Lock controls to prevent accidental touches |
| Volume buttons | Adjust master / audio player volume |
| BPM indicator | OLED BPM display (flashes to tempo) |
| Power button | ON/OFF |

## Arpeggiator

- **50 patterns** (up from 50 in V1 — same count but different patterns)
- Per-pattern parameters: ARP TIME, ARP SWING
- Access via arp button — indicator lights when active
- Can be applied to most programs (see program list)
- ARP parameters accessible on OLED display

## Loop Recording

- Record sounds via MIC IN or internal microphone
- REC button to start/stop recording
- PLAY button to play recorded loop
- Edit recorded loops: trim, adjust start point
- Loop length: variable (not limited to 8 beats like V1)
- Loop data shown on OLED during playback
- Import WAV files (16-bit 44.1 kHz / 48 kHz stereo) from microSD
- Export loops to microSD as WAV

## Audio Player Mode

- Play back audio files (WAV, MP3) copied from computer
- Files stored on microSD card
- Control playback via unit
- Volume adjustable via volume buttons

## Master Recorder

- Record entire performance to microSD as WAV
- 16-bit 44.1 kHz / 48 kHz stereo output
- Bounce everything playing on the unit

## Scales and Keys

- Full set of scales including: Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
- Exotic scales: Arabic, Spanish, Gypsy, Egyptian, Hawaiian, Balinese Pelog, Japanese Miyakobushi, Ryuku, Chinese
- Interval scales: Whole Tone, minor 3rd, Major 3rd, 4th, 5th, Octave
- Special scales: Bass Line, Combination Diminished, Melodic minor, Major/minor Pentatonic, Raga variants
- 26 scales total

## Key (Root Note)

- Select root note C through B across octaves
- Works with any selected scale

## Audio Routing

- **MIC IN**: stereo mini input for external sources
- **Direct monitoring**: input + effect mixed at output
- Input level shown on display; CLIP indicator if too hot
- Attenuator built into input section

## Linux USB MIDI

```bash
# Detect device
amidi -l | grep -i kaossilator

# Monitor MIDI
amidi -p hw:X,Y,Z -d
```

- Class-compliant USB MIDI
- Compatible with mainstream DJ/production software

## Source

`~/Downloads/current_music_docs/KAOSSILATOR_V2_OM_EFGSCJ2.pdf`
