import solara
import torch
import torch.nn as nn
import torch.nn.functional as F
import lightning as L
import torchmetrics


class LightningWrapper(L.LightningModule):
    def __init__(self, model: nn.Module, learning_rate=1e-3):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])
        self.model = model  # self.hparams["model"]: TODO use hparams
        self.lr = learning_rate
        solara.Text(self.model)
        metrics = torchmetrics.MetricCollection(
            {
                "accuracy": torchmetrics.Accuracy(
                    task="multiclass", num_classes=self.model.num_classes
                )
            }
        )
        self.train_metrics = metrics.clone(prefix="train_")
        self.val_metrics = metrics.clone(prefix="val_")

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
