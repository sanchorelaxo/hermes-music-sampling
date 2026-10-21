# Official Spotykach firmware — reference detail

Deep detail for `https://github.com/Synthux-Academy/Spotykach` (the manufacturer firmware). The behavioural summary and authoring workflow live in `SKILL.md`; this file is the numbers and tables you look up while working.

Everything here was read out of the repo, not inferred.

## Memory map (`alt_sram.lds`, STM32H750IB)

```text
FLASH      0x08000000  128K   bootloader only
DTCMRAM    0x20000000  128K   .data (tightly coupled, fast)
SRAM_EXEC  0x24000000  256K   .isr_vector + .text + .rodata   <-- CODE BUDGET
SRAM       0x24000000+256K  256K   .bss + heap + stack        <-- DATA BUDGET
RAM_D2     0x30000000   32K   .sram1_bss (audio DMA buffers)
RAM_D2CACHE 0x30000000+32K  256K   .d2_bss
RAM_D3     0x38000000   64K
BACKUP_SRAM 0x38800000    4K
ITCMRAM    0x00000000   64K
SDRAM      0xc0000000   64M   .sdram_bss                    <-- loop / echo / detector
QSPIFLASH  0x90000000    8M   unused by the official build
```

`_estack = 0x20020000` (top of DTCMRAM). libc/libm/libgcc are `DISCARD`ed.

## SDRAM allocation (`src/hw/buffer.sdram.cpp` / `.h`)

Static, not arena — every array is `DSY_SDRAM_BSS ALIGN32K` (`__attribute__((aligned(32768)))`):

| Buffer | Size |
|---|---|
| source buffer A / B / undo (3×) | `kSourceMaxSeconds (42) * kSampleRate (48000) * sizeof(Frame)` ≈ 16.1 MB each ≈ 48.4 MB total |
| echo L/R per deck (4×) | `48000 * 5` floats ≈ 0.96 MB each ≈ 3.84 MB total |
| detector windows, slice-point table (`kMaxSlicePointCount = 256`) | small |

The `ALIGN32K` (`__attribute__((aligned(32768)))`) matters: SDRAM goes through the write cache, and a ~16 MB array placed off that boundary straddles cache lines in ways the DMA-friendly layout is not written to tolerate. Keep new SDRAM buffers in `buffer.sdram.cpp` with the same attribute.

## Deck buffer semantics (`src/core/buffer.cpp`)

- `kRecordFade = 192` samples (4 ms) fade in/out around punch-in / punch-out — a recorded loop never clicks at its seam.
- `_feedback` = overdub amount, default `0.95`.
- `cut()` + `read_reset_did_cut()` = the tape-style erase-on-recross when play position wraps past the punch point.
- `rec_size()` = the **realized** loop length (what was recorded), distinct from the 42 s capacity.
- `Buffer::read` fades with `hann` windows at loop edges; `Buffer::write` mixes input + feedback.

## Storage layout (FatFS on SD card)

```text
SK/config.txt                       device config (see below)
SK/MEM                              preload pointer (which tape+slot to load at boot)
SK/<B|G|P|R|T|Y>/<1..6>.wav         six colour-named tapes × six slots
```

Both decks address the same tape set (there is one tape library, not one per deck). A `.wav` carries cue points that seed the Slice engine's slice table; loading is a chunked main-loop state machine (`Storage::process`), never an audio-path operation.

### `SK/config.txt`

Parsed by `Config::fill` (`src/core/config.cpp`). Keys, all optional:

| Key | Meaning |
|---|---|
| `mid_ch_a` / `mid_ch_b` | 1-based MIDI channel per deck (stored internally as `val-1`) |
| `mid_ps_a` / `mid_ps_b` | honour MIDI transport start/stop per deck |
| `slc_mn_a` / `slc_mn_b` | mono (one slice voice) vs poly slice playback |
| `cue_sm_a` / `cue_sm_b` | `CueSizeMode`: `0` ignore / `1` snap / `2` free — how WAV cue points set slice size (default `ignore`) |
| `pre_load` | preload `SK/MEM` at boot |

Parser gotcha: `Config::fill` **drops every space** and takes the first **8 characters** as the key (`line_size = 8`), matched with `memcmp` against the literals above. So keys are exactly 8 chars — a longer or differently abbreviated key silently never matches, and `mid_ch_a 2` / `mid_ch_a2` parse identically. Unknown lines are ignored; `_is_loaded` only drives re-application.

## MIDI CC map (`src/core/config.h`, `enum CC`)

```text
 3 CrossFade    14 RecExt      15 RecInt      20 Start       21 Offset
22 Size         23 Env         24 Pitch       25 IOMix       26 DeckFB
27 EnvSize      28 WinSize     85 Fwd         86 Rev         89 ModCycle
90 ModGlow     102 GritOn     103 GritIntens 104 GritMix    105 FluxOn
106 FluxIntes  107 FluxFB     108 FluxMix    109 GritChar
```

Clock: internal 48 PPQN (`kPPQNIntern`); external = TS-4 analog or MIDI clock.

## Boot / flash detail

- `APP_TYPE = BOOT_SRAM`, `LDSCRIPT = alt_sram.lds`, `BOOT_BIN = bootloader-spotykach-v2.bin` — the app is linked to run from AXI SRAM and is copied there by the bootloader.
- Bootloader entry: hold **Reset** on the back panel ~3 s → `AppImpl::Loop()` sees `GetBootButtonHeldTime() >= 3000` → `System::ResetToBootloader(DAISY_INFINITE_TIMEOUT)`. The UI stops; the device is now a DFU target. Then `make program-dfu`.
- Bootloader and app are separate images; flashing one leaves the other intact. A USB re-plug may be needed after DFU.
- `README.md` documents that the bootloader enables USB DFU firmware updating from the **external** (host) connection.

## Build flags that matter

```make
TARGET      = spotykach
CPP_STANDARD = -std=c++17
C_USR_FLAGS  = -ffast-math -funroll-loops
USE_FATFS    = 1
CPP_SOURCES  = main.cpp app.cpp $(wildcard src/core/*.cpp) $(wildcard src/core/fx/*.cpp) \
               $(wildcard src/hw/*.cpp) $(wildcard src/ui/*.cpp) $(wildcard src/memory/*.cpp)
```

- New `.cpp` under `src/core/`, `src/core/fx/`, `src/hw/`, `src/ui/`, `src/memory/` is picked up by the wildcard — **no registration step** (and no safety net: scratch files get compiled).
- `DEBUG=1` → `-DINFS_LOG=1`.
- `METER` (commented at the top of `app.cpp`) reports DSP load — use it after adding processing; CPU headroom, not just link fit, is the real constraint.
- Submodules: `lib/libDaisy` → `github.com/bleeptools/libDaisy` (fork: ws2812 driver, MPR121/MIDI changes), `lib/DaisySP` → `github.com/electro-smith/DaisySP`. Stock libDaisy will not build this firmware.

## Execution model

| Context | Rate | Content |
|---|---|---|
| `AudioCallback` → `AppImpl::ProcessAudio` | 48 kHz / 96 frames | `_hw.ProcessAnalogControls()`, `_ui.tick()`, `_ui.read_cv()`, `_core.process(in, out, 96)` |
| `T5Callback` (TIM5) | 250 Hz | `_ui.process_gate_in()`, `_core.prepare()`, LED render every 4th tick (~62.5 Hz) |
| `DACCallback` | audio rate | modulator sources → CV outs, `__USAT(x * (1<<12), 12)` |
| `main()` | free-running | boot-button check, `_ui.process()`, `_storage.process()`, debug log |

`Core::prepare()` → `Deck::prepare()` is where per-deck non-RT housekeeping (slice re-analysis, fade prep) happens — this is the official equivalent of the fork's `IEngine::prepare()`.

Deck control is **queued**, not immediate: `Deck::set_mode` / `trigger` / `toggle_play` / `clear` post commands that `Deck::process_commands()` drains at the top of each block. Any new async action should follow that pattern rather than mutating DSP state from the UI context.

## Extending recipes (detail)

### Add an effect to the deck chain

1. New `src/core/fx/fx.<name>.h` + `.cpp`; hold it as a member of `Fx` in `src/core/fx/fx.h`.
2. Add it to `Fx::process` — the live order is **Grit → Flux**, and the Flux send is a crossfade, so inserting between them alters the feedback path.
3. `init(sample_rate)`; if it needs a big buffer, add the array in `src/hw/buffer.sdram.cpp` as `DSY_SDRAM_BSS ALIGN32K` and hand the pointer in through `Fx::Params`.
4. Bind a control: normalizer in `src/ui/core.ui.cpp` (`_flux_fb[ref]`-style, `MValue`), LED state in `_draw_fx`, CC in `src/ui/core.midi.cpp` + `enum CC` in `src/core/config.h`.
5. Use `SoftSwitch` for the wet/dry engage — no hard switching.

### Add or change a deck mode

`Mode` is in `src/core/mode.h`. A mode touches: `Deck::_validate_mode`, `Generator`/`Vox` behaviour, `CoreUI::tick` (SIZE/ENV meanings differ per mode — see the knob table in `SKILL.md`), and the ring-LED drawing. Add a mode to all four or it will half-work.

### Add a pad gesture

`src/ui/core.ui.pads.cpp`: `_on_pad_touch` / `_on_pad_release` / `_on_alt_touch`. Alt is tested as `_touched.test(Alt)` inside other handlers; the tap-hold switch (`_tap_hold`, `Hold<ms>`) gates the long-press layer. Cue an intent in the handler and act on it in `CoreUI::tick` (`_ply_cue`, `_rec_cue`, `_hold_clear`).

### Add clock / sequencing behaviour

`Driver` (`src/core/driver.h`) owns tempo, source, PPQN division and key interval; `SynchClock`, `Tempo`, `Divider` do the math; `Track` records and replays per-deck parameter `Event`s. Do not add a second clock.
