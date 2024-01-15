from pathlib import Path
import subprocess


def compress(TWITCH_ID: str) -> str:
    file = f"{TWITCH_ID}.tar.lz4"
    subprocess.Popen(["tar", "-clvf", file, TWITCH_ID]).communicate()

    return file


def upload(file: str, prefix: str = "frames/"):
    subprocess.Popen(
        [
            "rclone",
            "--config",
            "rclone.conf",
            "copy",
            file,
            f"r2:lol-highlights-eu/{prefix}/",
        ]
    ).communicate()


def download(file: str, out_folder: str = "."):
    if not Path(file).exists():
        print(
            subprocess.Popen(
                [
                    "rclone",
                    "--config",
                    "rclone.conf",
                    "copy",
                    f"r2:lol-highlights-eu/{file}",
                    out_folder,
                ]
            ).communicate()
        )
        return file


def list_files(directory: str) -> list[str]:
    out, _ = subprocess.Popen(
        [
            "rclone",
            "--config",
            "rclone.conf",
            "ls",
            "--exclude",
            "*.jpg",
            f"r2:lol-highlights-eu/{directory}",
        ],
        stdout=subprocess.PIPE,
    ).communicate()
    out = [x.strip().split(" ")[-1] for x in out.decode("utf-8").split("\n") if len(x)]
    return out


def decompress(file: str):
    subprocess.Popen(["tar", "-xvf", file]).communicate()


def download_frames_and_unpack(filename: str):
    download(f"frames/{filename}")
    decompress(filename)
    Path(filename).unlink()
