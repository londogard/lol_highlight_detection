
import subprocess
from pathlib import Path


def download_twitch_stream(TWITCH_ID: str, end_time: str | None = None):
    if Path(f"{TWITCH_ID}.mkv").exists():
        print(f"Already downloaded {TWITCH_ID}")
        return

    end_time = ["-e", end_time] if end_time is not None else []
    subprocess.Popen(
        [
            "twitch-dl",
            "download",
            TWITCH_ID,
            "-q",
            "720p60",
            *end_time,
            "--output",
            f"{TWITCH_ID}.mkv",
        ],
    ).communicate()


def vid_to_frames(TWITCH_ID: str, use_cuda: bool = True, frames: int = 3):
    if Path(TWITCH_ID).exists():
        print(f"Already converted {TWITCH_ID} to frames")
        return
    Path(TWITCH_ID).mkdir(parents=True, exist_ok=True)

    use_cuda = ["-hwaccel", "cuda"] if use_cuda else []
    subprocess.Popen(
        [
            "ffmpeg",
            *use_cuda,
            "-i",
            f"{TWITCH_ID}.mkv",
            "-vf",
            f"fps={frames}",
            "-q:v",
            "25",
            f"{TWITCH_ID}/img%d.jpg",
        ],
    ).communicate()

# %%
download_twitch_stream("1913327875", "00:05:00")
# %%
