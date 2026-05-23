# FX Wizard — Patch Recipes Reference

16 preset patches from the official FX Wizard Cookbook. Each recipe shows suggested cable connections.

## FX Mode 1: DELAY (blue) — Page 1

### 1. Ducking Delay
**Sound:** Great for vocals — delay ducks under input signal.
**Patch:** `ENV` → `FX MODE`
> ENV output controls FX MODE input, attenuate with FX MODE + AMOUNT knob.

### 2. Vibrato + Chorus and Flanger
**Sound:** Adds pitch modulation. Lower AMOUNT for chorus, add FEEDBACK for flanger.
**Patch:** `LFO TRI` → `TIME MOD`
> Patch LFO triangle output into time modulation input for chorus/flanger.

### 3. Broken Tape
**Sound:** Randomly modulated triangle LFO warbles delay time (nostalgia effect).
**Patch:** `LFO TRI` → `STEP` → `TIME MOD`
> Chain: LFO TRI → STEP input, then STEP output → TIME MOD input.

### 4. Haas Effect
**Sound:** Detune delay between L/R channels for stereo widening.
**Patch:** None required — use STEREO knob (SHIFT + middle left) to detune L/R.

## FX Mode 2: FLANGER (green) — Page 1

### 5. Signal Responsive Stereo Chorus
**Sound:** ENV resets modulation with transients. Add FEEDBACK for flanging.
**Patch:** `ENV` → `RESET`
> ENV output resets the LFO timing on transients.

### 6. Auto Freezer
**Sound:** ENV triggers refreeze of audio buffer.
**Patch:** `ENV` → `TRIG`
> Adjust INPUT to set envelope sensitivity.

## FX Mode 3: FREEZER (blue) — Page 1

### 7. Rhythm Freezer
**Sound:** Refreeze with CV-modulated synced LFO. Add variation with TIME modulation.
**Patch:** `LFO TRI` → `TRIG`, `PATTERN R` → `LFO TEMPO`
> LFO resets freeze on rhythm; Pattern R controls LFO tempo.

### 8. Rhythm Glitcher
**Sound:** Rhythmical freezes synchronized to tempo. Be nuanced or totally glitch out!
**Patch:** `PATTERN G` → `TRIG`
> Gate pattern triggers freeze rhythm.

## FX Mode 4: PANNER (white) — Page 2

### 9. Tail Panner & Distorter
**Sound:** Loud parts stay centered; tails get panned. Add FEEDBACK to distort.
**Patch:** `ENV` → `FX MODE`, `LFO TRI` → `TIME MOD`
> ENV controls panning, LFO adds time-based wobble.

### 10. Stereo Ring Mod
**Sound:** Speed up panner to audio rate for stereo ring modulation.
**Patch:** `LFO TRI` → `TIME MOD`
> High LFO rate creates ring mod effect. Modulate TIME for more fun.

## FX Mode 5: CRUSHER (yellow) — Page 2

### 11. LO-FI Phaser
**Sound:** Animate downsampling frequency with LFO for subtle modulation. Add STEREO.
**Patch:** `LFO TRI` → `TIME MOD`
> Slow LFO sweep creates moving bitcrush artifacts.

## FX Mode 6: SLICER (light green) — Page 2

### 12. Dynamic Slicer
**Sound:** Modulate slicer decay with slow LFO for dynamic chops.
**Patch:** `LFO TRI` → `FX MODE`
> LFO modulates the slice envelope.

## FX Mode 7: PITCHER (red) — Page 2

### 13. Pitched Repeater (with crickets)
**Sound:** Pitch up and speed up. ENV → TRIG aligns with input.
**Patch:** `ENV` → `TRIG`, `LFO TRI` → `TIME MOD`
> Add FEEDBACK for "cricket" sounds.

## FX Mode 8: REPLAYER (orange) — Page 2

### 14. Twin Peaks Reverse Speech
**Sound:** Reverse-speech effect ("Hello agent Cooper").
**Patch:** `ENV` → `TIME MOD`, `LFO TRI` → `FX MODE`
> ENV modulates pitch window, LFO triggers mode changes.

## FX Mode 9: SHIFTER (pink) — Page 2

### 15. Space Vinyl Saucer
**Sound:** Adjust tempo changes modulation speed. Add FEEDBACK for "intergalactic lift off."
**Patch:** `STEP` → `TIME MOD`
> Stepped CV creates quantized time modulation.

### 16. 8bit Synth
**Sound:** Turn LFO into VCO. Use AMOUNT and FILTER for timbral modulation.
**Patch:** `LFO TRI` → `AUDIO IN L`, `LFO PULSE` → `TRIG`, `ENV` → `FX MODE`
> LFO triangle into audio input creates oscillator; pulse triggers envelope.