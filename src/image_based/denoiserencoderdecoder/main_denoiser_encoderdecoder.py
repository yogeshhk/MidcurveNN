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

    # Held-out split: reserve n_test samples for evaluation, excluded from BOTH stage-1
    # (simple encoder-decoder) and stage-2 (denoiser) training (previously both stages
    # trained on the full set and then "tested" on a subset of the same data -- see
    # analysis_report.md Bug 6).
    n_test = min(7, len(profile_gray_objs))
    all_indices = list(range(len(profile_gray_objs)))
    test_indices = random.sample(all_indices, n_test)
    test_index_set = set(test_indices)
    train_indices = [i for i in all_indices if i not in test_index_set]

    train_profile_objs  = np.asarray([profile_gray_objs[i] for i in train_indices])  / 255.
    train_midcurve_objs = np.asarray([midcurve_gray_objs[i] for i in train_indices]) / 255.
    test_profile_objs   = np.asarray([profile_gray_objs[i] for i in test_indices])   / 255.
    test_midcurve_objs  = np.asarray([midcurve_gray_objs[i] for i in test_indices])  / 255.

    endec = simple_encoderdecoder()
    endec.train(train_profile_objs, train_midcurve_objs)
    _, train_noisy_predicted = endec.predict(train_profile_objs)
    _, test_noisy_predicted  = endec.predict(test_profile_objs)

    denoiser = denoiser_encoderdecoder()
    retrain_model = True
    denoiser.train(train_noisy_predicted, train_midcurve_objs, retrain_model)

    original_noisy_imgs, clean_predicted_imgs = denoiser.predict(test_noisy_predicted)
    sample_gt = test_midcurve_objs

    RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # Cols: Noisy stage-1 output | GT clean midcurve | Denoiser prediction
    save_results_grid_images(
        original_noisy_imgs, sample_gt, clean_predicted_imgs,
        save_path=os.path.join(RESULTS_DIR, 'results_grid.png'),
        title='Denoiser Encoder-Decoder – Results (Noisy | GT | Denoised)'
    )
