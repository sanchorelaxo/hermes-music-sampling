# sk-engines per-engine docs (vendored)

One `.md` per engine, verbatim from the upstream `shakfu/sk-engines` repository,
release tag `0.6.1`, path `docs/engines/<engine>.md`.

- 18 release engines + 4 build-only engines = 22 files (see `engines.md` one
  level up for which is which).
- These are the authoritative *device-level* control maps: which knob/pad/switch
  does what on each engine, the LED colour legend, hold-macro missions, and
  clock/routing behaviour. Read the file for the engine currently flashed before
  describing how to use it.
- Verbatim upstream content: the internal cross-links (e.g. `README.md#…`,
  `../dev/…`) do not resolve in this vendored copy — ignore them.
- To refresh after a sk-engines bump:

      for e in $(cd ../../scripts && python3 sk_engines.py list 2>/dev/null); do
        curl -sL -o "$e.md" \
          "https://raw.githubusercontent.com/shakfu/sk-engines/<TAG>/docs/engines/$e.md"
      done

  (also fetch the four build-only engines `granular chorus gigaverb passthrough`,
  which `list` does not enumerate).