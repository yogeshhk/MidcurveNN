import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # image_based/

from utils.prepare_data import get_training_data
from utils.prepare_plots import save_results_grid_images
from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
import random
import numpy as np

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'image-pairs')

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data(datafolder=DATA_FOLDER)

    # Sample 5 paired (profile, GT midcurve) by index to keep correspondence
    n_test = min(7, len(profile_gray_objs))
    test_indices = random.sample(range(len(profile_gray_objs)), n_test)
    test_profiles_raw = [profile_gray_objs[i] for i in test_indices]
    test_gt_raw       = [midcurve_gray_objs[i] for i in test_indices]

    profile_gray_objs  = np.asarray(profile_gray_objs)  / 255.
    midcurve_gray_objs = np.asarray(midcurve_gray_objs) / 255.
    test_gray_images   = np.asarray(test_profiles_raw)  / 255.
    test_gt_midcurves  = np.asarray(test_gt_raw)        / 255.

    retrain_model = True
    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs, retrain_model)

    original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_results_grid_images(
        original_profile_imgs, test_gt_midcurves, predicted_midcurve_imgs,
        save_path=os.path.join(RESULTS_DIR, 'results_grid.png'),
        title='Simple Encoder-Decoder – Midcurve Results'
    )
