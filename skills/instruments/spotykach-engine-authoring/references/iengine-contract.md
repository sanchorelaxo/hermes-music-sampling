# IEngine contract reference (verbatim-derived from sk-engines)

Authoritative reconstruction of the engine contract, transcribed from the sk-engines headers so you author against the real surface without re-deriving it. Everything below is contract-owned under `namespace spotykach` in `src/engine/`. Keep it as the API reference; the workflow lives in [../SKILL.md](../SKILL.md).

**Scope:** this file documents the **fork** (`shakfu/sk-engines`) only. The manufacturer firmware (`Synthux-Academy/Spotykach`) has no `IEngine`, no `src/engine/`, and no `engine_select.h` — its equivalent is the concrete `Core`/`Deck`/`Fx` graph described in [official-firmware.md](official-firmware.md) and Part 1 of `SKILL.md`. If a member here looks missing on the device, that is why.

## The three required methods + the no-op strategy

`IEngine` (with `SPK_TERMINAL=0`) has exactly three pure-virtual methods — every engine implements these — and **every other method is a no-op default** you override only as needed. `capabilities()` advertises which optional regions are live so the platform knows what to drive.

```cpp
class IEngine {
public:
    virtual ~IEngine() = default;
    // required
    virtual void init(const EngineContext& ctx) = 0;              // alloc/subscribe; save sample_rate, block_size, arena, clock
    virtual void prepare() = 0;                                   // non-RT main-loop housekeeping
    virtual void process(const float* const* in, float** out, size_t size) = 0;  // 48 kHz / 96-frame audio ISR
    // opt-in
    virtual Capabilities capabilities() const { return 0; }       // bitset, see table below
    // params / config / pads / MIDI / CV / gate / storage / LEDs / render — all {} defaults
};
```

Guiding rules encoded in the interface (item-2 "Strategy A" lift):

- **Transport is not on IEngine.** The platform owns a `Transport` service and injects a read-only `ITransport` via `EngineContext` (see below). An engine reads tempo/ticks or subscribes; it cannot command the clock.
- **The contract carries no granular types.** `DeckRef`/`Route`/`ClockSource`/`ModType`/`GritMode`/`DeckSource`/`TransportTick` are contract-owned (`engine/*.h`); `core/…` headers `using`-alias them. You never `#include` the granular looper's DSP.
- `mode.h`'s `Mode` (`Reel/Slice/Drift`) is granular-specific and only leaks through the LED query structs; your engine defines its own modes internally.

## ParamId (the knob vocabulary) — `engine_params.h`

One physical control maps to many `ParamId`s via modifier layers; a single `ParamId` fans out per mode inside the engine's `set_param`. Logical `Params` reach the engine normalized **0..1**.

```cpp
enum class ParamId : uint8_t {
    Pos, FluxFb, Env, EnvSize, Size, Win, PolySlice, Speed,
    FluxIntensity, GritIntensity, FluxMix, GritMix, Feedback, Mix,
    ModSpeed, ModAmp,               // modulator speed/depth
    Tempo, ClickMix, PanSpeed, PanRange, KeyInterval, Crossfade,   // "global"
    AltPos,                          // Alt+POS layer (CapAltPos)
    Aux,                             // per-deck Alt+PITCH selector (CapAux)
    Count
};
```

Interpretation notes (read the header comments for the per-`ParamId` rationale):

- `Tempo`, `ClickMix`, `PanSpeed`, `PanRange`, `KeyInterval`, `Crossfade` are **global** — not engine params; the platform writes them straight to the transport/mixer, so a single-deck engine never receives them via `set_param`.
- `ModSpeed` is unreachable through `set_param` (it routes to `set_mod_speed(deck, value, sync)`).
- `Aux` needs `CapAux`; `AltPos` needs `CapAltPos` — without those capabilities the knob keeps its default meaning.
- The names are granular-flavored; a non-granular engine reinterprets whichever it uses (delay reads `Size`→time, `Pos`→offset, `Speed`→pitch factor, `Mix`→wet).

## ConfigId (categorical config) — `engine_params.h`

Switch-position writes delivered via `set_config(ConfigId, deck, int)`; the selector `int` is the raw switch bits, which the engine maps to its own enums. Separate from the continuous `ParamId` channel because the MValue pickup/threshold/value-display apparatus is meaningless for a categorical.

```cpp
enum class ConfigId : uint8_t {
    Route,       // global: 0=Stereo, 1=DoubleMono, 2=GenerativeStereo (deck ignored)
    ModType,     // per-deck: 0=LFO, 1=Follow
    LfoShape,    // per-deck selector (0/1); engine owns per-deck shape palette
    Mode,        // per-deck: 0=Slice, 1=Reel, 2=Drift
    StartModOn,  // per-deck: 0/1
    SizeModOn,   // per-deck: 0/1
    Count
};
```

`set_config` returns **true iff the value changed** (only `Mode` uses this, so the platform can re-apply size for the new mode). `toggle_grit_mode(deck)` cycles the grit sub-effect and returns `GritReseed {float intensity; float mix;}` so the platform can reseed its MValue pickup.

## DeckLayout — `engine_params.h`

Declares how the mode-dependent SIZE/ENV knobs behave for a deck, so the platform stops reading the granular `Mode` to branch the pot queue/apply pass. Defaults (`single`) suit a modeless engine.

```cpp
enum class DeckLayout : uint8_t {
    single,   // SIZE -> Size (always); ENV -> Env
    slice,    // SIZE -> Size/PolySlice (alt) or tap-hold tempo-fit; ENV -> Env
    chord,    // SIZE -> Size/Win (alt); ENV -> Env/EnvSize (alt)
    none      // uninitialised deck -> SIZE/ENV do nothing
};
```

## Capability bits — `engine_params.h`

A `uint32_t` bitset; each bit opts the engine into a platform toolkit region. The platform gates its behaviour on what's set (e.g. Storage skips tape ops unless `CapTapeStorage`).

```cpp
enum Capability : uint32_t {
    CapRecording     = 1u << 0,
    CapTapeStorage   = 1u << 1,
    CapStepSequencer = 1u << 2,
    CapLaunchQuant   = 1u << 3,
    CapTransport     = 1u << 4,
    CapDualDeck      = 1u << 5,
    CapOwnDisplay    = 1u << 6,   // engine fills DisplayModel in render(); platform blits directly
    CapAux           = 1u << 7,   // claim Alt+PITCH as per-deck selector (ParamId::Aux)
    CapAltPos        = 1u << 8,   // claim Alt+POS knob layer (ParamId::AltPos)
    CapPitchPickup   = 1u << 9,   // route PITCH through pickup-gated path (snap-holding engines)
    CapTerminal      = 1u << 10,  // implements custom SPK_TERMINAL verbs / queries
    CapWavCues       = 1u << 11,  // consume WAV `cue ` chunk markers via on_wav_cues()
};
using Capabilities = uint32_t;
```

## DeckRef / selectors — `deck_ref.h`, `mode.h`

```cpp
struct DeckRef { enum Ref : uint8_t { A, B, Count, None = 0xff }; };   // unscoped (used as array index)

enum class Route : uint8_t { DoubleMono = 1, Stereo, GenerativeStereo };
enum class ModType : uint8_t { Follow, LFO };       // (Note: Follow=0, LFO=1)
enum class GritMode : uint8_t { Drive, Reduce };
enum class DeckSource : uint8_t { external, internal };

struct ClockSource { enum Source : uint8_t { internal = 1, ts4 = 4, midi = 24 }; };  // values ARE external PPQN
enum kKeyInterval : int8_t {   // key-quarter grid in 1/16 units; values used arithmetically as tick divisors
    k1_16 = 1, k1_4 = 4, k2_4 = 8, k3_4 = 12, k4_4 = 16 /*1 bar*/, k5_4 = 20, k6_4 = 24,
    k7_4 = 28, k8_4 = 32, k9_4 = 36, k10_4 = 40, k11_4 = 44, k12_4 = 48, k13_4 = 52,
    k14_4 = 56, k15_4 = 60, k16_4 = 64 /*4 bars*/
};
```

(Note the ordering trap: `ModType{Follow=0, LFO=1}` and `Route{DoubleMono=1, Stereo, GenerativeStereo}` are not zero-based — the comment values in `engine_params.h` document `ConfigId::ModType 0=LFO`, i.e. the switch-bit order, whereas this enum has `Follow` first; rely on the header you are compiling against rather than any prose.)

## EngineContext / EngineArena / Arena — `engine_context.h`, `arena.h`

```cpp
struct EngineArena { uint8_t* base = nullptr; size_t bytes = 0; };   // opaque SDRAM block

struct EngineContext {
    float              sample_rate;      // 48000.0f
    float              block_size;       // 96.0f (frames per process() block)
    EngineArena        arena;            // 48 MB SDRAM block to sub-allocate
    const ITimeSource* time;
    ITransport*        transport;        // read-only clock view (see below)
    IStreamDeck*       stream = nullptr; // SD streaming service (tape/shuttle/radio); null otherwise
    void*              qspi  = nullptr;  // daisy::QSPIHandle* for settings blobs (cast in #ifndef TEST code)
};
```

Carve buffers with the bump allocator — never hold a big delay line as a static member (it lands in `.bss`, overflowing the 252 KB SRAM data region):

```cpp
class Arena {
    explicit Arena(const EngineArena& a);
    template <class T> T* alloc(size_t count, size_t align = alignof(T));  // nullptr if exhausted
    size_t remaining() const;
};
```

## ITransport / TransportTick — `itransport.h`

The engine-facing, read-only clock. Subscribe with `set_on_tick`; otherwise read `tempo()`. The tick event:

```cpp
struct TransportTick {
    uint32_t index;    // monotonic counter of divided ticks since boot (step placement)
    bool     tick;     // a common/divided tick this step
    bool     key;      // a bar boundary (per key-interval)
    bool     quarter;  // a quarter-note boundary
    float    tempo;    // current BPM
    bool     reset;    // grid realigned — realign your own divider
};

struct ITransport {
    virtual float tempo() const = 0;
    virtual ClockSource::Source source() const = 0;
    virtual bool  is_external_sync() const = 0;
    virtual uint8_t key_interval() const = 0;
    virtual bool  is_key_sub_quarter() const = 0;
    virtual void  set_on_tick(std::function<void(const TransportTick&)> on_tick) = 0;
};
```

- `index` is the disposable counter — use it for step placement without tracking your own tick count.
- `reset` carries the normal flags too, so a realign can also fire an immediate downbeat.

## Other noteworthy no-op-default methods

- `take_param_reseed(deck)` — an engine whose deck→value mapping can change underfoot (edrums's drum-swap repoints a deck's knobs) returns true once per change; the platform re-seeds its MValue pickup from `param()`. Default `false`.
- `tempo_to_fit(deck, fraction)` — the BPM that fits `fraction` of the deck's loop (Slice tap-hold gesture).
- `audio_*` group — the SD tape's audio byte port; only needed with `CapTapeStorage`.
- `on_wav_cues(deck, const WavCues&)` — platform-parsed WAV `cue ` markers (sample-frame offsets); only with `CapWavCues`.
- `process_cv(cv0, cv1, n)` — block-rate CV-out; the DAC ISR calls it once per block, not per sample (no per-sample virtual dispatch). Default silence.
- `render(DisplayModel&)` — fill the panel model; platform blits + composites overlays. Default draws nothing.
- `fx_leds/play_leds/alt_leds/deck_leds/render_ring` — the pre-`DisplayModel` LED query path, transitional; defaults inert.

Under `SPK_TERMINAL` additional members appear (`handle_command`, `engine_queries`, `param_label`, `live_params`/`live_configs`, `param_default`) — declared/read heuristically so a generic host can sweep engine state with no per-engine code. Ignore these unless you are also exposing a terminal surface.

## Build-time selection — `engine_select.h` + `Makefile`

The single place the firmware names a concrete engine:

```cpp
#elif defined(SPK_ENGINE_MYENGINE)
  #include "engine/myengine/myengine_engine.h"
  namespace spotykach { using ActiveEngine = MyEngine; }
```

```make
ifeq ($(ENGINE), myengine)
  C_DEFS += -DSPK_ENGINE_MYENGINE
  ENGINE_SOURCES = $(wildcard src/engine/myengine/*.cpp)
endif
CPP_SOURCES = main.cpp app.cpp $(ENGINE_SOURCES) <platform>
```

Both halves (define + source list) come from the one `ENGINE=` variable. `app.cpp` instantiates `ActiveEngine` as a static value member; `build/.engine-stamp` forces `app.o` — the only define-dependent TU — to rebuild on an engine switch. The Faust/gen~ generators append their `#elif`/`else ifeq` blocks inside `// >>> backend:name >>>` … `// <<< backend:name <<<` markers, upserted rather than hand-edited.

The full shipped set and their `ENGINE=`/marker names are enumerated in `engine_select.h` (granular, passthrough, delay, qdelay, edrums, reso, mosc, graincloud, tape, reverb, shuttle, softcut, radio, bard, glitch, pstretch, then gen~ `gigaverb`, faust `chorus/filter/voice`, and QSPI-only `csound`/`chuck`).

## Minimal reference — `passthrough_engine.h`

Header-only, ~35 lines of real code: `init` resets a peak, `process` copies in→out while tracking peak, `capabilities()` returns `CapOwnDisplay` only, and `render(DisplayModel&)` draws a symmetric level meter on both rings via `LEDRing` primitives (`m.ring[r].set_hex_color/set_segment/set_updated; m.play[r] = {0x00ff00, 1.f}`). Everything else on `IEngine` stays the no-op default. Copy this shape for any new single-deck engine.