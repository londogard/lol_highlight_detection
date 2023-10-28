import polars as pl


def balance_labels(df: pl.DataFrame, fraction: float = 0.5) -> pl.DataFrame:
    prev_num_labels, prev_total = df["label"].sum(), len(df)
    to_remove = df.filter(pl.col("label") == 0).sample(fraction=fraction)
    df = df.join(to_remove, on="path", how="anti")

    print(
        f"Previously {prev_num_labels / prev_total:.1%} highlights, now {df['label'].sum() / len(df):.1%}"
    )

    return df
