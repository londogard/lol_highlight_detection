from pathlib import Path
import numpy as np
from torch.utils.data import DataLoader
import polars as pl
import lightning as L
from data_utils.frame_dataset import FrameDataset
import torch

from models.lightning_wrapper import LightningWrapper


def run_inference(
    model_path: Path,
    image_folder: Path,
    aggregate_duration: int = 30,
    fps: int = 3,
) -> pl.DataFrame:
    model = LightningWrapper.load_from_checkpoint(model_path)
    trainer = L.Trainer()

    paths = list(image_folder.rglob("*.jpg"))
    df = pl.DataFrame(
        {"path": paths, "frame": [int(p.stem.removeprefix("img")) for p in paths]}
    )
    df = df.sort("frame")[5000:7000]

    ds = FrameDataset(df, model.get_transforms(is_training=False), 1, is_train=False)
    dls = DataLoader(ds, batch_size=32, num_workers=2, pin_memory=True)

    preds_list: list[torch.Tensor] = trainer.predict(model, dataloaders=dls)  # type: ignore
    preds = torch.cat(preds_list)
    pred_class = torch.argmax(preds, dim=1)
    preds_class = np.repeat(pred_class.numpy(), ds.frames_per_clip)

    df = df.with_columns(preds=pl.Series(preds_class))

    df_g = df.group_by(pl.col("frame") // (aggregate_duration * fps)).agg(
        pl.sum("preds")
    )
    seconds = pl.col("frame")
    df_g = (
        df_g.with_columns(pl.col("frame") * aggregate_duration)
        .with_columns(
            hour=seconds // (60 * 60), minute=(seconds // 60) % 60, second=seconds % 60
        )
        .with_columns(
            timestamp=pl.datetime(
                year=2023,
                month=12,
                day=10,
                hour=pl.col("hour"),
                minute="minute",
                second="second",
            )
        )
        .sort("timestamp")
    )

    return df_g
