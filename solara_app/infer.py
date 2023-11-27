from pathlib import Path
import solara
import polars as pl

from inference import run_inference
from utils.movie_clips import build_video


@solara.memoize
def solara_run_inference(
    model_path: Path,
    image_folder: Path,
    aggregate_duration: int = 30,
    fps: int = 3,
) -> pl.DataFrame:
    return run_inference(model_path, image_folder, aggregate_duration, fps)


@solara.memoize(key=lambda _, _2, higlight_vid: higlight_vid)
def convert_vid(
    file_name: str | Path, time_dict: list[dict[str, str]], highlight_vid: Path
):
    return build_video(file_name, time_dict, highlight_vid)
