# Hypno 2 — MIDI CC Map Reference

## Main / Master (MIDI Ch 16)

| CC | Parameter | Description |
|----|-----------|-------------|
| 0 | ch1 gain | Track A video level |
| 1 | feedback | Frame-to-frame feedback amount |
| 2 | ch2 gain | Track B video level |
| 3 | fb x | Feedback horizontal offset |
| 4 | fb zoom | Feedback zoom/scale |
| 5 | fb y | Feedback vertical offset |
| 6 | fb rotate | Feedback rotation angle |
| 7 | low key | Luminance keying low threshold (darker pixels keyed out) |
| 8 | hi key | Luminance keying high threshold (brighter pixels keyed out) |

## Track A (MIDI Ch 1) & Track B (MIDI Ch 2)

Parameters vary by loaded shader. Common defaults:

| CC | Parameter | Description |
|----|-----------|-------------|
| 0 | x offset | Horizontal position |
| 1 | frequency | Animation speed |
| 2 | y offset | Vertical position |
| 3 | x crop min / fold axis | Horizontal crop left (shader-dependent) |
| 4 | rotation | Rotation angle |
| 5 | x crop max / fold shape | Horizontal crop right (shader-dependent) |
| 6 | y crop min / aspect x | Vertical crop top (shader-dependent) |
| 7 | polarization | Polarization amount (shader-dependent) |
| 8 | y crop max / aspect y | Vertical crop bottom (shader-dependent) |
| 9 | aspect x / luma min | Horizontal stretch (shader-dependent) |
| 10 | --- | Unassigned (shader-dependent) |
| 11 | aspect y / luma max | Vertical stretch (shader-dependent) |
| 12 | mirror amt | Mirror effect intensity |
| 13 | mirror rot | Mirror axis rotation |
| 14 | --- | Unassigned |
| 15 | luma min | Luminance low threshold |
| 16 | polarization | Polarization amount |
| 17 | luma max | Luminance high threshold |
| 18–59 | (shader-dependent) | Additional shader parameters |
| 60 | --- | Unassigned |
| 61 | cross mod | Cross-channel modulation amount |
| 62 | fb mod amt | Feedback modulation depth |
| 63 | hue | OKLab hue shift |
| 64 | chrominance | OKLab color saturation |
| 65 | lightness | OKLab brightness |
| 66–127 | mod CC 0–61 | Modulation LFO control (mod CC = base CC + 66) |

> **Sampler shader note:** When a Sampler shader is loaded with multi-frame video, CCs 0–2 are reserved for loop in, framerate, and loop out. Shader parameters start at CC 3.

## MIDI Notes

| MIDI Channel | Note Function |
|-------------|---------------|
| Ch 1–2 | Chromatic video playback — each note shifts pitch/speed (middle C = normal) |
| Ch 3–16 | Preset save/load — short press loads, long hold saves to note slot |