from core.pix2pix.keras_gan_pix2pix import Pix2Pix
from config import *

if __name__ == "__main__":
    datasetpath = PIX2PIX_DATA_FOLDER
    datasetname = "pix2pix"
    rowpixels = 256
    colpixles = 256
    colorchannels = 1
    gan = Pix2Pix()
    gan.train(epochs=5, batch_size=1, sample_interval=200)
