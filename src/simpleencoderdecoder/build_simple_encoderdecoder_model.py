import os

import tensorflow as tf

from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Dropout
from tensorflow.keras.models import Model, load_model, save_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam

import numpy as np
import sys
import random
from pathlib import Path

sys.path.append('..')
from utils.utils import get_training_data
from utils.utils import plot_results

np.set_printoptions(threshold=sys.maxsize)


class simple_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 10000
        self.epochs = 200
        self.batch_size = 32  
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.autoencoder_model_pkl = self.models_dir / "autoencoder_model"
        self.encoder_model_pkl = self.models_dir / "encoder_model"
        self.decoder_model_pkl = self.models_dir / "decoder_model"

    def process_images(self, grayobjs):
        return np.array([x.reshape(self.input_dim) for x in grayobjs])

    def train(self,
              profile_pngs_gray_objs,
              midcurve_pngs_gray_objs,
              retrain_model=False):

        if not self.autoencoder_model_pkl.exists() or retrain_model:
            input_img = Input(shape=(self.input_dim,))

            encoded = Dense(self.encoding_dim, 
                          activation='relu',
                          kernel_initializer='he_normal',
                          activity_regularizer=regularizers.l1(1e-5))(input_img)
            encoded = BatchNormalization()(encoded)
            encoded = Dropout(0.2)(encoded)

            decoded = Dense(self.input_dim,
                          activation='sigmoid',
                          kernel_initializer='glorot_normal')(encoded)

            self.autoencoder = Model(input_img, decoded)
            self.encoder = Model(input_img, encoded)
            
            encoded_input = Input(shape=(self.encoding_dim,))
            decoder_layer = self.autoencoder.layers[-1]
            self.decoder = Model(encoded_input, decoder_layer(encoded_input))

            optimizer = Adam(learning_rate=0.001)
            self.autoencoder.compile(
                optimizer=optimizer,
                loss='binary_crossentropy',
                metrics=['accuracy', 'mae']
            )

            profile_pngs_objs = self.process_images(profile_pngs_gray_objs)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs)

            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    mode='min',
                    verbose=1,
                    patience=50,
                    restore_best_weights=True
                ),
                ModelCheckpoint(
                    filepath=str(self.autoencoder_model_pkl),
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]

            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            
            self.autoencoder.fit(
                self.x, self.y,
                epochs=self.epochs,
                batch_size=self.batch_size,
                validation_split=0.3,
                callbacks=callbacks,
                shuffle=True,
                verbose=1
            )

            self.autoencoder.save(self.autoencoder_model_pkl, save_format='tf')
            self.encoder.save(self.encoder_model_pkl, save_format='tf')
            self.decoder.save(self.decoder_model_pkl, save_format='tf')
        else:
            self.autoencoder = load_model(self.autoencoder_model_pkl)
            self.encoder = load_model(self.encoder_model_pkl)
            self.decoder = load_model(self.decoder_model_pkl)

    def predict(self, test_profile_images):
        png_profile_images = self.process_images(test_profile_images)
        encoded_imgs = self.encoder.predict(png_profile_images, batch_size=self.batch_size)
        decoded_imgs = self.decoder.predict(encoded_imgs, batch_size=self.batch_size)
        return test_profile_images, decoded_imgs


if __name__ == "__main__":
    tf.keras.mixed_precision.set_global_policy('mixed_float16')
    
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    test_gray_images = random.sample(profile_gray_objs, 5)

    profile_gray_objs = np.asarray(profile_gray_objs, dtype=np.float32) / 255.
    midcurve_gray_objs = np.asarray(midcurve_gray_objs, dtype=np.float32) / 255.
    test_gray_images = np.asarray(test_gray_images, dtype=np.float32) / 255.

    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)

    original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs, predicted_midcurve_imgs)