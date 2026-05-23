# Hypno 2 — Modulation Sources Reference

Each parameter has a modulation page (tap parameter label). Available sources:

## Internal LFO

| Control | Encoder | Description |
|---------|---------|-------------|
| gain | Left | Modulation amplitude (bipolar) |
| func | Center | Waveform selector |
| freq | Right | LFO speed |

**14 waveforms:** Sin, Cos, Tri, Ramp, Tan, Rnd, Pulse, Exp, Log, StpRnd, Bounce, Chaos, Heart, Pend

## Audio Input (AUX / Mic)

| Page | Controls |
|------|----------|
| Page 1 | gain (depth, bipolar), smooth (slew rate, 0–1) |
| Page 2 | LOW band gain, MID band gain, HIGH band gain |

Built-in mic used when no jack in AUX input.

## CV Input (4 jacks)

| Control | Description |
|---------|-------------|
| gain | Modulation depth from selected CV jack |
| smooth | Input smoothing (noise/jitter reduction) |
| CV 1–4 | Select by tapping CV badge — 0–5 V unipolar Eurorack |

## MIDI CC

| Control | Description |
|---------|-------------|
| gain | Modulation depth (bipolar) |
| smooth | Input smoothing (0–1) |
| cc# | Remap CC number (0–127), independent of default |

## Clock / BPM Sync

| Control | Description |
|---------|-------------|
| source | OFF, BPM (internal), CLK1 (trigger 1), CLK2 (trigger 2) |
| division | 1/32, 1/16, 1/8, 1/4, 1/2, 1/1, 2×, 4×, 8×, 16× |
| re-trig | ON/OFF — resets LFO phase on each clock pulse |

## Audio Track (uses channel audio as modulation)

| Page | Controls |
|------|----------|
| Page 1 | gain (depth), smooth (slew) |
| Page 2 | LOW band, MID band, HIGH band gain |