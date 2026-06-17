# Hypno 2 — Mezzz Wireless Controller Reference

Sleepy Circuits Mezzz is a handheld Bluetooth (BLE) MIDI controller with 8 haptic push-encoder knobs, 8 knob banks per channel (1,024 CC parameters), and a built-in IMU gyroscope. Mezzz has a dedicated Hypno Emulation Mode on Channel 16 that mirrors the Hypno's UI layout for intuitive wireless control.

**Manufacturer:** [Sleepy Circuits](https://sleepycircuits.com/mezzz)
**Docs:** [docs.sleepycircuits.com/mezzz/manual](https://docs.sleepycircuits.com/mezzz/manual)
**PDF manual (V1.4):** [Dropbox link](https://www.dropbox.com/scl/fi/lnbu7nvizg67lt33c3rl4/MezzzManualV1.4.pdf?rlkey=lcjhh2zhxxlnudxayur86amof&dl=1)
**Price:** $360 USD

## Connection Setup (BLE MIDI)

Hypno 2 has built-in Bluetooth (BLE MIDI Central + Peripheral). No adapter required.

1. Hypno 2: Settings → Bluetooth → toggle ON
2. Mezzz: Power on (switch left = ON), ensure Bluetooth is enabled
3. Put Mezzz in pairing mode (advertises as BLE MIDI device)
4. Hypno 2: Accept connection popup when it appears
5. Mezzz vibrates and center LED glows white when connected

Manage connection under Settings → MIDI Devices (per-device In/Out toggles, sync enable).

> **WIDI Bud Pro alternative:** If direct Bluetooth is unreliable, plug a WIDI Bud Pro into a Hypno 2 USB-A port as a BLE MIDI bridge. Useful in crowded 2.4 GHz environments or for range issues.

## Hypno Emulation Mode (CH 16)

Mezzz Channel 16 is dedicated to Hypno control. The Mezzz UI changes to mirror the Hypno's video engine layout.

- 2 pages are "locked" on Mezzz to create a Hypno-like UI
- Tap a knob: Toggle shape/feedback modes
- Combo gesture: Toggle "Button Patch" ON/OFF

Maps directly to Hypno 2 Main track (MIDI Ch 16) — the global mixer and feedback shader.

## MIDI Channel Mapping

Use Mezzz side buttons (hold L or R) to switch MIDI channels.

### CH 16 — Main / Mixer (Hypno Emulation Mode)

| Knob Page | CC | Parameter | Description |
|-----------|-----|-----------|-------------|
| 1 | 0 | ch1 gain | Track A video level |
| 1 | 1 | feedback | Frame-to-frame feedback amount |
| 1 | 2 | ch2 gain | Track B video level |
| 2 | 3 | fb x | Feedback horizontal offset |
| 2 | 4 | fb zoom | Feedback zoom/scale |
| 2 | 5 | fb y | Feedback vertical offset |
| 3 | 6 | fb rotate | Feedback rotation angle |
| 3 | 7 | low key | Luminance keying low threshold |
| 3 | 8 | hi key | Luminance keying high threshold |

### CH 1 — Track A / CH 2 — Track B

Same CC layout as the standard MIDI CC map. See [midi-cc.md](midi-cc.md) for full parameter details. Parameters vary by loaded shader.

Mezzz knob banks offset CC index by 8 per page:

| Bank | CC Range |
|------|----------|
| 1 | CC 0–7 |
| 2 | CC 8–15 |
| 3 | CC 16–23 |
| 4 | CC 24–31 |
| ... | ... |

For Hypno 2, banks 1–3 cover the Main track (CH 16) and Track A/B (CH 1/2) parameters.

## Mezzz Hardware Controls

### Knobs (8x haptic encoders)

| Action | Function |
|--------|----------|
| Turn | Send CC value (haptic buzz on valid change; no buzz at boundary) |
| Tap | Open that knob's parameter page |
| Hold (timer) | Init patch (sends 0 on all CCs for that channel) |
| Press + Turn | Send alternate CC (offset +64 from base) — useful for mod CCs |

### Center Button

| Action | Function |
|--------|----------|
| Tap | Show map overlay (active page controls) |
| Tap (no connection) | Show battery voltage |
| Hold + Turn Knob | Access global settings |
| Hold + L/R Hold (timer) | Save user CC map (teal / magenta) |
| Hold + Tap L/R | Send program change (increment/decrement) |

### L / R Side Buttons

| Action | Function |
|--------|----------|
| Hold L or R | Change MIDI channel (dark LED = active channel #) |
| Hold L + R | Toggle gyroscope ON/OFF (center LED = red when active) |

### Gyroscope

- Center LED red: 4D rotation data sent via sysex
- Active only when Bluetooth is connected
- Map to feedback position, rotation, or any orientation-controlled parameter

## Trigger Pages (Mezzz Firmware 1.4+)

| Action | Function |
|--------|----------|
| Hold 2 neighboring encoders | Open one of 8 trigger pages (6 notes each = 48 total) |
| Tap center (in trigger page) | Lock trigger page UI (no need to hold encoders) |
| Tap center again | Unlock and return to regular knob pages |

Use trigger pages to recall Hypno 2 presets, launch clips, or play sounds chromatically.

## Program Changes and Presets

Hold center button + tap a side button to send program changes. On Hypno 2, this switches between presets stored in `VIDOS-Resources/Presets/`.

## User CC Map Save/Recall

| Action | Function |
|--------|----------|
| Center hold + L or R hold (timer) | Save user CC map (teal = L, magenta = R) |
| Hold L or R at startup | Recall saved CC map |

## Practical Workflow Tips

1. Start on CH 16 (Hypno Emulation Mode) for live mixer/feedback control — maps to Hypno's own knob layout
2. Switch to CH 1 or CH 2 to tweak individual track parameters (shader frequency, rotation, crop, color)
3. Use press+turn on any knob to access the mod CC for that parameter (CC offset +64) — set modulation depth without touching the screen
4. Use the gyroscope (hold L+R to toggle) for gestural control — tilt/rotate Mezzz to send orientation data as MIDI CCs
5. Save your Mezzz CC map for Hypno sessions: center hold + L/R hold (timer)
6. If lost, tap center button to see the map overlay

## References

- Mezzz manual: https://docs.sleepycircuits.com/mezzz/manual
- Mezzz PDF (V1.4): https://www.dropbox.com/scl/fi/lnbu7nvizg67lt33c3rl4/MezzzManualV1.4.pdf
- Video — Mezzz + Hypno wireless control: https://www.youtube.com/watch?v=BZgiaMgilzw
- Video — Mezzz connection guide: https://www.youtube.com/watch?v=XKuClE_gv1Q
- Video — Mezzz + vidOS tutorial: https://www.youtube.com/watch?v=dzWRLWQJRaw
- Blank printable Mezzz channel map: https://www.dropbox.com/scl/fi/zgb29pcgrdwez79pgohym/Blank-Mezz-Map-100.jpg
