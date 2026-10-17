# Spotykach — MIDI Reference

Firmware v1.4.0 beta 2 (latest). Spotykach sends and receives MIDI over both USB and TRS (Type A).

## Sync

- Receives standard **MIDI Clock 24PPQN** and syncs to it (switch clock source with **tap + alt** until the clock LED is turquoise).
- Sends 24PPQN clock to MIDI Out continuously while the internal clock runs (or while external clock is received).
- **Start/Stop/Continue:** can start/stop decks (Start and Continue are treated identically — no timeline). Disabled by default; enable via `mid_ps_a` / `mid_ps_b` in config.txt.

## Channels

- Deck A = MIDI channel **1** (default), Deck B = channel **2** (default).
- Configurable via `mid_ch_a` / `mid_ch_b` in config.txt. Both decks may share a channel.

## Notes

MIDI notes act as trigger signals (gate-in LED blinks on receipt). Pitches are calculated relative to **middle C (C4 = note 60)**. Tune the loaded sample/recording to C (or use the pitch knob) for in-tune playback.

## CC Implementation Chart

| CC | Function | Remarks (equivalent control) |
|----|----------|------------------------------|
| — | MIDI Clock | 24PPQN (see external clock section) |
| — | Start | Enable via config.txt (`mid_ps_a`/`mid_ps_b`) |
| — | Stop | Enable via config.txt |
| — | Note On | Treated as trigger signal |
| 14 | Record from Input | Toggle (non-zero). Acts as alt + play |
| 15 | Record from other Deck | Toggle (non-zero). Acts as alt + reverse |
| 20 | Position | 0…127 |
| 21 | Position Offset | 0…127 |
| 22 | Size | 0…127 |
| 23 | Envelope | 0…127 |
| 24 | Pitch | 0…127 |
| 25 | Deck Mix | 0…127 |
| 26 | Overdub Feedback | 0…127. Equivalent to alt + mix |
| 27 | Drift Mode Envelope Size | 0…127. Equivalent to alt + env |
| 28 | Drift Mode Window Size | 0…127. Equivalent to alt + size |
| 85 | Play Forward | Toggle (non-zero). Acts as play |
| 86 | Play Reverse | Toggle (non-zero). Acts as reverse |
| 89 | Modulation Cycle | 0…127 |
| 90 | Modulation Glow | 0…127 |
| 102 | Grit On | Momentary (0 = off, 1…127 = on) |
| 103 | Grit Intensity | 0…127. Equivalent to grit + pitch |
| 104 | Grit Mix | 0…127. Equivalent to grit + mix |
| 105 | Flux On | Momentary (0 = off, 1…127 = on) |
| 106 | Flux Intensity | 0…127. Equivalent to flux + pitch |
| 107 | Flux Feedback | 0…127. Equivalent to flux + pos |
| 108 | Flux Mix | 0…127. Equivalent to flux + mix |

## Linux / USB MIDI

Class-compliant USB MIDI device.

```bash
# List MIDI ports
amidi -l

# Connect to a DAW / software
aconnect -l

# Play a C4 note on Deck A (channel 1)
sendmidi dev "Spotykach" note 60 127 1

# Toggle Play Forward on Deck A via CC 85
sendmidi dev "Spotykach" cc 85 127 1
```
