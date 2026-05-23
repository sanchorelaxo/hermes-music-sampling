# SP-404 MK2 — MFX (Multi-Effects) Reference

Selected via **MFX button** (hold + turn VALUE or CTRL 3 knob). **SHIFT + DJFX LOOPER** for #17–32, **SHIFT + ISOLATOR** for #33+.

## Filter/Distortion

| # | Name | Type | Parameters |
|---|------|------|------------|
| 1 | **Filter+Drive** | HPF/LPF + overdrive | CUTOFF (20–16000Hz), RESONANCE (0–100), DRIVE (0–100), FLT TYPE (HPF/LPF), LOW FREQ, LOW GAIN |
| 2 | **Resonator** | Karplus-Strong physical model | ROOT (C1–G9), BRIGHT (0–100), FEEDBACK (0–99%), CHORD (Root/Oct/UpDn/P5/m3/m5/m7/m7oct/m0/M3/M5/M7/M7oct/M9/M11), PANNING, ENV MOD |
| 3 | **Sync Delay** | Tempo-synced echo | TIME (1/32–1/1 bars + dotted/triplet), FEEDBACK (0–99%), LEVEL, L DAMP F (FLAT/80–10000Hz), H DAMP F (630–12500Hz/FLAT) |
| 4 | **Isolator** | 3-band kill | LOW, MID, HIGH (-INF to +12dB) |
| 5 | **DJFX Looper** | Turntable loop | LENGTH (0.230–0.012s), SPEED (-100–100, negative=reverse), LOOP SW (OFF/ON) |
| 6 | **Scatter** | Stepped loop direction/gate | TYPE (1–10), DEPTH, SCATTER (ON/OFF), SPEED (SINGLE/DOUBLE) |
| 7 | **Downer** | Pitch-linked slowdown | DEPTH (0–100), RATE (1/32–2 bars), FILTER (ON=restore pitch), RESONANCE |
| 8 | **Ha-Dou** | Wave-generation | MOD, DEPTH, TIME, LEVEL, LOW CUT, HIGH CUT, PRE DELAY |
| 9 | **Ko-Da-Ma** | Reverb | TIME (1/32–1/1 bars), FEEDBACK, SEND, L DAMP F, H DAMP F, MODE (SINGLE/PAN) |
| 10 | **Zan-Zou** | Negative-phase delay | TIME, FEEDBACK, HF DAMP, LEVEL, MODE (2TAP/3TAP/4TAP), SYNC (OFF/ON) |
| 11 | **To-Gu-Ro** | Undulating slowdown | DEPTH, RATE, RESONANCE, FLT MOD, AMP MOD, SYNC |
| 12 | **SBF** | Sideband filter | INTERVAL (0–100), WIDTH (0–100), BALANCE (100-0-100), TYPE (SBF1–SBF6), GAIN |
| 13 | **Stopper** | Turntable stop | DEPTH, RATE, RESONANCE, FLT MOD, AMP MOD |
| 14 | **Tape Echo** | Roland RE-201 Space Echo sim | TIME (10–800ms), FEEDBACK, LEVEL, MODE (S/M/L/S+M/S+L/S+M+L), W/F RATE, W/F DEPTH |
| 15 | **TimeCtrlDly** | Smooth delay | TIME, FEEDBACK, LEVEL, L DAMP F, H DAMP F, SYNC |
| 16 | **Super Filter** | Cyclic cutoff filter | CUTOFF (0–100), RESONANCE, FLT TYPE (LPF/BPF/HPF), DEPTH, RATE, SYNC |
| 17 | **WrmSaturator** | Warm saturator | DRIVE (0–48dB), Eq LOW (±24dB), Eq HIGH (±24dB), LEVEL |

## Vinyl/Cassette/Lo-fi

| # | Name | Parameters |
|---|------|------------|
| 18 | **303 VinylSim** | COMP, NOISE, WOW FLUT, LEVEL |
| 19 | **404 VinylSim** | FREQUENCY, NOISE, WOW FLUT |
| 20 | **Cassette Sim** | TONE, HISS, AGE (0–60 years), DRIVE, WOW FLUT, CATCH |
| 21 | **Lo-fi** | PRE FILT (1–6), LOFI TYPE (1–9), TONE, CUTOFF, BALANCE, LEVEL |

## Reverb/Chorus/Flanger/Phaser

| # | Name | Parameters |
|---|------|------------|
| 22 | **Reverb** | TYPE (AMBI/ROOM/HALL1/HALL2), TIME, LEVEL, LOW CUT, HIGH CUT, PRE DELAY |
| 23 | **Chorus** | DEPTH, RATE (0.33–2.30s), BALANCE, EQ LOW (±15dB), EQ HIGH (±15dB), LEVEL |
| 24 | **JUNO Chorus** | MODE (JUNO 1/2/12/JX-1 1/2), NOISE, BALANCE |
| 25 | **Flanger** | DEPTH, RATE, MANUAL, RESONANCE, BALANCE, SYNC |
| 26 | **Phaser** | DEPTH, RATE, MANUAL, RESONANCE, BALANCE, SYNC |
| 27 | **Wah** | PEAK, RATE, MANUAL, DEPTH, FLT TYPE (LPF/BPF), SYNC |

## Modulation/Pitch/Utility

| # | Name | Parameters |
|---|------|------------|
| 28 | **Slicer** | PATTERN (1–32), SPEED, DEPTH, SHUFFLE, MODE (LEGATO/SLASH), SYNC |
| 29 | **Tremolo/Pan** | DEPTH, RATE, TYPE (TRE/PAN/TRI/SQR/SIN/SAW1/SAW2/TRP), WAVE, SYNC |
| 30 | **Chromatic PS** | PITCH1/2 (±24 semi), BALANCE, PAN1/PAN2 (L50–R50) |
| 31 | **Hyper-Reso** | NOTE (±17–18 semitones from root), SPREAD (UNISON/TINY/SMALL/MEDIUM/HUGE), CHARACTER, SCALE (C maj–B min), FEEDBACK, ENV MOD |
| 32 | **Ring Mod** | FREQUENCY, SENS, BALANCE, POLARITY, EQ LOW, EQ HIGH |
| 33 | **Crusher** | FILTER (331–15392Hz), RATE (0–100), BALANCE |
| 34 | **Overdrive** | DRIVE, TONE (-100–100), BALANCE, LEVEL |
| 35 | **Distortion** | DRIVE, TONE (-100–100), BALANCE, LEVEL |
| 36 | **Equalizer** | LOW GAIN (±15dB), MID GAIN, HIGH GAIN, LOW FREQ, MID FREQ, HIGH FREQ |
| 37 | **Compressor** | SUSTAIN, ATTACK, RATIO, LEVEL |
| 38 | **SX Reverb** | TIME, TONE (±12), BALANCE |
| 39 | **SX Delay** | TIME, FEEDBACK, TONE, BALANCE |
| 40 | **Cloud Delay** | TIME, FEEDBACK, TONE, BALANCE (cloud/scatter algorithm) |
| 41 | **Back Spin** | Auto back-spin on cue |