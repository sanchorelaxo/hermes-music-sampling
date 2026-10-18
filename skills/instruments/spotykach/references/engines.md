# sk-engines — what the Spotykach becomes per engine

The Spotykach is a **dual-deck DSP platform**: two identical strips, each with
PITCH / SIZE / POS / SOS / ENV knobs, a Play pad, a Rev pad, a 3-way Mode switch
(L/C/R, silkscreened Reel/Slice/Drift), and a Route switch. Flashing an sk-engine
*turns the whole device into a different instrument or effect* — the shared
hardware is just the control surface, and each engine re-labels it.

There are **18 release engines** (shipped as `.bin` in the `0.6.1` release) plus
**4 build-only engines** (compiled from source, no release binary). Release engines
are what `sk_engines.py install <name>` flashes; build-only engines require a local
build and are documented here for completeness.

For the **full upstream control map of every engine** — the exact knob/pad/switch
remappings, hold-macro missions, LED legends, and clock/routing behaviour — the
verbatim upstream doc for each engine is vendored in
[references/engines/](/home/rjodouin/Documents/git/hermes-music-sampling/skills/instruments/spotykach/references/engines/)
(`<engine>.md`, e.g. `edrums.md`, `delay.md`). Use those when you need the
device-level detail; keep this file as the at-a-glance map.

| Engine | The device becomes | Type | Build | SD card | Notes |
|--------|--------------------|------|-------|---------|-------|
| granular | looper / sampler | Looper | SRAM | Optional (save/load) | Original stock firmware as an engine; build-only default |
| graincloud | granular looper | Looper | SRAM (`-Os`) | Optional (save/load) | Granular variant with a GrainflowLib cloud |
| tape | dual streaming tape deck | Looper/recorder | SRAM | **Required** (streams) | Two SD-streamed decks, no length cap |
| shuttle | bipolar/reverse varispeed tape | Looper | SRAM | Optional (load slots) | Four in-SDRAM tracks, capstan-style PITCH |
| softcut | crossfaded overdub looper | Looper | SRAM | Optional (load/save clips) | Vendored monome softcut-lib, 4 voices |
| radio | dual virtual RadioMusic | Player | SRAM | **Required** (streams) | `.raw`/`.wav` banks, free-running playhead |
| bard | audiobook decks | Player | SRAM (`-Os`) | **Required** (streams) | Bookmark-navigated; not yet hardware-tested |
| delay | tempo-synced stereo delay | Effect | SRAM | — | Clean / Tape / Shimmer characters |
| qdelay | dub/ambient delay | Effect | SRAM | — | Clean / Diffuse / Duck; GPLv3 |
| reverb | route-aware stereo reverb | Effect | SRAM (`-Os`) | — | Plate / hall / Greyhole (Faust) |
| gigaverb | reverb | Effect | SRAM | — | Tom Erbe gigaverb via gen~; build-only |
| chorus | stereo chorus | Effect | SRAM | — | generated Faust demo; build-only |
| filter | dual resonant filter | Effect | SRAM | — | parallel (DoubleMono) dual-deck demo |
| voice | drone → resonant filter chain | Instrument | SRAM | — | series (chain) dual-deck demo |
| pstretch | PaulStretch time-smear | Effect | SRAM | Optional (file source) | Real-time ambient stretch, vendored FFT |
| edrums | 4-voice Euclidean drum machine | Instrument | SRAM | — | Tweakable synthesized drums |
| reso | Rings resonator / plucked string | Instrument | SRAM (`-Os`) | — | Mutable Instruments Rings DSP |
| mosc | dual Plaits macro-oscillator | Instrument | **QSPI** | — | 24-engine Plaits voice, vendored in-tree |
| glitch | lo-fi circuit-bent noise voice | Instrument | SRAM | — | 12 Noisferatu algorithms; GPLv3 |
| csound | full Csound 7 synth | Synth | **QSPI** | Required (`.csd` patches) | One-time `libcsound.a` cross-build |
| chuck | ChucK language synth | Synth | **QSPI** | Required (`.ck` patches) | One-time `libchuck.a` cross-build |
| passthrough | minimal stereo passthrough | Effect | SRAM | — | Platform API demo; build-only |

## Build vs. flash

- **SRAM engines** run entirely from a RAM region and almost never enumerate USB
  MIDI after boot — a healthy SRAM engine shows `DFU mode: no` + `MIDI device: no`.
  That is the *running* state, not an error.
- **QSPI engines** (`mosc`, `csound`, `chuck`) are too large for SRAM and need a
  build pinned against the QSPI flash layout; they re-enumerate USB MIDI normally.
- **Build-only engines** (`granular`, `gigaverb`, `chorus`, `passthrough`) have no
  release `.bin` and are flashed only after a local `make`.

## Per-engine controls (release engines)

Each summary lists the non-obvious remappings of the shared surface. "Eh" means the
control is unused by that engine. See `docs/engines/<name>.md` in the sk-engines repo
for the full generated control map.

### delay — tempo-synced stereo delay
- PITCH = transpose ±1 oct; SIZE = delay time (musical divisions); POS = feedback;
  SOS = wet/dry; ENV = feedback tone; MODFREQ/MOD_AMT = mod LFO (chorus/flange/vibrato).
- Play = Freeze; Rev = Reverse. Reel/Slice/Drift = Clean/Tape/Shimmer. Route = Stereo/DoubleMono/Ping-pong.

### qdelay — dub/ambient delay
- Same grammar as delay. Character switch = Clean/Diffuse/Duck (Diffuse = 8-stage
  allpass diffuser wash; Duck = wet dips under the dry so repeats bloom in the gaps).

### reverb — route-aware reverb
- PITCH = Decay; SOS = Mix; ENV = Damp; POS = Tone; SIZE = size/pre-delay.
  Reel/Slice/Drift = Dattorro plate / Zita-rev1 hall / Greyhole.
- Route = Stereo (one voice) / DoubleMono (two independent mono plates; plate only).

### filter — dual resonant filter (parallel demo)
- One independent voice per channel. Knobs map to Faust filter sliders; Route switch
  sets the stereo topology. Demonstrates the generated parallel (DoubleMono) path.

### voice — drone → resonant filter (series demo)
- Deck A = drone oscillator, Deck B = resonant filter; the chain is instrument → FX.
  Demonstrates the generated series (chain) dual-deck path.

### tape — dual streaming tape deck
- Two independent record/playback decks, SD-streamed (no in-memory cap).
- Play = play toggle; Alt+Play = record toggle. MIX knob = per-deck playback volume.
  Route switch = pan topology (also lights the L/C/R mode LED).

### shuttle — bipolar/reverse varispeed tape
- Four in-RAM tracks, two per deck. PITCH = capstan speed (noon = stop, CW = forward,
  CCW = reverse). Play = toggle rolling (snaps to +1×). Rev = swap the deck's focused
  track. Seq = re-align all four tracks to loop start.

### softcut — crossfaded overdub looper
- monome softcut-lib, 4 voices (2/deck). Record-defines-loop: on an empty voice the
  first Alt+Play records, the second closes the loop; a voice with content overdubs.
- PITCH = bipolar varispeed/reverse; POS/SIZE = loop window; ENV = overdub feedback
  (sound-on-sound); FLUX pad = sweepable filter; MOD_AMT/MODFREQ = crossfade time/rate
  slew. Seq = realign (click-free cutToPos); Alt+PITCH = load clip from SD; Alt+Seq/
  Alt+Rev = save take/trimmed loop to SD.

### radio — dual virtual RadioMusic
- Two independent virtual radios over a shared SD bank of `.raw`/`.wav` files.
  Free-running playhead: each station "keeps broadcasting" while you tune elsewhere.
- PITCH = station tuning; POS = start offset; Alt+PITCH = bank; SIZE = varispeed;
  ENV = inter-station static; Play/gate = re-tune.

### bard — audiobook decks (bookmark-navigated)
- PITCH = book select; POS = bookmark select; SIZE = rate (0.5×–2.5×, unity centre).
  Play = play/pause; Rev = jump back 15 s. Alt+Play = drop mark; Alt+Rev = re-roll
  auto-marks; Seq = next; Alt+Seq = arm-to-clock. Mode switch = sequence mode.
  Flux pad = voice colour (wireless/gramophone/telephone); Grit pad = room.

### edrums — 4-voice Euclidean drum machine
- Play = stop/start focused drum; Rev = swap focused drum; Alt+Play = mute focused
  drum. Route knob = routing; four synthesized drums with tweakable parameters.

### reso — Rings resonator / plucked string
- Mutable Instruments Rings DSP. Knobs map to Rings targets (position, structure,
  brightness, damping); per the reso doc, PITCH = note/frequency, with CV jack in.

### mosc — dual Plaits macro-oscillator
- Each deck gets a full 24-engine Plaits voice (virtual analog, FM, wavetable,
  granular, additive, chord, speech, modal, drums, …).
- PITCH = note; Alt+PITCH = engine select (24 models); SIZE/POS/ENV = harmonics/
  timbre/morph; MOD_AMT/MODFREQ = LPG decay/colour. Mode switch = Gate vs Drone;
  Route = Stereo / DoubleMono / GenerativeStereo.
- **QSPI build**; no SD card or external library needed.

### glitch — lo-fi circuit-bent noise voice
- 12 Noisferatu algorithms per deck (buffer-players + synthesis). Alt+PITCH =
  algorithm select. Play = regenerate the glitch buffer. Rev inert. GPLv3.

### pstretch — real-time PaulStretch ambient time-smear
- Mode switch = SOURCE: Reel = Capture, Slice = Live, Drift = SD-file (`/pstretch`).
- Play = freeze read head (infinite drone); Rev = re-grab the ring (Capture);
  Alt+PITCH = clip select (SD source); Mod Type = LFO shape; routing switch = topology.

### csound — full Csound 7 synth (QSPI)
- The patch (a `.csd` orchestra) defines the sound. Load orchestras from SD and switch
  live with Alt+PITCH; play over MIDI. **QSPI build** + one-time `libcsound.a` build.

### chuck — ChucK language synth (QSPI)
- The patch (a `.ck` program) defines the sound, strongly-timed concurrent voices.
  Load programs from SD and switch live with Alt+PITCH (memory-stable). **QSPI build**
  + one-time `libchuck.a` build.

## Source

- Release manifest + docs: `https://github.com/shakfu/sk-engines` (tag `0.6.1`)
- Per-engine control maps: `docs/engines/<name>.md` in that repo.