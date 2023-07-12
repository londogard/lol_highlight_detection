import torch
import torch.nn as nn
import torch.functional as F
import pytorch_lightning as pl
import torchvision


class VideoModel(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.cnn = torchvision.models.resnet18(pretrained=True)
        self.rnn = nn.LSTM(512, 256, batch_first=True)
        self.classifier = nn.Linear(256, 2)

    def forward(self, x):
        # x shape: (batch, frames, C, H, W)

        x = self.cnn(x)
        # Reshape to (batch, frames, features)
        x = x.reshape(x.shape[0], x.shape[1], -1)
        x, _ = self.rnn(x)

        # Take the last timestep output
        x = x[:, -1, :]
        x = self.classifier(x)

        return x

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = F.cross_entropy(y_hat, y)
        self.log("val_loss", loss)

    def test_step(self, batch, batch_idx):
        # Similar to validation_step
        pass

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)
