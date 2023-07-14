from pathlib import Path
import ffmpeg


def format_video_to(
    input: Path, output: Path, size: str = "512x512", fps: int = 3, quality: int = 20
):
    (
        ffmpeg.input(str(input))
        .filter("scale", size=size)
        .filter("fps", fps=fps)
        .output(str(output), q=f"{quality}")
        .run()
    )


if __name__ == "__main__":
    format_video_to(Path("1863051677.mkv"), Path("frames") / "1863051677" / "img%d.jpg")
