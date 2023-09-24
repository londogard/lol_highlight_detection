from pathlib import Path
import polars as pl


def build_labels(label_file: Path, fps: int = 3):
    df = pl.read_parquet(label_file)
    highlights = df.select(
        "vid_id",
        frame=pl.int_ranges(
            pl.col("start").cast(pl.Duration).dt.seconds() * fps,
            pl.col("stop").cast(pl.Duration).dt.seconds() * fps,
        ),
        label=pl.lit(1),
    ).explode("frame")

    dfs = []
    for vid in df["vid_id"].unique():
        frames = len(list(Path(str(vid)).glob("*.jpg")))
        dfs.append(
            pl.DataFrame({"vid_id": [vid] * frames, "frame": np.arange(1, frames + 1)})
        )

    labeled_df = pl.concat(dfs)
    labeled_df = labeled_df.join(
        highlights, on=["vid_id", "frame"], how="left"
    ).fill_null(0)
    labeled_df = labeled_df.with_columns(
        path=pl.concat_str(
            [
                pl.col("vid_id").cast(pl.Utf8) + "/img",
                pl.col("frame").cast(pl.Utf8) + ".jpg",
            ]
        )
    )
    labeled_df = labeled_df.sort("vid_id", "frame")
    labeled_df.head(2)
