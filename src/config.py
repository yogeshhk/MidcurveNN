import os

BASE_DIR = r"D:\Yogesh\Projects\MidcurveNN\src" # os.getcwd() + "/.."

RAW_DATA_FOLDER = BASE_DIR + "/data/raw"
INPUT_DATA_FOLDER = BASE_DIR + "/data/input"
PIX2PIX_DATA_FOLDER = BASE_DIR + "/data/pix2pix"
MODELS_FOLDER = BASE_DIR + "/models/"
SEQUENCES_FILEPATH = BASE_DIR + "/data/sequences.json"

#UNet Approach Configurations
TWO_STAGE = True
IMG_SHAPE = (256, 256)

TRAIN_SIZE = 2100
TEST_SIZE = 900

COORD_CONV = True

#Stage 1 Hyperparameters
STAGE1_AUX_DECODER = True
STAGE1_ACTIVATION = 'sigmoid'
STAGE1_LOSS = 'wbce_stage1' #wbce_stage1/wbce_stage2/bce/mae

STAGE1_WBCE_BETA = 0.1
STAGE1_BALANCED = False

#Stage 2 Hyperparameters
STAGE2_AUX_DECODER = True
STAGE2_ACTIVATION = 'sigmoid'
STAGE2_LOSS = 'wbce_stage2' #wbce_stage1/wbce_stage2/bce/mae

STAGE2_WBCE_BETA = 0.1
STAGE2_BALANCED = True