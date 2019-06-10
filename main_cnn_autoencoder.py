from prepare_data import get_training_data
from prepare_plots import plot_results
from build_cnn_autoencoder_model import build_cnn_autoencoder_model

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data()
    original_imgs,decoded_imgs = build_cnn_autoencoder_model(profile_pngs_objs, midcurve_pngs_objs)
    plot_results(original_imgs,decoded_imgs)
