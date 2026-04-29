---
name: carla-rack
description: "Carla plugin chain rack — automated multi-effect processing via Carla's LV2/VST engine"
version: 0.1.0
author: Hermes Agent
license: MIT
inputs:
  - name: input_audio
    type: file
    description: Input audio file (WAV/FLAC/MP3)
  - name: chain_config
    type: list[dict]
    description: Ordered list of plugin descriptors and parameters
outputs:
  - name: output_audio
    type: file
    description: Rendered output file
---
# Carla-Rack Skill

Wraps [Carla](https://github.com/falkTX/Carla) in rack mode for automated multi-effect
plugin chains. Exposes `add_plugin()` and `render_once()` as a Python interface.

## Status
- **Phase**: TDD — initial stub implemented
- **Dependencies**: Carla binary (`carla` or `carla2`) on PATH
- **Real-world requirement**: Carla 2.5+ installed to fully exercise

## Purpose

Batch-processing audio through chains of VST2/VST3/LV2 plugins without manual DAW
work. Intended for clean headless operation: `carla --batch --input=in.wav …`

## Public Interface

```python
from carla_rack import CarlaRack, CARLA_AVAILABLE

if not CARLA_AVAILABLE:
    raise RuntimeError("Install Carla first")

rack = CarlaRack()
rack.add_plugin("/usr/lib/lv2/calf-studios/low_gear_lv2.so", {"drive": 0.7})
rack.chain([...])
output = rack.render_once("vocals.wav", "vocals-processed.wav")
```

## Test Coverage
- `tests/test_carla_rack.py`: availability detection, module imports, API shape

## Notes
- Carla's command-line batch mode varies between v1 and v2; the thin wrapper
  defers heavy parsing until the binary is confirmed available.
- In absence of Carla the module still exposes `CARLA_AVAILABLE = False` and raises
  `CarlaRackError` on instantiation.
