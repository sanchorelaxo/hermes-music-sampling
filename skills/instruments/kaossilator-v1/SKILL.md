---
name: kaossilator-v1
description: Korg KAOSSILATOR dynamic phrase synthesizer (2007 model) — X-Y touchpad, 100 programs, gate arpeggiator, phrase loop recording, USB MIDI on Linux
category: instruments
---

# KAOSSILATOR V1 Skill

Korg KAOSSILATOR dynamic phrase synthesizer, first generation (2007).

## Hardware

| Spec | Value |
|------|-------|
| Year | 2007 |
| Dimensions | 106 x 129 x 29 mm |
| Weight | 163 g (without batteries) |
| Power | 4x AA alkaline batteries (6V) or optional AC adapter (DC4.5V) |
| Battery life | ~5 hours |
| Connectors | LINE OUT (RCA L/R), PHONES (stereo mini), DC jack |
| USB | Type B (MIDI class-compliant) |
| Touchpad | X-Y position sensing |

## Programs

- **100 programs** (00-99), selected via PROGRAM/VALUE knob
- Programs organized in categories (0x-9x ranges)
- X axis and Y axis control different effect parameters per program
- Touch outer edges of pad for parameter extremes

## Controls

| Element | Function |
|---------|----------|
| PROGRAM/VALUE knob | Select program / adjust parameters |
| TAP/BPM button | Set BPM manually or via tap tempo |
| LOOP REC/PLAY button | Record and loop phrases (hold to rec, release to stop) |
| SCALE button | Select musical scale |
| GATE ARP button | Toggle gate arpeggiator on/off |
| VOLUME knob | Headphone volume only (does not affect LINE OUT) |
| ON/STANDBY switch | Power on/off |

## Gate Arpeggiator

- **50 patterns** (G.00 - G.49)
- Press and hold GATE ARP button, turn PROGRAM/VALUE to select pattern
- Press GATE ARP button again to return to program selection
- Cannot be applied to certain programs (see program list)
- Power-off reverts to default [G.00]

## Scales

- Selectable musical scale (abbreviation shown in display)
- Default: Ionian (major)
- Turn PROGRAM/VALUE while in scale mode
- SCALE button again to confirm
- Auto-returns to program selection after 5 seconds
- Scale cannot be applied to certain programs

## Key (Root Note / Octave)

1. Hold SCALE button + press TAP button — display shows current key
2. Turn PROGRAM/VALUE to select key
3. Press TAP button again to confirm (with SCALE held)

## Phrase Loop Recording

- Records up to **8 beats** (2 bars of 4/4) of live play on the touchpad
- Hold LOOP REC/PLAY to record; release to stop and begin loop playback
- LOOP STATUS indicator: red = recording, green = playback
- Press LOOP REC/PLAY again to stop playback
- Press LOOP REC/PLAY while stopped to start playback

### Overdubbing Layers

- Hold LOOP REC/PLAY during playback to add overdub layers
- Can save layered phrase and return to last saved version if new layers are unwanted
- Hold LOOP REC/PLAY + turn PROGRAM/VALUE: delete most recent phrase
- Hold LOOP REC/PLAY + press SCALE: delete all recorded phrases

## BPM Setting

1. Press TAP button to display current BPM
2. Manual: turn PROGRAM/VALUE
3. Tap tempo: tap TAP button repeatedly in tempo
4. Hold TAP button to confirm and exit BPM setting
5. Default: 120 BPM

## Linux USB MIDI

```bash
# Detect device
amidi -l | grep -i kaossilator

# Monitor MIDI messages
amidi -p hw:X,Y,Z -d
```

- Class-compliant USB MIDI — no driver needed
- X-Y pad outputs MIDI note and CC data
- Program changes via MIDI also supported

## Source

`~/Downloads/current_music_docs/KAOSSILATOR1_OM_EFG1.pdf`
