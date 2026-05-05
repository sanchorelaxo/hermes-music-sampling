---
name: sp404-mk2
description: Roland SP-404 MK2 — 16-pad sampler/sequencer with 4 bus effects, 29 MFX, 14 INPUT FX, DJ mode, TR-REC, BPM SYNC, resampling, skip-back sampling, and SD card storage. Source: ROLAND_SP-404_MK2.pdf reference manual.
category: instruments
---

# Roland SP-404 MK2 — Portable Sampler

## Hardware

| Spec | Value |
|------|-------|
| Pads | 16 velocity-sensitive pads + 1 SUB PAD |
| Pads velocity levels | 3 levels per pad (A/B/C) |
| Banks | 10 banks (A–J), 16 pads each = 160 samples per project |
| Patterns | 20 patterns × 10 banks = 200 patterns per project |
| Sequencer | Step (TR-REC), realtime, and per-pad mute automation |
| Effects | 4 buses (BUS 1, BUS 2, BUS 3, BUS 4), 29 MFX, 14 INPUT FX |
| Tempo | 40.00–200.00 BPM, tap tempo, BPM SYNC |
| Storage | SD/SDHC card (up to 32GB) |
| Audio | 16-bit/44.1kHz (internal), 24-bit via USB audio |
| Connectivity | 2× 3.5mm audio I/O, 6.35mm INPUT jack, USB (audio + MIDI), headphones |
| Power | DC in (5V, 1A) |
| Weight | 1.1 kg |

**I/O routing**: INPUT jack (6.35mm, mono), LINE OUT (3.5mm stereo L/R), PHONES (3.5mm stereo), USB (type B).

**⚠️ Never plug 3.5mm mic/line into a device with phantom power — this destroys the ports.**

---

## Modes

| Mode | Entry | Description |
|------|-------|-------------|
| **SAMPLE** | Default | Play/trigger samples from pads |
| **PATTERN** | PATTERN SELECT | 16-step sequencer (TR-REC or realtime) |
| **DJ** | D + E/J banks held | 2-channel DJ mixer with crossfader, BPM sync, roll, reverse |
| **UTILITY** | SHIFT + BANK | System settings, SD card, factory reset |

### Live Mode
**SHIFT + BANK (hold 3s)** disables edit/sampling buttons for live performance — only playback controls remain active.

---

## Sample Mode

### Playing Back Samples

| Action | Control |
|--------|---------|
| Trigger pad | Press pad (velocity-sensitive: A/B/C levels) |
| Stop playback | STOP button |
| Pause | SHIFT + PAUSE (latches until pressed again) |
| Reverse playback | REVERSE button |
| Loop on/off | LOOP button |
| One-shot mode | GATE button (plays once, ignores release) |
| BPM SYNC | BPM SYNC button (syncs loop to project/bank tempo) |

### Velocity System
Each pad stores 3 velocity layers (A = loud, B = medium, C = soft). Velocity auto-switches based on how hard you hit the pad. Additionally:
- **SHIFT + Pad 2**: FIXED VELOCITY (force all playback to velocity 127)
- **SHIFT + Pad 3**: 16 VELOCITY (cycle through 16 velocity levels)

### Pitch/Speed Controls
**PITCH/SPEED button** enters pitch screen:
| Parameter | Control |
|-----------|---------|
| PITCH | CTRL 1 knob (±50 semitones) |
| SPEED | CTRL 2 knob (50–200%) |
| VOLUME | CTRL 3 knob |
| PAN | SHIFT + CTRL 3 |
| BPM | VALUE knob |
| BPM SYNC | SHIFT + BPM SYNC button |

**BPM SYNC ON**: sample loops snap to tempo grid (1 bar, 2 bars, etc.)
**BPM SYNC OFF**: free speed, pitch and speed are linked

### Pad Mute Groups
**SHIFT + Pad 5**: PAD LINK — play multiple linked pads with single pad
**SHIFT + Pad 6**: MUTE GROUP — prevent samples in same group from layering

### Resampling
1. Press **RESAMPLE**
2. Play/perform — audio from output is captured
3. Press **RESAMPLE** again to stop
4. New sample auto-assigned to a pad

### Skip-Back Sampling
1. **SHIFT + SAMPLING** → enable skip-back
2. Pad constantly buffers last ~4 seconds
3. On event (clap, beat), press **SAMPLING**
4. Captures the 4 seconds **before** the trigger

---

## Sampling

### Recording a Sample

| Step | Action |
|------|--------|
| 1 | Press **SAMPLING** |
| 2 | Configure input: SOURCE, LEVEL, MONO/STEREO |
| 3 | Arm count-in if needed (SHIFT + Pad 9 = count-in on/off) |
| 4 | Press **SAMPLING** (or play the source) |
| 5 | Set END POINT (auto via END SNAP, or manual) |
| 6 | Press **SAMPLING** again to stop |

### Input Settings (SHIFT + INPUT SETTING)
| Parameter | Control |
|-----------|---------|
| SOURCE | LINE / MIC / USB |
| GAIN | Input sensitivity |
| MONO/STEREO | SHIFT + GAIN knob |
| **INPUT FX** | Press INPUT FX button to enable effects on input signal |

### END SNAP
Automatically sets end point at zero-crossing (eliminates clicks). Enabled: **SHIFT + RESAMPLE** (while lit).

### Mark + Chop
1. Press **MARK** at desired split points
2. Press **SHIFT + MARK** (3s+) → **CHOP**
3. Sample splits at all markers, resulting pieces auto-assigned to consecutive pads

---

## Effects System

### Bus Architecture

| Bus | Type | Purpose |
|-----|------|---------|
| **BUS 1** | Main FX bus | Apply to individual samples (per-pad BUS 1/2 assignment) |
| **BUS 2** | Alt FX bus | Alternative effect chain for samples |
| **BUS 3** | Master bus | Applied to overall output mix |
| **BUS 4** | Master alt | Secondary master bus |

**Per-pad BUS assignment**: Press **BUS FX** → orange (BUS 1) or blinking orange (BUS 2). Pads lit green = BUS 1, white = BUS 2, off = DRY (no effect).

### Direct FX (Per Effect Button)
You can assign any effect to the top-panel effect buttons (FILTER+DRIVE through MFX) via **UTILITY → EFX SET**:
- **SHIFT + any effect button** → direct access to that effect

### 6 Hardware Effect Buttons (BUS 1/2 routing)

| Button | Effect Type |
|--------|-------------|
| **FILTER+DRIVE** | HPF/LPF + overdrive |
| **EQ** | 3-band + isolator |
| **ISOLATOR** | 3-band Kill (LOW/MID/HIGH cut) |
| **DELAY** | Tempo-synced delay |
| **DJFX LOOPER** | Turntable-style loop slicer |
| **MFX** | Multi-effect (any of 29 MFX selectable) |

---

## MFX List (29 Multi-Effects)

Selected via **MFX button** (hold + turn VALUE or CTRL 3 knob). Use **SHIFT + DJFX LOOPER** for #17–32, **SHIFT + ISOLATOR** for #33+.

### Filter/Distortion

| # | Name | Type | Parameters |
|---|------|------|------------|
| 1 | **Filter+Drive** | HPF/LPF + overdrive | CUTOFF (20–16000Hz), RESONANCE (0–100), DRIVE (0–100), FLT TYPE (HPF/LPF), LOW FREQ, LOW GAIN |
| 2 | **Resonator** | Karplus-Strong physical model | ROOT (C1–G9), BRIGHT (0–100), FEEDBACK (0–99%), CHORD (Root/Oct/UpDn/P5/m3/m5/m7/m7oct/m0/M3/M5/M7/M7oct/M9/M11), PANNING, ENV MOD |
| 3 | **Sync Delay** | Tempo-synced echo | TIME (1/32–1/1 bars + dotted/triplet), FEEDBACK (0–99%), LEVEL, L DAMP F (FLAT/80–10000Hz), H DAMP F (630–12500Hz/FLAT) |
| 4 | **Isolator** | 3-band kill | LOW, MID, HIGH (-INF to +12dB) |
| 5 | **DJFX Looper** | Turntable loop | LENGTH (0.230–0.012s), SPEED (-100–100, negative=reverse), LOOP SW (OFF/ON) |
| 6 | **Scatter** | Stepped loop direction/gate | TYPE (1–10), DEPTH, SCATTER (ON/OFF), SPEED (SINGLE/DOUBLE) |
| 7 | **Downer** | Pitch-linked slowdown | DEPTH (0–100), RATE (1/32–2 bars), FILTER (ON=restore pitch), RESONANCE |
| 8 | **Ha-Dou** | Wave-generation | MOD, DEPTH, TIME, LEVEL, LOW CUT, HIGH CUT, PRE DELAY |
| 9 | **Ko-Da-Ma** | Reverb | TIME (1/32–1/1 bars), FEEDBACK, SEND, L DAMP F, H DAMP F, MODE (SINGLE/PAN) |
| 10 | **Zan-Zou** | Negative-phase delay | TIME, FEEDBACK, HF DAMP, LEVEL, MODE (2TAP/3TAP/4TAP), SYNC (OFF/ON) |
| 11 | **To-Gu-Ro** | Undulating slowdown | DEPTH, RATE, RESONANCE, FLT MOD, AMP MOD, SYNC |
| 12 | **SBF** | Sideband filter | INTERVAL (0–100), WIDTH (0–100), BALANCE (100-0-100), TYPE (SBF1–SBF6), GAIN |
| 13 | **Stopper** | Turntable stop | DEPTH, RATE, RESONANCE, FLT MOD, AMP MOD |
| 14 | **Tape Echo** | Roland RE-201 Space Echo sim | TIME (10–800ms), FEEDBACK, LEVEL, MODE (S/M/L/S+M/S+L/S+M+L), W/F RATE, W/F DEPTH |
| 15 | **TimeCtrlDly** | Smooth delay | TIME, FEEDBACK, LEVEL, L DAMP F, H DAMP F, SYNC |
| 16 | **Super Filter** | Cyclic cutoff filter | CUTOFF (0–100), RESONANCE, FLT TYPE (LPF/BPF/HPF), DEPTH, RATE, SYNC |
| 17 | **WrmSaturator** | Warm saturator | DRIVE (0–48dB), Eq LOW (±24dB), Eq HIGH (±24dB), LEVEL |

### Vinyl/Cassette/Lo-fi

| # | Name | Parameters |
|---|------|------------|
| 18 | **303 VinylSim** | COMP, NOISE, WOW FLUT, LEVEL |
| 19 | **404 VinylSim** | FREQUENCY, NOISE, WOW FLUT |
| 20 | **Cassette Sim** | TONE, HISS, AGE (0–60 years), DRIVE, WOW FLUT, CATCH |
| 21 | **Lo-fi** | PRE FILT (1–6), LOFI TYPE (1–9), TONE, CUTOFF, BALANCE, LEVEL |

### Reverb/Chorus/Flanger/Phaser

| # | Name | Parameters |
|---|------|------------|
| 22 | **Reverb** | TYPE (AMBI/ROOM/HALL1/HALL2), TIME, LEVEL, LOW CUT, HIGH CUT, PRE DELAY |
| 23 | **Chorus** | DEPTH, RATE (0.33–2.30s), BALANCE, EQ LOW (±15dB), EQ HIGH (±15dB), LEVEL |
| 24 | **JUNO Chorus** | MODE (JUNO 1/2/12/JX-1 1/2), NOISE, BALANCE |
| 25 | **Flanger** | DEPTH, RATE, MANUAL, RESONANCE, BALANCE, SYNC |
| 26 | **Phaser** | DEPTH, RATE, MANUAL, RESONANCE, BALANCE, SYNC |
| 27 | **Wah** | PEAK, RATE, MANUAL, DEPTH, FLT TYPE (LPF/BPF), SYNC |

### Modulation/Pitch

| # | Name | Parameters |
|---|------|------------|
| 28 | **Slicer** | PATTERN (1–32), SPEED, DEPTH, SHUFFLE, MODE (LEGATO/SLASH), SYNC |
| 29 | **Tremolo/Pan** | DEPTH, RATE, TYPE (TRE/PAN/TRI/SQR/SIN/SAW1/SAW2/TRP), WAVE, SYNC |
| 30 | **Chromatic PS** | PITCH1/2 (±24 semi), BALANCE, PAN1/PAN2 (L50–R50) |
| 31 | **Hyper-Reso** | NOTE (±17–18 semitones from root), SPREAD (UNISON/TINY/SMALL/MEDIUM/HUGE), CHARACTER, SCALE (C maj–B min), FEEDBACK, ENV MOD |
| 32 | **Ring Mod** | FREQUENCY, SENS, BALANCE, POLARITY, EQ LOW, EQ HIGH |
| 33 | **Crusher** | FILTER (331–15392Hz), RATE (0–100), BALANCE |
| 34 | **Overdrive** | DRIVE, TONE (-100–100), BALANCE, LEVEL |
| 35 | **Distortion** | DRIVE, TONE (-100–100), BALANCE, LEVEL |
| 36 | **Equalizer** | LOW GAIN (±15dB), MID GAIN, HIGH GAIN, LOW FREQ, MID FREQ, HIGH FREQ |
| 37 | **Compressor** | SUSTAIN, ATTACK, RATIO, LEVEL |
| 38 | **SX Reverb** | TIME, TONE (±12), BALANCE |
| 39 | **SX Delay** | TIME, FEEDBACK, TONE, BALANCE |
| 40 | **Cloud Delay** | TIME, FEEDBACK, TONE, BALANCE (cloud/scatter algorithm) |
| 41 | **Back Spin** | Auto back-spin on cue |

---

## INPUT FX (14 Input Effects)

Applied to audio coming into the INPUT jack. Access: **INPUT FX button** (in UTILITY → INPUT FX screen).

| Index | Effect | Parameters |
|-------|--------|------------|
| 0 | **Bypass** | — |
| 1 | **Auto Pitch** | For vocals |
| 2 | **Vocoder** | For synthesizer voice |
| 3 | **Harmony** | Adds harmonies |
| 4 | **Gt Amp Sim** | Guitar amplifier simulation |
| 5 | **Chorus** | DEPTH, RATE, BALANCE, EQ LOW, EQ HIGH, LEVEL |
| 6 | **JUNO Chorus** | MODE, NOISE, BALANCE |
| 7 | **Reverb** | TYPE, TIME, LEVEL, LOW CUT, HIGH CUT, PRE DELAY |
| 8 | **TimeCtrlDly** | TIME, FEEDBACK, LEVEL, SYNC |
| 9 | **Chromatic PS** | PITCH1/2, BALANCE, PAN |
| 10 | **Downer** | DEPTH, RATE, FILTER, RESONANCE |
| 11 | **WrmSaturator** | DRIVE, Eq LOW, Eq HIGH, LEVEL |
| 12 | **303 VinylSim** | COMP, NOISE, WOW FLUT, LEVEL |
| 13 | **404 VinylSim** | FREQUENCY, NOISE, WOW FLUT |
| 14 | **Cassette Sim** | TONE, HISS, AGE, DRIVE, WOW FLUT, CATCH |
| 15 | **Lo-fi** | PRE FILT, LOFI TYPE, TONE, CUTOFF, BALANCE, LEVEL |
| 16 | **Equalizer** | LOW/MID/HIGH GAIN, FREQ |
| 17 | **Compressor** | SUSTAIN, ATTACK, RATIO, LEVEL |

---

## Pattern Sequencer

### Creating a Pattern (TR-REC — Step Recording)

| Step | Action |
|------|--------|
| 1 | Select bank (A–J) |
| 2 | Press **PATTERN SELECT** → choose pattern number (1–20) with pads 1–16 |
| 3 | Press **PATTERN EDIT** → enters step recording |
| 4 | Set TR-REC on: **SHIFT + REC** |
| 5 | Set length: **SHIFT + pads 1–4** (1/4, 1/2, 1, 2 bars) |
| 6 | Press **REC** + tap pads in time |
| 7 | **SHIFT + REC** to finish |

### Realtime Recording
Press **PATTERN EDIT** without TR-REC — records as you play pads in realtime.

### Effect Motion Recording (EFX MOTION REC)
1. With pattern playing, hold **SHIFT + BUS FX**
2. Twist knobs to record effect changes
3. Each knob movement becomes a step in the pattern
4. **SHIFT + DEL + MARK**: erase effect motion data
5. **SHIFT + DEL + REVERSE**: erase all effect motions in pattern

### Pattern Chaining
Press **PATTERN SELECT** then **SHIFT + pad** to chain patterns into a continuous playback sequence (up to 64 patterns long).

### Converting Pattern → Sample (Bounce)
**SHIFT + BOUNCE** converts the entire pattern to a single sample on the current pad (freezes pattern into one audio file).

---

## DJ Mode

Entry: Press **D bank + E/J bank** simultaneously.

### Channel Controls
| Control | Function |
|---------|----------|
| CTRL 1 | CH1 LEVEL |
| CTRL 2 | CH2 LEVEL |
| CTRL 3 | CUE MIX (headphone monitoring) or X-FADE |
| VALUE | BPM |

### Pad Functions (DJ Mode)
| Pad | CH1 | CH2 |
|-----|-----|-----|
| 1, 2 | Play / Pause | — |
| 3, 4 | — | Play / Pause |
| 5, 6 | Reverse on/off | — |
| 7, 8 | — | Reverse on/off |
| 9, 10 | BPM SYNC to CH2 | — |
| 11, 12 | — | BPM SYNC to CH1 |
| 13, 14 | Mute | — |
| 15, 16 | — | Mute |
| 9+6 | BPM BEND+ | — |
| 11+8 | — | BPM BEND- |
| ROLL + 13/15 | Roll 1/4, 1/2, 1, 2 bars | — |

### BPM Sync in DJ Mode
Pad 10: CH1 follows CH2 tempo. Pad 12: CH2 follows CH1 tempo. **SHIFT + REVERSE + Pad 13/15**: reverse while held.

### Volume Curve Selection
**SHIFT + RESAMPLE + VALUE**: cycles through FAST CUT → LINEAR → SQUARE → CUBIC → FAST CUT.

---

## Utility Settings (SHIFT + UTILITY)

### System Parameters
| Parameter | Values | Description |
|-----------|--------|-------------|
| SWING | 50–80% | Timing swing |
| SYSTEM RESO | ON/OFF | Unknown/reserved |
| REVERSE TYPE | 303/404 | Which vinyl sim model for reverse |
| TRIG LAMP | ON/OFF | Pad LED behavior |
| CUE LEVEL | — | Headphone monitoring level |
| LINE OUT | ON/OFF | Enable/disable line out |
| BEAT METER | — | Tempo display mode |
| REC MODE | — | Sampling mode (manual/auto) |
| KNOB MODE | REL/ABS | Relative vs absolute knob behavior |

### Pad Settings (PAD SET)
| Parameter | Values | Description |
|-----------|--------|-------------|
| PAD VELOCITY | 3-VEL/16-VEL/FIXED | Velocity sensitivity mode |
| PAD COLOR | — | Assign color to pad |
| PAD LINK | ON/OFF | Per-pad link setting |
| MUTE GROUP | — | Per-pad mute group assignment |

### EFX SET
Assign effects to BUS 3 and BUS 4 (master buses). Up to 4 effects in series per bus.

---

## Key Shortcuts

| Shortcut | Action |
|----------|--------|
| SHIFT + PAD 1 | FIXED VELOCITY |
| SHIFT + PAD 2 | 16 VELOCITY |
| SHIFT + PAD 3 | CUE (headphone monitoring) |
| SHIFT + PAD 4 | CHROMATIC (play pads as chromatic scale) |
| SHIFT + PAD 5 | PAD LINK |
| SHIFT + PAD 6 | MUTE GROUP |
| SHIFT + PAD 7 | METRONOME |
| SHIFT + PAD 8 | COUNT-IN |
| SHIFT + PAD 9 | TAP TEMPO |
| SHIFT + PAD 10 | GAIN screen |
| SHIFT + PAD 11 | UTILITY menu |
| SHIFT + PAD 12 | IMPORT/EXPORT menu |
| SHIFT + PAD 13 | PAD SETTING |
| SHIFT + PAD 14 | EFX SETTING |
| SHIFT + PAD 15 | MUTE BUS |
| SHIFT + PAD 16 | PAUSE |
| SHIFT + MARK (3s) | CHOP (split at markers) |
| SHIFT + REVERSE + PADS 1–16 | Reverse each pad |
| SHIFT + LOOP | PING-PONG LOOP |
| SHIFT + GATE | GATE ALL ON/OFF |
| SHIFT + BPM SYNC | SYNC ALL ON/OFF |
| SHIFT + REC | TR-REC toggle |
| SHIFT + BANK A–J | BANK VOLUME adjustment |
| SHIFT + REMAIN (3s) | LIVE MODE on/off |
| HOLD + REMAIN (3s) | BANK PROTECT |
| COPY + EXIT | COPY all samples/patterns in bank |
| VALUE + PADS 1–16 | Select sample (no sound) |
| VALUE + PATTERN SELECT (lit) | Select pattern (no playback) |
| SUB PAD (blink) | Tap tempo active |

---

## SD Card Operations

| Operation | Menu |
|-----------|------|
| Import WAV | IMPORT SAMPLE (UTILITY → IMPORT/EXPORT) |
| Export WAV | EXPORT SAMPLE |
| Import project | IMPORT PROJECT (.zip) |
| Export project | EXPORT PROJECT |
| Backup all data | BACKUP (full archive) |
| Restore | RESTORE from backup |
| Format SD | FORMAT (UTILITY) |
| Factory reset | FACTORY RESET |

---

## Linux Integration

The SP-404 MK2 is class-compliant USB audio + MIDI on Linux.

```bash
# Check ALSA MIDI port
amidi -l
# Port    Client name          Port name
# 128:0   Roland              SP-404 MK2

# List USB audio devices
aplay -l | grep -i roland
# card X: SP404MK2

# Send MIDI CC to SP-404 MK2
sendmidi dev "SP-404 MK2" cc 0 74 127

# jackd connection example
jack_connect system:capture_1 "SP404MK2:input-left"
jack_connect "SP404MK2:output-left" system:playback_1

# DAW integration: SP-404 MK2 appears as 2-in/2-out USB audio
# Use ALSA or PulseAudio for direct routing
pulseaudio --log-level=debug 2>&1 | grep -i sp404
```
