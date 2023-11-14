from typing import Callable
import torch
import torch.nn as nn
import torch.nn.functional as F
import lightning as L
import torchmetrics
import timm


class LightningWrapper(L.LightningModule):
    def __init__(self, timm_model: str, num_classes: int, learning_rate: float = 1e-3):
        super().__init__()
        self.timm_model = timm_model
        self.lr = learning_rate
        self.model = timm.create_model(
            self.timm_model, pretrained=True, num_classes=num_classes
        )
        self.save_hyperparameters(ignore=["model"])

        metrics = torchmetrics.MetricCollection(
            {
                "accuracy": torchmetrics.Accuracy(
                    task="multiclass", num_classes=self.model.num_classes
                )
            }
        )

        self.train_metrics = metrics.clone(prefix="train_")
        self.val_metrics = metrics.clone(prefix="val_")

    def get_transforms(self, is_training: bool):
        data_config = timm.data.resolve_model_data_config(self.timm_model)
        return timm.data.create_transform(**data_config, is_training=is_training)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        self.log("train_loss", loss)
        self.train_metrics(logits, y)
        self.log_dict(self.train_metrics, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        self.log("val_loss", loss)
        self.val_metrics(logits, y)
        self.log_dict(self.val_metrics, prog_bar=True)

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)
        return optimizer
