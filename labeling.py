from pathlib import Path
import shutil
import polars as pl
import functools


@functools.cache
def get_label_intervals(file: str = "highlights.csv"):
    return pl.read_csv(file, try_parse_dates=True)


def label(highlights: pl.DataFrame, files: list[Path], root_path: Path, fps: int):
    highlights = highlights.select(
        range=pl.int_ranges(
            pl.col("start").cast(pl.Duration).dt.seconds() * fps,
            pl.col("stop").cast(pl.Duration).dt.seconds() * fps,
        ),
    ).explode("range")
    highlights = set(highlights.to_series().to_list())
    for f in files:
        if int(f.stem[3:]) in highlights:
            shutil.copy2(f, root_path / "1" / f.name)
        else:
            shutil.copy2(f, root_path / "0" / f.name)


if __name__ == "__main__":
    df = pl.read_csv("highlights.csv", try_parse_dates=True)
    files = Path("frames/1863051677").glob("*.jpg")
    sympath = Path("frames/labeled_data")
    (sympath / "1").mkdir(exist_ok=True, parents=True)
    (sympath / "0").mkdir(exist_ok=True, parents=True)

    label(df, files, sympath, fps=3)
