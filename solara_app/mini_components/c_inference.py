from pathlib import Path
import solara
from moviepy.editor import VideoFileClip


@solara.memoize
def write_video(start: str, stop: str, id: int, file_name: str) -> str:
    vid_clip = VideoFileClip(file_name)

    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True, parents=True)
    clip = vid_clip.subclip(start, stop)
    file = f"tmp/{file_name}_{start}_{stop}_{id}.mp4"
    clip.write_videofile(file)

    return tmp_dir / file
