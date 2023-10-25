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
            plot_lines(profile_lines,'black')
            plot_lines(midcurve_lines,'red')
            # for line in profile_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='black')
            # for line in midcurve_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='red')
        plt.axis('equal')
        plt.show()


def plot_lines(lines, color='black'):
    for line in lines:
        a = np.asarray(line)
        x = a[:, 0].T
        y = a[:, 1].T
        plt.plot(x, y, c=color)


if __name__ == "__main__":
    chatgpt_lines = [((2.5, 0), (2.5, 22.5)), ((2.5, 22.5), (2.5, 45.0)), ((2.5, 22.5), (25.0, 22.5)),
                     ((2.5, 22.5), (12.5, 22.5)), ((2.5, 22.5), (0, 22.5)), ((2.5, 22.5), (25.0, 22.5))]
    perplexity_lines = [((12.5,0), (12.5, 22.5)), ((12.5, 22.5),(12.5,45.0)), ((12.5, 22.5), (0,22.5)),
                        ((12.5, 22.5), (25.0,22.5))]
    bard_liens = [((12.5, 0), (12.5, 25.0)), ((12.5, 25.0), (25.0, 25.0)), ((25.0, 25.0), (25.0, 0))]
    huggingface_chat_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (25.0, 22.5)), ((25.0, 22.5), (25.0, 25.0))]
    gpt4_lines = [((12.5,0), (12.5,22.5)), ((12.5,22.5),(0,22.5)), ((12.5,22.5),(25.0,22.5))]
    plot_lines(huggingface_chat_lines,'red')
    plt.axis('equal')
    plt.show()
    # plot_jsons()