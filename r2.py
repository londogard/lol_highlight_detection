from pathlib import Path
import subprocess


def compress(TWITCH_ID: str):
    subprocess.Popen(["tar", "-clvf", f"{TWITCH_ID}.tar.lz4", TWITCH_ID]).communicate()


def upload(file: str, prefix: str = "frames/"):
    subprocess.Popen(
        [
            "rclone",
            "--config",
            "rclone.conf",
            "copy",
            file,
            f"r2:lol-highlights-eu/{prefix}",
        ]
    ).communicate()


def download(file: str):
    subprocess.Popen(
        [
            "rclone",
            "--config",
            "rclone.conf",
            "copy",
            f"r2:lol-highlights-eu/{file}",
            ".",
        ]
    ).communicate()


def decompress(file: str):
    subprocess.Popen(["tar", "-xvf", file]).communicate()


def download_frames_and_unpack(filename: str):
    download(f"frames/{filename}")
    decompress(filename)
    Path(filename).unlink()
