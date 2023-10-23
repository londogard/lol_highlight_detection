from pathlib import Path
import numpy as np
from torch import nn
from torch.utils.data import DataLoader
import polars as pl
import lightning as L
from data_utils.frame_dataset import FrameDataset
import torch
import torchvision.transforms as F


def run_inference(
    model: nn.Module,
    image_folder: Path,
    aggregate_duration: int = 30,
    fps: int = 3,
):
    trainer = L.Trainer()
    paths = list(image_folder.rglob("*.jpg"))
    transform = F.Compose([F.Resize((224, 224)), F.ToTensor()])
    df = pl.DataFrame(
        {"path": paths, "frame": [int(p.stem.removeprefix("img")) for p in paths]}
    )
    df = df.sort("frame")
    ds = FrameDataset(df, transform, 1, is_train=False)
    dls = DataLoader(ds, batch_size=32, num_workers=2, pin_memory=True)
    preds = trainer.predict(model, dataloaders=dls)
    preds = torch.cat(preds)

    print(preds.shape)
    pred_class = torch.argmax(preds, dim=1)
    print("% highlights predicted", pred_class.sum() / len(preds))
    preds_class = np.repeat(pred_class.numpy(), ds.frames_per_clip)
    df = df.with_columns(preds=pl.Series(preds_class))

    df["preds"].sum(), df["preds"].mean()

    df_g = df.group_by(pl.col("frame") // (aggregate_duration * fps)).agg(
        pl.sum("preds")
    )
    seconds = pl.col("frame")
    df_g = (
        df_g.with_columns(pl.col("frame") * aggregate_duration)
        .with_columns(
            hour=seconds // (60 * 60), minute=(seconds // 60) % 60, second=seconds % 60
        )
        .with_columns(timestamp=pl.time(pl.col("hour"), "minute", "second"))
        .sort("timestamp")
    )
    print("% highlights", df_g["preds"].sum() / len(df_g))

    # px.line(df_g, x="timestamp", y="preds", line_shape="hv")

    return df_g