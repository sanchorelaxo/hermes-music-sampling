---
name: quneo-led-mapping
description: Map QuNeo LED control messages per preset — CC-based vs Note On-based, preset slot layout, and empirical LED verification
category: quneo
---

# QuNeo LED Mapping Skill

Map Keith McMillen QuNeo LED control messages per preset.

## QuNeo MIDI Port
- Device: hw:24:0 (ALSA hardware port)
- mido port: QuNeo:QuNeo MIDI 1 24:0

## 16 Factory Preset Slots

| Slot | Preset Name |
|------|-------------|
| 0 | Drum C1-D#2 / Serato |
| 1 | Drum E2-G3 (factory default) |
| 2 | Drum G#3-B4 |
| 3 | Drum C5-D#6 |
| 4 | Grid Mode Ch.2 |
| 5 | Grid Mode Ch.3 |
| 6 | Grid Mode Ch.4 |
| 7 | Grid Mode Ch.5 |
| 8 | Ableton Live Clip Launching |
| 9 | Ableton Live Drum Rack |
| 10 | Logic |
| 11 | Traktor DJ / Mixxx |
| 12 | Reason |
| 13 | Battery |
| 14 | Korg iMS-20 - iPad |
| 15 | BeatMaker - iPad |

## Two LED Control Protocols

### CC-based (factory presets 0-15)
Factory presets use CC messages to set LED position/state.

### Note On-based (reference preset)
The reference SysEx (from queneo-editor test_visual_sweep.py) uses Note On velocity=127 to light LEDs.

## Loading All 16 Factory Presets

```bash
cd ~/Documents/git/quneo-linux
for i in $(seq 0 15); do
  python3 quneo-linux.py --device hw:24:0 preset \
    --preset_file presets_1.2.3/QuNeo_FactoryPresets.json \
    --in $i --out $i
  sleep 0.3
done
```

Key: --device hw:24:0 must come BEFORE the subcommand.

## Confirmed CC LED Mappings (Factory Preset 1)

| Component | CC | Effect |
|----------|-----|--------|
| LongSlider | 5 | Single LED position: 0=left, 127=right |
| Left Rotary | 16 | Single LED position: 0=bottom, 127=top |
| Right Rotary | 17 | Single LED position: 0=bottom, 127=top |
| HSlider2 | 2 | VU gradient (green to yellow to red) |
| HSlider3 | 3 | VU gradient |
| VSlider2 | 8 | VU gradient |
| VSlider3 | 9 | VU gradient |
| LongSlider ends | 8 | Left endpoint indicator (separate from CC5) |
| LongSlider ends | 9 | Right endpoint indicator (separate from CC5) |

Note: CC messages must be re-sent every ~50ms to hold LED state (not latched).

## Unresolved (Factory Preset 1)

- HSlider0 (topmost of 4 horizontal sliders): CC0 does NOT light LED
- HSlider1 (2nd from top): CC1 does NOT light LED
- VSlider0: CC6 does NOT light VSlider0
- VSlider1: CC7 may not light VSlider1

The JSON hidLeds CC assignments likely describe VU metering feedback rather than remote LED write control.

## Preset 1 Transport Arrows

Notes 40-47 confirmed for transport arrow buttons (visual flash).
Pads 1-16: notes 36-51 (from factory preset JSON).

## LED Sustained Hold Pattern

```python
import threading, time, mido

running = True
def hold(cc, value, port):
    while running:
        port.send(mido.Message('control_change', channel=0, control=cc, value=value))
        time.sleep(0.05)

port = mido.open_output('QuNeo:QuNeo MIDI 1 24:0')
t = threading.Thread(target=hold, args=(2, 127, port))
t.start()
time.sleep(3)  # LED stays lit for 3 seconds
running = False
t.join()
```

## Reference Files

- Factory presets: ~/Documents/git/quneo-linux/presets_1.2.3/QuNeo_FactoryPresets.json
- quneo-linux.py: ~/Documents/git/quneo-linux/quneo-linux.py
- Reference SysEx: /tmp/ref_preset_slot0.syx
- Test script: ~/Documents/git/queneo-editor/test_visual_sweep.py (Note On approach)
