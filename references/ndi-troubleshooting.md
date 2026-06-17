# NDI Webcam Streaming — Session Diagnostic Notes

## Session Summary (2026-05-24/25)
**Problem:** Webcam feed blank on Hypno2/Vidos despite NDI source visible.

**Root cause:** NDI Advanced SDK 30-minute development timeout.

**Confirmed via:**
1. Vidos ndi_log.txt: `Capture: WARNING - receiver has no active connection`
2. Vidos ndi_log.txt: `Capture: No first frame from 'SANCHOPOP (BisonCam)' after round N`
3. Source IP correct (192.168.1.119:5961), finder sees it, but no frames arrive
4. `ndi_test_pattern` (300 frames, ~10s) works; long-running webcam senders fail after ~30min
5. SDK binary license string confirmed: `"This version of the NDI Advanced SDK is designed for development use and will run on a stream for 30 minutes."`

---

## Key NDI Log Patterns

```
# Source appears/disappears
Source[n]: 'SANCHOPOP (BisonCam)' url='192.168.1.119:5961'

# Receiver trying to get first frame
Capture: Waiting for first frame from 'SANCHOPOP (BisonCam)' (round N)...
Capture: WARNING - receiver has no active connection to 'SANCHOPOP (BisonCam)'
Capture: No first frame from 'SANCHOPOP (BisonCam)' after round N, retrying in 60s...

# Vidos log location
/opt/VIDOS/release/Resources/.system/ndi_log.txt   # NDI-specific log
/opt/VIDOS/release/log.txt                          # Main application log
```

---

## Diagnostic Capture: Verify NDI Traffic

```bash
# 1. Kill all existing NDI senders
pkill -9 -f ndi_ 2>/dev/null; sleep 1

# 2. Run ndi_test_pattern (completes in ~10s, always works)
# 3. Immediately capture UDP traffic from laptop
sudo timeout 15 tcpdump -i wlp0s20f3 -n 'udp and src 192.168.1.119' -c 200

# Expected: packets on port 5961 (ndi_cam_send) or 5962 (ndi_test_pattern)
# If no packets: NDI library not transmitting (license timeout has fired)
```

**Key ports:**
- `5961` — ndi_cam_send / ffmpeg-ndi (webcam senders)
- `5962` — ndi_test_pattern (test pattern sender)

---

## Key Findings

| Aspect | Value |
|--------|-------|
| NDI SDK version | 6.3.2 (x86_64-linux-gnu) |
| License | Development — 30 min timeout per stream |
| ffmpeg-ndi installed | `/usr/local/ffmpeg-ndi/` (n5.1 branch, lplassman/FFMPEG-NDI patched) |
| NDI source name | `SANCHOPOP (BisonCam)` |
| Hypno2 IP | 192.168.1.54 |
| Sender port | 5961 (webcam), 5962 (test pattern) |
| Webcam | BisonCam NB Pro (5986:214c), /dev/video0, 1280x720 YUYV422 @ 10fps |
| ffmpeg dup=4 | Normal — 30fps requested, 10fps delivered; ffmpeg duplicates frames, not an error |

---

## BOTH Senders Hit the 30-Minute Timeout

- **ndi_cam_send** (custom C++): Uses `NDIlib_send_send_video_async_v2` → same timeout
- **ffmpeg-ndi**: Uses `NDIlib_send_send_video_async_v2` via libndi_newtek output device → same timeout

The ffmpeg-ndi sender is functionally identical to ndi_cam_send from an NDI SDK perspective. No framesync workaround exists — this is a license restriction.

## Current Workaround

For continuous webcam streaming, either:
1. Obtain a commercial NDI license (licensing@ndi.video)
2. Use a watchdog cron that restarts the sender every ~25 minutes
3. Investigate NDI Core (free) SDK which may not have the 30-minute limit