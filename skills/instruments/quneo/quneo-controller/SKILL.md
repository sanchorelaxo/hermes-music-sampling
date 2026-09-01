---
name: quneo-controller
description: Configure Keith McMillen QuNeo MIDI controller via SysEx on Linux — preset loading, reload command, mido port naming
category: quneo
---

# QuNeo Controller Configuration

Keith McMillen QuNeo 3D multi-touch pad controller requiring SysEx messages for preset configuration.

## Hardware Setup

### Device Detection
```bash
amidi -l | grep -i quneo
# Typical device: hw:2,0,0 at /dev/snd/midiC2D0
```

### Prerequisites
- **Official editor (preferred, Linux-native):** ~/Documents/git/quneo-qt6-editor/ (`bash install.sh`)
- Wine + KMI QuNeo Editor v2 (Windows) — **NOT required** for preset work on Linux; only needed if you specifically want the legacy Windows GUI under Wine
- quneo-linux: ~/Documents/git/quneo-linux/
- quneo-node: ~/Documents/git/quneo-node/ (Node.js v22+)
- MIDI group: sudo usermod -aG audio $USER

## Preset Workflow

### 1. Create/Edit Preset
- **Preferred:** run the native Qt6 editor: `quneo-editor` (build via `bash install.sh` in quneo-qt6-editor)
- Legacy Wine path (see midi-controller skill): wine QuNeoEditor.exe
- Configure CoMA mode: hold Mode button 1s until all LEDs flash
- Export preset as JSON

### 2. Modify Factory Presets (Only 16 Slots)

QuNeo has exactly 16 presets (slots 0-15), accessed by pressing pads 1-16 after tapping MODE button.

Preset Load Verification:
1. Tap MODE button on QuNeo (flashes blue)
2. Press Pad 6 (slot 5, since pads are 1-indexed)
3. Pad should blink GREEN to confirm load

### 3. Load Preset to Device (CRITICAL SYNTAX)

Use --device hw:24:0 BEFORE the subcommand:
```bash
cd ~/Documents/git/quneo-linux
python3 quneo-linux.py --device hw:24:0 preset \
  --preset_file presets_1.2.3/QuNeo_FactoryPresets.json \
  --in 1 --out 1
```

### 4. Send to QuNeo (Node.js)
```javascript
import { open, close, write } from 'fs';
const sysex = hexFile.split(' ').map(h => parseInt(h, 16));
const fd = await open('/dev/snd/midiC2D0', 'w');
for (let i = 0; i < sysex.length; i += 64) {
  await write(fd, Buffer.from(sysex.slice(i, i+64)));
}
await close(fd);
```

## mido Port Naming (Linux/ALSA)
```python
import mido
# Raw ALSA: hw:2,0,0
# mido port name: 'QuNeo:QuNeo MIDI 1'
mido.get_output_names()
port = mido.open_output('QuNeo:QuNeo MIDI 1')
```

## CRITICAL: Reload Command Required After SysEx

Sending preset SysEx alone does NOT activate the preset. MUST send reload command after SysEx.

**Official reload command (7-bit + CRC encoded, from quneo-qt6-editor `slotLoadPreset`):**
`F0 00 01 5F 7A 1E 00 01 00 02 30 <preset> <crc16> <padding> F7`
The `<crc16>` and padding are computed by the official encoder — do not hardcode the
raw form. See `midi-controller/references/QuNeo_Official_Protocol.md`.

The legacy raw form `F0 00 01 7B 30 00 <preset> F7` is a community-simplified variant,
NOT what the official editor emits.

```python
# Use the OFFICIAL encoder: midi-controller/scripts/quneo_sysex.py (matches
# quneo-qt6-editor sysexformat.cpp slotLoadPreset byte-for-byte).
import sys
sys.path.insert(0, "~/.hermes/skills/music/midi-controller/scripts")
from quneo_sysex import load_preset

sysex = build_syx_preset_data(preset, preset_number=0)
port_out.send(mido.Message.from_bytes(sysex))
time.sleep(0.5)
port_out.send(mido.Message.from_bytes(load_preset(0)))   # official 17-byte reload cmd
```

## Remote LED Control

Factory Preset 1: CC for sliders/rotaries, Note On for pads/buttons.

```python
# SLIDERS & ROTARIES — use CC
port.send(mido.Message('control_change', channel=0, control=CC, value=127))
# PADS & BUTTONS — use Note On (velocity=127 ON, velocity=0 OFF)
port.send(mido.Message('note_on', channel=0, note=N, velocity=127))
```

Sustained hold required: re-send every ~50ms or LED disappears.

## CC LED Mappings (Factory Preset 1)

Authoritative (official `QuNeo.json` → Preset 1, `*B1outLocation` fields):

| Component | Location CC |
|-----------|-------------|
| HSlider0–3 | 0, 1, 2, 3 |
| Rotary0–1 | 4, 5 |
| VSlider0–3 | 6, 7, 8, 9 |
| LongSlider0 | 10 (location), 11 (width) |

Press CCs: sliders 12–21, LongSlider 22, Pad0 23. See quneo-led-mapping skill for
the full table. (An earlier learned table here listed Rotary as CC 16/17 and
LongSlider as CC 5 — those were wrong; 16/17 are rotary outPress CCs.)

## Command Reference

Load preset: python3 -c "from quneo.exporter import json2syx; print(json2syx(preset, slot).hex())"
Flash: node ~/Documents/git/quneo-node/commands/flash.js presets/Custom.json --slot 0
Factory reset: node ~/Documents/git/quneo-node/commands/factory.js
Monitor: node ~/Documents/git/quneo-node/commands/monitor.js

## Related Skills
- quneo-led-mapping — LED control per preset
- quneo-osc-integration — OSC-based LED control
