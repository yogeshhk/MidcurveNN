from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense, Add, BatchNormalization
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import numpy as np
import os
import random
import sys
from config import MODELS_FOLDER

class cnn_encoderdecoder:
    def __init__(self,input_shape=(128,128,1)):
        self.encoding_dim = 100
        self.input_dim = 128
        self.epochs = 100
        self.batch_size = 16
        self.cnn_autoencoder_model_pkl = os.path.join("models","cnn_autoencoder_model")
        self.input_shape = input_shape

    def process_images(self,grayobjs,shape=(128,128,1)):
        flat_objs = [x.reshape(shape[0],shape[1],shape[2]) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
            profile_pngs_gray_objs, 
            midcurve_pngs_gray_objs,
            retrain_model=False):
        
        if not os.path.exists(self.cnn_autoencoder_model_pkl) or retrain_model:
            input_img = Input(shape=self.input_shape)

            # Level 1: 128x128
            x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
            x = BatchNormalization()(x)
            skip1 = x

            # Level 2: 64x64
            x = Conv2D(64, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            skip2 = x  # 64x64x64

            # Level 3: 32x32
            x = Conv2D(128, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            skip3 = x  # 32x32x128

            # Level 4: 16x16
            x = Conv2D(256, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Conv2D(256, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            
            # Decoder path
            # Level 3: 32x32
            x = Conv2DTranspose(128, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Add()([x, skip3])
            x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)

            # Level 2: 64x64
            x = Conv2DTranspose(64, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Add()([x, skip2])
            x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)

            # Level 1: 128x128
            x = Conv2DTranspose(32, (3, 3), strides=2, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Add()([x, skip1])
            x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
            x = BatchNormalization()(x)

            # Final output
            decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
            
            self.cnn_autoencoder = Model(input_img, decoded)
            self.cnn_autoencoder.summary()
            
            self.cnn_autoencoder.compile(
                optimizer='adam', 
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            profile_pngs_objs = self.process_images(profile_pngs_gray_objs,self.input_shape)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs,(128,128,1))                
            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            
            callbacks = [
                EarlyStopping(
                    monitor='loss',
                    patience=10,
                    restore_best_weights=True
                ),
                ReduceLROnPlateau(
                    monitor='loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-6
                )
            ]
            
            self.cnn_autoencoder.fit(
                self.x, self.y,
                epochs=self.epochs,
                batch_size=self.batch_size,
                shuffle=True,
                callbacks=callbacks,
                validation_split=0.2
            )
                            
            print("saving model at {}".format(self.cnn_autoencoder_model_pkl))
            self.cnn_autoencoder.save(self.cnn_autoencoder_model_pkl)
        else:
            print("loading model from {}".format(self.cnn_autoencoder_model_pkl))
            self.cnn_autoencoder = load_model(self.cnn_autoencoder_model_pkl)
    
    def predict(self, test_profile_images, expand_dims=True):
        if expand_dims:
            test_profile_images = np.expand_dims(np.asarray(test_profile_images),axis=-1)
        encoded_imgs = self.cnn_autoencoder.predict(test_profile_images)
        return test_profile_images, encoded_imgs
    

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data(size=(128,128))

    endec = cnn_encoderdecoder()
    endec.train(np.asarray(profile_gray_objs)/255., np.asarray(midcurve_gray_objs)/255.,100)
    
    test_gray_images = random.sample(profile_gray_objs,5)
    original_profile_imgs,predicted_midcurve_imgs = endec.predict(np.asarray(test_gray_images)/255.)

    print(np.max(predicted_midcurve_imgs))
    print(np.min(predicted_midcurve_imgs))

    plot_results(original_profile_imgs,predicted_midcurve_imgs,size=(128,128))

