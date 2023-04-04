# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 09:16:17 2019

@author: prnvb
"""

from config import *

from unet import unet_stage1, unet_stage2
from utils import get_coord_layers, weighted_cross_entropy
import numpy as np
from tensorflow.keras.losses import mean_absolute_error, binary_crossentropy
from tensorflow.keras.optimizers import Adam
from datagenerator import datagen
from tqdm import tqdm
import os
from tensorflow.keras.models import model_from_json


def init():
    loss = {'bce': binary_crossentropy,
            'mae': mean_absolute_error,
            'wbce_stage1': weighted_cross_entropy(STAGE1_WBCE_BETA, STAGE1_BALANCED),
            'wbce_stage2': weighted_cross_entropy(STAGE2_WBCE_BETA, STAGE2_BALANCED)}

    optimizer = Adam(decay=0.0001)
    loss_weights = [1E1, 1]

    generator_1 = unet_stage1()
    generator_1.compile(loss=[loss[STAGE1_LOSS], loss[STAGE1_LOSS]], optimizer=optimizer, loss_weights=loss_weights)

    if TWO_STAGE:
        generator_2 = unet_stage2()
        generator_2.compile(loss=[loss[STAGE2_LOSS], loss[STAGE2_LOSS]], optimizer=optimizer, loss_weights=loss_weights)
        return [generator_1, generator_2]

    return [generator_1]


def train_stage1(gen_model, epochs, batch_size, weight_path, loss_path, data_gen, load=False, load_at=0,
                 save_all=False):
    loss = []
    if load:
        with open(os.path.join(os.path.dirname(__file__),
                               'weights', 'stage1', 'generator_stage1.json'), 'r') as json_file:
            generator_stage1_json = json_file.read()
        gen_model = model_from_json(generator_stage1_json)
        if save_all:
            gen_model.load_weights(weight_path + str(load_at) + '_epochs_gen.h5')
            print("\nLoaded at: ", load_at, " epochs")
        else:
            gen_model.load_weights(weight_path + 'weights.h5')
            print("\nWeights Loaded")

    for num_epochs in range(1 + load_at, epochs + load_at + 1):
        loss = []  # Save loss for each epoch separately
        print('Epoch: ' + str(num_epochs))
        for num_batch in tqdm(range(int(TRAIN_SIZE / batch_size))):
            poly, midc = next(data_gen)
            coords = get_coord_layers(poly.shape[0], IMG_SHAPE)
            _loss = gen_model.train_on_batch([coords, poly], [midc, poly])
            print(_loss)
            loss.append([_loss])

        generator_stage1_json = gen_model.to_json()
        with open(weight_path + "generator_stage1.json", "w") as json_file:
            json_file.write(generator_stage1_json)

        if save_all:
            path_gen = os.path.join(weight_path, str(num_epochs) + '_epochs_gen.h5')
            gen_model.save_weights(path_gen)
        else:
            path_gen = os.path.join(weight_path, 'weights.h5')
            gen_model.save_weights(path_gen)

        gn_loss = np.array(loss)
        np.save(os.path.join(loss_path, str(num_epochs) + '_GN_LOSS.npy'), gn_loss)
        print("Saved : ", num_epochs)


def train_stage2(generator_stage1, generator_stage2, epochs, batch_size, weight_path, loss_path, data_gen, load=False,
                 load_at=0, save_all=False):
    if load:
        with open(os.path.join(os.path.dirname(__file__),'weights','stage2','generator_stage2.json'), 'r') as json_file:
            generator_stage2_json = json_file.read()
        generator_stage2 = model_from_json(generator_stage2_json)
        if save_all:
            generator_stage2.load_weights(os.path.join(weight_path, str(load_at) + '_epochs_gen.h5'))
            print("\nLoaded at: ", load_at, " epochs")
        else:
            generator_stage2.load_weights(weight_path + 'weights.h5')
            print("\nWeights Loaded")

    for num_epochs in range(1 + load_at, epochs + load_at + 1):
        loss = []  # Save loss for each epoch separately
        print('Epoch:', num_epochs)
        for num_batch in tqdm(range(int(TRAIN_SIZE / batch_size))):
            poly, midc = next(data_gen)
            coords = get_coord_layers(poly.shape[0], IMG_SHAPE)

            gen_midc, gen_recon = generator_stage1.predict([coords, poly])

            _loss = generator_stage2.train_on_batch([coords, poly, gen_midc],
                                                    [midc, np.concatenate((poly, gen_midc), axis=-1)])
            print(_loss)
            loss.append([_loss])

        generator_stage2_json = generator_stage2.to_json()
        with open(weight_path + "generator_stage2.json", "w") as json_file:
            json_file.write(generator_stage2_json)

        if save_all:
            path_gen = os.path.join(weight_path, str(num_epochs) + '_epochs_gen.h5')
            generator_stage2.save_weights(path_gen)
        else:
            path_gen = os.path.join(weight_path, 'weights.h5')
            generator_stage2.save_weights(path_gen)

        gn_loss = np.array(loss)
        np.save(os.path.join(loss_path, str(num_epochs) + '_GN_LOSS.npy'), gn_loss)
        print("Saved : ", num_epochs)


if __name__ == "__main__":
    generators = init()

    generators[0].summary()
    generators[1].summary()

    height = 256
    width = 256
    batch_size = 16

    epochs = 1

    data_gen = datagen(batch_size, height, width)

    pardir = os.path.dirname(__file__)

    train_stage1(generators[0], epochs, batch_size, os.path.join(pardir, 'weights', 'stage1'),
                 os.path.join(pardir, 'losses', 'stage1'), data_gen, False, 0)
    if TWO_STAGE:
        generators[0].load_weights(os.path.join(pardir, 'weights', 'stage1', '0_epochs_gen.h5'))
        train_stage2(generators[0], generators[1], epochs, batch_size,
                     os.path.join(pardir, 'weights', 'stage2'),
                     os.path.join(pardir, 'losses', 'stage2'),
                     data_gen, False, 0)
