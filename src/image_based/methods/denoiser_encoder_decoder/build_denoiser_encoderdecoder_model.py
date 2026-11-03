from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from tensorflow.keras import backend as K
from tensorflow.keras import regularizers
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam

import os
import sys
import numpy as np

np.set_printoptions(threshold=sys.maxsize)


class denoiser_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 100
        self.epochs = 500
        self.batch_size = 5
        _models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        os.makedirs(_models_dir, exist_ok=True)
        self.denoiser_autoencoder_model_pkl = os.path.join(_models_dir,
                                                           "denoiser_autoencoder_model.keras")

        self._build()

    def _build(self):
        """Build Keras model with random weights (no training data needed)."""
        input_img = Input(shape=(self.input_dim, self.input_dim, 1))

        x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
        x = MaxPooling2D((2, 2), padding='same')(x)
        x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        encoded = MaxPooling2D((2, 2), padding='same')(x)

        x = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)
        x = UpSampling2D((2, 2))(x)
        x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
        x = UpSampling2D((2, 2))(x)
        decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

        self.denoiser_autoencoder = Model(input_img, decoded)
        self.denoiser_autoencoder.compile(
            optimizer=Adam(1e-3), loss='binary_crossentropy', metrics=['accuracy'])

    def process_images(self, grayobjs):
        flat_objs = [x.reshape(self.input_dim, self.input_dim, 1) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self, noisy_images_objs, clean_images_objs, retrain_mdodel=False):

        if not os.path.exists(self.denoiser_autoencoder_model_pkl) or retrain_mdodel:
            self.x = self.process_images(noisy_images_objs)
            self.y = self.process_images(clean_images_objs)
            es = EarlyStopping(monitor='val_loss', mode='min', patience=20,
                               restore_best_weights=True)

            self.denoiser_autoencoder.fit(self.x, self.y,
                                          epochs=self.epochs,
                                          batch_size=self.batch_size,
                                          validation_split=0.3,
                                          callbacks=[es],
                                          shuffle=True)
            self.denoiser_autoencoder.save(self.denoiser_autoencoder_model_pkl)
        else:
            self.denoiser_autoencoder = load_model(self.denoiser_autoencoder_model_pkl)

    def predict(self, test_noisy_images):
        png_profile_images = self.process_images(test_noisy_images)
        denoised_imgs = self.denoiser_autoencoder.predict(png_profile_images)
        return test_noisy_images, denoised_imgs.squeeze(axis=-1)

# Run via main_denoiser_encoderdecoder.py, not this module directly: that entry point
# normalizes images to [0,1] before training (BCE targets must be in [0,1]), which this
# file's own now-removed __main__ block did not do (see analysis_report.md Bug 12).
