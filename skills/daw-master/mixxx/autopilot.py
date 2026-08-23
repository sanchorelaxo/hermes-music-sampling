"""Mixxx Autopilot — MIDI-based set automation agent.

Sends MIDI CC messages to a virtual MIDI port to control Mixxx for live sets.
Ported from cli-anything-mixxx autopilot/agent.py.

Requirements:
  - python-rtmidi (optional; the agent raises if rtmidi is missing)
  - A virtual MIDI port visible to Mixxx (Linux: a2jmidid / jack-midi)

Controller mapping used (see SKILL.md / references for how to set this up in
Mixxx Preferences -> Controllers):
  - CC 20 -> LoadSelectedTrack (Deck 1)
  - CC 21 -> LoadSelectedTrack (Deck 2)
  - CC 22 -> play toggle (Deck 1)
  - CC 23 -> play toggle (Deck 2)
  - CC 24 -> crossfader (0..127)

The run_sequence() demo performs a simple beat-agnostic crossfade set:
starts track A on deck 1, waits (durationA - crossfade), starts track B on
deck 2 and ramps the crossfader over `crossfade` seconds.
"""
import subprocess
import time

try:
    import rtmidi
except Exception:  # pragma: no cover - optional dependency
    rtmidi = None


def probe_duration(path):
    """Probe duration (seconds) via ffprobe, else None."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        if out:
            return float(out)
    except Exception:
        pass
    return None


class MidiAgent:
    """Thin rtmidi wrapper: opens a named port or a virtual 'mixxx-autopilot'
    port, and sends CC/note messages."""

    def __init__(self, port_name=None):
        if rtmidi is None:
            raise RuntimeError(
                "python-rtmidi not installed. Install with: pip install python-rtmidi"
            )
        self.midiout = rtmidi.MidiOut()  # type: ignore[attr-defined]
        self.port_name = port_name
        self.port = None
        self._open_port()

    def _open_port(self):
        ports = self.midiout.get_ports()
        if self.port_name:
            for i, p in enumerate(ports):
                if self.port_name in p:
                    self.midiout.open_port(i)
                    self.port = p
                    print("Opened MIDI out port:", p)
                    return
        # Not found (or no name) -> create virtual port
        try:
            self.midiout.open_virtual_port("mixxx-autopilot")
            self.port = "virtual:mixxx-autopilot"
            print("Opened virtual MIDI out port: mixxx-autopilot")
        except Exception as e:
            raise RuntimeError("Failed to open MIDI port: " + str(e))

    def send_cc(self, cc, value, channel=0):
        status = 0xB0 | (channel & 0x0F)
        msg = [status, cc & 0x7F, int(value) & 0x7F]
        self.midiout.send_message(msg)

    def send_note(self, note, velocity=127, channel=0):
        status = 0x90 | (channel & 0x0F)
        self.midiout.send_message([status, note & 0x7F, velocity & 0x7F])

    def close(self):
        try:
            self.midiout.close_port()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def run_sequence(files, crossfade=8.0, port_name=None, autoplay=True, dry_run=False):
    """Run the crossfade demo sequence.

    If dry_run=True, prints the CC sequence without needing MIDI or a running
    Mixxx (useful for verifying the mapping before a live run).
    """
    if not files:
        print("No input files")
        return

    agent = None if dry_run else MidiAgent(port_name=port_name)
    active_agent = agent  # non-None when not dry-run; helper for the closure

    def send(cc, value, desc):
        if dry_run:
            print(f"[dry-run] CC {cc} = {value}  # {desc}")
        elif active_agent is not None:
            active_agent.send_cc(cc, value)
            print(f"CC {cc} = {value}  # {desc}")

    try:
        send(20, 127, "load selected into deck1")
        time.sleep(0.2) if not dry_run else None
        if autoplay:
            send(22, 127, "play deck1")

        dur = probe_duration(files[0]) or 180.0
        print("Track duration:", dur)
        wait_time = max(1.0, dur - crossfade)
        print(f"Waiting {wait_time:.1f}s before starting next track")
        if not dry_run:
            time.sleep(wait_time)

        if len(files) > 1:
            send(21, 127, "load track2 into deck2")
            time.sleep(0.2) if not dry_run else None
            send(23, 127, "start deck2")
            steps = int(max(12, crossfade * 4))
            for i in range(steps + 1):
                v = int((i / steps) * 127)
                send(24, v, "crossfader")
                if not dry_run:
                    time.sleep(crossfade / max(1, steps))
            print("Crossfade complete")
        else:
            print("Only one track provided; playback started for deck1")
    finally:
        if agent is not None:
            agent.close()
