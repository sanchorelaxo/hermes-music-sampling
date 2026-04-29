import subprocess, sys

def sox_available():
    try:
        r = subprocess.run(['sox', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

def rubberband_available():
    try:
        r = subprocess.run(['rubberband', '--version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

def ffmpeg_available():
    try:
        r = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
        return r.returncode == 0
    except:
        return False

def librosa_available():
    try:
        import librosa
        return True
    except ImportError:
        return False

def dawdreamer_available():
    try:
        import dawdreamer
        return True
    except ImportError as e:
        print("DEBUG dawdreamer import error:", e, file=sys.stderr)
        return False

print("sox:", sox_available())
print("rubberband:", rubberband_available())
print("ffmpeg:", ffmpeg_available())
print("librosa:", librosa_available())
print("dawdreamer:", dawdreamer_available())