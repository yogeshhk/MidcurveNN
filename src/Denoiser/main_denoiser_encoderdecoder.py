from prepare_data import get_training_data
from prepare_plots import plot_results
from build_simple_encoderdecoder_w_denoiser_model import simple_encoderdecoder_w_denoiser

if __name__ == "__main__":
    profile_pngs_objs, midcurve_pngs_objs = get_training_data()
	endec = simple_encoderdecoder_w_denoiser()
    original_imgs,decoded_imgs = endec.simple_encoderdecoder_w_denoiser(profile_pngs_objs, midcurve_pngs_objs)
    plot_results(original_imgs,decoded_imgs)
