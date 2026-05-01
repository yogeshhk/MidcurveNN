import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # src/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # image_based/
from pix2pix.keras_gan_pix2pix import Pix2Pix
from utils.prepare_plots import save_results_grid_images

if __name__ == "__main__":
    gan = Pix2Pix()
    gan.train(epochs=5, batch_size=1, sample_interval=200)

    n_test = 7
    imgs_A, imgs_B = gan.data_loader.load_data(batch_size=n_test, is_testing=True)
    fake_B = gan.generator.predict(imgs_A)

    # imgs_A/B/fake_B shape: (N, 256, 256, 1); squeeze channel for grid
    inputs      = [imgs_A[i, :, :, 0] for i in range(n_test)]
    ground_truths = [imgs_B[i, :, :, 0] for i in range(n_test)]
    predictions   = [fake_B[i, :, :, 0] for i in range(n_test)]

    RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(RESULTS_DIR, exist_ok=True)
    save_results_grid_images(
        inputs, ground_truths, predictions,
        save_path=os.path.join(RESULTS_DIR, 'results_grid.png'),
        title='Pix2Pix GAN - Results (Profile | GT | Generated)'
    )
