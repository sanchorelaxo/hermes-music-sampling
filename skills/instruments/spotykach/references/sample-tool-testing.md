# Exercising the sample pipeline without touching the instrument

The chain is: fetch a URL → cut with ffmpeg → convert → install to a slot. Every step
can be run for real except the last, and the last is the one that changes the user's
tapes. Keep them separable.

## Layered switch-off, cheapest first

| What you want to prove | How | Hardware touched |
| --- | --- | --- |
| the cut and the rate | `build_sample(url, start, end, is_deck_a, install=False, speed=...)` | no |
| bridge validation, argv assembly | `--tool` pointing at a stub that prints its argv | no |
| bridge → tool → real ffmpeg | bridge with `--tool` at a Python wrapper, plus a local HTTP file | depends on transport |
| the slot write and shift | a scratch card root **with `SK/`** and `--transport card` | no |

`install=False` is the important one: it still downloads, cuts, converts and reports, so
the audio and the metadata are real. Only the placement is skipped.

## The `--card` trap

`open_transport("auto", card_root=...)` tries USB first. `--card` gives it a card root; it
does not ask it to use one. With a unit plugged in and in transfer mode, an "offline" run
writes tape slot 1, shifts the tape and archives whatever was in slot 6. If a scratch root
is the point, pass `--transport card` and check `--status` says `card: yes` before running.

## Bridge harness

The bridge runs its tool as `python3 <tool> …`, so a tool override must be a **Python**
script. A shell wrapper fails with `SyntaxError: Missing parentheses in call to 'exec'` and
you get a job whose stderr is a Python traceback.

```python
# /tmp/pin/tool.py — pins the tool to a scratch card and cache
import runpy, sys
sys.argv = ["sample_tool.py", "--card", "/tmp/pin/card",
            "--cache-dir", "/tmp/pin/cache", "--transport", "card"] + sys.argv[1:]
runpy.run_path("/path/to/tools/sample_tool.py", run_name="__main__")
```

Serve the media locally so no network is involved: `python3 -m http.server 8898` in a
directory holding a generated tone
(`ffmpeg -f lavfi -i "sine=frequency=440:duration=6" -c:a pcm_f32le -ar 48000 -ac 2 tone.WAV`).

Run the bridge on a port that is not the user's (`--port 8899`), because the installed
service usually holds the real one and still runs the previous code.

```bash
curl -s -X POST http://127.0.0.1:8899/sample -H 'Content-Type: application/json' \
  -d '{"url":"http://127.0.0.1:8898/tone.WAV","start":"0:00","end":"0:04","deck":"a","speed":0.5}'
# → {"ok": true, "job_id": "…", "meta": {…, "speed": 0.5}}
curl -s http://127.0.0.1:8899/jobs/<id>
```

Start long-lived processes with the background flag, then poll readiness in a separate
command (`curl /health`, `curl -o /dev/null -w '%{http_code}' <media>`); a foreground call
that starts a server is refused.

## Verifying the audio, not the exit code

- The tool's WAVs are **32-bit float**, so `wave.open()` fails with
  `Error: unknown format: 3`. Use `ffprobe -v error -show_entries format=duration -of default=nw=1`
  or `-show_entries stream=codec_name,sample_rate,channels,duration`, and compare durations to
  the expected `picked / speed`.
- Expect the stored duration to be a few milliseconds short of the arithmetic (ffmpeg frame
  rounding); 4 s at 0.5x measured 7.977 s. Assert a tolerance, not equality.
- `SampleResult` fields are `segment_path`, `installed`, `transport`, `tape`, `slot`,
  `card_path`, `speed` — there is no `.segment`. `build_sample` takes the deck as
  `is_deck_a` (positional), not `deck=`.
- Reading a slot back over USB (`transport.read(tape, slot)`) is read-only and the cheapest
  way to confirm what actually landed; compare bytes against the cached segment.

## Faking a device that vanishes

To test the drop path without touching hardware, hand the transport a **pty** and close the
master: the next write raises `EIO`, exactly as a tty whose device left the bus does.

```python
import os, pty
master, slave = pty.openpty()
path = os.ttyname(slave)
port = usb.SerialPort(path)      # the code under test
os.close(master)                 # the "unit" leaves transfer mode
# assert port.write(b"x") raises TransferDropped, not OSError
```

Two rules when patching the tool's dependencies from a test:

- **Grab the module off the tool, not a fresh copy.** `sample_tool` imports `sk_install` at
  module scope, so a second `_load("sk_usb")` produces a different module object and a
  `mock.patch` on it changes nothing the tool can see. Use
  `sample_tool.sk_install.sk_usb` — the identical object the code path holds.
- **Assert the order, not just the outcome.** Record whether the transport was open when the
  segment appeared (a spy that notes "opened" and the segments dir at that instant); an
  end-state assertion passes whether the link was opened early or late.

## Clean up after a live run

Stop the bridge and the HTTP server by PID, confirm the ports are closed with `curl -m 2`,
and delete the scratch tree. A stray bridge on a temporary port is invisible until it
collides with something.
