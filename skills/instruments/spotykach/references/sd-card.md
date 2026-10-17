# Spotykach — SD Card & config.txt Reference

## Storage Model

Storage is shared between decks. The root of everything Spotykach is the **`SK`** folder on the card. Files are grouped into 6 folders called **tapes**, each holding up to 6 **tracks** (36 tracks total).

| Tape | Folder | Color |
|------|--------|-------|
| Blue | `B` | Blue |
| Green | `G` | Green |
| Pink | `P` | Pink |
| Red | `R` | Red |
| Turquoise | `T` | Turquoise |
| Yellow | `Y` | Yellow |

Audio files have numeric names: `1.WAV` … `6.WAV`. Format is **32-bit float, 48kHz, stereo WAV**.

**⚠️ Lower volumes after loading files.**

- Card must be inserted **before** powering up to be recognized.
- Tested up to 32GB FAT32; larger may work but is untested.

## Navigating

1. Hold **tap** + tap the **play** pad of the deck to enter SD-card mode. The ring shows 6 segments in the current tape's color (default blue).
2. Switch tapes with the **trig** pad (last tape remembered until power-off).
3. Select a file with the **pitch** knob — bright segment = existing file, dim = empty, white = selected.

## Save / Load / Cancel

| Action | Keys | Ring feedback |
|--------|------|---------------|
| Save audio | **alt + play** | Progress in white (overwrites occupied slots) |
| Load audio | **play** or **alt + reverse** | Progress in tape color |
| Exit / cancel | **tap + play** | — |

## Importing Audio

Place a correctly-named file (`1.WAV`–`6.WAV`) in a tape folder (`B`/`G`/`P`/`R`/`T`/`Y`) under `SK/`; Spotykach will load it. Create the folder structure manually if it doesn't exist yet (Spotykach creates it on first save).

The file must match Spotykach's internal format: **32-bit float, 48kHz, stereo WAV**.

> ⚠️ **Format tag matters.** The WAV `fmt` chunk's format tag must be plain
> **IEEE float (`0x0003`)**, not `WAVE_FORMAT_EXTENSIBLE` (`0xFFFE`). ffmpeg's
> default float output uses `0xFFFE` plus a `fact` chunk, which the Spotykach's
> loader does not read — the load fails silently (the deck ring shows its
> normal mode color instead of tape-color loading progress). Use the
> `wav_builder.py convert` command, which writes the correct plain-float header.

- Files shorter than 42s → file length becomes the max loop size.
- Files longer than 42s → only the first 42 seconds are loaded.

## Pre-loading

Spotykach remembers the last tape+slot and pre-loads it on next power-on. Cancel a slow pre-load with **tap + deck play** (also discards pre-load info). Pre-load info is stored in the `MEM` file in the `SK` folder. Disable globally via `pre_load` in config.txt.

## config.txt

Some behaviors are configured via a `config.txt` file in the root of the `SK` folder. Settings are plain text: setting name (alphanumeric + underscore) followed by its numeric value on the next line.

```
mid_ch_b
5

mid_ps_a
1
```

| Setting | Description | Values | Default |
|---------|-------------|--------|---------|
| `mid_ch_a` | Deck A MIDI channel | 1–16 | 1 |
| `mid_ch_b` | Deck B MIDI channel | 1–16 | 2 |
| `mid_ps_a` | Start/Stop Deck A from MIDI | 0 / 1 | 0 |
| `mid_ps_b` | Start/Stop Deck B from MIDI | 0 / 1 | 0 |
| `pre_load` | Enable/disable pre-loading | 0 / 1 | 1 |
| `slc_mn_a` | Disable polyphony in Slice mode (Deck A) | 0 / 1 | 0 |
| `slc_mn_b` | Disable polyphony in Slice mode (Deck B) | 0 / 1 | 0 |

## WAV.builder Web App

A third-party web app (by Jon Waterschoot) for managing Spotykach samples — converts audio to the correct format, maintains folder structure, and offers a basic editor (trim, normalize, fades, automation, seamless looping). Still in heavy development; use with caution.

https://jonwaterschoot.github.io/spotykach_WAV_builder/
