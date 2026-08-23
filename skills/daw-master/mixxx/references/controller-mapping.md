# Mixxx MIDI Controller Mapping (Autopilot)

The autopilot sends Control Change (CC) messages to control Mixxx for live
sets. To make it work, bind these CCs to Mixxx functions:

## Mapping (defaults used by autopilot.py)

| CC | Function                 | Value range / semantics        |
|----|--------------------------|--------------------------------|
| 20 | LoadSelectedTrack (Deck 1) | 127 = load selected track     |
| 21 | LoadSelectedTrack (Deck 2) | 127 = load selected track     |
| 22 | play toggle (Deck 1)     | 127 = toggle play              |
| 23 | play toggle (Deck 2)     | 127 = toggle play              |
| 24 | crossfader               | 0..127 sweep                   |

## Setting it up in Mixxx

1. **Create a virtual MIDI port** so the agent has somewhere to send:
   - Linux: with JACK, `a2jmidid -e` exposes ALSA ports to JACK; or run
     `rtpmidi`/`midizap` to synthesize a port. A common approach is to start
     `jackd` + `a2jmidid -e` and point Mixxx at the ALSA/JACK MIDI bridge.
   - Without JACK, the agent tries `open_virtual_port("mixxx-autopilot")` —
     whether that works depends on your ALSA config.
2. **In Mixxx**: Preferences → Controllers → Add → (your virtual port) →
   load a *mixxx-autopilot* preset (or hand-map):
   - Bind CC 20 → `[Channel1] LoadSelectedTrack`
   - Bind CC 21 → `[Channel2] LoadSelectedTrack`
   - Bind CC 22 → `[Channel1] play` (toggle)
   - Bind CC 23 → `[Channel2] play` (toggle)
   - Bind CC 24 → `[Master] crossfader`
3. **Select a track** in the Mixxx library (so LoadSelectedTrack has a target).

## Verifying without a live setup

Always test with `--dry-run` first — it prints the exact CC sequence:

```
python skills/daw-master/mixxx/__main__.py autopilot a.mp3 b.mp3 --dry-run
```

Expected output:

```
[dry-run] CC 20 = 127  # load selected into deck1
Track duration: 242.5
Waiting 234.5s before starting next track
[dry-run] CC 21 = 127  # load track2 into deck2
[dry-run] CC 23 = 127  # start deck2
[dry-run] CC 24 = 0    # crossfader
[dry-run] CC 24 = 12   # crossfader
... (ramp to 127)
```

## Debugging

- **No port opens**: check `a2jmidid -e` is running (JACK) or that the ALSA
  port exists (`amidi -l`). Try a named port: `--port "mixxx"` to match the
  first port whose name contains "mixxx".
- **Mixxx doesn't react**: verify the binding in Preferences → Controllers and
  that the virtual port is selected as an *output* device.
- **Wrong deck**: CC 20/21 target decks 1 and 2 by default; rebind as needed.
