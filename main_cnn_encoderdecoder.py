from prepare_data import get_training_data
from prepare_plots import plot_results
from build_cnn_encoderdecoder_model import build_cnn_encoderdecoder_model

import numpy as np

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data(size = (128, 128))

    profile_pngs_objs = np.asarray(profile_pngs_objs)    
    midcurve_pngs_objs = np.asarray(midcurve_pngs_objs)    
    
    profile_pngs_objs = np.expand_dims(profile_pngs_objs, axis=-1)
    midcurve_pngs_objs = np.expand_dims(midcurve_pngs_objs, axis=-1)

    profile_pngs_objs = (profile_pngs_objs - 127.5)/127.5 #Normalize [-1, 1]
    midcurve_pngs_objs = (midcurve_pngs_objs - 127.5)/127.5 #Normalize [-1, 1]
    
    x_coord = np.zeros(shape=(128, 128, 1))
    y_coord = np.zeros(shape=(128, 128, 1))
    for i in range(0, 128):
        x_coord[:, i, 0] = i
        y_coord[i, :, 0] = i
    coords = np.append(x_coord, y_coord, axis=-1)
    coords = (coords - 63.5)/63.5 #Normalize [-1, 1]
    #coords = np.expand_dims(coords, axis=0)
    
    profile_pngs = []
    
    for i in range(len(profile_pngs_objs)):
        profile_pngs.append(np.append(profile_pngs_objs[i], coords, axis=-1))
    
    profile_pngs = np.asarray(profile_pngs)
    
    original_imgs,decoded_imgs = build_cnn_encoderdecoder_model(profile_pngs, midcurve_pngs_objs)
    plot_results(original_imgs,decoded_imgs)