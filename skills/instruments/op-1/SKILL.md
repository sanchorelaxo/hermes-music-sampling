---
name: "op-1"
description: "Use when working with the Teenage Engineering OP-1 portable synthesizer — 13 synth engines, 4 sequencers, 4-track tape recorder, mixer, and wireless radio. Covers synthesis, sequencing, effects, recording, and connectivity."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "synthesizer", "op-1", "teenage-engineering", "midi", "sequencer", "tape"]
    related_skills: []
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

**⚠️ Critical**: Never plug 3.5mm mic input or line output into a sound card with phantom power — destroys OP-1 ports.

## When to Use

- Synthesizing sound with any of 13 engines (FM, phase distortion, sampler, string, etc.)
- Sequencing melodies, drum patterns, or free-form shapes with 6 sequencer types
- Recording and overdubbing multi-track audio on the tape recorder
- Using OP-1 as a USB audio interface for a DAW
- Controlling external hardware/software via MIDI controller mode
- Using built-in wireless radio to sample broadcast audio

## Main Modes

Press one of four main mode keys (Synth, Drum, Tape, Mixer). Press **SHIFT + any main mode key** for the secondary function.

| Key | Primary Mode | Secondary (SHIFT+) |
|-----|--------------|-------------------|
| T1 | Synthesizer | Synth engine selector |
| T2 | Drum | Drum engine selector |
| T3 | Tape | Tape transport/settings |
| T4 | Mixer | Mixer views (sound path, main, EQ, master effect, master out) |

## Synthesizer Mode (T1)

**13 synth engines** (SHIFT + T1 → blue encoder scrolls): Cluster, Digital, String, Pulse, FM, Phase, Synth Sampler, D-Box, D-Synth, Drum Sampler, 6 Operator, DNA, CWO.

Full engine reference with parameters: [references/synth-engines.md](mdc:references/synth-engines.md)

**Per-voice controls:** Envelope (orange), Playmode (green), Effect (white), LFO (blue after pressing LFO key — 8 types: Element, Random, Tremolo, Value, MIDI, Crank, Bend, Free).

**Saving a sound:** SHIFT + T1 → blue encoder selects slot → long press saves.

## Drum Mode (T2)

**2 drum engines:** Drum Sampler (per-pad note/pitch, loop, reverse, gain) and D-Box (pitch, waveform, envelope, filter).

## 6 Sequencer Types

Access: **SHIFT + any main mode** → see sequencer options.

| # | Type | Key Use |
|---|------|---------|
| 1 | **Endless** (128 notes) | SHIFT + keyboard keys, auto-advance |
| 2 | **Pattern** (16-step grid) | Drum patterns, live insert |
| 3 | **Tombola** (physics random) | Bounce notes, adjust gravity/bounciness |
| 4 | **Finger** (two-sequence) | White keys = patterns, join/replace/fill-in |
| 5 | **Sketch** (shape drawing) | Blue+Green draw shapes, keyboard = vertical |
| 6 | **Arpeggio** | Trigger mode, pattern, note length, type |

Full sequencer reference: [references/sequencers.md](mdc:references/sequencers.md)

## Tape Mode (T3)

6-track tape recorder (4 audio tracks + 2 shared). Records real audio.

- **SHIFT + T3** → arm recording, select track
- **T3** again → record
- Arrow keys: rewind/forward | SHIFT + Arrow: jump to start/end
- Tape speed: white encoder (adjusts pitch + time)
- Reverse playback, overdubbing, bar markers, lift, bounce

## Mixer (T4)

Final stage. Press **T4** repeatedly to cycle: Mixer Main → EQ → Master Effect → Master Out.

**Mixer Main:** Blue/Green/White/Orange encoders = Track 1–4 levels. SHIFT + T4 → Sound Path screen.

**EQ:** Blue=Low, Green=Mid, White=High, Orange=EQ amount.

**Master Effect:** SHIFT + T3 → select stereo effect (same 8 types as synth: Delay, Grid, Nitro, Spring, Telematic, Power, CWO, Drum Effect).

**Master Out:** Blue+Green=balance L/R, Orange=drive, White=release.

## Effects & LFO

8 effects: Delay, Grid, Nitro, Spring, Telematic, Power, CWO, Drum Effect.

8 LFO modes: Element, Random, Tremolo, Value, MIDI, Crank, Bend, Free (non-retriggering).

Full effects and LFO reference: [references/effects-lfo.md](mdc:references/effects-lfo.md)

## Tempo, PO Sync, Clock

**Tempo modes:** Free (independent) | Beat Match (OP-1 = master, sends MIDI sync) | Sync (listens to external MIDI clock).

**Setting tempo:** Blue encoder, SHIFT + Blue for fine-tune, tap tempo key.

**PO Sync:** 3.5mm stereo dual mono: L = click track for Pocket Operator, R = mix. Set PO to SY4.

## Connectivity

Full reference for COM mode (USB audio interface), Album mode, TE-Boot, MIDI controller mode, Disk mode, key shortcuts: [references/connectivity.md](mdc:references/connectivity.md)

**COM modes:** T1=Album, T2=OP-1 (DAW as tape machine), T3=MIDI Controller, T4=Disk.

**TE-Boot:** Hold HELP + CONNECT → firmware update, factory reset, format, test.

## Linux / USB MIDI

Class-compliant. Enumerates as MIDI device + USB audio interface.

```bash
amidi -l  # shows "Teenage Engineering OP-1 MIDI" at port 128:0
```