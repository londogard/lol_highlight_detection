import lightning as L
import numpy as np
from torch.utils.data import DataLoader, Subset, Dataset

from data_utils.splitter import chunk_splitter


class FrameDataModule(L.LightningDataModule):
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        chunk_size_for_splitting: int = 3 * 30,
        num_workers: int = 2,
        pin_memory: bool = False,
    ):
        super().__init__()
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.chunk_size_for_splitting = chunk_size_for_splitting
        split = chunk_splitter(
            len(dataset), chunk_size=self.chunk_size_for_splitting, split=0.15
        )
        val_indices = np.where(split)[0]
        train_indices = np.where(split == 0)[0]
        self.ds_train = Subset(self.dataset, train_indices)
        self.ds_val = Subset(self.dataset, val_indices)

    def train_dataloader(self):
        return DataLoader(
            self.ds_train,
            shuffle=True,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )

    def val_dataloader(self):
        return DataLoader(
            self.ds_val,
            batch_size=self.batch_size,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
