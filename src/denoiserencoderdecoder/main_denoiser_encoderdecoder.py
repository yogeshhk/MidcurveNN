from utils.prepare_data import get_training_data
from utils.prepare_plots import plot_results
from denoiserencoderdecoder.build_denoiser_encoderdecoder_model import denoiser_encoderdecoder
from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
from random import random

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    original_profile_images, noisy_predicted_midcurve_images = endec.predict(profile_gray_objs)
    plot_results(original_profile_images[:5], noisy_predicted_midcurve_images[:5])

    denoiser = denoiser_encoderdecoder()
    retrain_model = True
    denoiser.train(noisy_predicted_midcurve_images, midcurve_gray_objs,retrain_model)
    sample_noisy_midcurve_images = random.sample(noisy_predicted_midcurve_images, 5)
    original_noisy_midcurve_images, clean_predicted_midcurve_images = denoiser.predict(sample_noisy_midcurve_images)
    plot_results(original_noisy_midcurve_images, clean_predicted_midcurve_images)
