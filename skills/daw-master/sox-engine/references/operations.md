# SoX Engine — Operations Reference

Full parameter details for every SoX operation. All ops are passed via `sox-engine.transform(pipeline=[...])`.

## Gain & Level

`gain {amount}` — Apply linear gain or dB adjustment.
- Param `amount`: float. `0.5` = half amplitude, `2.0` ≈ +6dB, `-3` = -3dB
- Alias: `volume`

`norm [-p peak] [{dc}]` — Normalize to peak level.
- Param `peak`: target peak in dBFS (default `-0.1`). Use `-1` for true 0 dBFS.
- Param `dc`: if true, remove DC offset first

**Examples:**
```python
{"op": "gain", "amount": 0.8}        # attenuate 20%
{"op": "gain", "amount": 3.0}        # ~+9.5 dB
{"op": "normalize", "peak": -0.1}
```

## Editing & Manipulation

`trim {start} [length]` — Extract segment.
- Param `start`: start time in seconds (float)
- Param `length` or `end`: duration or end time in seconds

`fade {type} {length}` — Fade in/out.
- Param `type`: `"in"`, `"out"`, `"in-out"` (both)
- Param `length`: fade duration in seconds

`pad {silence}` — Prepend silence.
- Param `silence`: seconds to add at beginning

`reverse` — Reverse entire audio. No parameters.

**Examples:**
```python
{"op": "trim", "start": 10.5, "end": 45.0}
{"op": "fade", "type": "in", "length": 0.3}
{"op": "fade", "type": "out", "length": 2.0}
{"op": "pad", "silence": 1.5}
{"op": "reverse"}
```

## Channels & Sample Rate

`channels {count}` — Convert channel count.
- Param `count`: integer (1=mono, 2=stereo, etc.)

`rate {sample_rate}` — Resample.
- Param `sample_rate`: e.g. `44100`, `48000`, `22050`

`remix -m {gain} ...` — Remix/mix down channels.
- Param `mixing`: boolean, for downmixing to mono

**Examples:**
```python
{"op": "channels", "count": 1}
{"op": "channels", "count": 2}
{"op": "rate", "sample_rate": 44100}
```

## Effects

`compand attack1:decay1{,attack2:decay2} [soft-knee-dB:]in-dB[,out-dB]` — Compressor/expander.
- Params: `attack`, `decay`: times as `"0.01:0.1"` string
- Param `threshold_in`: input threshold dB
- Param `threshold_out`: output threshold dB
- Param `soft_knee`: soft-knee width dB

`equalizer frequency[{=|+|-|/}width[k|o|q]] [gain[dB]]` — Parametric EQ.
- Params: `frequency` (Hz), `width` (Hz or `q` factor), `gain` (dB)

`bass {gain}` — Boost/cut bass.
- Param `gain`: dB (e.g., `10` or `-5`)

`treble {gain}` — Boost/cut treble.
- Param `gain`: dB

`echo gain-out:in-gain [delay]` — Simple echo/delay.
- Params: `gain_in`, `gain_out`, `delay` (seconds)

`reverb {wet}` — Algorithmic reverb.
- Param `wet`: wet/dry mix (0.0–1.0, typically 0.3)

**Examples:**
```python
{"op": "compand", "attack": "0.01:0.1", "threshold_in": -20, "threshold_out": -10}
{"op": "equalizer", "frequency": 1000, "width": "2q", "gain": 3}
{"op": "bass", "gain": 6}
{"op": "treble", "gain": -2}
{"op": "echo", "gain_in": 0.4, "gain_out": 0.4, "delay": 0.3}
{"op": "reverb", "wet": 0.3}
```

## Analysis (Read-Only)

`stats` — Print sample statistics. Returns: `min`, `max`, `mid`, `rms`, `rms_peak`, `rms_trough`.

`stat -freq {Hz}` — Get amplitude at specific frequency.

`spectrogram` — Generate spectrogram PNG (use `analyze` mode, not pipeline).

## Raw Effects (Full SoX Power)

Pass any raw SoX effect string:

```python
{"op": "raw_effect", "effect": "phaser"}
{"op": "raw_effect", "effect": "flanger 75 5"}
{"op": "raw_effect", "effect": "highpass 80"}
{"op": "raw_effect", "effect": "lowpass 12000"}
{"op": "raw_effect", "effect": "bandpass 500 2q"}
```

Common raw effects:
- `highpass {freq}` — HPF
- `lowpass {freq}` — LPF
- `bandpass {freq} {width}` — BPF
- `noisered {profile} {strength}` — Noise reduction (requires profile file)