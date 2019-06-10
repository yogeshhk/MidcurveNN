from keras_gan_pix2pix import Pix2Pix

if __name__ == "__main__":
	datasetpath = "D:/Yogesh/Projects/Learning/DataScience/Datasets/pix2pix/"
	datasetname = "facades"
	rowpixels = 256
	colpixles = 256
	colorchannels = 3
    gan = Pix2Pix(datasetpath, datasetname, rowpixels, colpixles, colorchannels)
    gan.train(epochs=5, batch_size=1, sample_interval=200)
