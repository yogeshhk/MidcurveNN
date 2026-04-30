# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:17:47 2019

@author: prnvb
"""

from config import *
# from src.config import BASE_DIR
from utils import get_coord_layers
import os
import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
from train import init

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(_HERE)))  # src/
from utils.prepare_plots import save_results_grid_images  # noqa: E402

#BASE_DIR = 'D:/dev/MidcurveNN/'

def generate_test_results(generator_stage1, generator_stage2, data_path, interpolation):
    plt.ioff()
    w = IMG_SHAPE[0]
    files = os.listdir(data_path)
    _grid_samples = []   # collect up to 5: (poly_img, midcurve_img_gt, midc_pred)
    for file in files:
        path = os.path.join(data_path, file)
        img = cv2.imread(path , cv2.IMREAD_GRAYSCALE)
        poly_img = img[:, :w]
        midcurve_img = img[:, w:]
        
        poly_img = poly_img/255.0
        midcurve_img = midcurve_img/255.0
        
        poly_img = np.expand_dims(poly_img, -1)
        midcurve_img = np.expand_dims(midcurve_img, -1)
    
        coords = get_coord_layers(1, (256,256,1))
    
        midc, recon = generator_stage1.predict( [coords, np.expand_dims(poly_img, 0)] )
        
        if TWO_STAGE:
            midc_st2, recon_st2 = generator_stage2.predict([coords, np.expand_dims(poly_img, 0), midc])
            midc_st2 = np.reshape(midc_st2, midcurve_img.shape)
        
        midc = np.reshape(midc, midcurve_img.shape)
        recon = np.reshape(recon, poly_img.shape)

        # Collect up to 5 samples for the summary grid
        if len(_grid_samples) < 5:
            best_midc = midc_st2 if TWO_STAGE else midc
            _grid_samples.append((poly_img[:, :, 0],
                                   midcurve_img[:, :, 0],
                                   best_midc[:, :, 0]))

        plt.figure(figsize=(800/100, 800/100), dpi=100)
        plt.subplots_adjust(left = 0, right=1, wspace = 0., hspace = 0, bottom=0, top=0.95)

        if TWO_STAGE:    
            plt.subplot(321).set_title('Polygon')
            plt.subplot(321).axis('off')
            plt.imshow(poly_img[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(322).set_title('Midcurve')
            plt.subplot(322).axis('off')
            plt.imshow(midcurve_img[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(323).set_title('ST1 Polygon (R)')
            plt.subplot(323).axis('off')
            plt.imshow(recon[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(324).set_title('ST1 Midcurve')
            plt.subplot(324).axis('off')
            plt.imshow(midc[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(326).set_title('ST2 Midcurve')
            plt.subplot(326).axis('off')
            plt.imshow(midc_st2[:, :, 0], cmap='gray', interpolation=interpolation)
            
            plt.savefig(os.path.join(os.path.dirname(__file__), 'results', file), dpi=100)

        else:    
            plt.subplot(221).set_title('Polygon')
            plt.subplot(221).axis('off')
            plt.imshow(poly_img[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(222).set_title('Midcurve')
            plt.subplot(222).axis('off')
            plt.imshow(midcurve_img[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(223).set_title('ST1 Polygon (R)')
            plt.subplot(223).axis('off')
            plt.imshow(recon[:, :, 0], cmap='gray', interpolation=interpolation)
        
            plt.subplot(224).set_title('ST1 Midcurve')
            plt.subplot(224).axis('off')
            plt.imshow(midc[:, :, 0], cmap='gray', interpolation=interpolation)
                    
            plt.savefig(os.path.join(os.path.dirname(__file__), 'results', file), dpi=100)
        
        print(file)

    # Save 5-sample summary grid after all per-file PNGs are written
    if _grid_samples:
        inputs = np.stack([s[0] for s in _grid_samples])
        gts    = np.stack([s[1] for s in _grid_samples])
        preds  = np.stack([s[2] for s in _grid_samples])
        grid_path = os.path.join(os.path.dirname(__file__), 'results', 'results_grid.png')
        save_results_grid_images(inputs, gts, preds, save_path=grid_path,
                                  title='UNet – Midcurve Results')


if __name__ == "__main__":
    generators = init()
    # Load the latest saved weights. train.py saves to 'weights.h5' by default (save_all=False).
    # If you trained with save_all=True, change 'weights.h5' to e.g. '5_epochs_gen.h5'.
    generators[0].load_weights(os.path.join(os.path.dirname(__file__), 'weights', 'stage1', 'weights.weights.h5'))
    generators[1].load_weights(os.path.join(os.path.dirname(__file__), 'weights', 'stage2', 'weights.weights.h5'))
    
    generate_test_results(generators[0], generators[1], os.path.join(os.path.dirname(__file__), '..', 'data', 'unet-splits', 'test'), None)
    