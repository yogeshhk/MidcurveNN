from keras.layers import Input, Dense
from keras.models import Model
from keras import regularizers

import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

def build_basic_autoencoder_model(profile_pngs_gray_objs, midcurve_pngs_gray_objs, encoding_dim = 100, input_dim = 10000):
    # this is our input placeholder
    input_img = Input(shape=(input_dim,))
    
    # "encoded" is the encoded representation of the input
    encoded = Dense(encoding_dim, activation='relu',activity_regularizer=regularizers.l1(10e-5))(input_img)
    # "decoded" is the lossy reconstruction of the input
    decoded = Dense(input_dim, activation='sigmoid')(encoded) 
    
    # Model 1: Full AutoEncoder, includes both encoder single dense layer and decoder single dense layer. 
    # This model maps an input to its reconstruction
    autoencoder = Model(input_img, decoded)
            
    # Model 2: a separate encoder model: -------------------
    # this model maps an input to its encoded representation
    encoder = Model(input_img, encoded)
    
    # Model 3: a separate encoder model: -------------------
    # create a placeholder for an encoded (32-dimensional) input
    encoded_input = Input(shape=(encoding_dim,))
    # retrieve the last layer of the autoencoder model
    decoder_layer = autoencoder.layers[-1]
    # create the decoder model
    decoder = Model(encoded_input, decoder_layer(encoded_input))
    
    # Compilation of Autoencoder (only)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
    
    # Training
    profile_pngs_flat_objs = [x.reshape(input_dim) for x in profile_pngs_gray_objs]
    midcurve_pngs_flat_objs = [x.reshape(input_dim) for x in midcurve_pngs_gray_objs]
    
    profile_pngs_objs = np.array(profile_pngs_flat_objs)
    midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
    
    train_size = int(len(profile_pngs_objs)*0.7)
    x_train = profile_pngs_objs[:train_size]
    y_train = midcurve_pngs_objs[:train_size]
    x_test = profile_pngs_objs[train_size:]
    y_test = midcurve_pngs_objs[train_size:]
    autoencoder.fit(x_train, y_train,
                epochs=200,
                batch_size=5,
                shuffle=True,
                validation_data=(x_test, y_test))
        
    encoded_imgs = encoder.predict(x_test)
    decoded_imgs = decoder.predict(encoded_imgs)    
    return x_test,decoded_imgs    



def build_dense_autoencoder_model(profile_pngs_gray_objs, midcurve_pngs_gray_objs,encoding_dim = 100, input_dim = 10000):
    # this is our input placeholder
    input_img = Input(shape=(input_dim,))
    
    # "encoded" is the encoded representation of the input
    encoded = Dense(encoding_dim, activation='relu')(input_img)
    encoded = Dense(100, activation='relu')(encoded)
    encoded = Dense(50, activation='relu')(encoded)
    
    # "decoded" is the lossy reconstruction of the input
    decoded = Dense(50, activation='relu')(encoded)
    decoded = Dense(100, activation='relu')(decoded)
    decoded = Dense(input_dim, activation='sigmoid')(decoded) 
    
    # Model 1: Full AutoEncoder, includes both encoder single dense layer and decoder single dense layer. 
    # This model maps an input to its reconstruction
    autoencoder = Model(input_img, decoded)
            
    # Compilation of Autoencoder (only)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
    
                
    # Training
    profile_pngs_flat_objs = [x.reshape(input_dim) for x in profile_pngs_gray_objs]
    midcurve_pngs_flat_objs = [x.reshape(input_dim) for x in midcurve_pngs_gray_objs]
    
    profile_pngs_objs = np.array(profile_pngs_flat_objs)
    midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
    
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

from keras.layers import Conv2D, MaxPooling2D, UpSampling2D
from keras import backend as K

def build_convolution_autoencoder_model(profile_pngs_gray_objs, midcurve_pngs_gray_objs,encoding_dim = 100, input_dim = 100):
    input_img = Input(shape=(input_dim, input_dim, 1))  # adapt this if using `channels_first` image data format
    
    x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    encoded = MaxPooling2D((2, 2), padding='same')(x)

    # at this point the representation is (4, 4, 8) i.e. 128-dimensional
    
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(16, (3, 3), activation='relu')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
    
    
    # Model 1: Full AutoEncoder, includes both encoder single dense layer and decoder single dense layer. 
    # This model maps an input to its reconstruction
    autoencoder = Model(input_img, decoded)
    
    # Compilation of Autoencoder (only)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
    
    
    # Training
    profile_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in profile_pngs_gray_objs]
    midcurve_pngs_flat_objs = [x.reshape(input_dim,input_dim,1) for x in midcurve_pngs_gray_objs]
    
    profile_pngs_objs = np.array(profile_pngs_flat_objs)
    midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
    
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

# def train_autoencoder_model(autoencoder,profile_pngs_objs, midcurve_pngs_objs):
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