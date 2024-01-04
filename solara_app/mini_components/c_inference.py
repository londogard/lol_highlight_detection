from pathlib import Path
import solara
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.editor import ImageSequenceClip
import torch


@solara.memoize(
    key=lambda _, disabled, file_name, cache_key: f"{disabled}_{file_name}{cache_key}"
)
def write_full_video(
    start_stop: list[dict[str, str]], disabled: dict, file_name: str, cache_key: str
) -> str:
    vid_clip = VideoFileClip(f"downloaded/{file_name}.mp4")
    clips = []
    for i, tstamp in enumerate(start_stop):
        if disabled.get(i):
            continue
        clips.append(vid_clip.subclip(tstamp["start"], tstamp["end"]))

    # Concatenate the video clips with transitions
    final_clip = concatenate_videoclips(clips)

    # Write the final concatenated movie to a file
    file = vid_clip.filename.replace("downloaded", "out")
    kwargs = {}

    if torch.cuda.is_available():
        kwargs["codec"] = "h264_nvenc"

    final_clip.write_videofile(file, **kwargs)

    return file


@solara.memoize
def write_video(start: str, stop: str, id: int, file_name: str) -> str:
    vid_clip = VideoFileClip(f"downloaded/{file_name}.mp4")
    vid_clip.write_videofile()
    tmp_dir = Path("tmp")
    tmp_dir.mkdir(exist_ok=True, parents=True)
    clip = vid_clip.subclip(start, stop)
    file = f"tmp/{file_name}_{start}_{stop}_{id}.mp4"

    kwargs = {}
    if torch.cuda.is_available():
        kwargs["codec"] = "h264_nvenc"

    clip.write_videofile(file, **kwargs)

    return file
