---
name: "fx-wizard"
description: "Bastl Kastle 2 FX Wizard — patchable stereo multi-FX unit with 9 effects (Delay/Flanger/Freezer/Panner/Crusher/Slicer/Pitcher/Replayer/Shifter), pattern generator, LFO, envelope follower, and full CV/Gate/MIDI modulation. Firmware v1.6+. Bastl Instruments, NOT Korg."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "fx", "kastle2", "bastl", "multi-fx", "patchbay", "midi", "cv"]
    related_skills: ["wave-bard", "kastle2-hardware"]
---

# Bastl Kastle 2 — FX Wizard

**Manufacturer:** [Bastl Instruments](https://bastl-instruments.com/instruments/kastle2-fx-wizard) (Czech Republic) — NOT Korg  
**Platform GitHub:** https://github.com/bastl-instruments/kastle2

Patchable stereo multi-FX unit with 9 effects, pattern generator, LFO, envelope follower, and full CV/Gate/MIDI modulation.

## When to Use

- Applying any of 9 FX types to audio (Delay, Flanger, Freezer, Panner, Crusher, Slicer, Pitcher, Replayer, Shifter)
- Routing audio through a Eurorack-compatible patchbay for modular FX chains
- Creating rhythmic, CV-modulated effects synchronized to an external clock
- Using MIDI CC to control FX parameters from a DAW or controller
- Building complex, self-modulating FX patches with LFO + Pattern Generator

## Quick Reference

| Control | Function |
|---------|----------|
| **FX MODE** button | Cycle to next FX mode |
| **SHIFT + FX MODE** | Previous FX mode |
| **SHIFT + KNOB** | Secondary (silver) function |
| **SHIFT + TIME knob** | Output volume |
| **SHIFT + TIME MOD knob** | Input gain |
| **SHIFT + FX MODE (>2s)** | Advanced settings |
| **SHIFT + FX MODE (>15s)** | Memory reset |
| **SHIFT + LFO knob** | Set internal tempo |
| **SHIFT + tap FX MODE** | Tap tempo |

## 9 FX Modes

All modes share 3 main knobs: **TIME** (top right), **FEEDBACK** (middle right), **AMOUNT** (center) — plus FILTER and STEREO (secondary SHIFT functions).

| # | Mode | Color | TIME | FEEDBACK | AMOUNT |
|---|------|-------|------|----------|--------|
| 1 | **Delay** | blue | delay time | feedback | mix |
| 2 | **Flanger** | green | speed | feedback | depth |
| 3 | **Freezer** | blue | freeze size | feedback | mix |
| 4 | **Panner** | white | panning freq (→audio rate = ring mod) | global feedback | amplitude mod (square clip=radical pan) |
| 5 | **Crusher** | yellow | downsampling freq | distorted tonal backdrop | downsampling+XOR bitcrush |
| 6 | **Slicer** | light green | slice pattern | random trigger inversion | decay + dry/wet |
| 7 | **Pitcher** | red | shifting window/grain size | global feedback | ramp mod pitch shift + dry/wet |
| 8 | **Replayer** | orange | tape speed (±=fwd/rev) | feedback for new signal only | output+input buffer mix |
| 9 | **Shifter** | pink | pitch change (±=±semitones) | global feedback | dry/wet |

## Common Parameters (All Modes)

| Parameter | Control | Description |
|-----------|---------|-------------|
| **TIME** | White rabbit (top right) | Main time/frequency parameter |
| **TIME MOD** | Top left knob | Attenuverting modulation of TIME (center=0, right=positive, left=negative) |
| **FREE TIME MOD** | Patch input | Real-time direct modulation of TIME |
| **STEP TIME MOD** | Patch input | Tempo-stepped S&H modulation of TIME |
| **FEEDBACK** | White rabbit (middle right) | Unique per-mode; feeds incoming audio into effect |
| **FEEDBACK MOD** | Middle left knob | Attenuverting modulation of FEEDBACK |
| **AMOUNT** | Center knob | Dry/wet mix; fully left = full dry (effect off) |
| **AMOUNT MOD** | Patch input | Modulation of AMOUNT |
| **FILTER** | SHIFT + middle right knob | LP (left) / HP (right) in feedback path; center = open |
| **STEREO** | SHIFT + middle left knob | Detunes TIME for L/R channels (widens stereo image) |
| **TRIG** | Patch input | Aligns effect to tempo or triggers rhythmic events |

**Mode-specific details:** [references/midi-cc.md](mdc:references/midi-cc.md) — see Mode-Specific Notes section

## Patch Recipes

16 preset patches from the official cookbook. Full recipes: [references/patch-recipes.md](mdc:references/patch-recipes.md)

## Tempo Generator

Tempo source priority: **USB MIDI clock > SYNC IN > Internal clock**

- **SHIFT + LFO knob**: Set tempo (magenta = internal, cyan = external active)
- **SHIFT + tap FX MODE**: Tap tempo

**SYNC Jacks:**
- **SYNC IN** (left channel): External clock detection
- **SYNC OUT**: Outputs master clock; acts as **SYNC THRU** when SYNC IN is connected

**Clock Priority (Advanced Settings → SHIFT + FX MODE >2s):** LFO knob left = ignore MIDI clock; center = normal; right = ignore SYNC IN.

## Modulation Sources

### LFO
- **LFO knob right**: Free-running (warm white light)
- **LFO knob center**: Synced to tempo (cold white light)
- **LFO outputs**: `TRI` (triangle), `PULSE` (high when triangle rises)
- **LFO inputs**: `RESET` (rising edge resets to peak), `LFO MOD` (speed modulation)

**Shaping:** PULSE → LFO MOD for ramp/saw; TRI → LFO MOD for exp/log; PULSE → LFO RESET for saw.

### Envelope Follower
- `ENV OUT`: Audio envelope amplitude output
- `ENV IN`: Envelope follower input (for ducking — audio in → ENV → modulates AMOUNT/FEEDBACK)

### Pattern Generator
Always tempo-synced:
- **GATE**: Rhythmic 8-step sequence (75% gate length per step)
- **CV**: Stepped voltage sequence, 8-step

**Patchbay inputs:** `PATTERN G` (left) modifies GATE rhythm; `PATTERN C` (right) modifies CV sequence; `PATTERN R` (middle) resets both on rising edge.

**GATE rhythm**: **SHIFT + LFO MOD knob** → cycles through 16 patterns.

## Patchbay Summary

### Triple Patch Points
Three horizontal points are interconnected. Multiple outputs → single input = combined signal.

### Output vs Input
- **Outputs**: White outline, labeled inside
- **Inputs**: White text or white arrows (no outline)

### Voltage Compatibility
- Inputs: 0–5V | Outputs: 0–5V

### Bi-Directional Ports (TRS at back)
| Symbol | Description |
|--------|-------------|
| **+** | Logic high output (~5V) |
| **−** | Logic low output (~0V) |
| **⏚** | Direct ground reference |

**⚠️ When connecting multiple Kastles: connect grounds together.** Audio/sync jacks connect grounds automatically; use ⏚ → ground for explicit connection.

## MIDI Implementation

Full CC table, note mapping, and clock sync: [references/midi-cc.md](mdc:references/midi-cc.md)

## Resources

| Document | Source |
|----------|--------|
| Quickstart Guide | `/home/rjodouin/Downloads/kastle2-stuff/manual-kastle2-fxwizard-quickstart.pdf` |
| Complete Manual | `/home/rjodouin/Downloads/kastle2-stuff/manual-kastle2-fxwizard-web.pdf` |
| Cookbook (recipes) | `/home/rjodouin/Downloads/kastle2-stuff/kastle2_fxwizard_cookbook.pdf` |
| Patch Sheets | `/home/rjodouin/Downloads/kastle2-stuff/kastle2_fxwizard_patchsheet.pdf` |
| PO Sync Guide | `/home/rjodouin/Downloads/kastle2-stuff/kastle2-po-sync-guide.pdf` |
| Web App (patterns) | [apps.bastl-instruments.com/fx-wizard-chamber](https://apps.bastl-instruments.com/fx-wizard-chamber/) |
| GitHub (open-source) | [github.com/bastl-instruments/kastle2](https://github.com/bastl-instruments/kastle2) |