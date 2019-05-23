from data_preparation import get_training_data
from plot_preparation import plot_results
from model_preparation import build_basic_autoencoder_model

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data()
    original_imgs,decoded_imgs = build_basic_autoencoder_model(profile_pngs_objs, midcurve_pngs_objs)
    plot_results(original_imgs,decoded_imgs)
