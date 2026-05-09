---
name: quneo-osc-integration
description: Add OSC (Open Sound Control) support to queneo-editor for network-based QuNeo communication — pyliblo implementation, QuNeOSC Bridge addresses
category: quneo
---

# QuNeo OSC Integration Skill

Add OSC support to queneo-editor for network-based communication with the QuNeo controller.

## Quick Reference

### OSC Address Structure (from QuNeOSC Bridge v0.9 BETA)

Output addresses (QuNeo to OSC):
```
/quneo/pads/{0-15}/drum/note_velocity   # 0-127
/quneo/pads/{0-15}/drum/pressure        # 0-127
/quneo/pads/{0-15}/drum/x               # 0-127 (center=63)
/quneo/pads/{0-15}/drum/y               # 0-127 (center=63)
/quneo/hSliders/{0-3}/note_velocity
/quneo/hSliders/{0-3}/pressure
/quneo/hSliders/{0-3}/location         # 0-127
/quneo/vSliders/{0-3}/note_velocity
/quneo/vSliders/{0-3}/pressure
/quneo/vSliders/{0-3}/location
/quneo/longSlider/{note_velocity,pressure,location,width}
/quneo/rotary/{0-1}/{note_velocity,pressure,direction,location}
/quneo/upButton/{0-1}/{note_velocity,pressure}
/quneo/downButton/{0-1}/{note_velocity,pressure}
/quneo/leftButton/{0-3}/{note_velocity,pressure}
/quneo/rightButton/{0-3}/{note_velocity,pressure}
/quneo/rhombus/{note_velocity,pressure}
/quneo/modeButton/{note_velocity,pressure}
/quneo/transport/{0-2}/{note_velocity,pressure}
```

LED control addresses (OSC to QuNeo, float 0.0-1.0):
```
/quneo/leds/pads/{0-15}/green
/quneo/leds/pads/{0-15}/red
/quneo/leds/hSliders/{0-3}/{0-7}       # segments
/quneo/leds/vSliders/{0-3}/{0-7}
/quneo/leds/rotaries/{0-1}/{0-11}      # 12 segments
/quneo/leds/longslider/{0-15}
/quneo/leds/upButton/{0-1}
/quneo/leds/downButton/{0-1}
/quneo/leds/leftButton/{0-1}
/quneo/leds/rightButton/{0-1}
/quneo/leds/rhombus
/quneo/leds/modeButton
/quneo/leds/transportButtons/{0-2}
```

Default network config:
- OSC Output Port: 7469 (QuNeOSC Bridge sends to this)
- OSC Input Port: 3478 (QuNeOSC Bridge receives LED commands)

## pyliblo Implementation (Recommended)

WARNING: pyliblo callback signature is (path, types, args, src) — NOT (path, args, types, src).

```python
import liblo

# Send LED brightness (float 0.0-1.0, NOT 0-255)
target = liblo.Address("127.0.0.1", 3478)  # QuNeOSC Bridge input (LED control)
target.send("/quneo/leds/pads/0/green", 0.75)

# Receive OSC from QuNeOSC Bridge
server = liblo.Server(7469)
def callback(path, types, args, src):
    # types e.g. 'fi' means float then int
    print(f"{path}: {dict(zip(types, args))}")
server.add_method(None, None, callback)
server.start()
```

Key patterns:
- Use target.send() NOT liblo.send()
- LED values are float 0.0-1.0 (QuNeOSC Bridge normalization)
- types parameter in callback is a format string

## osc_service.py Classes

```python
# QuNeoOSC — direct OSC LED control
osc = QuNeoOSC(target_host="127.0.0.1", target_port=3478, recv_port=7469)
osc.set_pad_led(pad=0, color="green", brightness=0.75)  # pad 0-15
osc.set_rotary_led(rotary=0, segment=5, brightness=1.0)  # rotary 0-1, segment 0-11

# QuNeoHybrid — MIDI SysEx preset upload + OSC LED control (RECOMMENDED)
hybrid = QuNeoHybrid(use_osc=True)
hybrid.flash_preset(preset, slot=0)        # MIDI SysEx preset upload
hybrid.set_all_pads_led("green", 0.5)       # OSC LED control
hybrid.blink_all_pads(duration=2.0, interval=0.5, color="green")
```

Default ports:
- OSC output (host to QuNeOSC Bridge): 3478 — LED control, transport
- OSC input (QuNeOSC Bridge to host): 7469 — receiving QuNeo sensor data

## LED Address Map (QuNeOSC Bridge)

| Component | Address Pattern | Range |
|-----------|---------------|-------|
| Pads | /quneo/leds/pads/{0-15}/{green,red} | 0.0-1.0 |
| Rotaries | /quneo/leds/rotaries/{0-1}/{0-11} | 0.0-1.0 |
| HSliders | /quneo/leds/hSliders/{0-3}/{0-7} | 0.0-1.0 |
| VSliders | /quneo/leds/vSliders/{0-3}/{0-7} | 0.0-1.0 |
| LongSlider | /quneo/leds/longslider/{0-15} | 0.0-1.0 |
| Buttons | /quneo/leds/{upButton,downButton,leftButton,rightButton,rhombus,modeButton} | 0.0-1.0 |
| Transport | /quneo/leds/transportButtons/{0-2} | 0.0-1.0 |

## Binary Analysis Reference

For reverse-engineering QuNeOSC Bridge:
- Mac binary: ~/Downloads/QuNeOSC_v0.9_BETA/QuNeOSC_Bridge_Mac/
- Win binary: ~/Downloads/QuNeOSC_v0.9_BETA/QuNeOSC_Bridge_Win/
- Max/MSP patches: ~/Downloads/QuNeOSC_v0.9_BETA/QuNeOSC_Max_Patch/

Use strings, objdump, or ghidra to extract OSC address tables and port configs.

## TDD Approach
1. RED: Write tests for set_pad_led(), set_rotary_led(), etc.
2. GREEN: Implement using pyliblo — use Address.send() for mockability
3. REFACTOR: Add QuNeoHybrid combining MIDI SysEx + OSC LED control

## Related Repos

| Repo | Path |
|------|------|
| queneo-editor | ~/Documents/git/queneo-editor/ (Python TDD, osc_service.py) |
| node-quneo | ~/Documents/git/node-quneo/ (JS module with getPadLedsPath) |
| ofxQuNeo | ~/Documents/git/ofxQuNeo/ (openFrameworks + OSC) |
