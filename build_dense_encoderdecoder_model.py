from keras import regularizers
from keras.layers import Input, Dense
from keras.models import Model, load_model
from prepare_data import get_training_data
from prepare_plots import plot_results
import numpy as np
import os
import sys
import random

np.set_printoptions(threshold=sys.maxsize)

class dense_encoderdecoder:
    def __init__(self):
        self.encoding_dim = 100
        self.input_dim = 10000
        self.epochs = 50
        self.autoencoder_model_pkl = "models/dense_autoencoder_model.pkl"
        self.encoder_model_pkl = "models/dense_encoder_model.pkl"
        self.decoder_model_pkl = "models/dense_decoder_model.pkl"
                
    def process_images(self,grayobjs):
        flat_objs = [x.reshape(self.input_dim) for x in grayobjs]
        pngs_objs = np.array(flat_objs)
        return pngs_objs

    def train(self,
            profile_pngs_gray_objs, 
            midcurve_pngs_gray_objs):
        if not os.path.exists(self.autoencoder_model_pkl):        
            # this is our input placeholder
            input_img = Input(shape=(self.input_dim,))
            
            # "encoded" is the encoded representation of the input
            encoded = Dense(self.input_dim, activation='relu')(input_img)
            encoded = Dense(self.input_dim, activation='relu')(encoded)
            encoded = Dense(self.encoding_dim, activation='relu')(encoded)
            
            # "decoded" is the lossy reconstruction of the input
            decoded = Dense(self.encoding_dim, activation='relu')(encoded)
            decoded = Dense(self.input_dim, activation='relu')(decoded)
            decoded = Dense(self.input_dim, activation='sigmoid')(decoded) 
            
            # Model 1: Full AutoEncoder, includes both encoder single dense layer and decoder single dense layer. 
            # This model maps an input to its reconstruction
            self.autoencoder = Model(input_img, decoded)
                    
            # Model 2: a separate encoder model: -------------------
            # this model maps an input to its encoded representation
            self.encoder = Model(input_img, encoded)
            
            # Model 3: a separate encoder model: -------------------
            # create a placeholder for an encoded (32-dimensional) input
            encoded_input = Input(shape=(self.encoding_dim,))
            # retrieve the last to last layer of the autoencoder model
            decoder_layer = self.autoencoder.layers[-2]
            # create the decoder model
            self.decoder = Model(encoded_input, decoder_layer(encoded_input))            
                    
            # Compilation of Autoencoder (only)
            self.autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
        
                
#             # Training
#             profile_pngs_flat_objs = [x.reshape(input_dim) for x in profile_pngs_gray_objs]
#             midcurve_pngs_flat_objs = [x.reshape(input_dim) for x in midcurve_pngs_gray_objs]
#              
#             profile_pngs_objs = np.array(profile_pngs_flat_objs)
#             midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
        
            profile_pngs_objs = self.process_images(profile_pngs_gray_objs)
            midcurve_pngs_objs = self.process_images(midcurve_pngs_gray_objs)
                    
#             train_size = int(len(profile_pngs_objs)*0.7)
#             self.x_train = profile_pngs_objs[:train_size]
#             self.y_train = midcurve_pngs_objs[:train_size]
#             self.x_test = profile_pngs_objs[train_size:]
#             self.y_test = midcurve_pngs_objs[train_size:]
#             self.autoencoder.fit(self.x_train, self.y_train,
#                         epochs=self.epochs,
#                         batch_size=32,
#                         shuffle=True,
#                         validation_data=(self.x_test, self.y_test))
                
            self.x = profile_pngs_objs
            self.y = midcurve_pngs_objs
            self.autoencoder.fit(self.x, self.y,
                        epochs=self.epochs,
                        batch_size=5,
                        shuffle=True)                     
            # Save models
            self.autoencoder.save(self.autoencoder_model_pkl)
            self.encoder.save(self.encoder_model_pkl)
            self.decoder.save(self.decoder_model_pkl)  
        else:
            # Save models
            self.autoencoder = load_model(self.autoencoder_model_pkl)
            self.encoder= load_model(self.encoder_model_pkl)
            self.decoder = load_model(self.decoder_model_pkl)
    
    def predict(self, test_profile_images):
        png_profile_images = self.process_images(test_profile_images)
        encoded_imgs = self.encoder.predict(png_profile_images)
        decoded_imgs = self.decoder.predict(encoded_imgs)    
        return test_profile_images,decoded_imgs  
    

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    endec = dense_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    
    test_gray_images = random.sample(profile_gray_objs,5)
    original_profile_imgs,predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs,predicted_midcurve_imgs)