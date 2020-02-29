# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:15:52 2019

@author: prnvb
"""

from config import *

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers.convolutional import Conv2D, Conv2DTranspose
from tensorflow.keras.layers.merge import Concatenate
from tensorflow.keras.layers.advanced_activations import LeakyReLU
from tensorflow.keras.layers.core import Activation, Dropout
from tensorflow.keras.layers.normalization import BatchNormalization

#UNET Hyperparameters
ENCODER_KERNELS = (5, 4)
DECODER_KERNEL = 4

def unet(input_shapes:list, aux_decoder_out_channels:int, decoder_out_channels:int, filters:int, auxiliary_decoder:bool):    
    #inputs: List of tuples denoting the shapes.
    model_inputs = []
    for input_shape in input_shapes:
        model_inputs.append(Input(shape=input_shape))

    #Encoder
    x = BatchNormalization()(Conv2D(filters*1, kernel_size = ENCODER_KERNELS[0], strides = 2, padding = "same")(Concatenate()(model_inputs)))
    x = LeakyReLU(0.2)(x); e1 = x
    x = BatchNormalization()(Conv2D(filters*2, kernel_size = ENCODER_KERNELS[0], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e2 = x
    x = BatchNormalization()(Conv2D(filters*4, kernel_size = ENCODER_KERNELS[0], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e3 = x
    x = BatchNormalization()(Conv2D(filters*8, kernel_size = ENCODER_KERNELS[0], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e4 = x
    x = BatchNormalization()(Conv2D(filters*8, kernel_size = ENCODER_KERNELS[1], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e5 = x
    x = BatchNormalization()(Conv2D(filters*8, kernel_size = ENCODER_KERNELS[1], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e6 = x
    x = BatchNormalization()(Conv2D(filters*8, kernel_size = ENCODER_KERNELS[1], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); e7 = x
    x = BatchNormalization()(Conv2D(filters*8, kernel_size = ENCODER_KERNELS[1], strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); 
    #e8 = x
    
    if auxiliary_decoder:
        #Auxiliary Decoder
        encoder = x
        y = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(encoder))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e7])
        y = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e6])
        y = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e5])
        y = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e4])
        y = BatchNormalization()(Conv2DTranspose(filters*4, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e3])
        y = BatchNormalization()(Conv2DTranspose(filters*2, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e2])
        y = BatchNormalization()(Conv2DTranspose(filters*1, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y))
        y = LeakyReLU(0.2)(y); y = Concatenate()([Dropout(0.5)(y), e1])
        y = Conv2DTranspose(aux_decoder_out_channels, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(y)
        y = Activation("sigmoid", name='recon')(y)
    
    #Decoder
    x = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e7])
    x = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e6])
    x = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e5])
    x = BatchNormalization()(Conv2DTranspose(filters*8, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e4])
    x = BatchNormalization()(Conv2DTranspose(filters*4, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e3])
    x = BatchNormalization()(Conv2DTranspose(filters*2, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e2])
    x = BatchNormalization()(Conv2DTranspose(filters*1, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x))
    x = LeakyReLU(0.2)(x); x = Concatenate()([Dropout(0.5)(x), e1])
    x = Conv2DTranspose(decoder_out_channels, kernel_size = DECODER_KERNEL, strides = 2, padding = "same")(x)
    x = Activation("sigmoid", name='midcurve')(x)
    
    if auxiliary_decoder:
        unet = Model(inputs=model_inputs, outputs = [x, y])
    else:
        unet = Model(inputs=model_inputs, outputs = [x])
    return unet

def unet_stage1():
    input_coords_shape = (IMG_SHAPE[0],IMG_SHAPE[1],2)
    input_image_shape  = (IMG_SHAPE[0],IMG_SHAPE[1],1)
    input_shapes = [input_coords_shape, input_image_shape]
    
    model = unet(input_shapes=input_shapes, aux_decoder_out_channels=1, decoder_out_channels=1, filters=64, auxiliary_decoder = STAGE1_AUX_DECODER)
    return model

def unet_stage2():
    input_coords_shape = (IMG_SHAPE[0],IMG_SHAPE[1],2)
    stage1_input_image_shape  = (IMG_SHAPE[0],IMG_SHAPE[1],1)
    stage1_output_image_shape  = (IMG_SHAPE[0],IMG_SHAPE[1],1)
    input_shapes = [input_coords_shape, stage1_input_image_shape, stage1_output_image_shape]
    
    model = unet(input_shapes=input_shapes, aux_decoder_out_channels=2, decoder_out_channels=1, filters=64, auxiliary_decoder = STAGE2_AUX_DECODER)
    return model
