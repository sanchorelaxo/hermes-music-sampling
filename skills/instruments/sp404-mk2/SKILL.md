---
name: "sp404-mk2"
description: "Use when working with the Roland SP-404 MK2 sampler/sequencer — 16-pad velocity-sensitive sampler, 29 MFX, 14 INPUT FX, 4 bus effects, TR-REC sequencer, DJ mode, BPM SYNC, resampling, and skip-back sampling."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "sampler", "sp404", "roland", "sequencer", "midi", "mfx"]
    related_skills: []
---

# Roland SP-404 MK2 — Portable Sampler

## Hardware

| Spec | Value |
|------|-------|
| Pads | 16 velocity-sensitive + SUB PAD |
| Banks | 10 (A–J), 16 pads each = 160 samples/project |
| Patterns | 20 patterns × 10 banks = 200/project |
| Effects | 4 buses, 29 MFX, 14 INPUT FX |
| Tempo | 40.00–200.00 BPM, tap tempo, BPM SYNC |
| Storage | SD/SDHC (up to 32GB) |
| Audio | 16-bit/44.1kHz internal, 24-bit via USB |
| Connectivity | 2× 3.5mm I/O, 6.35mm INPUT, USB (audio+MIDI), phones |

**⚠️ Never plug 3.5mm mic/line into a device with phantom power — destroys the ports.**

## When to Use

- Triggering and playing back samples with velocity sensitivity and 3 layers per pad
- Applying effects to individual samples (BUS 1/2) or the master mix (BUS 3/4)
- Recording samples from external sources (mic, line, USB)
- Step-sequencing drum patterns with TR-REC or realtime recording
- Resampling the output through effects for layered textures
- DJ-style crossfading and BPM sync with DJ mode

## Modes

| Mode | Entry | Description |
|------|-------|-------------|
| **SAMPLE** | Default | Play/trigger samples from pads |
| **PATTERN** | PATTERN SELECT | 16-step sequencer (TR-REC or realtime) |
| **DJ** | D + E/J banks held | 2-channel DJ mixer with crossfader, BPM sync, roll, reverse |
| **UTILITY** | SHIFT + BANK | System settings, SD card, factory reset |

**Live Mode (SHIFT + BANK hold 3s):** Disables edit/sampling buttons — only playback controls active.

## Sample Mode

**Playing:** Press pad (velocity-sensitive A/B/C). STOP to stop, SHIFT+PAUSE to latch, REVERSE for reverse, LOOP for loop, GATE for one-shot.

**Pitch/Speed:** PITCH/SPEED button → CTRL 1 = pitch (±50 semitones), CTRL 2 = speed (50–200%), CTRL 3 = volume, SHIFT+CTRL 3 = pan, VALUE = BPM.

**BPM SYNC ON:** sample loops snap to tempo grid. **BPM SYNC OFF:** free speed, pitch/speed linked.

**Velocity:** Each pad has 3 velocity layers (A=loud, B=medium, C=soft). SHIFT+Pad 2 = FIXED VELOCITY (127). SHIFT+Pad 3 = 16 VELOCITY.

**Pad linking/muting:** SHIFT+Pad 5 = PAD LINK (play multiple with one pad). SHIFT+Pad 6 = MUTE GROUP (prevent layering).

**Resampling:** Press RESAMPLE → perform → press RESAMPLE again → auto-assigns to a pad.

**Skip-back sampling:** SHIFT+SAMPLING enables 4-second buffer → press SAMPLING on event to capture the 4 seconds *before* the trigger.

**Mark + Chop:** Press MARK at split points → SHIFT+MARK (3s+) → CHOP → auto-assigns pieces to consecutive pads.

## Effects System

### Bus Architecture

| Bus | Type | Purpose |
|-----|------|---------|
| **BUS 1** | Main FX bus | Per-pad BUS 1/2 assignment |
| **BUS 2** | Alt FX bus | Alternative effect chain |
| **BUS 3** | Master bus | Applied to overall output mix |
| **BUS 4** | Master alt | Secondary master bus |

**Per-pad BUS assignment:** Press **BUS FX** → orange (BUS 1) or blinking orange (BUS 2). Green = BUS 1, white = BUS 2, off = DRY.

### Hardware Effect Buttons (BUS 1/2 routing)

| Button | Effect Type |
|--------|-------------|
| **FILTER+DRIVE** | HPF/LPF + overdrive |
| **EQ** | 3-band + isolator |
| **ISOLATOR** | 3-band Kill (LOW/MID/HIGH cut) |
| **DELAY** | Tempo-synced delay |
| **DJFX LOOPER** | Turntable-style loop slicer |
| **MFX** | Multi-effect (any of 29 MFX) |

### MFX — 29 Multi-Effects

Full list of all 41 effects: [references/mfx.md](mdc:references/mfx.md)

Groups: Filter/Distortion (#1–17), Vinyl/Cassette/Lo-fi (#18–21), Reverb/Chorus/Flanger/Phaser (#22–27), Modulation/Pitch/Utility (#28–41).

### INPUT FX — 14 Input Effects

Applied to INPUT jack audio. Access via INPUT FX button.

Full list: [references/input-fx.md](mdc:references/input-fx.md)

## Pattern Sequencer

**TR-REC (step recording):** PATTERN SELECT → pick pattern with pads 1–16 → PATTERN EDIT → SHIFT+REC to enable TR-REC → SHIFT+pads 1–4 set length (1/4, 1/2, 1, 2 bars) → REC + tap pads in time → SHIFT+REC to finish.

**Realtime:** PATTERN EDIT without TR-REC → records as you play.

**EFX MOTION REC:** Pattern playing → SHIFT+BUS FX → twist knobs to record effect changes per step. SHIFT+DEL+MARK = erase effect motion. SHIFT+DEL+REVERSE = erase all effect motions.

**Chaining:** PATTERN SELECT → SHIFT+pad to chain up to 64 patterns.

**Bounce:** SHIFT+BOUNCE converts pattern to a single sample on current pad.

## DJ Mode

Entry: **D bank + E/J bank** held simultaneously.

**Pads:** 1,2 = CH1 play/pause. 3,4 = CH2 play/pause. 5,6 = CH1 reverse. 7,8 = CH2 reverse. 9 = CH1 syncs to CH2 tempo. 11 = CH2 syncs to CH1 tempo. 13,14 = CH1 mute. 15,16 = CH2 mute. ROLL+13/15 = roll 1/4, 1/2, 1, 2 bars.

**Controls:** CTRL 1 = CH1 level, CTRL 2 = CH2 level, CTRL 3 = CUE mix or X-FADE, VALUE = BPM.

## Key Shortcuts

| Shortcut | Action |
|----------|--------|
| SHIFT + PAD 1 | FIXED VELOCITY |
| SHIFT + PAD 2 | 16 VELOCITY |
| SHIFT + PAD 3 | CUE monitoring |
| SHIFT + PAD 4 | CHROMATIC scale |
| SHIFT + PAD 5 | PAD LINK |
| SHIFT + PAD 6 | MUTE GROUP |
| SHIFT + PAD 7 | METRONOME |
| SHIFT + PAD 8 | COUNT-IN |
| SHIFT + PAD 9 | TAP TEMPO |
| SHIFT + MARK (3s) | CHOP (split at markers) |
| SHIFT + REMAIN (3s) | LIVE MODE on/off |
| HOLD + REMAIN (3s) | BANK PROTECT |
| SHIFT + REC | TR-REC toggle |
| SHIFT + LOOP | PING-PONG LOOP |
| SHIFT + GATE | GATE ALL ON/OFF |
| COPY + EXIT | COPY all samples/patterns in bank |

## Utility & SD Card

**Utility (SHIFT + UTILITY):** SWING (50–80%), REVERSE TYPE (303/404), TRIG LAMP, LINE OUT, KNOB MODE (REL/ABS), PAD VELOCITY (3-VEL/16-VEL/FIXED), PAD LINK, MUTE GROUP.

**EFX SET:** Assign effects to BUS 3/4 — up to 4 effects in series per bus.

**SD operations:** IMPORT/EXPORT WAV, project backup/restore, FORMAT, FACTORY RESET.