import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.prepare_data import get_training_data
from utils.prepare_plots import plot_results
from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
import random
import numpy as np

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    
    print(f"Original data shapes:")
    print(f"Profile images: {np.array(profile_gray_objs).shape}")
    print(f"Midcurve images: {np.array(midcurve_gray_objs).shape}")
    
    test_gray_images = random.sample(profile_gray_objs, 5)

    profile_gray_objs = np.asarray(profile_gray_objs) / 255.
    midcurve_gray_objs = np.asarray(midcurve_gray_objs) / 255.
    test_gray_images = np.asarray(test_gray_images) / 255.

    print(f"\nAfter normalization:")
    print(f"Profile images: {profile_gray_objs.shape}")
    print(f"Midcurve images: {midcurve_gray_objs.shape}")

    if len(profile_gray_objs.shape) == 3:
        profile_gray_objs = profile_gray_objs.reshape(-1, 100, 100)
        midcurve_gray_objs = midcurve_gray_objs.reshape(-1, 100, 100)
        test_gray_images = test_gray_images.reshape(-1, 100, 100)

    print(f"\nAfter reshaping:")
    print(f"Profile images: {profile_gray_objs.shape}")
    print(f"Midcurve images: {midcurve_gray_objs.shape}")

    retrain_model = True
    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs, retrain_model)

    original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs, predicted_midcurve_imgs)