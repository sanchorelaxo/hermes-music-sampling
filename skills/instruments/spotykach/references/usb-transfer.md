# Spotykach USB file transfer (firmware 1.4.0+)

Firmware before 1.4.0 exposes USB‑MIDI only. Sending the transfer SysEx to an
older unit produces no reply and no re‑enumeration — that silence is the firmware
version telling you it cannot do this.

## Requirements

1. Firmware **1.4.0** or newer (v1.4.0 is the release that added transfer).
2. A udev rule so the CDC node is usable without root:

```
# /etc/udev/rules.d/99-spotykach-cdc.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", MODE="0666"
```

`MODE="0660", TAG+="uaccess"` is the usual recommendation and it does **not**
reliably apply: `uaccess` only grants an ACL when the device is tagged at the
active seat, and a headless/SSH session has none. The ACL is then missing and the
node stays `root:dialout 660` with the user not in `dialout`. `MODE="0666"`
scoped to that one VID:PID is the rule that works.

## Entering transfer mode

USB PID is `0483:5740` in both modes; the MIDI port already exists, so the
handshake goes over MIDI, not over the serial node (which does not exist yet):

```
F0 7D 53 4B 01 F7      SYSEX_ENTER
F0 7D 53 4B 02 SS F7   SYSEX_REPLY   SS: 0 ok, 1 busy, 2 no card
```

Reply status `0` arrives within ~1.5 s, the unit re‑enumerates with a CDC
interface and `/dev/ttyACM0` appears. From a shell:

```bash
amidi -p hw:2,0,0 -S "F07D534B01F7"     # port from `amidi -l`
ls /dev/ttyACM*                          # appears a moment later
```

**Transfer mode is transient.** It times out on its own in well under a minute
and drops back to MIDI‑only, taking `/dev/ttyACM*` with it. Never cache the node
path across operations: open the link per operation, and re‑enter transfer mode
whenever the node is gone. A stale node path is the normal case, not an error.

**The timeout counts silence, not elapsed work.** A link opened while the fetch or the
ffmpeg pass is still running sits idle for tens of seconds and is gone by the time the
first byte is ready: `os.write` then fails `OSError: [Errno 5] Input/output error` on a
node whose device has already reverted to MIDI. A `HELLO` reply proves the port was alive
when it was sent, nothing more. So prepare the exact bytes to send first and open the link
immediately before the write; keep the up-front availability check a presence test
(`--status`, `/dev/serial/by-id/`, an existing `SK/`) that never switches mode.

**The node appears `0600` for a few milliseconds** before udev applies the rule.
Glob‑then‑open races and fails `EACCES` on a perfectly working rig. Poll until a
node is actually openable (`os.access(path, R_OK|W_OK)` or a real open in a
try) instead of trusting the first `glob()` result.

## Protocol

Frame: `'S' 'K' type seq len:u32le crc:u32le payload[len]`
with `crc = zlib.crc32(header[2:8] + payload)`. Reply carries `type|0x80`, the same
`seq`, and `payload[0]` = status.

| Step | Meaning |
|------|---------|
| `HELLO` | proto version, firmware, tape letters, slots per tape, `max_chunk`, `total_kib`/`free_kib` |
| `UPLOAD_BEGIN` | opens a temp file on the card |
| `UPLOAD_DATA*` | chunked payload, `max_chunk` bytes at a time (32768 on 1.4.0) |
| `UPLOAD_COMMIT` | verifies CRC + WAV header, then atomically replaces the slot |
| download | chunked read of one slot |
| `CMD 0x30` | remove one slot, payload `bytes([tape, slot, 0, 0])` |

Slots on the wire are **0‑based**; tape index is the position in the reported
tape string (`"BGPRTY"` → B=0 … Y=5). Expose 1‑based slots upward, because that
is what the card layout and the deck UI use (`SK/B/1.WAV`).

Commit only replaces the slot after CRC and header check, so an interrupted
upload leaves the old sample intact — prefer this to writing the slot directly.

## Retrying a drop

One retry, gated on "nothing has reached the tape". Put a `wrote` flag on the transport and
set it *before* the first upload frame; an install that already shifted slots must not run
twice, because the second pass moves every sample down again and there is no undo. Give the
drop its own error type (`TransferDropped`) carrying an actionable sentence — the user reads
"left transfer mode … send again", not a traceback — and translate the tty errnos that mean
"device gone" (`EIO`, `ENXIO`, `ENODEV`, `EBADF`) into it at the one place that calls
`os.write`/`os.read`.

Measured on a 1.4.0 unit: 3,072,044 bytes read in ~4.7 s, 384 KB written in
~0.7 s.

## Driving it from Python

No third‑party deps are needed. Raw `termios` on the tty node for the framed
protocol, and `amidi` (subprocess) for the sysfs MIDI port, is enough — that
avoids `pyserial`/`mido` and keeps the tool runnable on a bare system.

Do these in this order, and note *why* the order matters:

1. resolve transport **before** downloading or cutting audio — a missing unit or
   card should cost nothing, not a full fetch;
2. read the card/unit state and report `ready`/`transport` so a UI can show a
   red dot instead of failing at send time;
3. download, cut, retime and prepare the exact bytes to send — none of that needs
   the unit;
4. enter transfer mode, wait for an openable node, `HELLO`, then write — in one
   uninterrupted stretch.

## Placement when installing a sample

The device is one chain of slots: B G P R T Y in order, six slots each, files
always `1.WAV` .. `6.WAV`. Two modes, chosen by the caller (the user's GUI
offers both; nothing else is allowed to pick):

- **bump**: the new sample takes slot 1 of the target tape; every occupied slot
  behind it moves one place down the chain (`B/6.WAV` into `G/1.WAV`, and so
  on), each file renamed to its new slot. Only a full `Y/6` makes a file fall
  off the end, and the fallen file is archived, never deleted. A free target
  slot moves nothing else on the chain.
- **append**: the new sample takes the first free slot on the chain; nothing
  moves; a completely full chain is an error instead of a silent bump.

Implementation constraints, all of which exist to keep audio rather than lose it:

- move from the **far end of the chain backwards**, so nothing is read after
  being overwritten;
- read each slot back and compare bytes before the next move, so an
  interruption leaves a duplicate, never silence;
- skip empty slots rather than copying zeros: an empty slot has no file;
- archive the fallen file to the card ROOT as `<tape>_6_<timestamp>.WAV`
  whenever a writable card is mounted, even for a USB install; with no card at
  all, fall back to a host cache directory. The unit itself has no filesystem
  to put the overflow on.

## Failure signatures

| Symptom | Cause |
|---------|-------|
| `OSError: [Errno 5]` in `os.write`, node already gone | link held open across a download/cut; the mode timed out on silence. Open late, retry once |
| Drop after bytes reached the tape | not retryable — the slot shift is not idempotent. Report it, never re-run blindly |
| SysEx sent, no reply, no `/dev/ttyACM*` | firmware older than 1.4.0 |
| `PermissionError`/`EACCES` on the node | missing udev rule, or the `0600` race |
| Node vanished mid‑run | transfer mode idle timeout; re‑enter and retry |
| `amidi -l` shows a mangled name (`Љ MIDI 1`) | port numbering shifted after re‑enumeration; select by card index (`hw:N,0,0`) captured fresh, not by name |
