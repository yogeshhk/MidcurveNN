from keras_gan_pix2pix import Pix2Pix

if __name__ == "__main__":
    datasetpath = "data/pix2pix/"
    datasetname = "pix2pix"
    rowpixels = 256
    colpixles = 256
    colorchannels = 1
    gan = Pix2Pix()
    gan.train(epochs=5, batch_size=1, sample_interval=200)
