import polars as pl


def rebalance_labels(df: pl.DataFrame) -> pl.DataFrame:
    prev_num_labels = df["label"].sum()
    to_remove = df.filter(pl.col("label") == 0).sample(fraction=0.7)
    df = df.join(to_remove, on="path", how="anti")

    print(
        f"Previously {prev_num_labels / len(df):.1%} highlights, now {df['label'].sum() / len(df):.1%}"
    )

    return df
