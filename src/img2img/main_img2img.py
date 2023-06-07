import os
import random
import numpy as np

INPUT_DATA_FOLDER = "../data/input"


def read_input_image_pairs(datafolder=INPUT_DATA_FOLDER):
    profile_pngs = []
    midcurve_pngs = []
    for file in os.listdir(datafolder):
        fullpath = os.path.join(datafolder, file)
        if os.path.isdir(fullpath):
            continue
        if file.endswith(".png"):
            if file.find("Profile") != -1:
                profile_pngs.append(fullpath)
            if file.find("Midcurve") != -1:
                midcurve_pngs.append(fullpath)
    profile_pngs = sorted(profile_pngs)
    midcurve_pngs = sorted(midcurve_pngs)
    return profile_pngs, midcurve_pngs


def get_training_data(datafolder=INPUT_DATA_FOLDER, size=(100, 100)):
    profile_pngs, midcurve_pngs = read_input_image_pairs(datafolder)

    profile_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in profile_pngs]
    midcurve_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in midcurve_pngs]

    #     profile_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in profile_pngs_objs])
    #     midcurve_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in midcurve_pngs_objs])

    profile_pngs_gray_objs = [x[:, :, 3] for x in profile_pngs_objs]
    midcurve_pngs_gray_objs = [x[:, :, 3] for x in midcurve_pngs_objs]

    #     profile_pngs_gray_objs = [np.where(x>128, 0, 1) for x in profile_pngs_gray_objs]
    #     midcurve_pngs_gray_objs =[np.where(x>128, 0, 1) for x in midcurve_pngs_gray_objs]

    # shufle them
    zipped_profiles_midcurves = [(p, m) for p, m in zip(profile_pngs_gray_objs, midcurve_pngs_gray_objs)]
    shuffle(zipped_profiles_midcurves)
    profile_pngs_gray_objs, midcurve_pngs_gray_objs = zip(*zipped_profiles_midcurves)

    return profile_pngs_gray_objs, midcurve_pngs_gray_objs


if __name__ == "__main__":
    profile_gray_objs, midcurve_gray_objs = get_training_data()
    test_gray_images = random.sample(profile_gray_objs, 5)

    # profile_gray_objs = np.asarray(profile_gray_objs) / 255.
    # midcurve_gray_objs = np.asarray(midcurve_gray_objs) / 255.
    # test_gray_images = np.asarray(test_gray_images) / 255.
    #
    # retrain_model = True
    # endec = simple_encoderdecoder()
    # endec.train(profile_gray_objs, midcurve_gray_objs, retrain_model)
    #
    # original_profile_imgs, predicted_midcurve_imgs = endec.predict(test_gray_images)
    # plot_results(original_profile_imgs, predicted_midcurve_imgs)
