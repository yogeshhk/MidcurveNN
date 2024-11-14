import os
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from utils.metric_utils import MetricsHistory, print_best_metrics
import numpy as np
import sys
import random

class dense_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 10000
        self.epochs = 100
        self.batch_size = 16
        self.autoencoder_model_pkl = os.path.join("models", "dense_autoencoder_model")
        self.encoder_model_pkl = os.path.join("models", "dense_encoder_model")
        self.decoder_model_pkl = os.path.join("models", "dense_decoder_model")

    def process_images(self, grayobjs):
        flat_objs = [x.reshape(self.input_dim) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
              profile_pngs_gray_objs,
              midcurve_pngs_gray_objs,
              retrain_model=False):
        if not os.path.exists(self.autoencoder_model_pkl) or retrain_model:
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

            optimizer = Adam(learning_rate=0.0001)
            self.autoencoder.compile(
                optimizer=optimizer, 
                loss='binary_crossentropy',
                metrics=['accuracy', 'mae']
            )

            profile_pngs_objs = self.process_images(profile_pngs_gray_objs)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs)

            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            
            metrics_history = MetricsHistory()
            callbacks = [
                EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=50),
                metrics_history
            ]

            history = self.autoencoder.fit(
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
            print_best_metrics(metrics_history.history)
        else:
            self.autoencoder = load_model(self.autoencoder_model_pkl)
            self.encoder = load_model(self.encoder_model_pkl)
            self.decoder = load_model(self.decoder_model_pkl)
            
        print_best_metrics(metrics_history.history, "Dense Encoder-Decoder")

    def predict(self, test_profile_images):
        png_profile_images = self.process_images(test_profile_images)
        encoded_imgs = self.encoder.predict(png_profile_images)
        decoded_imgs = self.decoder.predict(encoded_imgs)
        decoded_imgs = decoded_imgs.reshape(-1, 100, 100)  # Reshape to original image dimensions
        return test_profile_images, decoded_imgs


if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    test_gray_images = random.sample(profile_gray_objs, 5)

    profile_gray_objs = np.asarray(profile_gray_objs) / 255.
    midcurve_gray_objs = np.asarray(midcurve_gray_objs) / 255.
    test_gray_images = np.asarray(test_gray_images) / 255.

    endec = dense_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)

    original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs, predicted_midcurve_imgs)
