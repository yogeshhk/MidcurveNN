# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:16:08 2019

@author: prnvb
"""

import os
import cv2
import numpy as np
from random import shuffle

from config import *

#BASE_DIR = 'D:/dev/MidcurveNN/'

def datagen(batch, h, w):
    train_path = BASE_DIR + 'data/train/'
    files = os.listdir(train_path)
    shuffle(files)
    
    i = 0
    while(1):
        poly_list = []
        midcurve_list = []
        
        limit = i + batch

        if i + batch > TRAIN_SIZE:
            limit = TRAIN_SIZE
            i = TRAIN_SIZE-batch
        
        for j in range(i,limit):
            path = os.path.join(train_path , files[j])
            img = cv2.imread(path , cv2.IMREAD_GRAYSCALE)
            
            poly_img = img[:, :w]
            midcurve_img = img[:, w:]
            
            poly_img = cv2.resize(poly_img, (h,w))
            midcurve_img = cv2.resize(midcurve_img, (h,w))
            
            poly_img = poly_img/255.0
            midcurve_img = midcurve_img/255.0
            
            poly_list.append(poly_img)
            midcurve_list.append(midcurve_img)
        
        poly_list = np.array(poly_list)
        midcurve_list = np.array(midcurve_list)

        poly_list = np.expand_dims(poly_list, -1)
        midcurve_list = np.expand_dims(midcurve_list, -1)

        i = i + batch

        if limit == TRAIN_SIZE:
            i = 0
        yield (poly_list, midcurve_list)
