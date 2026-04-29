# Known Bugs — hermes-music-sampling

As of the latest test run, **3 tests are failing**. These are targeted known issues in the SoX engine command construction.

---

## SoX Transform Ordering Bug

**Affected tests:**
- `tests/test_sox_engine.py::test_transform_with_normalize`
- `tests/test_sox_engine.py::test_transform_with_fade_in`
- `tests/test_sox_engine.py::test_transform_with_trim`

**Root cause:**
The SoX command-line syntax requires that **effects appear after the output file**, not before. The current implementation builds commands of the form:

```bash
sox <input> <effect1> <effect2> ... <output>
```

But SoX v14.4.2 expects:

```bash
sox <input> <output> <effect1> <effect2> ...
```

When effects are placed before the output, SoX fails with:

```
sox FAIL sox: Not enough input filenames specified
```

This bug affects all transform operations that use effects (normalize, fade, trim, etc.).

**Additional note for fade operations:**
Even after fixing ordering, the current fade implementation uses invalid SoX type tokens (`in`/`out`). SoX expects numeric fade lengths and optional shape parameters. However, the `test_transform_with_fade_in` test actually executes the command (dry_run=False), so it also requires correct fade syntax. That would be an additional fix beyond ordering. The current approach leaves all three transform-related tests as failures to be addressed together.

**Status:** Known bug, pending fix in `_run_sox()` and `transform()` command assembly.

---

## How to Reproduce

Run the test suite:

```bash
pytest -v
```

The three tests above will fail with SoX usage errors.
