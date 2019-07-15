from keras.layers import Input, Dense
from keras.models import Model
from keras import regularizers

import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from keras import backend as K

def build_cnn_encoderdecoder_model(profile_pngs_gray_objs, midcurve_pngs_gray_objs,encoding_dim = 100, input_dim = 128):
    
    input_img = Input(shape=(input_dim, input_dim, 3))  # adapt this if using `channels_first` image data format
    
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
    autoencoder = Model(input_img, decoded)
    autoencoder.summary()
    
    # Compilation of Autoencoder (only)
    autoencoder.compile(optimizer='adam', loss='binary_crossentropy')
    
    
    # Training
    #profile_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in profile_pngs_gray_objs]
    #midcurve_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in midcurve_pngs_gray_objs]
    
    #profile_pngs_objs = np.array(profile_pngs_flat_objs)
    #midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)

    profile_pngs_objs = profile_pngs_gray_objs
    midcurve_pngs_objs = midcurve_pngs_gray_objs
    
    train_size = int(len(profile_pngs_objs)*0.7)
    x_train = profile_pngs_objs[:train_size]
    y_train = midcurve_pngs_objs[:train_size]
    x_test = profile_pngs_objs[train_size:]
    y_test = midcurve_pngs_objs[train_size:]
    autoencoder.fit(x_train, y_train,
                epochs=50,
                batch_size=5,
                shuffle=True,
                validation_data=(x_test, y_test))
        
    encoded_imgs = autoencoder.predict(x_test)
    decoded_imgs = autoencoder.predict(encoded_imgs)    
        
    return x_test,decoded_imgs

# def train_encoderdecoder_model(autoencoder,profile_pngs_objs, midcurve_pngs_objs):
#     train_size = int(len(profile_pngs_objs)*0.7)
#     x_train = profile_pngs_objs[:train_size]
#     y_train = midcurve_pngs_objs[:train_size]
#     x_test = profile_pngs_objs[train_size:]
#     y_test = midcurve_pngs_objs[train_size:]
#     autoencoder.fit(x_train, y_train,
#                 epochs=50,
#                 batch_size=5,
#                 shuffle=True,
#                 validation_data=(x_test, y_test))
#     return autoencoder,x_test,encoded_imgs

if __name__ == "__main__":
    pass