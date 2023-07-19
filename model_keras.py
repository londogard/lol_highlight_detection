from keras_core.models import Model
from keras_core.layers import Input, LSTM, Dense, TimeDistributed, Flatten


class VideoClassifier:
    def __init__(self, num_classes):
        self.num_classes = num_classes

        # Feature extraction layers
        self.video_input = Input(shape=(NUM_FRAMES, H, W, C))
        self.cnn = ResNet50(
            weights="imagenet", include_top=False, input_shape=(H, W, C)
        )
        self.cnn_features = TimeDistributed(cnn)(video_input)
        self.cnn_features = Flatten()(cnn_features)

        # Classification layers
        self.x = LSTM(256, return_sequences=True)(cnn_features)
        self.x = LSTM(256)(x)
        self.x = Dense(512, activation="relu")(x)
        self.outputs = Dense(num_classes, activation="softmax")(x)

        # Compile model
        self.model = Model(video_input, outputs)
        self.model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

    def fit(self, x_train, y_train, epochs=10, validation_data=None):
        self.model.fit(x_train, y_train, epochs=epochs, validation_data=validation_data)

    def evaluate(self, x_test, y_test):
        return self.model.evaluate(x_test, y_test)
