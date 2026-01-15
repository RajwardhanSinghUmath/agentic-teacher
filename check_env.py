
import shutil
import sys
import subprocess

print("Checking for ffmpeg...")
ffmpeg_path = shutil.which("ffmpeg")
print(f"ffmpeg path: {ffmpeg_path}")

try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    print("ffmpeg execution success")
    print(result.stdout[:100])
except Exception as e:
    print(f"ffmpeg execution failed: {e}")

print("Checking for gTTS...")
try:
    import gtts
    print("gTTS is installed")
except ImportError:
    print("gTTS is NOT installed")
