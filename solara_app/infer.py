from pathlib import Path
import solara
import polars as pl

from inference import run_inference


@solara.memoize
def solara_run_inference(
    model_path: Path,
    image_folder: Path,
    aggregate_duration: int = 30,
    fps: int = 3,
) -> pl.DataFrame:
    return run_inference(model_path, image_folder, aggregate_duration, fps)
