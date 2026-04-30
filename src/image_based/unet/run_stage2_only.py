# Runs UNet stage-2 training only, using already-saved stage-1 weights.
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)  # unet/ must come first

from config import *

import train as _train_mod
_train_mod.TRAIN_SIZE = 320  # 20 batches/epoch at batch_size=16

from train import init, train_stage2
from datagenerator import datagen

generators = init()
stage1_weights = os.path.join(_HERE, 'weights', 'stage1', 'weights.weights.h5')
print(f"Loading stage-1 weights from: {stage1_weights}")
generators[0].load_weights(stage1_weights)
print("Stage-1 weights loaded.")

batch_size = 16
epochs = 5
data_gen = datagen(batch_size, 256, 256)

os.makedirs(os.path.join(_HERE, 'losses', 'stage2'), exist_ok=True)
os.makedirs(os.path.join(_HERE, 'weights', 'stage2'), exist_ok=True)

train_stage2(
    generators[0], generators[1],
    epochs, batch_size,
    os.path.join(_HERE, 'weights', 'stage2') + os.sep,
    os.path.join(_HERE, 'losses', 'stage2'),
    data_gen, False, 0
)
print("Stage-2 training complete.")
