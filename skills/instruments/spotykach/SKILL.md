---
name: "spotykach"
description: "Use when working with the Synthux Spotykach — a screenless dual-deck looper/sampler with Reel (tape), Slice (clocked sampler) and Drift (granular) modes, per-deck trigger sequencer, grit/flux effects, Eurorack-compatible CV/Gate I/O, MIDI, and SD-card tape storage."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["instrument", "looper", "sampler", "granular", "synthux", "eurorack", "cv", "midi", "sd-card"]
    related_skills: []
---

# Synthux Spotykach — Looping Playground

**Manufacturer:** [Synthux](https://synthux.academy) (Roey Tsemah & Vlad Litvinenko)  \
**Manual:** https://tsemah.notion.site/Spotykach-Manual-22c6331933b880c59108c0de25102bb5

Spotykach is a screenless, dual-deck looper built for hands-on sound exploration. Two recording decks (A and B), each with its own transport, effects, and trigger sequencer. The word "spotykach" is Ukrainian for "something that makes one stumble."

## Hardware

| Spec | Value |
|------|-------|
| Decks | 2 (A and B), independent loopers |
| Deck modes | Reel (tape), Slice (clocked sampler), Drift (granular) |
| Max loop | 42 seconds per deck |
| Audio in | 2× mono (up to ~10Vpp / −5V to +5V), shunt-protected |
| Audio out | 2× mono + stereo headphones (TRS only) |
| CV/Gate in | Eurorack-compatible (tolerates full Eurorack range) |
| CV/Gate out | 0 to +5V |
| MIDI | TRS Type A In/Out + USB |
| Power | USB-C (5V 1A) and/or 15V 1A center-positive barrel (5.5mm/2.5mm) |
| Storage | microSD (up to 32GB FAT32 tested) |

**Power notes:**
- USB-C **and** 15V barrel can be powered at the same time (safe).
- Powering via a *computer's* USB port can cause a high-pitched ground-loop whine — use a standalone USB adapter instead.
- There is **no on/off switch** (a hardware switch would require a PCB redesign).

**Reset button (back):** short press = reboot · long press = firmware-update mode.

**⚠️ Headphones out is stereo TRS only — do not use a TS mono cable.**

## When to Use

- Recording and looping audio with hands-on, no-menu interaction
- Tape-style speed/pitch manipulation (Reel), clocked time-stretch (Slice), or granular textures (Drift)
- Resampling one deck into the other for layered builds
- Step-triggering deck playback with the per-deck trigger sequencer
- Using Spotykach as a real-time distortion / delay / stutter effect (effects process live input too)
- Integrating with Eurorack via CV/Gate, or as a 4PPQN↔24PPQN clock converter

## Deck Modes

Each deck can be in one of three modes (color shown on the deck's LED ring):

| Mode | Color | Character |
|------|-------|-----------|
| **Reel** | Yellow/Amber | Monophonic tape — speed and pitch are linked |
| **Slice** | Blue | Clocked sampler/looper — pitch independent of speed (time-stretch/pitch-shift). Polyphonic by default (3 voices/deck); mono/poly via **alt+size** |
| **Drift** | Purple | Granular generator — multiple grains stretch micro-movements into texture |

## Playback & Triggering

- Tap **play** or **reverse** to toggle loop playback in that direction. Tapping the active pad stops; tapping the opposite pad switches direction.
- **trig** pad = one-shot pass. Behavior by mode:
  - **Reel:** re-triggers playback from the start.
  - **Slice mono** (alt+size full CCW): re-triggers. **Slice poly** (alt+size full CW): triggers up to 3 voices (voice stealing).
  - **Drift:** if **envelope** is full CCW (suspended), trig is ignored — start/stop only via play/reverse. If envelope is above CCW, trig re-triggers the envelope.

## Recording

- **Arm:** tap **alt + play** (play LED blinks red).
- **Reel / Drift:** recording starts automatically when input crosses −40dB; tap **play** to stop and immediately begin loop playback. Ensure input levels are high enough for the detector.
- **Slice:** recording is quantized — starts on the next Key Beat after arming, stops on the next Key Beat after tapping play/reverse.
- **Overdub:** while a deck is playing, tap **alt + play**; control feedback (loop decay) with **alt + mix**. During overdub the record head stays on a fixed loop (unaffected by pos/size/speed knobs); the playhead stays interactive and changes are non-destructive.
- **Looper-pedal setup:** pitch/speed to 1× (center), pos + envelope to zero, size to maximum.
- **Deck-to-deck resampling:** tap **alt + reverse** (records the other deck's output). A↔B simultaneously is possible.

## Deck Controls

Most knobs are multifunction; a **visual catch-up** system prevents jumps — a red LED-ring segment shows when the physical knob position differs from the stored value. Turn until the red segment disappears to take control.

| Knob | Reel | Slice | Drift | Alt function |
|------|------|-------|-------|--------------|
| **Pitch/Speed** | Speed+pitch (CW=faster) | Pitch only (pitch shift) | Like Reel (subtler) | Quantized pitch: −2oct, −1oct, −5th, 0, +5th, +1oct, +2oct |
| **Position** | Loop start | Loop start (quantized to 1/8) | Middle of the grain cloud | — |
| **Size** | Loop length (exponential) | Loop length (rounded to 16ths, linear) | Grain spread (linear) | Grain size |
| **Envelope** | Loop fade in/out | Loop fade in/out | 0 = suspended drone state | Envelope length |
| **Mix** | Input↔buffer balance | Input↔buffer balance | Input↔buffer balance | Overdub feedback |

**Position/size CV switch:** Up = CV controls position · Down = CV controls size · Center = CV controls both.

## Modulation Sources

Two internal sources (A and B), patchable via output jacks. Each has two LFO waveforms + an envelope follower.

| Source | LFO waveforms |
|--------|---------------|
| A | Sample & Hold, Square |
| B | Sine, Sawtooth |

- **cycle** knob = LFO frequency; **alt + cycle** = clock-synced (1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 3, 4 bars).
- **glow** knob = attenuator.
- **Envelope follower:** listens to the same-named deck's output *after* the mix knob. **cycle** controls attack/release, **glow** compensates quiet sources.

**CV inputs:** position/size · gate in (like trig) · mix · v·oct (pitch/speed) · a/b fader.

## Effects

Effects sit on the **grit** and **flux** pads and process **both** live input and recorded audio (usable as real-time FX without recording).

- **Hold** an effect pad = effect active while held. **alt + effect** = latch toggle. **Hold pad + tap "tap" button** = switch effect type (ring color changes).
- While holding, the deck ring glows in the effect color; adjust params with **pitch / mix / pos** knobs.

| Pad | Effects |
|-----|---------|
| **Grit** (texture) | Distortion (yellow, analog saturation), Bit crusher (orange, digital) |
| **Flux** (time) | Tape delay (pink) |

- Grit: **pitch** = intensity (L soft → R harsh), **mix** = effect mix.
- Flux (tape delay): **pitch** = tape speed, **mix** = delay mix, **pos** = feedback.

## Trigger Sequencer

Each deck has a 1/16th-resolution trigger sequencer (works in all three modes; sequence shared across modes). When a sequence is recorded, playback starts on the next Key Beat in all modes.

- **Record:** tap **alt + trig** (alt LED blinks white to the clock). Starts on the Key Beat (or on the first trig tap if pre-count is sub-quarter and the ring glows). Tap **trig** to the rhythm; tap **alt** or **play** to stop.
- **Delete:** hold **alt + sequence pad** for 2s (play LED blinks quickly).

## Clock, Tempo, Metronome

The clock (always running once powered) drives Slice-mode playback/recording and the sequencer.

- **Tempo** (internal clock only, 20–250 BPM): tap **tap** button · or hold **tap** + turn **cycle A** · or (Slice, sample loaded) hold **tap** + turn the deck's **size** knob — ring shows dots, one per quarter note (each 4th dot white); pick e.g. 8 dots for a 2-bar loop.
- **Key Beat / launch quantization:** hold **tap** + turn **mix A**. 1 white dot = every quarter (default); white + colored dots = longer interval (1 white + 3 color = every 4/4 bar); fully CCW = 1/16th subdivision (no Key Beat).
- **Metronome volume:** hold **tap** + turn **glow A**.

### External clock

Expects **4PPQN** at the TS (clock) input, **24PPQN** on MIDI. Cycle sources with **tap + alt** repeatedly — clock LED color: green = internal · pink = TRS · turquoise = MIDI.

- **Reset clock:** hold **tap** + tap **trig A** (aligns internal/external beats).
- Spotykach can convert 4PPQN Eurorack clock ↔ 24PPQN MIDI clock.

## MIDI

Sends and receives MIDI over USB and TRS. Syncs to 24PPQN MIDI Clock and sends clock continuously. Deck A = channel 1, Deck B = channel 2 (configurable). Notes are relative to C4 (60) — tune samples to C for in-tune playback.

Full CC implementation chart: [references/midi-cc.md](mdc:references/midi-cc.md)

## SD Card

Tape-based storage (6 tapes × 6 tracks = 36 slots), 32-bit float 48kHz stereo WAV. Files live under the `SK` folder; tapes are B/G/P/R/T/Y (blue/green/pink/red/turquoise/yellow).

Full navigation, import, pre-loading and config.txt reference: [references/sd-card.md](mdc:references/sd-card.md)

## Firmware

Latest: **v1.4.0 beta 2** (adds USB file transfer) · stable: v1.3.1. A Daisy device doesn't expose its installed version over USB, so confirming "latest" means flashing it and verifying the unit boots into normal (MIDI) mode. The bootloader is fail-safe — a bad flash just leaves it in DFU mode.

Flash on Linux with `dfu-util` (QSPI address `0x90040000`; a udev rule grants userspace access). Full procedure, bootloader entry, and verification: [references/firmware.md](mdc:references/firmware.md)

## WAV.builder Automation

Getting sounds onto the card is deterministic and can be automated headlessly. The script `scripts/wav_builder.py` (in this skill's directory) reproduces the file pipeline of the [WAV.builder webapp](https://jonwaterschoot.github.io/spotykach_WAV_builder/) — conversion to the native format, the `SK/` folder layout, and `config.txt` — so it runs from the CLI and is covered by tests. It uses ffmpeg/ffprobe, no mocks.

```bash
# convert any file to 32-bit float / 48 kHz / stereo WAV
python3 scripts/wav_builder.py convert input.wav output.WAV

# place a file into a tape/track slot (builds the SK/ tree under the mount)
python3 scripts/wav_builder.py build-card --file input.wav --tape B --track 1 -o /media/$USER/SD

# write SK/config.txt (omitted keys keep device defaults)
python3 scripts/wav_builder.py write-config --mid-ch-b 5 --pre-load 0 -o /media/$USER/SD

# report whether a file already matches the native format
python3 scripts/wav_builder.py validate file.WAV
```

Tape letters map to colors (B blue, G green, P pink, R red, T turquoise, Y yellow); tracks are 1–6. `write-config` validates keys and ranges (MIDI channels 1–16, flags 0/1) and rejects unknown settings.

**When to use the browser app instead:** the webapp is still the right tool for the *interactive* waveform editor (trim/fade/EQ/pitch/slice), the curated sample packs, and the beta USB transfer. This script covers the deterministic file-layout half; the app covers hands-on editing.

**Tests:** `tests/test_spotykach_wav_builder.py` (repo root) runs real ffmpeg/ffprobe and asserts the native format, the tape/track tree, and the `config.txt` layout:

```bash
pytest tests/test_spotykach_wav_builder.py
```

## Resources

| Document | Source |
|----------|--------|
| Manual (digital) | https://tsemah.notion.site/Spotykach-Manual-22c6331933b880c59108c0de25102bb5 |
| Firmware | https://tsemah.notion.site/p/Spotykach-Firmware-2396331933b880d89f04f61ecf0f58e6 |
| Firmware releases | https://github.com/Synthux-Academy/Spotykach/releases |
| WAV.builder (sample manager) | https://jonwaterschoot.github.io/spotykach_WAV_builder/ |
