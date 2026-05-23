# Mix Engineer — Per-Stem Processing Chains

Detailed processing chains for each stem type. All operations use `sox-engine.transform` with genre-specific overrides.

## Common Operations

| Effect | SoX op | Parameters |
|--------|--------|------------|
| Highpass | `"raw_effect": "highpass {freq}"` | cutoff Hz, e.g., 30, 80 |
| Lowpass | `"raw_effect": "lowpass {freq}"` | cutoff Hz |
| Bandpass | `"raw_effect": "bandpass {freq} {width}"` | center freq, Q or width |
| Noise reduction | `"raw_effect": "noisered {profile} {strength}"` | profile file, strength 0–1 |
| EQ (shelf/peak) | `"equalizer"` | frequency, width, gain dB |
| Compression | `"compand"` | attack, soft_knee, threshold_in, threshold_out |
| Fade | `"fade"` | type (in/out/in-out), length sec |
| Normalize | `"normalize"` | peak dB (default -0.1) |
| Reverse | `"reverse"` | — |
| Trim/Pad | `"trim"`, `"pad"` | start/end or silence |

> **Note**: SoX `noisered` requires a noise profile file. Auto-generated from the quietest 100ms segment via `sox -n stat`. If no suitable silent region found, noise reduction is skipped.

## Per-Stem Chains

### Lead Vocals
1. Noise reduction (strength 0.5)
2. Presence boost (+2 dB at 3 kHz, Q=1.0)
3. High tame (-2 dB shelf at 7 kHz)
4. Gentle compress: attack=0.01:0.1, soft_knee=0, in=-20dB, out=-10dB
5. Optional: fade in/out on track boundaries

### Backing Vocals
1. Noise reduction (0.5)
2. Presence boost (+1 dB at 3 kHz)
3. High tame (-2.5 dB at 7 kHz)
4. Stereo width enhancement (via ffmpeg `pan` or `stereotools` — optional)
5. Tighter compress: attack=0.008:0.1, threshold_in=-14dB, threshold_out=-10dB

### Drums
1. Click removal (high-amplitude transient detection; threshold 6σ)
2. Gentle compress: attack=0.005:0.1, threshold_in=-12dB, threshold_out=-10dB

### Bass
1. Highpass (30 Hz Butterworth)
2. Mud cut: equalizer freq=200 gain=-3 width=2q
3. Gentle compress: attack=0.01:0.1, threshold_in=-15dB, threshold_out=-10dB

### Guitar
1. Highpass (80 Hz)
2. Mud cut: eq freq=250 gain=-2.5 width=2q
3. Presence boost: eq freq=3000 gain=+1.5 width=1.2
4. High tame: highshelve freq=8000 gain=-1.5
5. Stereo width (mild)
6. Compress: attack=0.012:0.1, threshold_in=-14dB, threshold_out=-10dB

### Keyboard
1. Highpass (40 Hz)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. Presence boost: eq freq=2500 gain=+1 width=0.8
4. High tame: highshelve freq=9000 gain=-1.5
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

### Strings
1. Highpass (35 Hz)
2. Mud cut: eq freq=250 gain=-1.5 width=0.8
3. Presence boost: eq freq=3500 gain=+1
4. High tame: highshelve freq=9000 gain=-1
5. Wide stereo
6. Very light compress: attack=0.02:0.1, threshold_in=-18dB, threshold_out=-10dB

### Brass
1. Highpass (60 Hz)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. Presence boost: eq freq=2000 gain=+1.5
4. High tame: highshelve freq=7000 gain=-2
5. Compress: attack=0.01:0.1, threshold_in=-14dB, threshold_out=-10dB

### Woodwinds
1. Highpass (50 Hz)
2. Mud cut: eq freq=250 gain=-1.5 width=0.8
3. Presence boost: eq freq=2500 gain=+1
4. High tame: highshelve freq=8000 gain=-1
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

### Percussion
1. Highpass (60 Hz)
2. Click removal (transient detection)
3. Presence boost: eq freq=4000 gain=+1
4. High tame: highshelve freq=10000 gain=-1
5. Stereo width (1.2×)
6. Compress: attack=0.008:0.1, threshold_in=-15dB, threshold_out=-10dB

### Synth
1. Highpass (80 Hz)
2. Mid boost: eq freq=2000 gain=+1 width=0.8
3. High tame: highshelve freq=9000 gain=-1.5
4. Stereo width (1.2×)
5. Light compress: attack=0.015:0.1, threshold_in=-16dB, threshold_out=-10dB

### Other (catch-all)
1. Light noise reduction (0.3)
2. Mud cut: eq freq=300 gain=-2 width=2q
3. High tame: highshelve freq=8000 gain=-1.5

## Full-Mix Fallback

When stems aren't available, process the full stereo mix with a lighter chain:
- Noise reduction (0.3 strength, if profile available)
- Highpass 35 Hz
- Click removal (transient spike detection)
- Mud cut: eq freq=250 gain=-2
- Presence boost: eq freq=3000 gain=+1.5
- High tame: highshelve freq=7000 gain=-1.5
- Gentle compress

## Genre Presets

| Genre | Vocal boost | Bass boost | Drum boost | High-mid cut |
|-------|-------------|------------|------------|--------------|
| Default | 0 dB | 0 dB | 0 dB | –2 dB @ 7 kHz |
| Hip-Hop/Rap | +1 dB | +1 dB | +0.5 dB | aggressive |
| Rock/Metal | 0 dB | 0 dB | +0.5–1 dB | –2.5 to –3 dB |
| EDM/Electronic | 0 dB | +0.5–1 dB | +0.5–1 dB | lighter |
| Folk/Country | +0.5 dB | 0 dB | +0.5 dB | –1.5 dB |
| Ambient/Lo-Fi | 0 dB | 0 dB | 0 dB | –1.5 dB; lighter NR |

## Quality Standards

Before handoff to mastering:
- [ ] No clipping (peak < –0.1 dBFS)
- [ ] All samples finite
- [ ] Noise floor reduced vs original (where applicable)
- [ ] No obvious processing artifacts
- [ ] Polished files written to `polished/` subfolder