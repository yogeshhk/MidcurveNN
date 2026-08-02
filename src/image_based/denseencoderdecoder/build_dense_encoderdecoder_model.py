import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from utils.metric_utils import MetricsHistory, print_best_metrics
import numpy as np

class dense_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 10000
        self.epochs = 100
        self.batch_size = 16
        _models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(_models_dir, exist_ok=True)
        self.autoencoder_model_pkl = os.path.join(_models_dir, "dense_autoencoder_model.keras")
        self.encoder_model_pkl = os.path.join(_models_dir, "dense_encoder_model.keras")
        self.decoder_model_pkl = os.path.join(_models_dir, "dense_decoder_model.keras")

        self._build()

    def _build(self):
        """Build Keras sub-models with random weights (no training data needed)."""
        input_img = Input(shape=(self.input_dim,))
        encoded = Dense(2048, activation='elu')(input_img)
        encoded = Dense(1024, activation='elu')(encoded)
        encoded = Dense(self.encoding_dim, activation='elu')(encoded)
        decoded = Dense(1024, activation='elu')(encoded)
        decoded = Dense(2048, activation='elu')(decoded)
        decoded = Dense(self.input_dim, activation='sigmoid')(decoded)

        self.autoencoder = Model(input_img, decoded)
        self.encoder = Model(input_img, encoded)

        encoded_input = Input(shape=(self.encoding_dim,))
        decoder_layers = self.autoencoder.layers[-3:]
        x = encoded_input
        for layer in decoder_layers:
            x = layer(x)
        self.decoder = Model(encoded_input, x)

        self.autoencoder.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'mae']
        )

    def process_images(self, grayobjs):
        flat_objs = [x.reshape(self.input_dim) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
              profile_pngs_gray_objs,
              midcurve_pngs_gray_objs,
              retrain_model=False):
        if not os.path.exists(self.autoencoder_model_pkl) or retrain_model:
            profile_pngs_objs = self.process_images(profile_pngs_gray_objs)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs)

            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs

            metrics_history = MetricsHistory()
            callbacks = [
                EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=50,
                              restore_best_weights=True),
                metrics_history
            ]

            self.autoencoder.fit(
                self.x, self.y,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=0.3,
                callbacks=callbacks,
                shuffle=True
            )

            self.autoencoder.save(self.autoencoder_model_pkl)
            self.encoder.save(self.encoder_model_pkl)
            self.decoder.save(self.decoder_model_pkl)
            print_best_metrics(metrics_history.history, "Dense Encoder-Decoder")
        else:
            self.autoencoder = load_model(self.autoencoder_model_pkl)
            self.encoder = load_model(self.encoder_model_pkl)
            self.decoder = load_model(self.decoder_model_pkl)

    def predict(self, test_profile_images):
        png_profile_images = self.process_images(test_profile_images)
        encoded_imgs = self.encoder.predict(png_profile_images)
        decoded_imgs = self.decoder.predict(encoded_imgs)
        decoded_imgs = decoded_imgs.reshape(-1, 100, 100)  # Reshape to original image dimensions
        return test_profile_images, decoded_imgs

# Run via main_dense_encoderdecoder.py, not this module directly: that entry point holds
# out a real test split before training (this file's own now-removed __main__ block
# trained on the same data it then "tested" on -- see analysis_report.md Bug 6).
