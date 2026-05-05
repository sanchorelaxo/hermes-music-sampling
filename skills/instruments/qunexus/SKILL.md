---
name: qunexus
description: Keith McMillen Instruments QuNexus — ultra-portable 25-key USB MIDI keyboard with pressure, tilt, bend pad, and patchable CV/expression on Linux
category: instruments
---

# QuNexus Skill

Keith McMillen QuNexus is a 25-key ultra-portable USB MIDI keyboard with polyphonic aftertouch (pressure), tilt (x/y bend), and patchable CV/expression inputs.

## Device Overview

| Spec | Detail |
|------|--------|
| Keys | 25 keys (one octave each for C–B, across 2 octaves) |
| Sensors | Pressure (per key), X-tilt, Y-tilt |
| Bend | Touch-sensitive bend pad (horizontal) |
| Inputs | Dual expression (1/4" TRS), CV (1/8" TS) |
| MIDI | USB MIDI, 5-pin DIN (with KMI MIDI Expander) |
| Presets | Multiple configurable presets |
| Power | USB bus powered |

## Key Features

### Pressure-Sensitive Keys
Each key reports polyphonic aftertouch (MIDI Channel Pressure / CP).

### Bend Pad
Horizontal touch strip above keys: up/down pitch bend. Assignable to CC.

### Tilt / X-Y
Keys report X (left/right tilt) and Y (front/back tilt) per key.

### CV/Expression Inputs
- `CV IN` — 1/8" TS, accepts +/-10V or 0-5V (switchable)
- `EXPR 1`, `EXPR 2` — 1/4" TRS expression pedals

## Modes

### Preset Mode
Press `SHIFT + [0-9]` to select preset slots 0-9. Factory presets store common configurations.

### CoMA Mode (Controller Mapping)
Hold `SHIFT` + `MODE` to enter CoMA. The QuNexus learns any MIDI mapping from connected software.

### Live Edit Mode
Editable via QuNexus Editor software (Mac/Windows/Linux via Wine).

## MIDI Implementation

```bash
# QuNexus USB MIDI on Linux
amidi -l  # find QuNexus port

# QuNexus MIDI channel: per-preset (default=1)
```

### Typical MIDI Messages
| Message | Data |
|---------|------|
| Note On/Off | Standard 0x90/0x80 |
| Channel Pressure | Per-key pressure (0-127) |
| Pitchbend | Bend pad (14-bit, ~0-16383) |
| CC | X-tilt, Y-tilt, expression 1/2 |

### Mapping (Factory Defaults)
| Control | CC |
|---------|----|
| X-tilt | 74 (default) |
| Y-tilt | 1 (modwheel) |
| Expression 1 | 7 (volume) |
| Expression 2 | 11 (expression) |
| CV In | 20 |

## Linux Integration

```bash
# QuNexus uses standard USB MIDI class driver
# No special driver needed — appears as USB MIDI device

# Route MIDI
aconnect -i | grep QuNexus
aconnect 128:0 24:0  # to your synth

# Monitor
amidi -p hw:X -d  # raw MIDI dump
```

### CV Conversion (requires hardware)
CV input requires the KMI CV Cable Kit or similar to convert +/-10V CV to 0-5V for the QuNexus.

## QuNexus + QuNeo Synergy

The QuNexus and QuNeo are both KMI products and share:
- Same editor software family (QuNexus Editor cross-compatible conceptually)
- CoMA mode for MIDI learn
- SysEx preset structure (similar but not identical)

Unlike the QuNeo, the QuNexus does NOT have SysEx for preset upload — presets are stored on-device via the editor.

## Reference

- Manual: `~/Downloads/current_music_docs/qunexus.pdf`
- Note: QuNexus is from Keith McMillen Instruments (same manufacturer as QuNeo)
