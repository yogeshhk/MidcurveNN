import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # image_based/

from utils.prepare_data import get_training_data
from utils.prepare_plots import save_results_grid_images
from denoiserencoderdecoder.build_denoiser_encoderdecoder_model import denoiser_encoderdecoder
from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
import random
import numpy as np

DATA_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'image-pairs')

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data(datafolder=DATA_FOLDER)
    profile_gray_objs  = np.asarray(list(profile_gray_objs))  / 255.
    midcurve_gray_objs = np.asarray(list(midcurve_gray_objs)) / 255.

    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    original_profile_images, noisy_predicted_midcurve_images = endec.predict(profile_gray_objs)

    denoiser = denoiser_encoderdecoder()
    retrain_model = True
    denoiser.train(noisy_predicted_midcurve_images, midcurve_gray_objs, retrain_model)

    # Sample 5 by index to keep noisy-input / GT / denoised aligned
    n_test = min(7, len(noisy_predicted_midcurve_images))
    test_indices = random.sample(range(len(noisy_predicted_midcurve_images)), n_test)
    sample_noisy = [noisy_predicted_midcurve_images[i] for i in test_indices]
    sample_gt    = np.asarray([midcurve_gray_objs[i] for i in test_indices])

    original_noisy_imgs, clean_predicted_imgs = denoiser.predict(sample_noisy)

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # Cols: Noisy stage-1 output | GT clean midcurve | Denoiser prediction
    save_results_grid_images(
        original_noisy_imgs, sample_gt, clean_predicted_imgs,
        save_path=os.path.join(RESULTS_DIR, 'results_grid.png'),
        title='Denoiser Encoder-Decoder – Results (Noisy | GT | Denoised)'
    )
