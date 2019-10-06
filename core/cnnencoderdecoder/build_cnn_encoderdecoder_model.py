from keras import regularizers
from keras.layers import Input, Dense
from keras.models import Model, load_model
from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from keras import backend as K

import numpy as np
import os
import random
import sys

np.set_printoptions(threshold=sys.maxsize)

<<<<<<< HEAD
sys.path.append('..')
=======
#sys.path.append('...')
>>>>>>> ca58f4f5c08634fd0f1d2265872bdac166ce85c6
from utils.utils import get_training_data
from utils.utils import plot_results


class cnn_encoderdecoder:
    def __init__(self,input_shape=(128,128,1)):
        self.encoding_dim = 100
        self.input_dim = 128 #100
        self.epochs = 50
        self.cnn_autoencoder_model_pkl = "models/cnn_autoencoder_model.pkl"
        self.input_shape = input_shape

    def process_images(self,grayobjs,shape=(128,128,1)):
        flat_objs = [x.reshape(shape[0],shape[1],shape[2]) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
            profile_pngs_gray_objs, 
            midcurve_pngs_gray_objs,
            epochs=50):
        
        if not os.path.exists(self.cnn_autoencoder_model_pkl):       
            input_img = Input(shape=self.input_shape)  # adapt this if using `channels_first` image data format
            
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
            decoded = Conv2DTranspose(1, (3, 3), strides = (2, 2), activation='sigmoid', padding='same')(y)
            
            
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
                
            profile_pngs_objs = self.process_images(profile_pngs_gray_objs,self.input_shape)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs,(128,128,1))                
            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            
            self.cnn_autoencoder.fit(self.x, self.y,
                        epochs=epochs,
                        batch_size=32,
                        shuffle=True)
                            
            # Save models
            self.cnn_autoencoder.save(self.cnn_autoencoder_model_pkl)
        else:
            # Save models
            self.cnn_autoencoder = load_model(self.cnn_autoencoder_model_pkl)

    
    def predict(self, test_profile_images,expand_dims=True):
        if expand_dims:
            test_profile_images = np.expand_dims(np.asarray(test_profile_images),axis=-1)
        #test_profile_images = np.asarray(test_profile_images)
        encoded_imgs = self.cnn_autoencoder.predict(test_profile_images)
        #encoded_imgs = np.expand_dims(np.asarray(encoded_imgs),axis=-1)
        #decoded_imgs = self.cnn_autoencoder.predict(encoded_imgs)       
        return test_profile_images,encoded_imgs  
    

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data(size=(128,128))

    endec = cnn_encoderdecoder()
    endec.train(np.asarray(profile_gray_objs)/255., np.asarray(midcurve_gray_objs)/255.,100)
    
    test_gray_images = random.sample(profile_gray_objs,5)
    original_profile_imgs,predicted_midcurve_imgs = endec.predict(np.asarray(test_gray_images)/255.)

    print(np.max(predicted_midcurve_imgs))
    print(np.min(predicted_midcurve_imgs))

    plot_results(original_profile_imgs,predicted_midcurve_imgs,size=(128,128))

