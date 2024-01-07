import torch.nn as nn
from torchvision.models import ResNet


class ResNetClassifier(nn.Module):
    def __init__(self, model: ResNet, num_classes: int = 2):
        super().__init__()
        self.num_classes = num_classes
        self.model = model
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)
