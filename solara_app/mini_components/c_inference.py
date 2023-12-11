from pathlib import Path
import solara


@solara.memoize(
    key=lambda _, start_stop, id, file_name: f"{start_stop}_{id}_{file_name}"
)
def write_video(clip, start_stop: str, id: int, file_name: str) -> str:
    clip.write_videofile(f"tmp/{file_name}_{start_stop}_{id}.mp4")
    return f"tmp/{file_name}_{start_stop}_{id}.mp4"
