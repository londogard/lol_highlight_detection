from pathlib import Path
import ffmpeg


def format_video_to(input: Path, output: Path, size: str = "1280x720", fps: int = 5):
    (
        ffmpeg.input(str(input))
        .filter("scale", size="1280x720")
        .filter("fps", fps=fps)
        .output(str(output))
        .run()
    )


if __name__ == "__main__":
    format_video_to(Path("bauss.mkv"), Path("frames") / "img%03d.png")
