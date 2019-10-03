from prepare_data import get_training_data
from prepare_plots import plot_results
from build_simple_encoderdecoder_model import simple_encoderdecoder
import random

if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    endec = simple_encoderdecoder()
    endec.train(profile_gray_objs, midcurve_gray_objs)
    
    test_gray_images = random.sample(profile_gray_objs,5)
    original_profile_imgs,predicted_midcurve_imgs = endec.predict(test_gray_images)
    plot_results(original_profile_imgs,predicted_midcurve_imgs)
