---
name: "spotykach-engine-authoring"
description: "Use when writing a new DSP engine (firmware variant) for the Spotykach / sk-engines framework — the IEngine contract, the three authoring methods (native C++, Faust/cyfaust, gen~/gen-dsp), build-time registration, the SDRAM arena memory model, and the shared knob grammar."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["spotykach", "sk-engines", "firmware", "engine", "daisy", "stm32h7", "faust", "gen~", "cpp", "dsp", "embedded", "authoring"]
    related_skills: ["spotykach"]
---

# Spotykach engine authoring (sk-engines)

How to write a **new engine** for the [sk-engines](https://github.com/shakfu/sk-engines) firmware — a swappable DSP "firmware variant" that turns the Spotykach's fixed knobs/pads/CV/MIDI surface into a new instrument. This skill is the *authoring* counterpart to the user-facing `spotykach` skill: that one documents **using** the device and **installing/running/removing** shipped engines (`scripts/sk_engines.py install|status|restore`); this one documents **building a whole new engine from scratch**.

- Repo: https://github.com/shakfu/sk-engines
- Clone: `git clone https://github.com/shakfu/sk-engines` (worked in this session at `~/Documents/git/sk-engines`)
- Full API reference (the `IEngine` surface, enums, context/transport/arena, registration): [references/iengine-contract.md](mdc:references/iengine-contract.md)

## The model: a fixed platform hosting one engine

Spotykach's firmware is a fixed hardware/UI **platform** plus one swappable DSP **engine**, chosen at **build time** (never runtime). One engine per binary: the STM32H7 boots from SRAM bare-metal (no RTOS, no heap on the audio path), with only hundreds of bytes of headroom, so two engines neither fit nor make sense in one image.

- **The platform** (`src/ui/`, `src/hw/`, `src/memory/`, `src/transport/`) owns everything reusable: the multi-function knob grammar (`MValue` pickup), pad gestures, ring LEDs, SD tape storage, CV/gate, MIDI, the clock/transport. It is **polymorphic over `IEngine` only** — it never names a concrete engine, and it includes no engine DSP header. `make check-boundary` (a prerequisite of `all`) greps `hw/ui/memory/transport` for `engine/granular/` includes and fails the build if one is reintroduced.
- **The engine** (`src/engine/<name>/`) implements `IEngine` (`src/engine/iengine.h`) and owns its DSP privately. `app.cpp` is the composition root — the one place the concrete engine type is named (`ActiveEngine` from `engine_select.h`).

Because the platform does all the interaction mechanics, **engine #2 is small** — a minimal engine (`passthrough`) is a few dozen lines.

## Choosing an authoring method

Three ways to build an engine; all three end in the same place (a class implementing `IEngine`, selected via `ENGINE=`). They differ in how much you hand-write.

| Method | You write | Codegen | Use when | Examples |
|---|---|---|---|---|
| **Native C++** | DSP *and* the `IEngine` wrapper, by hand | none | not a pure signal graph: sequencers, SD streaming, dual-deck instruments, custom display, vendoring a C++ DSP lib or an audio VM | granular, delay, edrums, reso, tape, shuttle, bard, radio, glitch, pstretch, mosc, passthrough; csound, chuck (runtime VMs) |
| **Faust (cyfaust)** | DSP in `.dsp`; wrapper + knob binds by hand (or none — see generated) | `make faust-kernels` / `make faust-engine` | closed-form DSP you want to write declaratively, esp. several interchangeable algorithms | reverb, tape (tapefx); chorus, filter, voice (generated) |
| **gen~ (gen-dsp)** | a Max `gen~` patch + a small JSON manifest; **no C++** | `make gen-engine` → a whole engine dir | you already have (or want to patch) a Max `gen~` graph; fastest to a running engine | gigaverb |

A single engine can mix methods (tape = native C++ + an embedded Faust `tapefx` kernel).

- **Native C++** is the only capability-rich path (sequencing, storage, MIDI, CV out, custom panel). Everything that isn't a pure signal graph is native.
- **Faust generated** (a `.dsp` + a JSON manifest, *no* C++) covers a single-kernel mono/stereo effect or knobs-only instrument — the generator emits the whole wrapper on the shared `FaustEngine<Traits>` template.
- **gen~** is the least firmware: the wrapper is fully generic; you only write a `knobs` JSON manifest. Currently `capabilities() = 0` (stereo audio + knob params only, no custom display/MIDI/CV).

## The audio lifecycle (required of every engine)

Every engine implements three pure-virtual methods; the rest of `IEngine` is **no-op defaults** you override only as needed (`capabilities()` advertises what's live):

```cpp
class MyEngine : public IEngine {
  void init(const EngineContext& ctx) override;   // sample rate, block size, SDRAM arena, clock, transport
  void prepare() override;                          // non-RT main-loop housekeeping
  void process(const float* const* in, float** out, size_t size) override;  // 48 kHz / 96-frame block, audio ISR
  Capabilities capabilities() const override { return CapOwnDisplay | CapDualDeck; }
  void set_param(ParamId, DeckRef::Ref, float) override;   // platform knob -> your DSP (0..1)
  void render(DisplayModel&) override;             // if CapOwnDisplay
};
```

- `init(ctx)` allocates/subscribes — placement-new big state into the SDRAM arena, save `sample_rate`/`block_size`, optionally `ctx.transport->set_on_tick(cb)`.
- `process()` is the hard real-time audio ISR: **no allocation, no blocking, no SD/flash**. Keep per-sample work in non-virtual engine code.
- `prepare()` runs in the main loop for non-real-time housekeeping.
- `set_param` arrives **normalized 0..1**; scale into your units (delay feeds `v*0.95` feedback, `exp2f((v-0.5)*2)` ratio; reso passes `v` straight to Rings `damping`). Categorical switches come via `set_config(ConfigId, deck, int)`.

See [references/iengine-contract.md](mdc:references/iengine-contract.md) for the full surface and every enum.

## Writing a native C++ engine — the checklist

1. Subclass `IEngine` in `src/engine/<name>/<name>_engine.{h,cpp}`; implement the three lifecycle methods. **Own your DSP privately** — do not reuse `src/engine/granular/` (that is the looper's private DSP).
2. Return the right `capabilities()` bitset; override only the method groups you support.
3. Map `ParamId`s in `set_param`/`param`; own any mode fanout internally (the platform never sees your `Mode`).
4. If `CapTapeStorage`: implement the `audio_*` byte port so the platform's SD tape can save/load your buffer. If you need tempo/clock: consume `ctx.transport` (read `tempo()`, or subscribe `set_on_tick`).
5. If `CapOwnDisplay`: fill `render(DisplayModel&)` for your panel (the platform blits + composites its overlays). Otherwise leave the LED queries as defaults.
6. Register in `src/engine/engine_select.h` (`#elif defined(SPK_ENGINE_<NAME>)` → `using ActiveEngine = <Name>Engine;`) and add an `ENGINE=<name>` block to the root `Makefile` (set `-DSPK_ENGINE_<NAME>` + `ENGINE_SOURCES`), plus an `engine-<name>` one-shot target.
7. Add a headless test in `host/` and build/verify: `make check-boundary && make -j8 ENGINE=<name>` (watch the `SRAM_EXEC` usage the link prints).

### Reference engines (copy the right one)

- **`passthrough`** — the minimum: header-only, `in → out` copy, `render` meters, `CapOwnDisplay` only. Start here.
- **`delay`** — reads transport tempo; clean `set_param` scaling.
- **`edrums`** — subscribes to transport ticks, sequences voices, `set_config` routing, two "drums" per deck.
- **`reso`** — PIMPL (vendored Mutable Instruments Rings), arena placement-new, `-Os`, block chunking, `CapAux` model select.
- **`csound` / `chuck`** — the runtime-compiler extreme: thin wrapper over a vendored audio VM, QSPI build, live recompile from an SD patch bank.

### Owning the DSP (PIMPL is sometimes mandatory)

Hold DSP as members, or behind an opaque `Impl*` (PIMPL). **PIMPL is mandatory, not stylistic, when a vendored dependency declares a global symbol that collides with the composition root** — reso needs it because `stmlib.h` declares a global `namespace impl` and `app.cpp` has a `static AppImpl impl;`. Keep third-party types inside the `.cpp`.

### Memory: the arena, and the block size

- **Allocate big state from `ctx.arena`, never as static members.** The platform hands an opaque `EngineArena {base, bytes}` (48 MB SDRAM block); sub-allocate with the `Arena` bump allocator (`src/engine/arena.h`). Static members land in `.bss` and overflow the 252 KB `SRAM` data region.
- **The binding budget is `SRAM_EXEC` (code), 260 KB** (per `linker/alt_sram.lds`), not data — arena placement-new keeps `SRAM` flat regardless of delay-line size. `pstretch` gets its own 200 KB / 312 KB split. A big engine may need its Makefile branch at `-Os`.
- **Chunk if your DSP's max block < 96.** The platform block is 96 frames; reso runs Rings at `kMaxBlockSize=24` and processes in four chunks.

## Generated engines (no hand-written C++)

### Faust — `.dsp` + JSON manifest

Drop `src/engine/<name>/<name>.dsp` + a `<name>.json` manifest; the generator emits the kernel and the whole wrapper (a `Traits` struct keyed by `ParamId`, bound to the shared `FaustEngine<Traits>` / `FaustChainEngine<Traits>`).

```text
make faust-engine MANIFEST=src/engine/chorus/chorus.json   # kernel + wrapper + build + diagram
make -j8 ENGINE=chorus
```

The manifest only maps platform knobs to Faust slider labels (ranges are captured from the kernel at `init()`, so they aren't duplicated) plus feature flags (`meter`, `soft_limit`, `wet_dry`, `color`) and a `deck_mode`:

```json
{ "engine": "chorus", "backend": "faust", "title": "...", "subtitle": "...",
  "knobs": { "Cycle": "rate", "Glow": "depth", "Size": "delay", "Mix (SOS)": "mix" },
  "capabilities": [], "features": { "meter": true, "color": "0x33ccff" } }
```

- **Single control set** (default, `chorus`): one kernel, `decks = 1`.
- **`"deck_mode": "parallel"`** (DoubleMono, `filter`): two instances of one mono kernel, deck A→left, deck B→right, each with its own knob bank (`FaustEngine` with `decks = 2`).
- **`"deck_mode": "series"`** (chain, `voice`): two different kernels wired A→B (instrument→FX) on the sibling `FaustChainEngine<Traits>`.

The `.dsp` must use **flat `hslider`s each 0..1** (the wrapper linear-maps into the native range). See the Faust pitfalls in [the method docs](https://github.com/shakfu/sk-engines/blob/main/docs/engine-types/faust.md) — the two that bite are:

- **`os.osc` builds a static 64 KB `rdtable` that lands in `.bss` and overflows SRAM** (the chorus comment records a 98,808 B overflow). Use **`os.m_oscsin`** (a `sinf()`-based phase accumulator — no table, continuous rather than stepped, which also avoids zipper noise on fractional-delay LFOs).
- Use `de.fdelay(n, d, x)` for fractional delays (compile-time max).

cyfaust runs **only at codegen time on the host**, from the repo-local `.venv`: `python3 -m venv .venv && .venv/bin/pip install cyfaust` (one-time). Generated headers are checked in, so the firmware build is plain `arm-none-eabi-g++` with no cyfaust.

### gen~ — Max patch + JSON manifest

Author in Max `gen~`, export, and run the gen-dsp generator:

```text
.venv/bin/pip install -e /path/to/gen-dsp                                # one-time
.venv/bin/python scripts/gen_engine.py /path/to/export myverb            # bootstrap (positional knob map)
make gen-engine MANIFEST=src/engine/myverb/myverb.json FORCE=1          # gen-dsp + glue from manifest
make gen-engine MANIFEST=src/engine/myverb/myverb.json NOGEN=1 FORCE=1  # glue only, after a knob edit
make clean && make -j8 ENGINE=myverb && make ENGINE=myverb program-dfu
```

The one file you write is the manifest (same declarative `knobs` map as Faust, `"backend": "gen"`, plus an `export` path). `scripts/gen_engine.py <name> --remove` deletes an engine and unwires it. Batch-regenerate with `make gen-engines`. gen~ engines share wrapper object basenames and have a stale-`.d` quirk, so **always `make clean` between engine switches**. [Full gen~ method](https://github.com/shakfu/sk-engines/blob/main/docs/engine-types/gen.md).

## Registration: `engine_select.h` + the Makefile

The `ENGINE` variable does both halves of selection — a `-D` define **and** the source list:

```make
ifeq ($(ENGINE), myengine)
  C_DEFS += -DSPK_ENGINE_MYENGINE
  ENGINE_SOURCES = $(wildcard src/engine/myengine/*.cpp)
endif
CPP_SOURCES = main.cpp app.cpp $(ENGINE_SOURCES) <platform>
```

```cpp
// engine_select.h
#elif defined(SPK_ENGINE_MYENGINE)
  #include "engine/myengine/myengine_engine.h"
  namespace spotykach { using ActiveEngine = MyEngine; }
```

The Faust/gen~ generators **append** their `else ifeq` / `#elif` blocks inside marker delimiters (`// >>> faust:chorus >>>` … `// <<< faust:chorus <<<`), so generated registration is upserted, not hand-edited. `build/.engine-stamp` forces `app.o` (the only define-dependent TU) to rebuild on an `ENGINE` switch — but generated engines need `make clean` (see gen~ note).

## Build & flash

```text
make -j8 libs                    # once: libDaisy/DaisySP deps
make -j8 ENGINE=delay            # build; the link prints SRAM_EXEC usage
make ENGINE=delay program-dfu    # flash (device in DFU mode first)
make engine-delay                # one-shot: clean + build + flash
make check-boundary              # platform must not include engine DSP
make faust-kernels               # regenerate every Faust kernel
make gen-engines                 # regenerate every gen~ engine
```

Release binaries are only built for some engines; `granular`, `passthrough`, `chorus`, `gigaverb` require building from source. QSPI-variant engines (`csound`, `chuck`) build via `make engine-csound` / `make engine-chuck` (not `ENGINE=`), need a one-time `scripts/fetch_csound.sh` / `fetch_chuck.sh`, and link huge runtimes into 8 MB of QSPI flash — code size moves off the 260 KB budget, and CPU headroom becomes the limit. Every engine needs the sk-engines Spotykach bootloader (`bootloader-spotykach-v2.bin`, in-tree, `APP_TYPE=BOOT_SRAM`) to run — see the `spotykach` skill's firmware notes for the bootloader caveat.

## The knob grammar (how a control reaches your engine)

The platform reads the 7 analog knobs/deck + crossfade, applies its pickup/modifier grammar, and calls `set_param(ParamId, deck, 0..1)` (or `set_mod_speed`). **The same physical knob maps to different `ParamId`s depending on the held modifier** (Flux/Grit/Alt pads, tap-hold). For a non-granular engine (`DeckLayout::single`, the default) the per-deck routing is:

| Knob | default | Flux-pad held | Grit-pad held | Alt held | Tap-hold |
|---|---|---|---|---|---|
| POS | `Pos` | `FluxFb` | — | — | — |
| ENV | `Env` | — | — | — | — |
| SIZE | `Size` | — | — | — | — |
| PITCH | `Speed` | `FluxIntensity` | `GritIntensity` | `Aux` (CapAux) / else pitch-quantize | — |
| MODFREQ | `set_mod_speed` | — | — | (sync flag) | **Tempo** (A) / PanSpeed (B) → platform |
| MOD_AMT | `ModAmp` | — | — | — | ClickMix (A) / PanRange (B) → platform |
| SOS | `Mix` | `FluxMix` | `GritMix` | `Feedback` | **KeyInterval** (A) → platform |

The `ParamId` names are granular-flavored (the platform's vocabulary); **a non-granular engine just interprets whichever it cares about** (delay reads `Size/Pos/Speed/Mix` as time/feedback/pitch/mix). `Tempo` and `KeyInterval` are *not* engine params — the platform writes them straight to the transport. The six plain panel knobs (`Size/Pos/Speed/Env/Mix/ModAmp`) plus the no-capability modifier layers are what a single-deck engine receives via `set_param`; `ModSpeed` is unreachable (it routes to `set_mod_speed`), and `Aux`/`AltPos` need `CapAux`/`CapAltPos`.

## The transport (shared clock)

The clock is a **platform service**, not part of any engine. `ctx.transport` (read-only `ITransport`) gives `tempo()`, `source()`, `is_external_sync()`, `key_interval()`, `is_key_sub_quarter()` and `set_on_tick(cb)`. A tick is a `TransportTick {index, tick, key, quarter, tempo, reset}` — `index` is a monotonic counter of divided ticks (use it for step placement); `reset` means the grid realigned (realign your own sequencer). `delay` reads tempo; `edrums` subscribes and steps; a non-synced engine ignores it entirely.

## Pitfalls (the ones that have burned authors)

- **Static Faust tables overflow `.bss`** — `os.osc`'s 64 KB `rdtable` did (98 KB over). Use `os.m_oscsin`.
- **Third-party globals collide with `app.cpp`** — stmlib's `namespace impl` vs `AppImpl impl`. Use PIMPL.
- **`-DTEST` host-only** — stmlib gates ARM `ssat`/`usat`/`vsqrt` asm behind `#ifndef TEST`; desktop tests define `TEST`, firmware must not.
- **`M_PI`** is not in `<cmath>` under strict `-std=c++17` on `arm-none-eabi` — define `-DM_PI`.
- **`-Os` per engine** for a large DSP that won't fit `SRAM_EXEC` at `-O2`.
- **gen~ `t_sample` is `double` off-target** (no `GENLIB_USE_FLOAT32` unless ARM) — desktop builds of a gen~ engine must pass `-DGENLIB_USE_FLOAT32` or read floats as doubles and run off the block end. `host/Makefile`'s `GIGAVERB_FLAGS` does; `genlib_arena.cpp` `static_assert`s on `sizeof(t_sample)` to fail at compile time.
- **gen~ engines: `make clean` between switches** (shared object basenames + a stale-`.d` mtime race).

## Resources

| Document | What it covers |
|---|---|
| `docs/architecture.md` | platform/engine decoupling, layer map, execution model, memory model |
| `docs/engine-types/README.md` + `cpp.md` / `faust.md` / `gen.md` | the three methods and how to choose |
| `docs/engines/README.md` | contract, transport, knob grammar, build/flash, the engine table |
| `docs/engine-layout.md` | which files belong to platform vs contract vs engine |
| `docs/source-guide.md` | source-tree navigational map |
| `docs/dev/<name>-impl.md` | per-engine impl notes (the shipped engines' gotchas) |
| `src/engine/iengine.h`, `engine_params.h`, `engine_context.h`, `itransport.h`, `arena.h`, `engine_select.h` | the contract (see [references/iengine-contract.md](mdc:references/iengine-contract.md)) |
| `src/engine/passthrough/passthrough_engine.h` | the minimal reference engine |