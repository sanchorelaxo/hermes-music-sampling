---
name: quneo
description: Keith McMillen QuNeo 3D multi-touch MIDI controller skills — SysEx preset management, LED mapping, and OSC integration
category: quneo
---

# QuNeo Skills

Keith McMillen QuNeo 3D multi-touch pad controller skills for Linux.

## Official Reference (Authoritative)

The **official** Muse-Kinetics source is the authority and supersedes the
reverse-engineered ("learned") content in this directory wherever they differ.

- **Official editor repo:** `~/Documents/git/quneo-qt6-editor/`
  (https://github.com/Muse-Kinetics/quneo-qt6-editor) — Linux-capable Qt6 fork of
  the KMI QuNeo Editor. Native Linux build (no Wine). `bash install.sh` to build.
- **Official protocol reference:** `/home/rjodouin/.hermes/skills/music/midi-controller/references/QuNeo_Official_Protocol.md`
- **Authoritative SysEx facts:** PRESET_LENGTH = **1279** (not 1515); header
  `F0 00 01 5F 7A 1E 00`; product ID 0x1E (30); 7-bit encoder `SX_ENCODE_LEN=7`
  with automatic high-bits-byte emission; 16-bit KMI CRC init `0xFFFF` high-byte-first;
  load-preset command is 7-bit+CRC encoded (not the raw 20-byte Bome form).
- **Current versions:** Editor 2.0.4, Firmware 1.2.31 (firmware ships in
  `Content/SysEx/Quneo_Firmware_v1.2.31.syx`).
- **KMI v2 Windows editor under Wine is NOT needed** on Linux — use the native Qt6 build.

## Related Repos

| Repo | Path | Purpose |
|------|------|---------|
| quneo-qt6-editor | ~/Documents/git/quneo-qt6-editor/ | **Official** Qt6 editor (authoritative source) |
| quneo-linux | ~/Documents/git/quneo-linux/ | Python SysEx encoder, factory presets (learned) |
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
