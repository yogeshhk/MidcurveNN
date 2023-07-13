import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import json
import os
from config import JSON_FOLDER
matplotlib.use('TKAgg')


def plot_results(original_imgs, computed_imgs):
    n = len(original_imgs)  # 10 # how many digits we will display
    plt.figure(figsize=(20, 4))
    for i in range(n):
        # display original
        ax = plt.subplot(2, n, i + 1)
        plt.imshow(original_imgs[i].reshape(100, 100), cmap='gray_r')
#         plt.gray()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    
        # display reconstruction
        ax = plt.subplot(2, n, i + 1 + n)
        plt.imshow(computed_imgs[i].reshape(100, 100), cmap='gray_r')
#         plt.gray()
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    plt.show()


def plot_jsons(datafolder=JSON_FOLDER):
    for file in os.listdir(datafolder):
        if file.endswith(".json"):
            with open(os.path.join(JSON_FOLDER, file)) as json_file:
                shape_dict = json.load(json_file)
            profile_lines = shape_dict['Profile_lines']
            midcurve_lines = shape_dict['Midcurve_lines']
            for line in profile_lines:
                a = np.asarray(line)
                x = a[:, 0].T
                y = a[:, 1].T
                plt.plot(x, y, c='black')
            for line in midcurve_lines:
                a = np.asarray(line)
                x = a[:, 0].T
                y = a[:, 1].T
                plt.plot(x, y, c='red')
        plt.axis('equal')
        plt.show()


if __name__ == "__main__":
    plot_jsons()
