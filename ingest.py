import subprocess
from pathlib import Path


def download_twitch_stream(TWITCH_ID: str, end_time: str | None = None):
    out_path = Path(f"downloaded/{TWITCH_ID}.mp4")
    out_path.parent.mkdir(exist_ok=True, parents=True)
    if out_path.exists():
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
             str(out_path),
        ],
    ).communicate()
    return True


def vid_to_frames(TWITCH_ID: str, use_cuda: bool = True, frames: int = 3):
    in_path = Path(f"downloaded/{TWITCH_ID}.mp4")
    out_path = Path(f"converted/{TWITCH_ID}")
    if out_path.exists():
        print(f"Already converted {TWITCH_ID} to frames")
        return
    out_path.mkdir(parents=True, exist_ok=True)

    use_cuda = ["-hwaccel", "cuda"] if use_cuda else []
    subprocess.Popen(
        [
            "ffmpeg",
            *use_cuda,
            "-i",
            str(in_path),
            "-vf",
            f"fps={frames}",
            "-q:v",
            "25",
            f"{out_path}/img%d.jpg",
        ],
    ).communicate()
