from utils.prepare_data import get_training_data
from utils.prepare_plots import plot_results
from core.simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
import random
import numpy as np

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    test_gray_images = random.sample(profile_gray_objs, 5)

    profile_gray_objs = np.asarray(profile_gray_objs) / 255.
    midcurve_gray_objs = np.asarray(midcurve_gray_objs) / 255.
    test_gray_images = np.asarray(test_gray_images) / 255.

    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)

    original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs, predicted_midcurve_imgs)
