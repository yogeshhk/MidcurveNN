from keras.layers import Input, Dense
from keras.models import Model, load_model
from keras.layers import Conv2D, MaxPooling2D, UpSampling2D, Conv2DTranspose, ZeroPadding2D
from keras import backend as K
from keras import regularizers
from build_simple_encoderdecoder_model import simple_encoderdecoder
from prepare_data import get_training_data
from prepare_plots import plot_results
import os
import numpy as np
import random
import sys
np.set_printoptions(threshold=sys.maxsize)

class denoiser_encoderdecoder:
	def __init__(self):
		self.encoding_dim = 100
		self.input_dim = 100
		self.epochs = 50
		self.denoiser_autoencoder_model_pkl = "models/denoiser_autoencoder_model.pkl"

				
	def process_images(self,grayobjs):
		flat_objs = [x.reshape(self.input_dim,self.input_dim,1) for x in grayobjs]
		pngs_objs = np.array(flat_objs)
		return pngs_objs

	def train(self,noisy_images_objs, clean_images_objs):
		
		if not os.path.exists(self.denoiser_autoencoder_model_pkl):	   
			# this is our input placeholder
			input_img = Input(shape=(self.input_dim,self.input_dim,1))
			
			x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
			x = MaxPooling2D((2, 2), padding='same')(x)
			x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
			encoded = MaxPooling2D((2, 2), padding='same')(x)
			
			# at this point the representation is (7, 7, 32)
			
			x = Conv2D(32, (3, 3), activation='relu', padding='same')(encoded)
			x = UpSampling2D((2, 2))(x)
			x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
			x = UpSampling2D((2, 2))(x)
			decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
			
			# create the self.denoiser_autoencoder model
			self.denoiser_autoencoder = Model(input_img, decoded)
			
			# Compilation of Autoencoder (only)
			self.denoiser_autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')
			
# 			# Training
# 			profile_pngs_flat_objs = [x.reshape(input_dim) for x in profile_pngs_gray_objs]
# 			midcurve_pngs_flat_objs = [x.reshape(input_dim) for x in midcurve_pngs_gray_objs]
# 			
# 			profile_pngs_objs = np.array(profile_pngs_flat_objs)
# 			midcurve_pngs_objs= np.array(midcurve_pngs_flat_objs)
# 			
# 			train_size = int(len(profile_pngs_objs)*0.7)
# 			x_train = profile_pngs_objs[:train_size]
# 			y_train = midcurve_pngs_objs[:train_size]
# 			x_test = profile_pngs_objs[train_size:]
# 			y_test = midcurve_pngs_objs[train_size:]
# 			autoencoder.fit(x_train, y_train,
# 						epochs=200,
# 						batch_size=5,
# 						shuffle=True,
# 						validation_data=(x_test, y_test))
				
			self.x = noisy_images_objs
			self.y = clean_images_objs
			self.denoiser_autoencoder.fit(self.x, self.y,
						epochs=self.epochs,
						batch_size=5,
						shuffle=True)					 
			# Save models
			self.denoiser_autoencoder.save(self.denoiser_autoencoder_model_pkl)

		else:
			# Save models
			self.denoiser_autoencoder = load_model(self.denoiser_autoencoder_model_pkl)

	
	def predict(self, test_noisy_images):
		png_profile_images = self.process_images(test_noisy_images)
		encoded_imgs = self.denoiser_autoencoder.predict(png_profile_images)
		decoded_imgs = self.denoiser_autoencoder.predict(encoded_imgs)	
		return test_noisy_images,decoded_imgs  
	

if __name__ == "__main__":
	profile_gray_objs, midcurve_gray_objs = get_training_data()
	endec = simple_encoderdecoder()
	endec.train(profile_gray_objs, midcurve_gray_objs)
	original_profile_images,noisy_predicted_midcurve_images = endec.predict(profile_gray_objs)
	plot_results(original_profile_images[:5],noisy_predicted_midcurve_images[:5])
	
	denoiser = denoiser_encoderdecoder()
	denoiser.train(noisy_predicted_midcurve_images, midcurve_gray_objs)
	sample_noisy_midcurve_images = random.sample(noisy_predicted_midcurve_images,5)
	original_noisy_midcurve_images,clean_predicted_midcurve_images = denoiser.predict(sample_noisy_midcurve_images)
	plot_results(original_noisy_midcurve_images,clean_predicted_midcurve_images)	