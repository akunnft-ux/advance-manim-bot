import glob
import os
import random
import subprocess


def composite_bgm(video_path: str, output_path: str) -> str:
    bgm_files = glob.glob("audio/*.mp3")
    if not bgm_files:
        return video_path

    bgm_path = random.choice(bgm_files)

    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True, timeout=10,
    )
    has_audio = bool(probe.stdout.strip())

    temp_output = output_path + ".tmp.mp4"
    if has_audio:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.12[a1];[0:a][a1]amix=inputs=2:duration=first",
            "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart",
            temp_output,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", bgm_path,
            "-filter_complex", "[1:a]volume=0.12[a1]",
            "-map", "0:v:0", "-map", "[a1]",
            "-c:v", "copy", "-c:a", "aac", "-shortest", "-movflags", "+faststart",
            temp_output,
        ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        if os.path.exists(temp_output):
            os.replace(temp_output, output_path)
            return output_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        if os.path.exists(temp_output):
            os.remove(temp_output)

    return video_path
