# OP-1 — Synthesizer Engine Reference

Access: **SHIFT + T1** → blue encoder scrolls engines → any key confirms.

## 13 Synth Engines

| Engine | Type | Key Parameters |
|--------|------|---------------|
| **Cluster** | Multi-layered oscillator cluster | Number of waves (0–6), wave envelope, spread |
| **Digital** | True digital synthesis, ring mod | Wave shaper, octave, detune, digitalness |
| **String** | Waveguide string model | Tension, impulse decay, detune, impulse type |
| **Pulse** | Dual pulsetrain oscillator + FM | Filter, amplitude, second pulse mod |
| **FM** | 4-operator FM synthesis | FM amount, freq, topology, detune |
| **Phase** | Phase distortion | Phase shift, distortion amount, phase filter, tilt, drive wave |
| **Synth Sampler** | Teenage sample player | Start, loop in/out, end, reverse, fine tune, gain |
| **D-Box** | Drum synthesizer | Pitch, waveform, envelope, cross mod |
| **D-Synth** | Multi-envelope dual oscillator | Voltage, waveform, envelope, cross mod |
| **Drum Sampler** | Teenage percussion player | Note/pitch, in/out, loop off/once/reverse, gain |
| **6 Operator** | Multi oscillator electric synthesis | Ampere modulation, induction w/shaper, phase filter, voltage detune |
| **DNA** | CPU ID Noise synthesis | Filter, wave number, wave modifier, noise |
| **CWO** | Pitch shifting delay | Frequency, delay, feedback, sideband |

## Synth Controls (per voice)

| Parameter | Control | Secondary (SHIFT+) |
|-----------|---------|-------------------|
| Envelope | Orange encoder | Attack, decay, sustain, release via envelope screen |
| Playmode | Green encoder | LFO sync, retrig types |
| Effect | White encoder | 8 built-in effects (delay, grid, nitro, spring, telematic, punch, power, cwo) |
| LFO | Blue encoder (after pressing LFO key) | 8 LFO types: Element, Random, Tremolo, Value, MIDI, Crank, Bend, Free |

## Saving a Sound

1. Hold **SHIFT + T1** (synth engine screen) — long press saves
2. **Blue encoder** → select slot (1–8 per category)
3. Release all keys — sound is saved