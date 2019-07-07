# Original : https://github.com/eriklindernoren/Keras-GAN/tree/master/pix2pix
from glob import glob
import numpy as np
import imageio

#datasetpath = "D:/Yogesh/Projects/Learning/DataScience/Datasets/pix2pix/"

class DataLoader():
    def __init__(self, dataset_name, img_res=(256, 256)):
        self.dataset_name = dataset_name
        self.img_res = img_res
        
    def binarize(self, image):
        h, w = image.shape
        for i in range(h):
          for j in range(w):
              if image[i][j] <= 192:
                image[i][j] = 0
        return image

    def load_data(self, batch_size=1, is_testing=False):
        data_type = "train" if not is_testing else "test"
        path = glob('data/%s/datasets/%s/%s/*' % (self.dataset_name, self.dataset_name, data_type))
        #path = glob(PATH + '%s/*' % (data_type))
        batch_images = np.random.choice(path, size=batch_size)

        imgs_A = []
        imgs_B = []
        for img_path in batch_images:
            img = self.imread(img_path)
            img = self.binarize(img)
            img = np.expand_dims(img, axis=-1)
            h, w, _ = img.shape
            _w = int(w/2)
            img_A, img_B = img[:, :_w, :], img[:, _w:, :]

            #  img_A = scipy.misc.imresize(img_A, self.img_res)
            #  img_A = np.array(Img.fromarray(img_A).resize(self.img_res))
            #img_A = np.array(skimage.transform.resize(img_A,self.img_res))
            #  img_B = scipy.misc.imresize(img_B, self.img_res)
            #  img_B = np.array(Img.fromarray(img_B).resize(self.img_res))
            #img_B = np.array(skimage.transform.resize(img_B,self.img_res))

            # If training => do random flip
            if not is_testing and np.random.random() < 0.5:
                img_A = np.fliplr(img_A)
                img_B = np.fliplr(img_B)

            imgs_A.append(img_A)
            imgs_B.append(img_B)

        imgs_A = np.array(imgs_A)/127.5 - 1.
        imgs_B = np.array(imgs_B)/127.5 - 1.

        return imgs_A, imgs_B

    def load_batch(self, batch_size=1, is_testing=False):
        data_type = "train" if not is_testing else "val"
        path = glob('data/%s/datasets/%s/%s/*' % (self.dataset_name, self.dataset_name, data_type))
        #path = glob(PATH + '%s/*' % (data_type))
        self.n_batches = int(len(path) / batch_size)

        for i in range(self.n_batches-1):
            batch = path[i*batch_size:(i+1)*batch_size]
            imgs_A, imgs_B = [], []
            for img in batch:
                img = self.imread(img)
                img = self.binarize(img)
                img = np.expand_dims(img, axis=-1)
                h, w, _ = img.shape
                half_w = int(w/2)
                img_A = img[:, :half_w, :]
                img_B = img[:, half_w:, :]

                #  img_A = scipy.misc.imresize(img_A, self.img_res)
                #  img_A = np.array(Img.fromarray(img_A).resize(self.img_res))
                #img_A = np.array(skimage.transform.resize(img_A,self.img_res))
                #  img_B = scipy.misc.imresize(img_B, self.img_res)
                #  img_B = np.array(Img.fromarray(img_B).resize(self.img_res))
                #img_B = np.array(skimage.transform.resize(img_B,self.img_res))

                if not is_testing and np.random.random() > 0.5:
                        img_A = np.fliplr(img_A)
                        img_B = np.fliplr(img_B)

                imgs_A.append(img_A)
                imgs_B.append(img_B)

            imgs_A = np.array(imgs_A)/127.5 - 1.
            imgs_B = np.array(imgs_B)/127.5 - 1.

            yield imgs_A, imgs_B


    def imread(self, path):
        return imageio.imread(path).astype(np.float)
