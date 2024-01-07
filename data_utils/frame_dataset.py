from torchvision.transforms import Compose
import torch
from torch.utils.data import Dataset
from torchvision.datasets.folder import default_loader
import polars as pl


class FrameDataset(Dataset):
    def __init__(
        self,
        df: pl.DataFrame,
        augments: Compose,
        frames_per_clip: int,
        stride: int | None = None,
        is_train: bool = True,
    ):
        super().__init__()
        self.paths = df["path"].to_list()
        self.is_train = is_train
        if is_train:
            self.y = torch.tensor(df["label"])
        self.frames_per_clip = frames_per_clip
        self.augments = augments
        self.stride = stride or frames_per_clip

    def __len__(self):
        return len(self.paths) // self.stride

    def __getitem__(self, idx):
        start = idx * self.stride
        stop = start + self.frames_per_clip
        if stop - start <= 1:
            path = self.paths[start]
            frames_tr = self._open_augment_img(path)
            if self.is_train:
                y = self.y[start]
        else:
            frames = [self._open_augment_img(path) for path in self.paths[start:stop]]
            frames_tr = torch.stack(frames)
            if self.is_train:
                y = self.y[start:stop].max()
        if self.is_train:
            return frames_tr, y
        else:
            return frames_tr

    def _open_augment_img(self, path):
        img = default_loader(path)
        img = self.augments(img)
        return img
