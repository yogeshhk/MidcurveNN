import sys
#sys.path.append('...')
from utils.utils import get_training_data
from utils.utils import plot_results

from core.cnnencoderdecoder.build_cnn_encoderdecoder_model import cnn_encoderdecoder

import numpy as np
import random

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data(size = (128, 128))

    test_gray_images = random.sample(profile_pngs_objs,5)
    test_gray_images = np.expand_dims(np.asarray(test_gray_images),axis=-1)/255.

    profile_pngs_objs = np.asarray(profile_pngs_objs)    
    midcurve_pngs_objs = np.asarray(midcurve_pngs_objs)    
    
    profile_pngs_objs = np.expand_dims(profile_pngs_objs, axis=-1)
    midcurve_pngs_objs = np.expand_dims(midcurve_pngs_objs, axis=-1)

    profile_pngs_objs = profile_pngs_objs/255. #Normalize [0,1]
    midcurve_pngs_objs = midcurve_pngs_objs/255. #Normalize [0,1]

    #profile_pngs_objs = (profile_pngs_objs - 127.5)/127.5 #Normalize [-1, 1]
    #midcurve_pngs_objs = (midcurve_pngs_objs - 127.5)/127.5 #Normalize [-1, 1]
    
    x_coord = np.zeros(shape=(128, 128, 1))
    y_coord = np.zeros(shape=(128, 128, 1))
    for i in range(0, 128):
        x_coord[:, i, 0] = i
        y_coord[i, :, 0] = i
    coords = np.append(x_coord, y_coord, axis=-1)
    coords = coords/127. #Normalize [0,1]
    #coords = (coords - 63.5)/63.5 #Normalize [-1, 1]
    #coords = np.expand_dims(coords, axis=-1)
    
    profile_pngs = []
    test_profile_pngs = []

    print(profile_pngs_objs.shape)
    print(profile_pngs_objs[0].shape)
    print(test_gray_images.shape)
    print(test_gray_images[0].shape)
    print(coords.shape)

    for i in range(len(profile_pngs_objs)):
        profile_pngs.append(np.concatenate((coords, profile_pngs_objs[i]), axis=-1))
    for i in range(len(test_gray_images)):
        test_profile_pngs.append(np.concatenate((coords, test_gray_images[i]), axis=-1))
    
    profile_pngs = np.asarray(profile_pngs)
    test_profile_pngs = np.asarray(test_profile_pngs)

    endec = cnn_encoderdecoder(input_shape = (128,128,3))
    endec.train(profile_pngs, midcurve_pngs_objs)
    
    #print(test_profile_pngs.shape)

    original_profile_imgs,predicted_midcurve_imgs = endec.predict(test_profile_pngs,expand_dims=False)
    plot_results(original_profile_imgs[:,:,:,2],predicted_midcurve_imgs,size=(128,128))
    #original_imgs,decoded_imgs = build_cnn_encoderdecoder_model(profile_pngs, midcurve_pngs_objs)
    #plot_results(original_imgs,decoded_imgs)