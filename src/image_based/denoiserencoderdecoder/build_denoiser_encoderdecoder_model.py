from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from tensorflow.keras import backend as K
from tensorflow.keras import regularizers
from tensorflow.keras.callbacks import EarlyStopping

from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
from utils.prepare_data import get_training_data
from utils.prepare_plots import plot_results
import os
import sys
import numpy as np
import random

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
            optimizer='adadelta', loss='binary_crossentropy', metrics=['accuracy'])

    def process_images(self, grayobjs):
        flat_objs = [x.reshape(self.input_dim, self.input_dim, 1) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self, noisy_images_objs, clean_images_objs, retrain_mdodel=False):

        if not os.path.exists(self.denoiser_autoencoder_model_pkl) or retrain_mdodel:
            self.x = self.process_images(noisy_images_objs)
            self.y = self.process_images(clean_images_objs)
            es = EarlyStopping(monitor='val_accuracy', mode='max', min_delta=1)

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


if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    original_profile_images, noisy_predicted_midcurve_images = endec.predict(profile_gray_objs)
    plot_results(original_profile_images[:5], noisy_predicted_midcurve_images[:5])

    denoiser = denoiser_encoderdecoder()
    denoiser.train(noisy_predicted_midcurve_images, midcurve_gray_objs)
    sample_noisy_midcurve_images = random.sample(noisy_predicted_midcurve_images, 5)
    original_noisy_midcurve_images, clean_predicted_midcurve_images = denoiser.predict(sample_noisy_midcurve_images)
    plot_results(original_noisy_midcurve_images, clean_predicted_midcurve_images)
