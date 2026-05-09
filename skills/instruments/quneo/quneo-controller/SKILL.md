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
- Wine + QuNeo Editor (Windows binary) for initial preset creation
- quneo-linux: ~/Documents/git/quneo-linux/
- quneo-node: ~/Documents/git/quneo-node/ (Node.js v22+)
- MIDI group: sudo usermod -aG audio $USER

## Preset Workflow

### 1. Create/Edit Preset (QuNeo Editor via Wine)
- Run via Wine: wine QuNeoEditor.exe
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

Reload SysEx format: [0xf0, 0x00, 0x01, 0x7b, 0x30, 0x00, <preset>, 0xf7]

```python
def reload_preset(preset_number):
    # SysEx: F0 00 01 7B 30 00 <preset> F7
    return bytes([0xf0, 0x00, 0x01, 0x7b, 0x30, 0x00, preset_number, 0xf7])

sysex = build_syx_preset_data(preset, preset_number=0)
port_out.send(mido.Message.from_bytes(sysex))
time.sleep(0.5)
port_out.send(mido.Message.from_bytes(reload_preset(0)))
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

| Component | CC | Effect |
|----------|-----|--------|
| LongSlider | 5 | LED position: 0=left, 127=right |
| Left Rotary | 16 | LED position: 0=bottom, 127=top |
| Right Rotary | 17 | LED position: 0=bottom, 127=top |
| HSlider2 | 2 | VU gradient green-yellow-red |
| HSlider3 | 3 | VU gradient |
| VSlider2 | 8 | VU gradient |
| VSlider3 | 9 | VU gradient |

## Command Reference

Load preset: python3 -c "from quneo.exporter import json2syx; print(json2syx(preset, slot).hex())"
Flash: node ~/Documents/git/quneo-node/commands/flash.js presets/Custom.json --slot 0
Factory reset: node ~/Documents/git/quneo-node/commands/factory.js
Monitor: node ~/Documents/git/quneo-node/commands/monitor.js

## Related Skills
- quneo-led-mapping — LED control per preset
- quneo-osc-integration — OSC-based LED control
