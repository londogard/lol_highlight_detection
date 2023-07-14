import polars as pl
import functools


@functools.cache
def get_label_intervals(file: str = "highlights.csv"):
    return pl.read_csv(file, try_parse_dates=True)


def label(highlights: pl.DataFrame, fps: int = 3):
    pass


if __name__ == "__main__":
    df = pl.read_csv("highlights.csv", try_parse_dates=True)
    label(df)
