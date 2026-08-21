# Mix Engineer — Creative Mixing Craft

The art-layer counterpart to the automated polish pipeline. This file holds the
decision frameworks and workflows a mix engineer applies when actually *mixing* —
the "why" and "what order" behind the per-stem chains in
[stems.md](mdc:references/stems.md) and the genre gain presets in
[mix-presets.md](mdc:mix-presets.md). Read this before answering "how do I mix a
track" style questions; read stems.md for the automated per-stem cleanup defaults.

Every concept is mapped to the `daw-master` engines (SoX / FFmpeg / DawDreamer /
Carla), never to abstract "plugins."

## Tool Mapping Cheat Sheet

| Craft concept | daw-master tool | Concrete op |
|---------------|-----------------|-------------|
| Fader / level | `sox-engine` `gain`/`volume`, `mix` per-track gain | `{"op":"gain","gain":-6}` |
| Pan / stereo width | `ffmpeg-audio` `pan`, `sox-engine` `raw_effect remix` | `{"op":"pan","pan":"stereo|FL=0.5FR|FR=0.5FL"}` |
| Subtractive EQ / HPF | `sox-engine` `equalizer`, `raw_effect highpass` | `{"op":"raw_effect","effect":"highpass 100"}` |
| Additive EQ / shelf | `sox-engine` `equalizer`, `highshelve` | `{"op":"equalizer","frequency":3000,"width":"1.0","gain":2}` |
| Compression | `sox-engine` `compand` | `{"op":"compand","compand_str":"0.01:0.1 0:-20,-10"}` |
| Multiband compression | `sox-engine` `raw_effect mcompand` | `{"op":"raw_effect","effect":"mcompand ..."}` |
| Sidechain compression | `ffmpeg-audio` `sidechaincompress`, `dawdreamer` graph, `carla-rack` (Calf sidechain) | see "Sidechain Compression" |
| Parallel compression | `sox-engine` `mix` of dry + crushed copy, `dawdreamer` parallel graph | see "Parallel Compression" |
| Saturation | `sox-engine` `raw_effect overdrive`, `dawdreamer` `distortion`/`overdrive` | `{"op":"raw_effect","effect":"overdrive 20 20"}` |
| Reverb | `sox-engine` `reverb` (has pre-delay), `dawdreamer` `reverb`, `carla-rack` (Calf reverb) | `{"op":"reverb","pre_delay":40}` |
| Delay | `sox-engine` `echo`, `dawdreamer` `delay`/`echo` | `{"op":"echo","delay":0.25,"decay":0.4}` |
| BPM (for tempo-synced FX) | `audio-analyzer` `analyze` / `dawdreamer` `beat_track` | `analyze(path, features=['tempo'])` |

## Philosophy of Mixing

A mix has one job: **serve the song**. Every EQ move, compressor setting, and
reverb send must answer "does this help the listener feel what the song is trying
to communicate?" If the reason for a processing step cannot be articulated, skip it.

Three pillars:

1. **Clarity** — every element can be heard and identified.
2. **Balance** — relative loudness feels natural and intentional.
3. **Emotion** — the mix amplifies the arrangement's emotional intent.

## The Five-Pass System

Apply in order. Do not skip Pass 1 — it is the most important.

### Pass 1 — Static Mix (Gain + Pan Only)

Build a rough mix with level and pan only, before any processing. If the mix does
not work here, no amount of processing saves it.

- Pick the anchor element (usually lead vocal or lead instrument); set it to
  `-6 dB` via `{"op":"gain","gain":-6}`.
- Bring in every other element relative to the anchor, one at a time.
- Pan to build a stereo field; keep **bass, kick, snare, and lead vocal centered**.
- Render and listen repeatedly (`sox-engine.mix` or `ffmpeg-audio.mix`); iterate
  30-45 minutes before touching EQ or dynamics.

### Pass 2 — Subtractive EQ (Problem Solving)

Remove what should not be there before adding anything.

- **High-pass everything that doesn't need low-end.** Vocals 80-120 Hz, guitars
  80-100 Hz, hi-hats 300-500 Hz (`raw_effect highpass <freq>`).
- **Find and cut resonances.** Sweep a narrow boost (Q 5-8, +10 dB) slowly across
  the spectrum; where it sounds terrible, cut 2-5 dB at that frequency.
- **Cut mud (200-400 Hz)** — the most common amateur-mix problem.
- **Cut harshness (2-5 kHz)** — the second most common.

The repo's default mud cuts (-2 to -3 dB at 200-300 Hz) and high tames live in
[stems.md](mdc:references/stems.md); these are the craft-level heuristics behind
them.

### Pass 3 — Compression & Dynamics

Control dynamic range and add character. Attack/release per element:

| Element | Attack | Release | Gain reduction |
|---------|--------|---------|----------------|
| Kick | 5-15 ms | 50-100 ms | 4-6 dB |
| Snare | 10-25 ms | 100-200 ms | 3-5 dB |
| Bass | 30-50 ms | auto | 4-8 dB |
| Vocals | 15-30 ms | auto | 3-6 dB (or 2 stages × 2-3 dB for transparency) |
| Mix bus | 30 ms+ | auto | 1-3 dB max |

Map to SoX `compand` via `compand_str: "<attack>:<decay> <soft_knee>:<in_dB>,<out_dB>"`.

### Pass 4 — Additive EQ, Saturation & Color

Enhance what already works:

- **Sweet-spot boosts (1-3 dB):** kick 60-80 Hz (weight) + 3-5 kHz (beater);
  snare 200 Hz (body) + 5-8 kHz (crack); vocal 3 kHz (presence) + 8-12 kHz (air);
  acoustic guitar 5-8 kHz (shimmer).
- **Saturation for harmonic richness:** `raw_effect overdrive` (light), tape-style
  on the mix bus, tube-style on bass, light distortion on a parallel drum bus.
- **Broad shelving** for tone: a high shelf at ~8 kHz on the mix bus opens the mix.

### Pass 5 — Spatial Processing (Reverb, Delay, Width)

Add depth last, on sends, never as destructive inserts:

- 2-3 reverb flavors (short plate, medium room, long hall); send varying amounts.
- **Pre-delay 20-80 ms** keeps the dry signal clear while adding space
  (`sox-engine` `reverb` exposes `pre_delay`; `dawdreamer` `reverb` too).
- **Short delays 50-120 ms** add width/thickness without obvious echo.
- **Long delays** (quarter-note, dotted-eighth) are rhythmic effects — tempo-sync
  them using BPM from `audio-analyzer`.
- Automate sends: more space in verses, less in choruses (or the reverse for effect).

## Gain Staging

Maintain healthy levels throughout the chain:

- Target **-18 dBFS average** at each processing input (the digital equivalent of
  0 VU; where most processors are calibrated).
- **Never clip individual channels** — keep peaks below **-6 dBFS** per track.
- Set level *before* processing (gain first in the pipeline); re-check after each
  gain-adding processor (compressors and EQs accumulate gain).
- **Mix bus peaks at -6 to -3 dBFS** before the mastering limiter — leave headroom.

> Convention note: the automated `polish_audio` pipeline normalizes its **delivered
> stems** to -0.1 dBFS peak (see [stems.md](mdc:references/stems.md)). That is a
> *deliverable* convention for the polish step, NOT a creative-mix target. A creative
> pre-master mix must still leave -6 to -3 dBFS for
> [mastering-engineer](../mastering-engineer/SKILL.md).

## Bus Routing Strategy

Group tracks into buses so macro balance decisions (drums vs vocals vs music) don't
require touching individual faders. With the CLI engines, a bus is a sub-mix
(`sox-engine.mix` of its member stems), which then feeds the final mix.

| Bus | Contents | Purpose |
|-----|----------|---------|
| Drum Bus | Kick, snare, hats, toms, overheads | Unit processing + glue compression |
| Bass Bus | Bass DI, amp, sub layers | Control low-end as one element |
| Vocal Bus | Lead, doubles, harmonies, ad-libs | Consistent vocal processing, level control |
| Music Bus | Guitars, keys, synths, pads | Balance instruments against vocals |
| FX Bus | Reverbs, delays | Master control over ambience |
| Mix Bus | All of the above | Final glue, tone shaping |

Concrete CLI shape: process each stem (stems.md chains) → `sox-engine.mix` per
bus → apply bus-level `compand` (glue) → final `mix` of the five buses into the
mix bus → hand to mastering-engineer.

## EQ Decision Framework

Ask in this order before reaching for EQ:

1. **Level problem?** Turn the fader down instead of cutting frequencies.
2. **Arrangement problem?** Mute a conflicting element instead of EQing both.
3. **Frequency masking?** Cut the *less important* element in the contested range.
4. **Resonance?** Narrow surgical cut.
5. **Enhancement?** Broad, gentle boost.

### Frequency Cheat Sheet

| Range | Character | Common issues |
|-------|-----------|---------------|
| 20-60 Hz | Sub, rumble, weight | Mud, room noise, proximity effect |
| 60-200 Hz | Bass, warmth, body | Boominess, kick/bass masking |
| 200-500 Hz | Low-mids, thickness | Mud, boxiness, nasal quality |
| 500 Hz-2 kHz | Midrange, presence, honk | Harshness, telephone quality, masking |
| 2-5 kHz | Upper-mids, clarity, bite | Harshness, fatigue, sibilance |
| 5-8 kHz | Brilliance, edge, consonants | Sibilance, brittleness |
| 8-20 kHz | Air, sparkle, space | Hiss, shrillness; lifeless if absent |

## Compression: Beyond the Basics

### Parallel Compression

Crush a duplicate hard (10-15 dB GR, fast attack/release) and blend it under the
dry original — adds density and sustain without killing transients. Essential for
drums and vocals.

CLI shape: `sox-engine.transform` a copy with heavy `compand`, then
`sox-engine.mix` dry + crushed at ~-6 dB relative. `dawdreamer` offers a true
parallel graph; `carla-rack` can run a parallel Calf compressor chain.

### Sidechain Compression

One signal controls the compressor on another:

- **Kick → bass:** rhythmic pumping; fast attack, release to the groove
  (100-300 ms). Ensures the kick punches through.
- **Kick → pads/synths:** classic EDM pump; longer release for the obvious effect.
- **Vocal → music bus:** duck the music 1-2 dB when the vocal plays, for clarity.

CLI shape: `ffmpeg-audio` `sidechaincompress` (key = kick, input = bass); or a
`dawdreamer` graph; or `carla-rack` with Calf `sidechaincompressor`.

### Multiband Compression

Compresses frequency ranges independently. Use only for specific problems:

- Bass has inconsistent low-end but consistent mids → compress below ~200 Hz only.
- Vocals harsh only on loud phrases → compress only 2-5 kHz.
- Mix bus needs controlled low-end without touching highs.

CLI shape: `sox-engine` `raw_effect mcompand` (band-split compand), or
`carla-rack` Calf `multibandcompressor`. Do **not** reach for it by default.

## Genre-Specific Mixing Notes

Structural mixing notes per genre. These complement (not replace) the per-stem
gain numbers in [mix-presets.md](mdc:mix-presets.md) — presets tune *balance*,
these shape *architecture*.

- **Pop** — vocal is king, sits clearly on top; heavy vocal processing is expected.
  Must translate on phone speakers.
- **Hip-Hop/Trap** — 808/kick relationship is the foundation; massive but
  controlled low-end; hats need sparkle and width.
- **Rock** — drums hit hard with real room; guitars wide (double-tracked,
  hard-panned); bass fills center; more natural dynamics than pop.
- **Electronic/EDM** — sidechain compression is *structural*, not optional; sub-bass
  must be mono; width from stereo synthesis and effects; loud and punchy.
- **Acoustic/Folk** — minimal processing; natural room/plate reverb; preserve
  dynamics; high-pass aggressively to avoid low-end buildup.

## Anti-Patterns: What NOT To Do

- **Don't solo-mix.** A stem that sounds great alone may be terrible in context.
  In the CLI this means: never judge a stem's EQ in isolation — always re-render
  the full mix and re-listen before committing.
- **Don't boost when you should cut.** Two competing elements → cut one, don't
  boost both. Boosting escalates; cutting resolves.
- **Don't use presets without understanding them.** The genre presets in
  [mix-presets.md](mdc:mix-presets.md) are starting points; adjust attack, release,
  ratio, and threshold for the actual material.
- **Don't over-compress.** Flat, lifeless, or unnaturally pumping = too far. Back off.
- **Don't mix loud.** Work at conversation level (~75-80 dB SPL); loud monitoring
  masks problems and causes fatigue. Check loud briefly, work quiet.
- **Don't skip referencing.** A/B against a professional reference track in the
  target genre constantly. See
  [mastering-engineer](../mastering-engineer/SKILL.md) `master_with_reference` for
  the automated spectral-match tool.
- **Don't mix 3-4+ hours without breaks.** Ear fatigue is cumulative; ~15 min away
  per 90 min.
- **Don't add effects "because you should."** Not every track needs reverb or
  delay. Process with purpose or leave it dry.
