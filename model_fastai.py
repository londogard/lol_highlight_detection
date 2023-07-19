from fastai.vision.all import *  # noqa: F403


# fastai equivalent model
class VideoClassifier(Module):
    def __init__(self, num_classes: int):
        self.cnn = resnet50(pretrained=True)
        self.rnn = LSTM(256, batch_first=True, bidirectional=True)
        self.linear = nn.Linear(512, num_classes)

    def forward(self, x):
        batch_size, seq_len, channels, height, width = x.shape

        # CNN features
        x = x.reshape(batch_size * seq_len, channels, height, width)
        x = self.cnn(x)

        # RNN
        x = x.reshape(batch_size, seq_len, -1)
        x, _ = self.rnn(x)

        # Classifier
        x = self.linear(x[:, -1, :])

        return F.log_softmax(x, dim=1)


# fastai style dataloaders and training loop
dls = DataLoader(videos, bs=64)

learn = Learner(
    dls, VideoClassifier(num_classes), loss_func=CrossEntropyLoss(), metrics=accuracy
)

learn.fit(10)
