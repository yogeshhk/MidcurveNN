from prepare_data import get_training_data
from prepare_plots import plot_results
from build_simple_encoderdecoder_model import simple_encoderdecoder

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data()
    endec = simple_encoderdecoder()
    endec.train(profile_pngs_objs, midcurve_pngs_objs)
    original_imgs,decoded_imgs = endec.predict()
    plot_results(original_imgs,decoded_imgs)
