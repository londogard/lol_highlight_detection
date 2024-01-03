import datetime
import polars as pl

SECONDS_10 = pl.duration(seconds=10)
RANDOM_DATE = pl.date(2023, 1, 1).dt


def create_start_end_time(
    df: pl.DataFrame, cut_off: int, forward: dict, backward: dict
) -> pl.DataFrame:
    df = df.filter(pl.col("preds") >= cut_off).select(
        start=pl.col("timestamp"),
        end=pl.col("timestamp") + pl.duration(seconds=10),
    )
    if len(df) == 0:
        return df

    new_data = df[0].to_dicts()
    for row in df[1:].to_dicts():
        if new_data[-1]["end"] == row["start"]:
            new_data[-1]["end"] = row["end"]
        else:
            new_data.append(row)
    new_data = [
        {
            "start": d["start"] - datetime.timedelta(seconds=backward.get(i, 0)),
            "end": d["end"] + datetime.timedelta(seconds=forward.get(i, 0)),
        }
        for i, d in enumerate(new_data)
    ]
    return pl.DataFrame(new_data).with_columns(active=pl.lit(True))


def merge_overlaps_into_dict(df: pl.DataFrame):
    if len(df) == 0:
        return []

    data = df.cast(pl.Time).cast(pl.Utf8).to_dicts()
    new_data = [data[0]]
    for row in data[1:]:
        if new_data[-1]["end"] == row["start"]:
            new_data[-1]["end"] = row["end"]
        else:
            new_data.append(row)
    return new_data
