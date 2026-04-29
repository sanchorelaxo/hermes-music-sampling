---
name: ardour-automator
category: daw-master
description: Headless Ardour DAW automation via Lua scripting and CLI.
triggers: []
provides: [run_script, probe, export, arpeggiators]
---

# Ardour Automator Skill

Wraps Ardour's headless operation modes:
- `ardour8-lua` / `ardour6-lua` — Lua scripting interpreter (versioned binaries preferred)
- `luasession` — headless session access
- `ardour --script` — run Lua scripts (legacy, may not be available in all builds)

## Functions

- `run_script(script_path, session_path=None, dry_run=False, cleanup=False)` — Execute a Lua automation script
- `probe(session_path)` — Get session metadata (tracks, duration, tempo)
- `export(session_path, output_path, format="wav", dry_run=False)` — Render session or stems
- **arpeggiators subskill** — three parameterized arpeggiator generators (simple, Barlow, raptor)

## Arpeggiators subskill

The `arpeggiators` module provides Lua script generators for three classic arpeggiator
DSP plugins by Albert Gräf, copied from his [ardour-lua](https://github.com/agraef/ardour-lua/tree/main/dsp) collection.

All functions return a complete Lua script as a string.  Use the convenience runners
(`run_simple_arp()`, `run_barlow_arp()`, `run_raptor_arp()`) to render a script to a
temporary file and execute it via `run_script()` automatically.

### Simple Arp (`simple_arp`)

Basic monophonic arpeggiator with up/down/exclusive/inclusive/order/random patterns.

- `render_simple_arp(division=2, octave_up=0, octave_down=0, pattern=1, ...)` → str
- `run_simple_arp(dry_run=False, cleanup=False, **render_kwargs)` → dict

Key parameters:
- `division`: beat subdivisions (1–16)
- `pattern`: 1=up, 2=down, 3=exclusive, 4=inclusive, 5=order, 6=random
- `latch` / `sync`: boolean modes

### Barlow Arp (`barlow_arp`)

Uses indispensability theory (Barlow) to accentuate notes rhythmically. Includes velocity
and filter accentuation based on metric weight.

- `render_barlow_arp(division=1, pattern=1, min_vel=60, max_vel=120, min_filter=0.0, max_filter=1.0, ...)` → str
- `run_barlow_arp(dry_run=False, cleanup=False, **render_kwargs)` → dict

Key parameters:
- `min_filter` / `max_filter`: filter pulses by indispensability weight [0,1]
- `division`: note value (1=whole, 4=quarter, 7=32nd)
- `debug`: verbosity (0–2)

### Raptor Arp (`raptor_arp`)

Advanced random arpeggiator with harmonicity-based filtering, step width, density,
and uniqueness control.

- `render_raptor_arp(division=1, mode=0, min_vel=60, max_vel=120, velmod=0, gain=0.5, ...)` → str
- `run_raptor_arp(dry_run=False, cleanup=False, **render_kwargs)` → dict

Key parameters:
- `mode`: 0=random, 1=up, 2=down, 3=up-down, 4=down-up, 5=outside-in
- `pref`, `pmin`, `pmax`, `pmod`: pitch select filter
- `hmin`, `hmax`, `hmod`: harmonicity filter
- `smin`, `smax`, `smod`: step width / density filter
- `nmax`, `uniq`: repetition limit / uniqueness filter
- `raptor`: enable raptor algorithm (0/1)

### Example

```python
from ardour_automator import arpeggiators as arp

# Generate and run a Barlow arpeggiator on a running Ardour session
result = arp.run_barlow_arp(
    division=4,          # 1/4 notes
    pattern=3,           # exclusive up/down
    min_filter=0.3,      # accent stronger pulses
    max_filter=0.9,
    latch=1,
    dry_run=False,
)
```