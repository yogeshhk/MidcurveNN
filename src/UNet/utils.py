# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 13:51:30 2019

@author: prnvb
"""

import numpy as np
import tensorflow as tf

def get_coord_layers(batch_size, img_res):
    x_coord = np.zeros(shape=(img_res[0], img_res[1], 1), dtype=np.float32)
    y_coord = np.zeros(shape=(img_res[0], img_res[1], 1), dtype=np.float32)
    for i in range(0, img_res[0]):
        x_coord[:, i, 0] = i
        y_coord[i, :, 0] = i
    coords = np.append(x_coord, y_coord, axis=-1)
    k = (img_res[0]-1)/2
    coords = (coords - k)/k #Normalize [-1, 1]
    coords = np.expand_dims(coords, 0)
    
    return np.tile(coords, (batch_size,1,1,1))

def weighted_cross_entropy(beta, balanced=False):
    '''
    WCE(y, y') = -(βylog(y') + (1-y)log(1-y'))
    
    To decrease the number of false negatives, set β>1.
        Actual: 1 Predicted: 0
    To decrease the number of false positives, set β<1.
        Actual: 0 Predicted: 1
        
    Balanced WCE = -(βylog(y') + (1-β)(1-y)log(1-y'))
    '''
    def convert_to_logits(y_pred):
        # see https://github.com/tensorflow/tensorflow/blob/r1.10/tensorflow/python/keras/backend.py#L3525
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1 - tf.keras.backend.epsilon())        
        return tf.log(y_pred / (1 - y_pred))
    
    def loss(y_true, y_pred):
        y_pred = convert_to_logits(y_pred)
        if balanced:
            pos_weight = beta/(1-beta)
        else:
            pos_weight = beta
        loss = tf.nn.weighted_cross_entropy_with_logits(logits=y_pred, targets=y_true, pos_weight=pos_weight)        
        # or reduce_sum and/or axis=-1
        return tf.reduce_mean(loss)    
    
    return loss

