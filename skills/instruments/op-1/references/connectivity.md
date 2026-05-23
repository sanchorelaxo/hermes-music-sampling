# OP-1 — Connectivity & Advanced Reference

## COM Mode (SHIFT + COM)

**Computer mode** — OP-1 acts as a USB audio interface:
- 2-in/2-out audio over USB (OP-1 audio engine + DAW)
- Simultaneous stereo recording and playback
- 44.1kHz, 16/24-bit

### OP-1 Mode (SHIFT + COM → T2)
OP-1 treats the DAW as a tape machine — sends and receives multi-track audio over USB, synchronized to OP-1's sequencer.

### MIDI Controller Mode (SHIFT + COM → T3)
OP-1's keys, encoders, and sensors send standard MIDI CC messages to control external software/hardware.

### Disk Mode (SHIFT + COM → T4)
Access internal 4GB drive as a USB mass storage device. Tape recordings appear as WAV files.

## Album Mode (SHIFT + COM → T1)
- Arrange full performances (tape + sequences) into a song
- Each "slot" holds one complete OP-1 session
- **T1**: Enter album mode | **T3**: Play/pause
- Export entire session as a single file

## TE-Boot Mode (Press and hold HELP + CONNECT simultaneously)

For firmware updates and factory reset.

| Function | Access |
|----------|--------|
| Firmware update | Press UPDATE (displayed in TE-Boot) |
| Factory reset | Press FACTORY RESET |
| Format internal drive | Press FORMAT |
| Function test | Press TEST |

## Tempo Mode

Press **SHIFT + T4** → select tempo view.

| Mode | Description | Green Encoder |
|------|-------------|---------------|
| **Free** | Tempo and tape speed independent; no sync transmitted or received | Counterclockwise |
| **Beat Match** | OP-1 is master clock; sends MIDI sync over USB; tempo and tape speed linked (green link symbol) | Center-right |
| **Sync** | OP-1 listens to external MIDI clock over USB (EXT displayed if no external tempo detected); tempo not linked to tape speed (orange link symbol) | Clockwise |

### Setting Tempo
- **Blue encoder**: set tempo
- **SHIFT + Blue encoder**: fine-tune tempo
- **Tap tempo**: Hit the tempo key multiple times

### Metronome
- **Orange encoder**: set pitch/volume of metronome
- **Play**: start metronome
- **Orange encoder to minimum**: turn off

### PO Sync
OP-1 outputs dual mono over 3.5mm: L = click track for Pocket Operator, R = mix of audio. Set PO unit to SY4. Connect 3.5mm stereo cable.

**1/16 Sync** (variation): Sends double-tempo click track for Eurorack. Hold **SHIFT + Green encoder** while in PO sync to toggle.

### External Sync Control
- **Arrow keys < and >**: nudge beat by ±1 MIDI clock per press (even while synced to external tempo)

## Recording External Sources

### Mic/Input Key (SHIFT + T3)
- **Synth/Drum mode**: Routes external audio through the selected engine's effect chain
- **Tape/Mixer mode**: Arms recording directly to tape track

### Sampling Methods
1. **Built-in microphone**: Direct sampling (mic in 3.5mm)
2. **Line input**: Connect external instrument
3. **USB audio recording**: Route DAW audio to OP-1 and record to tape
4. **FM radio sampling**: Use built-in radio to sample broadcast audio
5. **Skip-back sampling**: Records ~4 seconds before you press record

## Key Shortcuts

| Shortcut | Action |
|----------|--------|
| **SHIFT + HELP** | Key name and function of any key |
| **Hold HELP + play keys** | Note information |
| **SHIFT + HELP** (from any mode) | TOOLS (time/date) |
| **SHIFT + T1–T4** | Enter secondary mode for that key |
| **SHIFT + Arrow keys** (in tape) | Move between bar markers |
| **SHIFT + T3 + Tape** | Arm tape recording |

## Linux / USB MIDI

OP-1 is class-compliant on Linux — no driver needed. Enumerates as both MIDI device and USB audio interface.

```bash
# List OP-1 MIDI ports
amidi -l
# Port    Client name              Port name
# 128:0   Teenage Engineering     OP-1 MIDI

# Send MIDI to OP-1
sendjack or aconnect from your DAW to OP-1 MIDI port

# USB Audio
# OP-1 appears as a USB audio device (hw:OP1 or similar)
# Use with jackd, pulseaudio, or ALSA utilities
```

> **Tip**: OP-1's USB audio is 2-in/2-out. When connected, it can simultaneously record its own audio output and receive DAW audio input for reamping or DAW-based processing.