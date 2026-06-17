# Hypno 2 — Vidos NDI Streaming Operations

Operate Hypno 2 (Raspberry Pi 5 running Vidos) as an NDI media receiver.
Covers configuring channels, streaming live webcam video from a Linux PC via NDI,
and troubleshooting blank/black video issues.

## Hypno 2 Access

- **IP**: `192.168.1.54`
- **User**: `pi`
- **SSH key**: `~/.ssh/id_ed25519` (password-free auth)
- **Media directory**: `/home/pi/Documents/VIDOS-Resources/`
- **Vidos log**: `/opt/VIDOS/release/log.txt`
- **NDI log**: `/opt/VIDOS/release/Resources/.system/ndi_log.txt`
- **Screenshots**: `/home/pi/Documents/VIDOS-Resources/Screenshots/`
- **Crash logs**: `/opt/VIDOS/release/Resources/.system/crash_logs/`

Connect: `ssh -i ~/.ssh/id_ed25519 pi@192.168.1.54`

## NDI Pipeline: Linux PC → Hypno 2

```
┌─────────────────┐     NDI over WiFi      ┌─────────────────┐
│  Linux PC       │ ────────────────────▶  │  Hypno 2        │
│  (sanchopop)    │                        │  (192.168.1.54) │
│                 │                        │                 │
│  BisonCam       │   sender ────────────▶ │  Vidos          │
│  /dev/video0   │   [v4l2→FFmpeg→NDI]    │  Channel 2      │
└─────────────────┘                        └─────────────────┘
```

## Alternative 1: ndi_cam_send (C++ Binary)

### Prerequisites

```bash
sudo apt install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev
```

NDI SDK: `~/opt/ndi-sdk/`

### Critical Linker Order

FFmpeg libs MUST come after `-lndi` with `--no-as-needed`:

```bash
g++ ndi_cam_send.cpp -o ndi_cam_send \
    -Wl,--no-as-needed \
    -L"$HOME/opt/ndi-sdk/lib/x86_64-linux-gnu" \
    -lavformat -lavcodec -lavdevice -lavutil -lswscale \
    -lndi -lpthread \
    -Wl,-rpath,"$HOME/opt/ndi-sdk/lib/x86_64-linux-gnu"
```

**Without correct order**, `avformat_open_input` is silently dropped by the linker → no frames captured → blank video.

### Run

```bash
cd ~/opt/ndi-sdk/build
LD_LIBRARY_PATH=~/opt/ndi-sdk/lib/x86_64-linux-gnu ./ndi_cam_send /dev/video0
```

## Alternative 2: ffmpeg-ndi (FFmpeg with NDI Output)

Build from the `lplassman/FFMPEG-NDI` patched fork (NDI removed from mainline).

### Build

```bash
# Prerequisites
sudo apt install nasm yasm cmake git

# Clone
cd ~/ffmpeg-ndi
git clone --depth=1 https://git.ffmpeg.org/ffmpeg.git -b n5.1 .
git clone --depth=1 https://github.com/lplassman/FFMPEG-NDI.git ~/FFMPEG-NDI

# Patch
cd ~/ffmpeg-ndi
git config user.email "you@example.com" && git config user.name "You"
git am ~/FFMPEG-NDI/libndi.patch
cp ~/FFMPEG-NDI/libavdevice/libndi_newtek_* libavdevice/

# GCC >= 13 requires mathops.patch
git am ~/FFMPEG-NDI/mathops.patch

# SDK install
sudo cp -r /opt/ndi-sdk/include/* /usr/include/Processing/
sudo cp /opt/ndi-sdk/lib/x86_64-linux-gnu/libndi* /usr/lib/x86_64-linux-gnu/
sudo ldconfig

# Build
./configure --prefix=/usr/local/ffmpeg-ndi \
  --enable-gpl --enable-nonfree --enable-libndi_newtek \
  --disable-doc --disable-static --enable-shared
make -j$(nproc) && sudo make install
```

### Stream

```bash
export LD_LIBRARY_PATH=/usr/local/ffmpeg-ndi/lib:$LD_LIBRARY_PATH
/usr/local/ffmpeg-ndi/bin/ffmpeg \
  -f v4l2 -framerate 10 -video_size 1280x720 \
  -pixel_format yuyv422 -i /dev/video0 \
  -f libndi_newtek -pix_fmt uyvy422 "SANCHOPOP (BisonCam)"
```

## Init Order (for C++ recompilation)

```cpp
NDIlib_initialize();                      // 1st
avdevice_register_all();                  // 2nd — AFTER NDI init, BEFORE avformat_open_input
avformat_open_input(&pFormatCtx, ...);   // 3rd
```

## NDI SDK 30-Minute Development Timeout

The NDI Advanced SDK (libndi.so 6.3.2) is **development-use only**: stops sending frames after 30 minutes.

**Symptoms:**
- Source visible in NDI finder, but Vidos shows "Waiting for first frame"
- Vidos log: `Capture: WARNING - receiver has no active connection`
- TX bytes on WiFi stop increasing
- `ndi_test_pattern` (300 frames, ~10s) still works

**Workaround:**
- Use short-running senders only, OR
- Commercial NDI license (licensing@ndi.video), OR
- Watchdog cron to restart sender every ~25 minutes

Both `ndi_cam_send` and `ffmpeg-ndi` share the same timeout (both use `NDIlib_send_send_video_async_v2`).

## Troubleshooting: Blank Video on Hypno 2

Diagnostic order:

1. **Wrong binary running?** `ps aux | grep ndi_` — `ndi_test_pattern` shows gradient, not webcam
2. **Vidos not displaying the NDI source** ← **#1 cause** — source registered but not selected in Vidos source picker
3. **Screenshot:** `ssh pi@192.168.1.54 "ls -laht /home/pi/Documents/VIDOS-Resources/Screenshots/*.png | head -3"` then scp
4. **Vidos log:** `ssh pi@192.168.1.54 "tail -200 /opt/VIDOS/release/log.txt | grep -iE 'ndi|source|sanchopop|error'"`
5. **Webcam LED:** OFF = capture failed (linking), ON = capture works, problem is NDI/Vidos
6. **Linker check:** `nm ~/opt/ndi-sdk/build/ndi_cam_send | grep avformat` — must show `avformat_open_input`

### Known Root Causes (priority order)

1. Vidos not set to display the NDI source (most common)
2. Wrong binary running (test pattern vs webcam)
3. avformat linking missing → silent capture failure
4. WiFi power management → NDI UDP loss (`sudo iwconfig wlp0s20f3 power off`)
5. NDI SDK 30-minute timeout
6. First ~10 v4l2 frames are black (camera warm-up)
7. avdevice_register_all() wrong call order

## Known Hardware

**BisonCam NB Pro** (USB ID `5986:214c`)
- `/dev/video0` and `/dev/video1` (two nodes, same camera)
- YUYV422 1280×720 @ 10fps (USB bandwidth limit)
- MJPEG: corrupted APP fields → use YUYV422
- `dup=4` in ffmpeg = normal (30fps requested, 10fps delivered)
