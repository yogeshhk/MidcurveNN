from prepare_data import get_training_data
from prepare_plots import plot_results
from main_dense_encoderdecoder import build_dense_encoderdecoder_model

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data()
    original_imgs,decoded_imgs = build_dense_encoderdecoder_model(profile_pngs_objs, midcurve_pngs_objs)
    plot_results(original_imgs,decoded_imgs)
