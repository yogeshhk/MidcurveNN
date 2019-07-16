from keras import regularizers
from keras.layers import Input, Dense
from keras.models import Model, load_model
from prepare_data import get_training_data
from prepare_plots import plot_results
import numpy as np
import os
import random
import sys
np.set_printoptions(threshold=sys.maxsize)

from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from keras import backend as K

class cnn_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 100
        self.epochs = 50
        self.cnn_autoencoder_model_pkl = "models/cnn_autoencoder_model.pkl"

                
    def process_images(self,grayobjs):
        flat_objs = [x.reshape(self.input_dim,self.input_dim,1) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
            profile_pngs_gray_objs, 
            midcurve_pngs_gray_objs):
        
        if not os.path.exists(self.cnn_autoencoder_model_pkl):       
            input_img = Input(shape=(self.input_dim, self.input_dim, 3))  # adapt this if using `channels_first` image data format
            
            #x = ZeroPadding2D((5,5))(input_img)
            x = Conv2D(32, (3, 3), strides=(2, 2), activation='relu', padding='same')(input_img)
            #x = MaxPooling2D((2, 2), padding='same')(x)
            x = Conv2D(16, (3, 3), strides=(2, 2), activation='relu', padding='same')(x)
            #x = MaxPooling2D((2, 2), padding='same')(x)
            x = Conv2D(16, (3, 3), strides=(2, 2), activation='relu', padding='same')(x)
            x = Conv2D(8, (3, 3), strides=(2, 2), activation='relu', padding='same')(x)
            encoded = Conv2D(8, (3, 3), strides=(2,2), activation='relu', padding='same')(x)
            #
            #encoded = MaxPooling2D((2, 2), padding='same')(x)
        
            # at this point the representation is (4, 4, 8) i.e. 128-dimensional
            
            '''x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
            x = UpSampling2D((2, 2))(x)
            x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
            x = UpSampling2D((2, 2))(x)
            x = Conv2D(16, (3, 3), activation='relu')(x)
            x = UpSampling2D((2, 2))(x)
            decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)'''
            #y = ZeroPadding2D()(encoded)
            y = Conv2DTranspose(8, (3, 3), strides = (2, 2), padding='same', activation='relu')(encoded)
            y = Conv2DTranspose(4, (3, 3), strides = (2, 2), padding='same', activation='relu')(y)
            y = Conv2DTranspose(4, (3, 3), strides = (2, 2), padding='same', activation='relu')(y)
            y = Conv2DTranspose(2, (3, 3), strides = (2, 2), padding='same', activation='relu')(y)
            decoded = Conv2DTranspose(1, (3, 3), strides = (2, 2), activation='tanh', padding='same')(y)
            
            
            # Model 1: Full AutoEncoder, includes both encoder single dense layer and decoder single dense layer. 
            # This model maps an input to its reconstruction
            self.cnn_autoencoder = Model(input_img, decoded)
            self.cnn_autoencoder.summary()
            
            # Compilation of Autoencoder (only)
            self.cnn_autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
            
            
            # Training
            #profile_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in profile_pngs_gray_objs]
            #midcurve_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in midcurve_pngs_gray_objs]
            
            #profile_pngs_objs = np.array(profile_pngs_flat_objs)
            #midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
        
#             profile_pngs_objs = profile_pngs_gray_objs
#             midcurve_pngs_objs = midcurve_pngs_gray_objs
#             
#             train_size = int(len(profile_pngs_objs)*0.7)
#             x_train = profile_pngs_objs[:train_size]
#             y_train = midcurve_pngs_objs[:train_size]
#             x_test = profile_pngs_objs[train_size:]
#             y_test = midcurve_pngs_objs[train_size:]
#             self.cnn_autoencoder.fit(x_train, y_train,
#                         epochs=50,
#                         batch_size=5,
#                         shuffle=True,
#                         validation_data=(x_test, y_test))
                
            profile_pngs_objs = self.process_images(profile_pngs_gray_objs)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs)                
            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            
            self.cnn_autoencoder.fit(self.x, self.y,
                        epochs=5,
                        batch_size=5,
                        shuffle=True)
                            
            # Save models
            self.cnn_autoencoder.save(self.autoencoder_model_pkl)
        else:
            # Save models
            self.cnn_autoencoder = load_model(self.autoencoder_model_pkl)

    
    def predict(self, test_profile_images):
        encoded_imgs = self.cnn_autoencoder.predict(test_profile_images)
        decoded_imgs = self.cnn_autoencoder.predict(encoded_imgs)       
        return test_profile_images,decoded_imgs  
    

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    endec = cnn_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    
    test_gray_images = random.sample(profile_gray_objs,5)
    original_profile_imgs,predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs,predicted_midcurve_imgs)