# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:17:47 2019

@author: prnvb
"""

from config import *
from utils import get_coord_layers
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from train import init

#BASE_DIR = 'D:/dev/MidcurveNN/'

def generate_test_results(generator_stage1, generator_stage2, data_path, interpolation):
    plt.ioff()
    w = IMG_SHAPE[0]
    files = os.listdir(data_path)
    for file in files:
        path = data_path + file
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
            
            plt.savefig('results/' + file , dpi=100)

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
                    
            plt.savefig('results/' + file , dpi=100)
        
        print(file)

if __name__ == "__main__":
    generators = init()
    generators[0].load_weights('weights/stage1/5_gen_epochs.h5')
    generators[1].load_weights('weights/stage2/2_gen_epochs.h5')
    
    generate_test_results(generators[0],generators[1],BASE_DIR + 'data/test/',None)
    