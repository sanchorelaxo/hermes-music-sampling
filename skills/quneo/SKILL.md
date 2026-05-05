---
name: quneo
description: Keith McMillen QuNeo 3D multi-touch MIDI controller skills — SysEx preset management, LED mapping, and OSC integration
category: quneo
---

# QuNeo Skills

Keith McMillen QuNeo 3D multi-touch pad controller skills for Linux.

## Related Repos

| Repo | Path | Purpose |
|------|------|---------|
| quneo-linux | ~/Documents/git/quneo-linux/ | Python SysEx encoder, factory presets |
| quneo-node | ~/Documents/git/quneo-node/ | Node.js CLI (monitor, flash, dump, watch) |
| queneo-editor | ~/Documents/git/queneo-editor/ | Python TDD editor, data models, SysEx |
| node-quneo | ~/Documents/git/node-quneo/ | Node.js module for OSC LED paths |
| ofxQuNeo | ~/Documents/git/ofxQuNeo/ | openFrameworks addon + OSC preset |

## Skills

| Skill | Description |
|-------|-------------|
| [quneo-controller](quneo-controller/) | Device setup, SysEx preset loading, Linux MIDI, reload command |
| [quneo-led-mapping](quneo-led-mapping/) | CC-based vs Note On-based LED control, preset verification |
| [quneo-osc-integration](quneo-osc-integration/) | OSC LED control, QuNeOSC Bridge, pyliblo implementation |
