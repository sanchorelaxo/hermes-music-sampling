---
name: "spotykach-engine-authoring"
description: "Use when writing Spotykach firmware or sk-engines DSP engines, or when the unit will not flash / enter DFU."
version: 2.2.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["spotykach", "sk-engines", "firmware", "engine", "daisy", "stm32h7", "granular", "faust", "gen~", "cpp", "dsp", "embedded", "authoring"]
    related_skills: ["spotykach"]
---

# Spotykach firmware & engine authoring

Two codebases run on the same Spotykach hardware and **they are not the same firmware** — most mistakes come from mixing them up. The manufacturer repo is the authority on device behaviour; the fork is a platform/engine restructure of it.

## When to Use

- Modifying or extending the shipped Spotykach firmware (DSP, an FX, a mode, a pad gesture, storage, MIDI).
- Writing a **new engine** (a whole different DSP behind the same panel) on `shakfu/sk-engines`.
- Answering "how does the device actually behave?" — knob grammar, pad gestures, clock, memory budget, bootloader.
- Debugging a link failure (`SRAM_EXEC` / `.bss` overflow), a click on FX engage, or an SD-load hang on this platform.
- The unit will not take a flash: no "DFU in FS mode" in the browser programmer, Reset does nothing, or a previous update was interrupted (Part 5).

Not for *playing* the device or installing/removing shipped engines — that is the `spotykach` skill.

## The two codebases

| | **Official (manufacturer)** | **sk-engines (fork)** |
|---|---|---|
| Repo | https://github.com/Synthux-Academy/Spotykach | https://github.com/shakfu/sk-engines |
| What it is | the shipped product: a **two-deck granular looper** (Reel / Slice / Drift) with a fixed FX chain | that firmware restructured into **fixed platform + one swappable `IEngine`**, selected at build time |
| Abstraction | none — `Core` owns `Deck`s directly; no `IEngine`, no `engine/` dir, no `engine_select.h` | `IEngine` contract, `src/engine/<name>/`, `ENGINE=` picks one engine per binary |
| Adding code | edit the tree directly; new `.cpp` files are compiled by wildcard | new engine dir **plus** registration in two places |
| Grit FX | **3 modes** — Drive, Reduce, Filter | **2 modes** — Drive, Reduce (port of an older snapshot) |
| AXI SRAM split | `SRAM_EXEC` 256K / `SRAM` 256K | `SRAM_EXEC` 260K / `SRAM` 252K |
| Big buffers | static `DSY_SDRAM_BSS ALIGN32K` arrays in `src/hw/buffer.sdram.cpp` | placement-new into a 48 MB `ctx.arena` |
| Tests | none (build + hardware) | `host/` headless tests + `make check-boundary` |
| Reach for it when | you want new behaviour on the real instrument | you want a new *instrument* |

**Ground rule:** never settle a semantics question by reading the fork alone. The fork reimplements manufacturer behaviour and can lag it (its `granular` engine has no `Filter` Grit mode and no `Config`/`Tempo`/`SynchClock` modules).

---

# Part 1 — The official firmware

## 1.1 Stack, clone, build, flash

STM32H750IB, libDaisy + DaisySP, `-std=c++17`, `-ffast-math`, FatFS on, bare metal (no RTOS). `main.cpp` instantiates one `static Application app`; `app.cpp` holds the single `static AppImpl impl` (composition root over `Core`, `CoreUI`, `Hardware`, `Settings`, `Storage`).

```text
git clone --recursive https://github.com/Synthux-Academy/Spotykach
# submodules: lib/libDaisy -> github.com/bleeptools/libDaisy  (ws2812 + MPR121/MIDI changes: REQUIRED)
#             lib/DaisySP  -> github.com/electro-smith/DaisySP
make -j8 libs && make -j8        # link prints SRAM_EXEC usage = the binding budget
make program-dfu                 # after putting the unit in DFU mode
```

DFU: hold **Reset** on the back panel ~3 s → `AppImpl::Loop()` sees `GetBootButtonHeldTime() >= 3000` → `System::ResetToBootloader(DAISY_INFINITE_TIMEOUT)`; the UI stops running, then `make program-dfu`. The app is linked for SRAM (`APP_TYPE = BOOT_SRAM`, `LDSCRIPT = alt_sram.lds`) and started by the in-tree `bootloader-spotykach-v2.bin`; README is explicit that bootloader and app are separate images, so flashing one leaves the other intact. If the device will not enumerate (no "DFU in FS mode"), see **Part 5**.

`CPP_SOURCES` wildcards `src/core/`, `src/core/fx/`, `src/hw/`, `src/ui/`, `src/memory/` — a new file compiles with **no registration**, and a stray scratch file compiles silently. `DEBUG=1` → `-DINFS_LOG=1`; the commented `METER` define in `app.cpp` reports DSP load.

## 1.2 Execution model

| Context | Rate | Content |
|---|---|---|
| Audio ISR (`AudioCallback` → `ProcessAudio`) | 48 kHz / 96 frames | `ProcessAnalogControls()`, `_ui.tick()`, `read_cv()`, `_core.process(in, out, 96)` — all DSP |
| TIM5 (`T5Callback`) | 250 Hz | `process_gate_in()`, `_core.prepare()`, LED render every 4th tick (~62.5 Hz) |
| DAC ISR (`DACCallback`) | audio rate | modulator sources → CV outs |
| `main()` | free-running | boot-button check, `_ui.process()`, `_storage.process()` |

- **No allocation, blocking, or SD/flash in `process()`.** SD work lives in `Storage`, pumped from the main loop.
- **The UI never mutates DSP state directly.** `Deck::set_mode/trigger/toggle_play/clear` *post* commands, drained by `Deck::process_commands()` at the top of each block. Follow that for new async actions.
- Smooth everything a knob can jump: `OnePoleSmoother`/`Smooth`, `SoftSwitch` crossfades.

## 1.3 Audio graph

```text
Core::process(in, out, 96)  per sample:
  route        Stereo: both decks get stereo in | DoubleMono: A=in[0], B=in[1]
  Deck::process_out   Generator (granular/slice/drift) -> in/out mix (SOS) -> Fx
                      Fx = Grit (Drive|Reduce|Filter) then Flux (5 s echo)
  Deck::process_in    record: external input OR the *other deck's* output
                      (Source::internal = generative / ping-pong path)
                      -> detector (auto-start on threshold) -> Buffer::write (overdub fb)
  Modulator::follow   envelope follower / LFO per deck
  Panner -> XFade (A/B) -> Click (metronome) -> SoftLimit
```

Buffer semantics worth knowing before touching `Buffer`: `kRecordFade = 192` (4 ms) fades around punch in/out, `_feedback` = overdub amount (default `0.95`), `cut()` + `read_reset_did_cut()` = tape-style erase on recross, `rec_size()` = realized loop length (not the 42 s capacity).

## 1.4 Memory

`SRAM_EXEC` 256 KB is **code** (`.text`+`.rodata`), `SRAM` 256 KB is **data** (`.bss`+heap+stack), DTCMRAM 128 KB holds `.data`, SDRAM 64 MB holds the loop/echo/detector buffers — all **statically** allocated with `DSY_SDRAM_BSS ALIGN32K`: 3 source buffers (A, B, undo) of `42 s × 48 kHz × 8 B` ≈ 16.1 MB each (~48.4 MB total) plus 4 × 5 s echo buffers (~3.84 MB). A large static array in the wrong region is the classic build failure. Full numbers, storage layout, `config.txt` keys and the MIDI CC map: [references/official-firmware.md](mdc:references/official-firmware.md).

## 1.5 Extending it

- **New FX**: header + `.cpp` under `src/core/fx/`, member of `Fx`, called from `Fx::process` (order Grit → Flux; the Flux send is a crossfade, so inserting between them changes the feedback path), big buffers from `src/hw/buffer.sdram.cpp`, control normalized via `MValue` in `core.ui.cpp`, LED in `_draw_fx`, CC in `core.midi.cpp` + `enum CC` in `core/config.h`, engage through `SoftSwitch`.
- **New mode**: touches `Deck::_validate_mode`, `Generator`/`Vox`, `CoreUI::tick` (SIZE/ENV change meaning per mode — see Part 2) and the ring LEDs. All four, or it half-works.
- **New pad gesture**: `core.ui.pads.cpp` (`_on_pad_touch`/`_on_pad_release`/`_on_alt_touch`); cue an intent there, act in `CoreUI::tick` (`_ply_cue`, `_rec_cue`, `_hold_clear`).
- **Clock/sequencer**: `Driver` owns tempo/source/PPQN/key interval, `SynchClock`/`Tempo`/`Divider` do the math, `Track` replays `Event`s. Do not add a second clock.
- **Do not** re-purpose the granular core to host a different instrument — that is what the fork is for.

---

# Part 2 — The knob grammar (shared vocabulary)

Manufacturer behaviour, verified line by line in `CoreUI::_process_ui_queue()` (`src/ui/core.ui.cpp`, the `potMoved` switch). The fork preserves this grammar and forwards it as normalized `ParamId`s (Part 3.7).

Every knob calls `MValue::process(val, layer_is_active, changing_id[, threshold])` — several candidate layers per knob, exactly one armed at a time. The **Flux/Grit pads are per deck** (`FluxA`/`GritA` vs `FluxB`/`GritB`); Alt and the tap-hold are global. Holding either FX pad on a deck also *blocks* that deck's base layers (`fx_a_touched` gates POS, pitch and mix).

| Knob | default | Flux held (that deck) | Grit held (that deck) | Alt held | Tap-switch hold |
|---|---|---|---|---|---|
| POS | `voxs().set_start()` | `flux().set_fb_norm()` | `grit().set_character()` | `set_start_offset_interval()` — only if the deck has a cue | — |
| ENV | `set_shape()` | — | — | `set_env_size()` — Drift only (ignored in Reel/Slice) | — |
| SIZE | `set_size()` (Reel/Slice) | — | — | `set_win_size()` — Drift only | Slice: `set_size_quarters()` + tempo-by-size |
| PITCH | `set_speed()` (Reel/Drift) / `set_pitch()` (Slice); while a deck is in SlotSelect this scrolls tapes instead | `flux().set_time_norm()` | `grit().set_intensity()` | pitch-quantize: MValue threshold drops to `.1`, and the quantize flag is armed for the next move | — |
| MODFREQ | `mod().set_speed_norm()` | — | — | mod sync flag → `set_speed_norm(v, sync)` | **Tempo** (A) / PanSpeed (B) — transport/panner, not the engine |
| MOD_AMT | `mod().set_amp_norm()` | — | — | — | ClickMix (A) / PanRange (B) |
| SOS | `set_inout_mix()` | `flux().set_mix_norm()` | `grit().set_mix()` | `set_feedback()` | **KeyInterval** (A only — deck B has no key-interval layer) |

The CROSSFADE knob is outside this table: it calls `Core::set_mix()` directly (A/B blend), never an engine parameter.

Tap switch (`_process_switches`, edge-detected, 4 ms debounce): **Alt held** → `driver().toggle_source()` (clock source); **Grit pad held** → `grit().switch_mode()` *and re-seed all three Grit MValues* (`intensity`, `mix`, `character`) from the new mode — this is why a mode switch never jumps the knob; **Flux pad held** → `flux().switch_mode()`; **plain tap** → `driver().tap_tempo()` (skipped when externally synced) and begins the tap-hold window, whose release ends the alternate layer. Grit modes cycle Drive → Reduce → Filter; Flux modes FreeDelay ↔ ClockedDelay.

Every knob is `MValue` (pickup) — it will not jump until it crosses the stored value, which is why any mapping change must re-seed the pickup. New controls follow the same contract: normalized at the boundary, pickup, smoothing inside DSP, re-seed on any mapping change.

---

# Part 3 — A new engine (sk-engines fork)

Start from the fork's own docs (`docs/architecture.md`, `docs/engines/README.md`, `docs/engine-types/*.md`) and treat Parts 1–2 as the behaviour spec it is trying to match. Full API surface (enums, context/arena, transport tick, no-op defaults): [references/iengine-contract.md](mdc:references/iengine-contract.md).

## 3.1 The model

Fixed platform (`src/ui/`, `src/hw/`, `src/memory/`, `src/transport/`) plus exactly one DSP engine, chosen at build time. The platform is polymorphic over `IEngine` only and includes no engine DSP header — `make check-boundary` (prerequisite of `all`) greps `hw/ui/memory/transport` for `engine/granular/` includes and fails the build. The engine lives in `src/engine/<name>/` and owns its DSP privately; `src/app.cpp` is the composition root, the only place `ActiveEngine` is named. A minimal engine (`passthrough`) is a few dozen lines.

## 3.2 Choosing a method

| Method | You write | Codegen | Use when | Examples |
|---|---|---|---|---|
| **Native C++** | DSP *and* the `IEngine` wrapper | none | not a pure signal graph: sequencers, SD streaming, dual-deck, custom display, vendored C++ DSP or audio VM | granular, delay, qdelay, edrums, reso, softcut, tape, shuttle, bard, radio, glitch, pstretch, mosc, graincloud, passthrough; csound, chuck |
| **Faust (cyfaust)** | DSP in `.dsp`; wrapper from a JSON manifest | `make faust-kernels` / `make faust-engine` | closed-form DSP, esp. several interchangeable algorithms | chorus, filter, voice (generated); reverb (3 kernels, hand-written wrapper); tape (`tapefx` kernel inside a native engine) |
| **gen~ (gen-dsp)** | a Max `gen~` export + a JSON manifest; **no C++** | `make gen-engine` → whole engine dir | you already have a `gen~` graph | gigaverb |

An engine can mix methods: `tape` is native C++ around an embedded Faust `tapefx` kernel, and `reverb` is a hand-written engine over three Faust kernels (`dattorro`, `greyhole`, `zita`) with no manifest at all. gen~ reports `capabilities() = 0` (stereo + knob params only).

## 3.3 Lifecycle

```cpp
class MyEngine : public IEngine {
  void init(const EngineContext& ctx) override;   // arena, sample rate/block, transport subscribe
  void prepare() override;                        // non-RT: called from the main loop, alongside _ui/_storage.process()
  void process(const float* const* in, float** out, size_t size) override;  // 48 kHz / 96 frames, ISR
  Capabilities capabilities() const override { return CapOwnDisplay | CapDualDeck; }
  void set_param(ParamId, DeckRef::Ref, float) override;   // normalized 0..1
  void render(DisplayModel&) override;                     // if CapOwnDisplay
};
```

`set_param` is normalized: scale inside (`v*0.95` feedback, `exp2f((v-0.5)*2)` ratio; reso passes `v` straight to Rings `damping`). Categorical switches arrive via `set_config(ConfigId, deck, int)`. No allocation, blocking or SD in `process()`.

## 3.4 Native C++ checklist

1. Subclass `IEngine` in `src/engine/<name>/<name>_engine.{h,cpp}`; own the DSP privately (never reuse `src/engine/granular/`).
2. Return the right `capabilities()` bitset; override only what you support.
3. Map `ParamId`s; own mode fanout internally (the platform never sees your mode).
4. `CapTapeStorage` → implement the `audio_*` byte port; tempo → consume `ctx.transport`.
5. `CapOwnDisplay` → fill `render(DisplayModel&)`.
6. Register (§3.6).
7. Add a `host/` test, then `make check-boundary && make -j8 ENGINE=<name>` and watch `SRAM_EXEC`.

Copy the closest reference: **`passthrough`** (minimum: header-only, `in → out`, meters), **`delay`** (transport tempo, clean scaling), **`edrums`** (ticks, voices, `set_config`), **`reso`** (PIMPL + Rings + block chunking), **`csound`/`chuck`** (vendored VM, QSPI).

PIMPL is **mandatory, not stylistic**, when a vendored dependency declares a global colliding with the composition root — `reso` needs it because `stmlib.h` declares `namespace impl` and `app.cpp` has `static AppImpl impl;`.

## 3.5 Memory

- Big state from `ctx.arena` (48 MB of the 64 MB SDRAM, `EngineArena {base, bytes}`), sub-allocated with the `Arena` bump allocator (`src/engine/arena.h`) — never a static member, which lands in `.bss` and eats the 252 KB `SRAM` data region.
- The binding budget is **code**: `SRAM_EXEC` 260 KB (fork); `pstretch` selects `linker/alt_sram_pstretch.lds`, which re-splits the same 512 KB to 200 KB / 312 KB. A big engine may need its Makefile branch at `-Os`.
- Chunk if your DSP's max block < 96 (`reso` runs Rings at 24, four chunks).

## 3.6 Generated engines & registration

```text
make faust-engine MANIFEST=src/engine/chorus/chorus.json   # kernel + wrapper + build + diagram
make -j8 ENGINE=chorus
.venv/bin/python scripts/gen_engine.py /path/to/export myverb   # gen~ bootstrap
make gen-engine MANIFEST=src/engine/myverb/myverb.json FORCE=1
make gen-engine MANIFEST=src/engine/myverb/myverb.json NOGEN=1 FORCE=1   # glue only
```

The manifest maps panel knobs to kernel slider labels (ranges read back at `init()`) plus `meter`/`soft_limit`/`wet_dry`/`color` and a `deck_mode`: default = one kernel (`chorus`); `"parallel"` = two instances of one mono kernel, A→left / B→right (`filter`); `"series"` = two kernels A→B on `FaustChainEngine<Traits>` (`voice`). `.dsp` rules: flat `hslider`s, each 0..1. For gen~, `"backend": "gen"` + an `export` path; `scripts/gen_engine.py <name> --remove` unwires one; `make gen-engines` regenerates all.

Both generators **upsert** their registration inside markers (`// >>> faust:chorus >>>` …), so hand-editing is never needed:

```make
ifeq ($(ENGINE), myengine)
  C_DEFS += -DSPK_ENGINE_MYENGINE
  ENGINE_SOURCES = $(wildcard src/engine/myengine/*.cpp)
endif
```

```cpp
// src/engine/engine_select.h
#elif defined(SPK_ENGINE_MYENGINE)
  #include "engine/myengine/myengine_engine.h"
  namespace spotykach { using ActiveEngine = MyEngine; }
```

`build/.engine-stamp` forces `app.o` (the only define-dependent TU) to rebuild on a switch; generated engines still need `make clean`.

```text
make -j8 libs | make -j8 ENGINE=delay | make ENGINE=delay program-dfu | make engine-delay
make check-boundary | make faust-kernels | make gen-engines
```

QSPI engines (`csound`, `chuck`) build via `make engine-csound` / `engine-chuck`, need `scripts/fetch_csound.sh` / `fetch_chuck.sh` once, and move code size to the 8 MB QSPI flash — CPU headroom then limits you. Every engine needs the **same `bootloader-spotykach-v2.bin`** as the official firmware.

## 3.7 ParamIds (fork vocabulary)

`ParamId` is the fork's name for the Part 2 table — a non-granular engine picks the names it uses (`delay`: `Size`→time, `Pos`→offset, `Speed`→pitch, `Mix`→wet):

```text
Pos FluxFb Env EnvSize Size Win PolySlice Speed FluxIntensity GritIntensity
FluxMix GritMix Feedback Mix ModSpeed ModAmp | global: Tempo ClickMix PanSpeed
PanRange KeyInterval Crossfade | capability-gated: AltPos (CapAltPos), Aux (CapAux)
```

`ModSpeed` never arrives via `set_param` (it routes to `set_mod_speed(deck, value, sync)`); the globals never reach `set_param`. `DeckLayout` (`single|slice|chord|none`) tells the platform how mode-dependent SIZE/ENV behave — granular maps Reel→`single`, Slice→`slice`, Drift→`chord`; a modeless engine returns `single`. Transport: `ctx.transport` gives `tempo()`, `source()`, `is_external_sync()`, `key_interval()`, `is_key_sub_quarter()`, `set_on_tick(cb)`; a tick is `TransportTick {index, tick, key, quarter, tempo, reset}` (use `index` for step placement; `reset` = realign your sequencer).

---

# Part 4 — Pitfalls

**Both trees**

- **`.bss`/`.text` overflow is the classic failure** — a large static array (or Faust `os.osc`'s 64 KB `rdtable`, which once overflowed by 98,808 B) blows the budget with only hundreds of bytes left. Official: `DSY_SDRAM_BSS ALIGN32K`. Fork: `ctx.arena`. Faust: use `os.m_oscsin` instead of `os.osc`.
- **SD/flash from the audio path** hangs the ISR.
- **`M_PI`** is absent from `<cmath>` under strict `-std=c++17` on `arm-none-eabi` — define `-DM_PI`.
- **`-DTEST` is host-only** — stmlib gates ARM `ssat`/`usat`/`vsqrt` asm behind `#ifndef TEST`.
- **No hard switching** — every on/off goes through `SoftSwitch`; click on engage is a bug.
- **`-Os`** for a DSP that will not fit `SRAM_EXEC` at `-O2`.

**Official only**

- libDaisy is a **fork** (`bleeptools/libDaisy`) — clone `--recursive`.
- Wildcard sources → scratch `.cpp` files compile silently.
- Deck control is queued: a setter called from the UI lands after the current block.

**Fork only**

- Third-party global collisions with `src/app.cpp` → PIMPL.
- gen~ `t_sample` is `double` off-target — desktop gen~ builds pass `-DGENLIB_USE_FLOAT32`; `genlib_arena.cpp` `static_assert`s on `sizeof(t_sample)`.
- gen~ engines: `make clean` between switches (shared object basenames + stale-`.d` mtime race).
- Its `granular` engine is an **older snapshot**: two Grit modes (no `Filter`), no `Config`/`Tempo`/`SynchClock`. Behaviour questions → official repo.

---

# Part 5 — Troubleshooting a flash that will not happen

Manufacturer guidance (Synthux Notion, *Spotykach Firmware → Troubleshooting steps*) for the player-facing path. It applies to **both trees**: `make program-dfu` (Part 1.1) and the browser WebUSB programmer behave identically at the USB level, because both talk to the same in-tree `bootloader-spotykach-v2.bin`.

**The default failure is not a brick — it is the device never enumerating.** After Reset, the Daisy web programmer's port list stays empty (or never shows *"DFU in FS mode"*). Work the list in order, cheapest first.

**Cable and port**

- **Data cable, not a charge-only cable.** This is the single most common cause. Prove it by using the same cable to move files to a phone/external drive or to talk to a MIDI keyboard. Powered hubs are usually fine with a good cable (confirmed by a user on an older MacBook Pro); unpowered hubs and adapters are not — plug straight into the machine.
- **Different USB port, then a different computer**, before touching drivers.
- **Rear USB-C on the main PCB only** — not the USB port on the Seed.

**Getting into bootloader mode**

- Hold rear **Reset** 3–5 s, release when the LED ring **glows white** (pads breathe white). The application firmware sees this as `GetBootButtonHeldTime() >= 3000` and resets into DFU.
- **Button does nothing → plug in power while holding Reset.** Normal boot can fail after an interrupted update (power loss mid-flash); the bootloader itself is a separate image and survives a failed app flash, so this is the failsafe.
- The rear button has both roles: normal update while the app runs, forced DFU when the app cannot start.

**Host side**

- **Google Chrome only** — WebUSB. Firefox/Safari cannot flash. Keep Chrome current (`chrome://settings/help`), and fully quit and relaunch all Chrome windows when the device is not listed.
- **Windows:** install the driver with **Zadig** once (`https://daisy.audio/tutorials/zadig`). If Zadig still does not surface the device, uninstall Zadig and/or Chrome, reboot, reinstall.
- **Verify enumeration independent of the programmer:** Windows Device Manager (should show a Daisy bootloader entry), macOS System Information → USB, and Chrome `chrome://device-log` (connect in bootloader mode and watch whether the browser sees it at all — this separates "Chrome cannot see it" from "the programmer page is broken").

**After a successful flash**

- Windows flow reads `Erasing Daisy → Flashing Daisy → Done`, then returns to the flash screen. Once the LED rings are back to **block orange**, **unplug and replug** to restart cleanly.

**Escalation.** If it still does not respond, collect a short video of the current state plus the manufacturer checklist — cable is data-capable and tested, bootloader white LEDs, direct USB port, several ports tried, current Chrome, Chrome and machine restarted, Zadig installed (Windows), device visible in Device Manager / System Information / `chrome://device-log`, Chrome+Zadig reinstalled, another computer tried — and post to the Synthux Discord `#spotykach-firmware` channel: `https://discord.com/channels/802197755442626590/1345797126038487122`.

**For firmware work specifically:** if you are debugging your own build rather than a stock update, reproduce the same steps *before* suspecting the binary, then check that you built and flashed the same artifact — `make program-dfu` flashes whatever is already in `build/` and does **not** rebuild (`make ENGINE=<name> && make program-dfu`, or `make ENGINE=<name> program-dfu`).

---

# References

| File | Contents |
|---|---|
| [references/official-firmware.md](mdc:references/official-firmware.md) | memory map + SDRAM table, buffer semantics, SD layout, `config.txt` keys, MIDI CC map, boot/DFU detail, source-map |
| [references/iengine-contract.md](mdc:references/iengine-contract.md) | the fork's full `IEngine` surface: every enum, `EngineContext`, `EngineArena`, `ITransport`, `TransportTick`, default methods |

In-repo docs: `docs/architecture.md`, `docs/engines/README.md`, `docs/engine-layout.md`, `docs/source-guide.md`, `docs/engine-types/{cpp,faust,gen}.md`, `docs/dev/<name>-impl.md`.
