from pathlib import Path
import solara


@solara.memoize(key=lambda _, id, file_name: f"{id}_{file_name}")
def write_video(clip, id: int, file_name: str):
    clip.write_videofile(f"tmp/{file_name}_{id}.mp4")
    return True
