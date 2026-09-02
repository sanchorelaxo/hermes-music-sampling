---
name: quneo-led-mapping
description: Map QuNeo LED control messages per preset — CC-based vs Note On-based, preset slot layout, and empirical LED verification
category: quneo
---

# QuNeo LED Mapping Skill

Map Keith McMillen QuNeo LED control messages per preset.

## QuNeo MIDI Port
- Device: hw:24:0 (ALSA hardware port) — verify with `aconnect -l` / `aplaymidi -l`; this number can change
- mido port: QuNeo:QuNeo MIDI 1 24:0
- Official editor (Linux): ~/Documents/git/quneo-qt6-editor (bash install.sh → `quneo-editor`)

## Authoritative LED/CC source (official)
The official factory preset JSON is the authoritative source for CC/Note LED
assignments: `quneo-qt6-editor/Content/Presets/QuNeo.json` (Preset N →
`ComponentSettings.Pads/...`). The reverse-engineered `quneo-linux/presets_1.2.3/`
copy is older. Prefer the in-repo `QuNeo.json` when it disagrees.

## 16 Factory Preset Slots

Official names from `quneo-qt6-editor/Content/Presets/QuNeo.json` (authoritative):

| Slot | Preset Name |
|------|-------------|
| 0 | Drum C1-D#2 / Serato & djay |
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
| 12 | QuNeo MPE 1.0 |
| 13 | Battery |
| 14 | Korg iMS-20 - iPad |
| 15 | Reason |

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

**Authoritative source:** `quneo-qt6-editor/Content/Presets/QuNeo.json` → `Preset 1.ComponentSettings` (`*B1outLocation` = location CC, `*B1outNote` = outNote, `*B1outPress` = press CC):

| Component | Location CC (outLocation) | outNote | outPress |
|-----------|--------------------------|---------|----------|
| HSlider0 | 0 | 0 | 12 |
| HSlider1 | 1 | 1 | 13 |
| HSlider2 | 2 | 2 | 14 |
| HSlider3 | 3 | 3 | 15 |
| Rotary0 | 4 | 4 | 16 |
| Rotary1 | 5 | 5 | 17 |
| VSlider0 | 6 | 6 | 18 |
| VSlider1 | 7 | 7 | 19 |
| VSlider2 | 8 | 8 | 20 |
| VSlider3 | 9 | 9 | 21 |
| LongSlider0 | 10 (location), 11 (width) | 10 | 22 |

Empirically confirmed effects (from prior hardware testing on factory Preset 1):
- LongSlider location CC moves the single position LED (0=left → 127=right)
- Rotary location CC moves the position LED (0=bottom → 127=top)
- HSlider2/3, VSlider2/3 location CCs light the slider VU gradient (green→yellow→red)

Note: CC messages must be re-sent every ~50ms to hold LED state (not latched).

## Unresolved (Factory Preset 1)

Prior hardware observations that conflicted with the old (wrong) CC table — now
explained: the learned table had CC numbers wrong (e.g. listed Rotary CC 16/17,
LongSlider CC 5, which are actually outPress CCs or other components' locations).
HSlider0/HSlider1 and VSlider0/VSlider1 LEDs are controlled by CC 0/1 and 6/7
respectively per the official JSON. If a CC does not light its LED on hardware,
re-check against the official `QuNeo.json` first.

## Preset 1 Note Numbers (official, from QuNeo.json Preset 1)

| Component | Note(s) | Press CC |
|-----------|---------|----------|
| Pads 1–16 (Pad0–15, drum mode) | 52–67 | 23 (Pad0: outDmPress) |
| Transport 0–2 (rewind/play/record) | 24, 25, 26 | 84, 85, 86 |
| Left/Right 0–3 (L, R) | 11–18 | 71–78 |
| Rhombus | 19 | 79 |
| Up/Down 0–1 (U, D) | 20–23 | 80–83 |

(Note: an earlier learned version of this file claimed transport notes 40–47 and
pad notes 36–51 — those were from an older non-official factory preset and do NOT
match the official Preset 1.)

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

## Preset-Agnostic Testing Tool

`scripts/led_sweep.py` ingests QuNeo.json, derives expected LED maps for any preset
slot, records a webcam sweep, and compares observed vs expected. Empirically
validated results (webcam + human-confirmed) live in
`references/empirical-led-mapping.md` — read it before running tests.

## Reference Files

- **Empirical webcam-validated mapping:** references/empirical-led-mapping.md

- **Official factory presets (authoritative):** ~/Documents/git/quneo-qt6-editor/Content/Presets/QuNeo.json
- **Official preset SysEx dumps:** ~/Documents/git/quneo-qt6-editor/QT6-QuNeo/sysex/data/dataPreset{0-15}.syx
- **Official load-preset SysEx:** ~/Documents/git/quneo-qt6-editor/QT6-QuNeo/sysex/loadPresets/loadPreset{0-15}.syx
- Official protocol reference: ~/.hermes/skills/music/midi-controller/references/QuNeo_Official_Protocol.md
- Older learned copy: ~/Documents/git/quneo-linux/presets_1.2.3/QuNeo_FactoryPresets.json (superseded)
- Test script: ~/Documents/git/queneo-editor/test_visual_sweep.py (Note On approach)
