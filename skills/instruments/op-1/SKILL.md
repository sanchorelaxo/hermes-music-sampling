---
name: op-1
description: Teenage Engineering OP-1 — portable synthesizer with 13 synth engines, 4 sequencers, tape recorder, mixer, and built-in wireless radio. Key capabilities: 4-track tape, 6 sequencer types, multi-engine synthesis, MIDI controller mode, PO sync, wireless audio.
category: instruments
---

# OP-1 — Teenage Engineering Portable Synthesizer

## Hardware

| Spec | Value |
|------|-------|
| Keys | 25-key musical keyboard (C1–C3, octave shiftable) |
| Display | OLED, 64×128 px |
| Audio | 24-bit, USB audio class compliant |
| Connectivity | USB (charging, audio, MIDI), 3.5mm audio I/O, wireless |
| Battery | Internal Li-ion (~8–9 hours heavy use, ~2 years standby) |
| Storage | Internal 4GB drive |
| Weight | ~350g |
| Dimensions | 282×106×17mm |

**Power**: 5V USB charging. Charge time 2.5–6 hours (1800mA battery).

**I/O Panel**: Headphone jack (3.5mm stereo), line out (3.5mm), mic in (3.5mm), DC in (5V USB).

**⚠️ Critical**: Never plug 3.5mm mic input or line output into a sound card with phantom power — this destroys the OP-1 ports.

---

## The Four Main Modes

Press one of the four main mode keys (Synth, Drum, Tape, Mixer) to enter that mode. Press **SHIFT + any main mode key** to enter the secondary function of that mode (indicated by the letter below each key).

| Key | Primary Mode | Secondary (SHIFT+) |
|-----|--------------|-------------------|
| T1 | Synthesizer | Synth engine selector |
| T2 | Drum | Drum engine selector |
| T3 | Tape | Tape transport/settings |
| T4 | Mixer | Mixer views (sound path, main, EQ, master effect, master out) |

---

## Synthesizer Mode (T1)

### 13 Synth Engines

Access: **SHIFT + T1** → blue encoder scrolls engines → any key confirms.

| Engine | Type | Key Parameters |
|--------|------|---------------|
| **Cluster** | Multi-layered oscillator cluster | Number of waves (0–6), wave envelope, spread |
| **Digital** | True digital synthesis, ring mod | Wave shaper, octave, detune, digitalness |
| **String** | Waveguide string model | Tension, impulse decay, detune, impulse type |
| **Pulse** | Dual pulsetrain oscillator + FM | Filter, amplitude, second pulse mod |
| **FM** | 4-operator FM synthesis | FM amount, freq, topology, detune |
| **Phase** | Phase distortion | Phase shift, distortion amount, phase filter, tilt, drive wave |
| **Synth Sampler** | Teenage sample player | Start, loop in/out, end, reverse, fine tune, gain |
| **D-Box** | Drum synthesizer | Pitch, waveform, envelope, cross mod |
| **D-Synth** | Multi-envelope dual oscillator | Voltage, waveform, envelope, cross mod |
| **Drum Sampler** | Teenage percussion player | Note/pitch, in/out, loop off/once/reverse, gain |
| **6 Operator** | Multi oscillator electric synthesis | Ampere modulation, induction w/shaper, phase filter, voltage detune |
| **DNA** | CPU ID Noise synthesis | Filter, wave number, wave modifier, noise |
| **CWO** | Pitch shifting delay | Frequency, delay, feedback, sideband |

### Synth Controls (per voice)

| Parameter | Control | Secondary (SHIFT+) |
|-----------|---------|-------------------|
| Envelope | Orange encoder | Attack, decay, sustain, release via envelope screen |
| Playmode | Green encoder | LFO sync, retrig types |
| Effect | White encoder | 8 built-in effects (delay, grid, nitro, spring, telematic, punch, power, cwo) |
| LFO | Blue encoder (after pressing LFO key) | 8 LFO types: Element, Random, Tremolo, Value, MIDI, Crank, Bend, Free |

### Saving a Sound
1. Hold **SHIFT + T1** (synth engine screen) — long press saves
2. **Blue encoder** → select slot (1–8 per category)
3. Release all keys — sound is saved

---

## Drum Mode (T2)

### 2 Drum Engines

Access: **SHIFT + T2** → blue encoder selects engine.

| Engine | Type |
|--------|------|
| **Drum Sampler** | Teenage percussion sample player — per-pad note/pitch, loop off/once/reverse, gain |
| **D-Box** | Teenage drum synthesizer — pitch, waveform, envelope, filter cutoff freq |

### Drum Sampler Controls
- **Blue encoder**: select pad 1–8
- **Green encoder**: pitch
- **White encoder**: attack/in
- **Orange encoder**: decay/out
- **Loop**: pad 5 toggles loop off/once/on
- **Reverse**: pad 6 toggles reverse
- **Dynamic envelope**: SHIFT + T2 → green encoder adjusts

### Laying Out a Kit
Each pad (1–8) can have its own sample assigned. OP-1's standard layout assigns melodic percussion across the keyboard. Import your own samples via USB audio recording directly to a pad.

---

## 6 Sequencer Types

All sequencers store **note data** (unlike the tape which records raw audio). Synth and Drum modes each have their own sequencer memory and can use different sequencer types independently.

Access: Press **SHIFT + any main mode** to see sequencer options.

### 1. Endless Sequencer (128 notes max)

| Action | Control |
|--------|---------|
| Store notes | **SHIFT + any musical keyboard key** |
| Auto-advance | Releases key → automatically moves one step forward |
| Insert long note | Hold key + press Forward Arrow (`>`) |
| Insert space | **SHIFT + Forward Arrow** |
| Delete last note | **SHIFT + Rewind Arrow** (`<`) |
| Play original pitch | Press **C key** on musical keyboard |
| Hold playback | Orange encoder → until **HOLD** lights up |
| Change direction | **SHIFT + Orange encoder** (Forward / Reverse / Random) |
| Set time signature | Blue encoder |
| Add swing | Green encoder (50% = no swing) |
| Apply pattern | White encoder |
| Rotate pattern | **SHIFT + White encoder** |
| Activate Crank mode | **SHIFT + Blue encoder** |

### 2. Pattern Sequencer (16-step grid)

Ideal for drum patterns.

| Action | Control |
|--------|---------|
| Insert notes | **SHIFT + any musical keyboard key** |
| Erase notes | **SHIFT + Blue encoder** |
| Move cursor | Arrow keys or Blue encoder |
| Add swing | Green encoder |
| Rotate notes | **SHIFT + Green encoder** |
| Live mode | Orange encoder → **HOLD** lights up |
| Live insert | **SHIFT + any key** while sequencer runs |
| Live edit mode | **SHIFT + Arrow key** while running |
| Set sequence length | White encoder |
| Set playback direction | **SHIFT + Orange encoder** (Forward / Reverse / Cycle) |

### 3. Tombola Sequencer (Physics-based random)

Notes **bounce** — harder bounces play louder.

| Action | Control |
|--------|---------|
| Drop notes | Play any key on musical keyboard |
| Adjust bounciness | Orange encoder (affects volume via mass) |
| Adjust heaviness | Green encoder (sets gravity) |
| Release notes | White encoder (opens Tombola) |
| Set speed/direction | Blue encoder |
| Crank mode | **SHIFT + Blue encoder** (manual spin) |

> **Pro tip**: Keep Tombola open with high rotation speed → creates random echo effect.

### 4. Finger Sequencer (Two-sequence combinator)

Each white key represents a pattern. Two gorillas appear in drum mode.

| Action | Control |
|--------|---------|
| Insert notes | **SHIFT + any musical keyboard key** |
| Move cursor + erase | **SHIFT + Blue encoder** |
| Set sequence length | White encoder |
| Add swing | Green encoder |
| Hold playback | Orange encoder |
| Layer second pattern | Push second key (**Join**) |
| Play on release | Push second key (**Replace**) |
| Play fill-ins | Push second key (**Fill in**) |

### 5. Sketch Sequencer (Free-form shape drawing)

| Action | Control |
|--------|---------|
| Draw shapes | Blue + Green encoders (shape controls pitch) |
| Move cursor | White + Orange encoders |
| Move cursor vertically | Musical keyboard |
| Select speed divider | **SHIFT + Green encoder** (/4 to x16) |
| Enable grid | **SHIFT + White encoder** |
| Start sequencer | **SHIFT + Orange encoder** (clockwise) |

### 6. Arpeggio Sequencer

| Action | Control |
|--------|---------|
| Trigger mode | Blue encoder |
| Trigger pattern | Green encoder |
| Note length | White encoder |
| Type | Orange encoder |
| Pause / skip | Arrow keys |
| Swing level | Blue encoder (while playing) |

---

## Tape Mode (T3)

OP-1 has a **6-track tape recorder** (4 audio tracks + 2 shared tracks). It records real audio, not just note data.

### Recording

| Action | Control |
|--------|---------|
| Arm recording | **SHIFT + T3** → select track with blue encoder |
| Record | Press **T3** again → play on tape |
| Overdub | Record over existing audio |
| Rewind / Fast Forward | Arrow keys (hold for continuous) |
| Jump to start/end | **SHIFT + Arrow keys** |
| Reverse playback | **SHIFT + T3** → white encoder |
| Change tape speed | White encoder (adjusts pitch + time) |

### Recording Level
Green encoder adjusts input gain. Watch the VU meter — avoid clipping.

### Advanced Recording
- **Lift**: Extracts the recorded audio from the tape (leaves a silent version)
- **Bounce**: Mixes tracks down to a single track
- **Bars/Bar Markers**: SHIFT + arrow keys to set and move between bar markers (useful for looping and live variations)

### Tape Tricks
- Reverse playback
- Pitch/tempo independent (tape speed adjustable separately)
- Multi-track overdubbing
- Loop recording with bar markers in beat match mode

### Backing Up Tape
In **Disk mode** (SHIFT + COM), tape files can be accessed as WAV files over USB.

---

## Mixer (T4)

The mixer is the **final stage** of the OP-1 sound path. Press **T4** repeatedly to cycle through screens.

### T1: Mixer Main
Transforms four tape tracks into one stereo signal.

| Encoder | Parameter | Range |
|---------|-----------|-------|
| Blue | Track 1 level | 0–99 |
| Green | Track 2 level | 0–99 |
| White | Track 3 level | 0–99 |
| Orange | Track 4 level | 0–99 |
| SHIFT + Blue/Green | Adjust LEFT + RIGHT simultaneously | — |

**SHIFT + T4** → Sound Path screen (shows routing of current sound).

### T2: EQ (3-Band Equalizer)
| Encoder | Parameter |
|---------|-----------|
| Blue | Low (bass) |
| Green | Mid |
| White | High (treble) |
| Orange | EQ amount (counterclockwise = clean, no EQ) |

### T3: Master Effect
Same effects as Synth/Drum mode, **modified for stereo**.
- **SHIFT + T3** → Effect browser → blue encoder scrolls → any key confirms.
- **T3** toggles effect on/off.

### T4: Master Out
| Parameter | Control |
|-----------|---------|
| Master balance L/R | Blue + Green encoders |
| Drive | Orange encoder |
| Release | White encoder (controls how quickly drive narrows the dynamic range; mid-to-long = pumping sound) |

> **Drive** narrows the difference between high and low audio levels, making the output louder and more compact. At high levels, audio becomes distorted. Can add texture for a dirty, raw mix.

---

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

---

## LFO (Shift + T4 on any synth/drum sound 1–8)

Press **Shift + T4** on any drum or synth sound → blue encoder selects LFO mode.

### 8 LFO Modes

| Mode | Source | Key Encoders |
|------|--------|--------------|
| **Element** | External: g-force sensor, external input (radio/line/mic), synth engine envelope/level | Blue (source), Green (amount), White (destination), Orange (parameter) |
| **Random** | Random parameter modulation with envelope | Blue (amount), Green (speed), White (destination), Orange (attack/decay) |
| **Tremolo** | Pitch + volume modulation | Blue (speed), Green (pitch), White (volume), Orange (attack/decay) |
| **Value** | Single parameter modulation | Blue (speed), Green (amount), White (destination), Orange (parameter) |
| **MIDI** | External MIDI CC (up to 4 channels routable) | Compatible with Ableton Live, Logic, Reason, Pro Tools |
| **Crank** | Manual hands-on control (requires manual turning) | Blue (speed), White (destination), Green (amount) |
| **Bend** | Physical control via bender accessory | Orange (control), White (amount), Green/Blue (destination) |
| **Free LFO** | Non-retriggering LFO | Symbol followed by "F" = does not retrigger on every note |

### LFO Shapes (Shift + Orange encoder while in Tremolo mode)
Sine, Saw, Exp, Square, Blip

---

## Effects (Reference)

Press **SHIFT + T3** → **T1/T2** to select effect. Available in Synth, Drum, and as Master Effect (stereo versions):

| Effect | Type | Key Parameters |
|--------|------|---------------|
| **Delay** | Solid state delay | Size, speed, feedback, mix |
| **Grid** | 3D feedback plate | X/Y size, Z feedback, mix |
| **Nitro** | Dual resonant turbo filter | Frequency, filter frequency follow, resonance, phone, punch |
| **Spring** | Hacked telephone system | Tone, phonic, baud |
| **Telematic** | Hard-hitting low-pass filter | Frequency, punch, rounds, power |
| **Power** | Mathematic reverb | Tone, turns, damping, send |
| **CWO** | Pitch shifting delay | Frequency, delay, feedback, sideband |
| **Drum Effect** | (engine-specific) | Per engine |

---

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

### Creating a Drum Kit from FM Radio
1. Select Drum mode
2. Press Mic/Input key
3. Set source to radio
4. Cycle through frequencies to find interesting textures
5. Each pad records a different radio moment

---

## Song Rendering / Connectivity

### Album Mode (SHIFT + COM → T1)
- Arrange full performances (tape + sequences) into a song
- Each "slot" holds one complete OP-1 session
- **T1**: Enter album mode
- **T3**: Play/pause
- Export entire session as a single file

### COM Mode (SHIFT + COM)
**Computer mode** — OP-1 acts as a USB audio interface:
- 2-in/2-out audio over USB (OP-1 audio engine + DAW)
- Simultaneous stereo recording and playback
- 44.1kHz, 16/24-bit (check official specs)

### OP-1 Mode (SHIFT + COM → T2)
OP-1 treats the DAW as a tape machine — sends and receives multi-track audio over USB, synchronized to OP-1's sequencer.

### MIDI Controller Mode (SHIFT + COM → T3)
OP-1's keys, encoders, and sensors send standard MIDI CC messages to control external software/hardware.

### Disk Mode (SHIFT + COM → T4)
Access internal 4GB drive as a USB mass storage device. Tape recordings appear as WAV files.

### Propellerhead Reason / Ableton Live Control
OP-1 can send specific key mappings to control Reason's transport and Ableton Live's session view. See official guide for the full mapping table.

---

## TE-Boot Mode (Press and hold HELP + CONNECT simultaneously)

For firmware updates and factory reset.

| Function | Access |
|----------|--------|
| Firmware update | Press UPDATE (displayed in TE-Boot) |
| Factory reset | Press FACTORY RESET |
| Format internal drive | Press FORMAT |
| Function test | Press TEST |

---

## Key Shortcuts

| Shortcut | Action |
|----------|--------|
| **SHIFT + HELP** | Key name and function of any key |
| **Hold HELP + play keys** | Note information |
| **SHIFT + HELP** (from any mode) | TOOLS (time/date) |
| **SHIFT + T1–T4** | Enter secondary mode for that key |
| **SHIFT + Arrow keys** (in tape) | Move between bar markers |
| **SHIFT + T3 + Tape** | Arm tape recording |

---

## Linux / USB MIDI

OP-1 is class-compliant on Linux — no driver needed. It enumerates as both a MIDI device and a USB audio interface.

```bash
# List OP-1 MIDI ports
amidi -l
# Output looks like:
# Port    Client name              Port name
# 128:0   Teenage Engineering     OP-1 MIDI

# Send MIDI to OP-1
sendjack or aconnect from your DAW to OP-1 MIDI port

# USB Audio
# OP-1 appears as a USB audio device (hw:OP1 or similar)
# Use with jackd, pulseaudio, or ALSA utilities
```

> **Tip**: OP-1's USB audio is 2-in/2-out. When connected, it can simultaneously record its own audio output and receive DAW audio input for reamping or DAW-based processing.
