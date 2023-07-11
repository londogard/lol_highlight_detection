import torch
import torch.nn as nn
from torchvision.models import ResNet


class RNNClassifier(nn.Module):
    def __init__(self, model: ResNet, num_classes: int = 2):
        super().__init__()
        self.num_classes = num_classes
        self.feature_extractor = model  # repeat thrice
        self.feature_extractor.fc = nn.Linear(512, 512)  # New fc layer
        self.rnn = nn.LSTM(
            input_size=512, hidden_size=256, num_layers=1, batch_first=True
        )
        self.classifier = nn.Linear(256, num_classes)

    def forward(self, x):
        features = []

        # Pass each frame through ResNet sequentially
        for i in range(x.shape[1]):
            frame_feat = self.feature_extractor(x[:, i])
            features.append(frame_feat)

        x = torch.reshape(torch.stack(features), [x.shape[0], x.shape[1], -1])

        # Apply RNN
        out, _ = self.rnn(x)
        out = out[:, -1, :]

        # Classify
        out = self.classifier(out)

        return out
