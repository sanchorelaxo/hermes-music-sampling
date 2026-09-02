# QuNeo Empirical LED Mapping (webcam-validated)

Hardware-verified findings from video-recorded sweep tests (Sept 2026).
Method: record webcam while sweeping MIDI messages, diff frames per event,
classify lit blobs by color and position. Human-confirmed alongside.

## Test Rig
- Webcam: Razer Kiyo Pro /dev/video2, MJPEG 1920x1080 → scale 960x540 for analysis
  (watch for Cheese or other apps stealing the camera — causes silent failures)
- MIDI out: raw writes to /dev/snd/midiC1D0 (ALSA hw port; client number changes
  across reboots — check with `amidi -l`; was hw:1,0,0 / client 24 earlier)
- Recorder: ffmpeg `-f v4l2 -input_format mjpeg ... -vf scale=960:540,fps=10 -c:v libx264 -preset ultrafast`
- Timing that works: 0.45s note on, 0.15s gap, clear all notes/CCs between events
- LED response is NOT latched for note-on in grid mode: clears on note-off / clear sweep

## 540p Calibrated Regions (grid orientation: image r0 = TOP row = pads 13-16)
- Pad columns x: c0=362-437, c1=457-535, c2=557-636, c3=658-737
- Pad rows y: r0=36-104, r1=121-193, r2=212-287, r3=307-384
- Physical pad# = (3-r)*4 + c + 1 (pad1 = bottom-left, pad16 = top-right)
- User convention: pad1 bottom-left, rows bottom→up numbered 1-16

## Empirical Results (Grid Mode presets 4/5, slots active on device)

### Preset 5 (Grid Mode Ch.3) — comprehensive sweep (notes 0-127, CC 0-31, ch 0/1/2)
Confirmed by whole-frame video analysis + human observation:

**Channel 0** (2 notes per pad, sequential pairs — green):
- pads 1-4: notes 2-9; pads 5-8: 10-17; pads 9-12: 18-25; pads 13-16: 26-33
- Buttons (from JSON + confirmed hits): transport 24-26, up/down 20-21(U/D per pair), left/right 11-18, rhombus 19
- Slider CCs: HSlider 0-3, Rotary 4-5, VSlider 6-9, LongSlider 10(loc)/11(width) — LEDs require ~50ms refresh to hold
- Non-pad button notes 0-9 lit HSlider/VSlider/slider-adjacent LEDs green

**Channel 1** (4 consecutive notes per pad = 4 corners — green; RED on specific notes):
- pad1: 18-21, pad2: 22-25, pad3: 26-29, pad4: 30-33
- pad5: 50-53, pad6: 54-57, pad7: 58-61, pad8: 62-65
- pad9: 82-85, pad10: 86-89, pad11: 90-93, pad12: 94-97
- pad13: 114-117, pad14: 118-121, pad15: 122-125, pad16: 126-127 + cc0/cc1

**Channel 2** (sparse reds + weak greens; red hits):
- 21→pads1/2, 41→pad3, 55→pad6, 75→pad7, 95→pad12, 115→pads13/14, 121→pad15
- evens 82-96→pads 9-12, evens 104-126→pads 13-16 (weak green)

**Color rules observed:**
- Green = default Note On response (velocity 127)
- Red = specific notes (likely inDmNoteR/red-note assignments per preset JSON), NOT velocity-driven
- Orange = intermediate (needs more testing with mid velocities; user requested mid-range sweep)
- Unlit "pauses" during sweeps = messages the preset ignores (no dead time in event log)

### Preset 4 (Grid Mode Ch.2) — expected-vs-observed MISMATCH
JSON says pads ch1, corner notes 0-63 (Pad0: SW=0 SE=1 NW=8 NE=9, +2/+8 per pad).
Observed behavior instead matched Preset 5's layout (ch1 notes 50-65 → pads 5-8 etc).
⇒ Either the dataPreset4.syx + loadPreset4.syx load didn't take effect, or firmware
slot-4 LED behavior differs from its JSON. TODO: verify preset load with a
distinguishing test (e.g. send ch2 note 0 — lights pad1 on P5 layout).

## JSON-ingestion tool
`scripts/led_sweep.py` — preset-agnostic pipeline:
- `--expected-only` prints JSON-derived map for any slot
- full run: sweep (recorded) → one-pass frame extraction (`ffmpeg fps=10` to PNGs)
  → blob diff analysis → classify by region → expected-vs-observed compare
- Frame extraction must be one ffmpeg pass (per-frame `select=eq(n)` spawns are
  ~10x too slow for 480-event videos)

## Open items
- Mid-range velocity sweep (orange zones on pads, half-value sliders)
- Rhombus half-position test (user: "rhombus lit at 6pm clockwise (bottom)")
- Cross-fader (LongSlider width CC 11) extensive testing
- Button zones (transport/updown/rhombus/vslider regions in BUTTON_ZONES) need
  precise calibration — current coarse zones misclassify some blobs
- Verify preset-load reliability (amidi -s dataPresetN.syx + loadPresetN.syx)
