---
name: ardour-automator
category: daw-master
description: Headless Ardour DAW automation via Lua scripting and CLI.
triggers: []
provides: [run_script, probe, export]
---

# Ardour Automator Skill

Wraps Ardour's headless operation modes:
- `ardour6-lua` — Lua scripting interpreter
- `luasession` — headless session access
- `ardour --script` — run Lua scripts against sessions

## Functions

- `run_script(script_path, session_path=None, dry_run=False)` — Execute a Lua automation script
- `probe(session_path)` — Get session metadata (tracks, duration, tempo)
- `export(session_path, output_path, format="wav", dry_run=False)` — Render session or stems
