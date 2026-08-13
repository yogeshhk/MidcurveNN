"""
    Prepare Data: populating input images from raw profile data
    Takes raw data from "data/raw/*" files for both, profile shape (shape.dat) and midcurve shape (shape.mid)
    Generates raster image files from svg (simple vector graphics)
    Multiple variations are populated using image transformations.
    Shared data directories under image_based/data/:
      image-pairs/   -- PNG pairs used by simple/cnn/dense/denoiser encoder-decoders
      unet-splits/   -- train/test split PNGs for the UNet approach
      images-combo/  -- side-by-side combo JPGs (train/val/test) for pix2pix and img2img
    Only raw .dat/.mid files remain in src/data/raw/.
"""
from random import shuffle
import PIL
import PIL.ImageOps
import numpy as np
import os

# TensorFlow is only needed for image rasterization (generate_images / get_training_data).
# Import lazily so that geometry/text tests can import this module without TF installed.
try:
    from tensorflow.keras.preprocessing.image import img_to_array, load_img, array_to_img
    _TF_AVAILABLE = True
except ImportError:
    _TF_AVAILABLE = False
    img_to_array = load_img = array_to_img = None

# matplotlib is only needed for visualisation helpers (plot_profie, plot_profile_dict).
# Import lazily so CI jobs that skip rendering can still import this module.
try:
    import matplotlib.pyplot as plt
    _MPL_AVAILABLE = True
except ImportError:
    _MPL_AVAILABLE = False
    plt = None

import math
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RAW_DATA_FOLDER

# src/ directory (parent of utils/)
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Shared image data directories (consolidated under image_based/data/)
IMAGE_PAIRS_DIR = os.path.join(SRC_DIR, 'image_based', 'data', 'image-pairs')
UNET_SPLITS_DIR = os.path.join(SRC_DIR, 'image_based', 'data', 'unet-splits')
IMAGES_COMBO_DIR = os.path.join(SRC_DIR, 'image_based', 'data', 'images-combo')

# ---------------------------------------------------------------------------
# Leave-one-shape-out split configuration (analysis_report.md Bugs 7 and 11)
# ---------------------------------------------------------------------------
# Splitting by a flat shuffle over augmented variants leaks: a held-out sample
# can be a rotated/translated variant of a training shape, so reported accuracy
# measures interpolation rather than generalization. Splitting by BASE SHAPE
# identity instead means no variant of a held-out shape is ever seen in
# training.
#
# Rotate which shape is held out by editing TEST_SHAPES / VAL_SHAPES. With only
# four base shapes this is necessarily coarse -- holding out one shape removes
# 25% of all topological families, and using a second for validation leaves
# just two for training. That is a real limitation of the current dataset, not
# of the split strategy; it improves as more shape families are added.
BASE_SHAPES = ('I', 'L', 'T', 'Plus')
TEST_SHAPES = ('Plus',)
VAL_SHAPES = ('T',)


def base_shape_from_filename(path):
    """Return the base shape name encoded in a generated PNG filename.

    Generated files are named ``<Shape>_<Profile|Midcurve>[_<transform>...].png``
    (e.g. ``Plus_Midcurve_mirrored_0_rotated_120.png``), so the base shape is
    the segment before the first underscore. Returns None if it is not one of
    the known BASE_SHAPES, so callers can decide how to treat strays.
    """
    stem = os.path.basename(path).split('.')[0]
    candidate = stem.split('_')[0]
    return candidate if candidate in BASE_SHAPES else None


def split_indices_by_base_shape(paths, test_shapes=TEST_SHAPES, val_shapes=VAL_SHAPES):
    """Group indices of `paths` into (train, val, test) by base shape identity.

    Returns three lists of indices into `paths`. Files whose base shape cannot
    be determined are put in train and reported, rather than silently dropped
    or silently leaked into the held-out sets.
    """
    train_idx, val_idx, test_idx, unknown = [], [], [], []
    for i, p in enumerate(paths):
        shape = base_shape_from_filename(p)
        if shape is None:
            unknown.append(os.path.basename(p))
            train_idx.append(i)
        elif shape in test_shapes:
            test_idx.append(i)
        elif shape in val_shapes:
            val_idx.append(i)
        else:
            train_idx.append(i)

    if unknown:
        print(f"Warning: {len(unknown)} file(s) had an unrecognized base shape "
              f"and were assigned to train, e.g. {unknown[:3]}")
    if not test_idx:
        print(f"Warning: no files matched TEST_SHAPES={test_shapes}; test split is empty")

    return train_idx, val_idx, test_idx


np.set_printoptions(threshold=sys.maxsize)


def combine_images(imga, imgb):
    """
    Combines two color image ndarrays side-by-side.
    Ref: https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
    """
    ha, wa = imga.shape[:2]
    hb, wb = imgb.shape[:2]
    max_height = np.max([ha, hb])
    total_width = wa + wb
    new_img = np.zeros(shape=(max_height, total_width))
    new_img[:ha, :wa] = imga
    new_img[:hb, wa:wa + wb] = imgb
    return new_img


#     images = map(Image.open, [imga,imgb])
#     widths, heights = zip(*(i.size for i in images))
#     total_width = sum(widths)
#     max_height = max(heights)
# 
#     new_im = Image.new('RGB', (total_width, max_height))
# 
#     x_offset = 0
#     for im in images:
#         new_im.paste(im, (x_offset,0))
#         x_offset += im.size[0]    
#     return new_im

def generate_pix2pix_dataset(inputdatafolder=None, pix2pixdatafolder=None):
    if inputdatafolder is None:
        inputdatafolder = IMAGE_PAIRS_DIR
    if pix2pixdatafolder is None:
        pix2pixdatafolder = IMAGES_COMBO_DIR
    profile_pngs, midcurve_pngs = read_input_image_pairs(inputdatafolder)

    profile_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=(256, 256))) for f in profile_pngs]
    midcurve_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=(256, 256))) for f in midcurve_pngs]

    #     combo_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in combo_pngs_objs])
    profile_pngs_gray_objs = [x[:, :, 3] for x in profile_pngs_objs]
    midcurve_pngs_gray_objs = [x[:, :, 3] for x in midcurve_pngs_objs]

    #     combo_pngs_gray_objs = [np.where(x>128, 0, 1) for x in combo_pngs_gray_objs]

    combo_pngs = [combine_images(p, m) for p, m in zip(profile_pngs_gray_objs, midcurve_pngs_gray_objs)]

    # Split by base shape identity, NOT by a flat shuffle over augmented
    # variants (analysis_report.md Bug 7). `profile_pngs` is index-aligned with
    # `combo_pngs`, so its filenames give each combo image its base shape.
    train_idx, val_idx, test_idx = split_indices_by_base_shape(profile_pngs)

    train_combo_files = [combo_pngs[i] for i in train_idx]
    val_combo_files = [combo_pngs[i] for i in val_idx]
    test_combo_files = [combo_pngs[i] for i in test_idx]

    # Shuffle WITHIN each split only. This keeps batch order random without
    # moving any sample across a split boundary.
    shuffle(train_combo_files)
    shuffle(val_combo_files)
    shuffle(test_combo_files)

    print(f"images-combo split by base shape -> "
          f"train={len(train_combo_files)} (shapes: "
          f"{sorted(set(BASE_SHAPES) - set(TEST_SHAPES) - set(VAL_SHAPES))}), "
          f"val={len(val_combo_files)} (shapes: {list(VAL_SHAPES)}), "
          f"test={len(test_combo_files)} (shapes: {list(TEST_SHAPES)})")

    if os.path.exists(pix2pixdatafolder):
        shutil.rmtree(pix2pixdatafolder, ignore_errors=True)

    os.makedirs(pix2pixdatafolder)
    for phase in "train", "val", "test":
        os.mkdir(os.path.join(pix2pixdatafolder, phase))

    # SAVE into 3 dirs
    for i, arr in enumerate(train_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = os.path.join(pix2pixdatafolder, "train", str(i) + ".jpg")
        img.save(filename)

    for i, arr in enumerate(val_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = os.path.join(pix2pixdatafolder, "val", str(i) + ".jpg")
        img.save(filename)

    for i, arr in enumerate(test_combo_files):
        img = PIL.Image.fromarray(arr.astype('uint8'))
        img = PIL.ImageOps.invert(img)
        filename = os.path.join(pix2pixdatafolder, "test", str(i) + ".jpg")
        img.save(filename)

    return train_combo_files, val_combo_files, test_combo_files


def generate_unet_splits(inputdatafolder=None, unetsplitsfolder=None, size=(256, 256)):
    """Generate the UNet train/test split PNGs from the image pairs.

    Fixes analysis_report.md Bug 11: `unet-splits/` existed on disk but nothing
    regenerated it, so the split could not be reproduced from raw data. Note
    that `unet/test_unet.py` already tells the user to "run utils/prepare_data.py"
    when the directory is missing -- until now that advice was wrong, because
    `__main__` never created it.

    Output matches what `unet/datagenerator.py` consumes: one PNG per sample,
    profile on the left half and midcurve on the right half, split at `size[0]`
    and read via `cv2.IMREAD_GRAYSCALE`.

    Two deliberate differences from the legacy committed files:

    - Splits are grouped by base shape (see `split_indices_by_base_shape`)
      rather than flat-shuffled, so no augmented variant of a held-out shape
      appears in training. This is the Bug 7 fix applied here too.
    - Files are written as single-channel 'L' PNGs. The legacy files are RGBA
      carrying the shape in the alpha channel, which `cv2.IMREAD_GRAYSCALE`
      does not read; grayscale is what the consumer actually wants.

    Only train/ and test/ are produced, matching the existing layout -- the
    UNet pipeline has no val/ directory.
    """
    if not _TF_AVAILABLE:
        raise ImportError("TensorFlow is required for generate_unet_splits(). "
                          "Install it or use a geometry/text-based approach.")
    if inputdatafolder is None:
        inputdatafolder = IMAGE_PAIRS_DIR
    if unetsplitsfolder is None:
        unetsplitsfolder = UNET_SPLITS_DIR

    profile_pngs, midcurve_pngs = read_input_image_pairs(inputdatafolder)

    profile_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size))[:, :, 3]
                    for f in profile_pngs]
    midcurve_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size))[:, :, 3]
                     for f in midcurve_pngs]

    combos = [combine_images(p, m) for p, m in zip(profile_objs, midcurve_objs)]

    # val indices fold into train: the UNet layout has no val/ directory.
    train_idx, val_idx, test_idx = split_indices_by_base_shape(profile_pngs)
    train_idx = train_idx + val_idx

    if os.path.exists(unetsplitsfolder):
        shutil.rmtree(unetsplitsfolder, ignore_errors=True)
    for phase in ("train", "test"):
        os.makedirs(os.path.join(unetsplitsfolder, phase))

    for phase, indices in (("train", train_idx), ("test", test_idx)):
        for counter, i in enumerate(indices):
            img = PIL.Image.fromarray(combos[i].astype('uint8'), mode='L')
            img.save(os.path.join(unetsplitsfolder, phase, f"C{counter}.png"))

    print(f"unet-splits split by base shape -> "
          f"train={len(train_idx)}, test={len(test_idx)} "
          f"(test shapes: {list(TEST_SHAPES)})")

    return train_idx, test_idx


def get_training_data(datafolder=None, size=(100, 100), return_shapes=False):
    """Load Profile/Midcurve PNG pairs as grayscale arrays.

    By default returns ``(profiles, midcurves)`` shuffled together, which is the
    long-standing signature every caller relies on.

    Pass ``return_shapes=True`` to also get a per-sample base shape label, as
    ``(profiles, midcurves, shapes)``. Callers that want a leave-one-shape-out
    split (analysis_report.md Bug 7) need that label: a flat shuffle here means
    a held-out sample can be a rotated variant of a training shape. See
    ``split_indices_by_base_shape`` for the grouping helper.
    """
    if not _TF_AVAILABLE:
        raise ImportError("TensorFlow is required for get_training_data(). "
                          "Install it or use a geometry/text-based approach.")
    if datafolder is None:
        raise ValueError("datafolder must be provided explicitly")
    profile_pngs, midcurve_pngs = read_input_image_pairs(datafolder)

    profile_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in profile_pngs]
    midcurve_pngs_objs = [img_to_array(load_img(f, color_mode='rgba', target_size=size)) for f in midcurve_pngs]

    #     profile_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in profile_pngs_objs])
    #     midcurve_pngs_objs = np.array([x.reshape((1,) + x.shape) for x in midcurve_pngs_objs])

    profile_pngs_gray_objs = [x[:, :, 3] for x in profile_pngs_objs]
    midcurve_pngs_gray_objs = [x[:, :, 3] for x in midcurve_pngs_objs]

    #     profile_pngs_gray_objs = [np.where(x>128, 0, 1) for x in profile_pngs_gray_objs]
    #     midcurve_pngs_gray_objs =[np.where(x>128, 0, 1) for x in midcurve_pngs_gray_objs]

    # Shuffle profiles, midcurves and their base shape labels together, so the
    # three stay aligned however the caller splits them afterwards.
    shapes = [base_shape_from_filename(f) for f in profile_pngs]
    zipped = list(zip(profile_pngs_gray_objs, midcurve_pngs_gray_objs, shapes))
    shuffle(zipped)
    profile_pngs_gray_objs, midcurve_pngs_gray_objs, shapes = zip(*zipped)

    if return_shapes:
        return profile_pngs_gray_objs, midcurve_pngs_gray_objs, shapes
    return profile_pngs_gray_objs, midcurve_pngs_gray_objs


def get_index(shapename, profile_dict_list):
    for i, dct in enumerate(profile_dict_list):
        if dct['ShapeName'] == shapename:
            return i
    return -1


def get_profile_dict(shapename, profiles_dict_list):
    i = get_index(shapename, profiles_dict_list)
    if i == -1:  # not present
        profile_dict = {'ShapeName': shapename}
        return profile_dict
    return profiles_dict_list[i]


def read_dat_files(datafolder=RAW_DATA_FOLDER):
    profiles_dict_list = []
    for file in os.listdir(datafolder):
        if os.path.isdir(os.path.join(datafolder, file)):
            continue
        filename = file.split(".")[0]
        profile_dict = get_profile_dict(filename, profiles_dict_list)
        if file.endswith(".dat"):
            with open(os.path.join(datafolder, file)) as f:
                profile_dict['Profile'] = [tuple(map(float, i.split())) for i in f]
        if file.endswith(".mid"):
            with open(os.path.join(datafolder, file)) as f:
                profile_dict['Midcurve'] = [tuple(map(float, i.split())) for i in f]
        if get_index(profile_dict['ShapeName'], profiles_dict_list) == -1:
            profiles_dict_list.append(profile_dict)
    return profiles_dict_list


try:
    import drawsvg as draw
    _DRAWSVG_AVAILABLE = True
except ImportError:
    draw = None
    _DRAWSVG_AVAILABLE = False


def create_image_file(fieldname, profile_dict, datafolder, imgsize=100, isOpenClose=True):
    if not _DRAWSVG_AVAILABLE:
        raise ImportError("drawsvg is required for image creation. Install it with: pip install drawsvg")
    d = draw.Drawing(imgsize, imgsize, origin='center')
    profilepoints = []
    for tpl in profile_dict[fieldname]:
        profilepoints.append(tpl[0])
        profilepoints.append(tpl[1])
    d.append(
        draw.Lines(profilepoints[0], profilepoints[1], *profilepoints, close=isOpenClose, fill='none', stroke='black'))

    shape = profile_dict['ShapeName']
    #     d.saveSvg(datafolder+"/"+shape+'.svg')
    d.savePng(os.path.join(datafolder, shape + '_' + fieldname + '.png'))


def get_original_png_files(datafolder):
    pngfilenames = []
    for file in os.listdir(datafolder):
        fullpath = os.path.join(datafolder, file)
        if os.path.isdir(fullpath):
            continue
        if file.endswith(".png") and file.find("_rotated_") == -1 and file.find("_translated_") == -1 and file.find(
                "_mirrored_") == -1:
            pngfilenames.append(fullpath)
    return pngfilenames


from PIL import Image


def rotate_images(pngfilenames, angle=90):
    for fullpath in pngfilenames:
        picture = Image.open(fullpath)
        newfilename = fullpath.replace(".png", "_rotated_" + str(angle) + ".png")
        picture.rotate(angle).save(newfilename)


def mirror_images(pngfilenames, mode=PIL.Image.TRANSPOSE):
    mirrored_filenames = []
    for fullpath in pngfilenames:
        picture = Image.open(fullpath)
        newfilename = fullpath.replace(".png", "_mirrored_" + str(mode) + ".png")
        picture.transpose(mode).save(newfilename)
        mirrored_filenames.append(newfilename)
    return mirrored_filenames


def translate_images(pngfilenames, dx=1, dy=1):
    for fullpath in pngfilenames:
        picture = Image.open(fullpath)
        x_shift = dx
        y_shift = dy
        a = 1
        b = 0
        c = x_shift  # left/right (i.e. 5/-5)
        d = 0
        e = 1
        f = y_shift  # up/down (i.e. 5/-5)
        translate = picture.transform(picture.size, Image.AFFINE, (a, b, c, d, e, f))
        #         # Calculate the size after cropping
        #         size = (translate.size[0] - x_shift, translate.size[1] - y_shift)
        #         # Crop to the desired size
        #         translate = translate.transform(size, Image.EXTENT, (0, 0, size[0], size[1]))
        newfilename = fullpath.replace(".png", "_translated_" + str(dx) + "_" + str(dy) + ".png")
        translate.save(newfilename)


def read_input_image_pairs(datafolder):
    profile_set = set()
    midcurve_set = set()
    for file in os.listdir(datafolder):
        fullpath = os.path.join(datafolder, file)
        if os.path.isdir(fullpath):
            continue
        if file.endswith(".png"):
            if file.find("Profile") != -1:
                profile_set.add(fullpath)
            if file.find("Midcurve") != -1:
                midcurve_set.add(fullpath)

    # Pair explicitly by filename substitution rather than independently sorting the
    # two lists (which silently misaligns X/Y pairs if any shape ever has an unpaired
    # Profile/Midcurve file -- see analysis_report.md Bug 24).
    profile_pngs = []
    midcurve_pngs = []
    for profile_path in sorted(profile_set):
        expected_midcurve = profile_path.replace("Profile", "Midcurve")
        if expected_midcurve in midcurve_set:
            profile_pngs.append(profile_path)
            midcurve_pngs.append(expected_midcurve)
        else:
            print(f"Warning: no matching Midcurve file for {profile_path}, skipping")

    return profile_pngs, midcurve_pngs


def generate_images(datafolder):
    if not os.path.exists(datafolder):
        os.makedirs(datafolder)
    else:
        for file in os.listdir(datafolder):
            if file.endswith(".png") and (file.find("_rotated_") != -1 or file.find("_translated_") != -1):
                print("files already present, not generating...")
                return

    print("transformed files not present, generating...")
    profiles_dict_list = read_dat_files()

    for profile_dict in profiles_dict_list:
        create_image_file('Profile', profile_dict, datafolder, 100, True)
        create_image_file('Midcurve', profile_dict, datafolder, 100, False)

    pngfilenames = get_original_png_files(datafolder)
    mirrored_filenames_left_right = mirror_images(pngfilenames, PIL.Image.FLIP_LEFT_RIGHT)
    mirrored_filenames_top_bottom = mirror_images(pngfilenames, PIL.Image.FLIP_TOP_BOTTOM)
    mirrored_filenames_transpose = mirror_images(pngfilenames, PIL.Image.TRANSPOSE)

    files_list_list = [pngfilenames, mirrored_filenames_left_right, mirrored_filenames_top_bottom,
                       mirrored_filenames_transpose]
    for filelist in files_list_list:
        for angle in range(30, 360, 30):
            rotate_images(filelist, angle)

        for dx in range(5, 21, 5):
            for dy in range(5, 21, 5):
                translate_images(filelist, dx, -dy)


def plot_profie(output_seqeunce, close=False):
    xs = []
    ys = []
    linestyle = 'dashed'
    color = "red"
    output_seqeunce_row_array = np.array(output_seqeunce)
    for row in output_seqeunce_row_array:
        x, y = row
        xs.append(x)
        ys.append(y)
        plt.scatter(x, y)
    if close:
        xs.append(xs[0])
        ys.append(ys[0])
        linestyle = "solid"
        color = "black"
    plt.plot(xs, ys, color=color, linestyle=linestyle)


def scale_sequence(sequence, factor=1):
    input_point_sequence_extended = [(x, y, 1) for x, y in sequence]
    scaled_points_list = []
    A = np.array(input_point_sequence_extended)
    T_s = np.array([[factor, 0, 0], [0, factor, 0], [0, 0, 1]])
    for row in A:
        output_row = T_s @ row
        x_s, y_s, _ = output_row
        scaled_points_list.append((round(x_s, 2), round(y_s, 2)))
    return scaled_points_list


def rotate_sequence(sequence, theta=30):
    theta = math.radians(theta)
    input_point_sequence_extended = [(x, y, 1) for x, y in sequence]
    rotated_points_list = []
    a = np.array(input_point_sequence_extended)
    # T_s = np.array([[0, math.sin(theta), 0], [-1 * math.cos(theta), 0, 0], [0, 0, 1]])
    t_s = np.array([[math.cos(theta), -1 * math.sin(theta), 0], [math.sin(theta), math.cos(theta), 0], [0, 0, 1]])

    for row in a:
        output_row = t_s @ row
        x_s, y_s, _ = output_row
        rotated_points_list.append((round(x_s, 2), round(y_s, 2)))
    return rotated_points_list


def translate_sequence(sequence, distance_x=10, distance_y=10):
    input_point_sequence_extended = [(x, y, 1) for x, y in sequence]
    translated_points_list = []
    A = np.array(input_point_sequence_extended)
    T_s = np.array([[1, 0, distance_x], [0, 1, distance_y], [0, 0, 1]])
    for row in A:
        output_row = T_s @ row
        x_s, y_s, _ = output_row
        translated_points_list.append((round(x_s, 2), round(y_s, 2)))
    return translated_points_list


def mirror_sequence(sequence, axis_is_x):
    input_point_sequence_extended = [(x, y, 1) for x, y in sequence]
    mirrored_points_list = []
    A = np.array(input_point_sequence_extended)
    if axis_is_x:
        T_s = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
    else:
        T_s = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
    for row in A:
        output_row = T_s @ row
        x_s, y_s, _ = output_row
        mirrored_points_list.append((round(x_s, 2), round(y_s, 2)))
    return mirrored_points_list


def plot_profile_dict(profile_dict):
    fig = plt.figure()
    ax = plt.gca()

    p1 = profile_dict['Profile']
    plot_profie(p1, close=True)

    m1 = profile_dict['Midcurve']
    plot_profie(m1, close=False)

    # for i, factor in enumerate(np.linspace(1.2, 2.2, 10)):
    # plot_profie(profile_dict['Scaled_Profile_' + str(i+1)] , close=True)
    # plot_profie(profile_dict['Scaled_Midcurve_' + str(i+1)], close=False)

    # for ix, distance_x in enumerate(np.linspace(-100, 110, 20)):
    #     for iy, distance_y in enumerate(np.linspace(-100, 110, 20)):
    #         plot_profie(profile_dict['Translated_Profile_' + str(ix + 1) + str(iy + 1)], close=True)
    #         plot_profie(profile_dict['Translated_Midcurve_' + str(ix + 1) + str(iy + 1)], close=False)

    # for i, theta in enumerate(np.linspace(30, 370, 12)):
    #     plot_profie(profile_dict['Rotated_Profile_' + str(i + 1)], close=True)
    #     plot_profie(profile_dict['Rotated_Midcurve_' + str(i + 1)], close=False)

    ax.set_xticks(np.arange(-110, 110, 10))
    ax.set_yticks(np.arange(-110, 110, 10))
    plt.title(profile_dict['ShapeName'])
    plt.grid()
    plt.show()


import json


def generate_sequences(sequences_filepath=None, recreate_data=False):
    if sequences_filepath is None:
        sequences_filepath = os.path.join(RAW_DATA_FOLDER, 'sequences.json')
    profiles_dict_list = []
    if not os.path.exists(sequences_filepath) or recreate_data:
        with open(sequences_filepath, 'w') as fout:
            print("transformed sequence csv file not present, generating...")
            profiles_dict_list = read_dat_files()

            for profile_dict in profiles_dict_list:
                # Scale
                for i, factor in enumerate(np.linspace(1.2, 2.2, 10)):
                    profile_dict['Scaled_Profile_' + str(i + 1)] = scale_sequence(profile_dict['Profile'], factor)
                    profile_dict['Scaled_Midcurve_' + str(i + 1)] = scale_sequence(profile_dict['Midcurve'], factor)

                # Translate
                for ix, distance_x in enumerate(np.linspace(-100, 110, 20)):
                    for iy, distance_y in enumerate(np.linspace(-100, 110, 20)):
                        profile_dict['Translated_Profile_' + str(ix + 1) + str(iy + 1)] = translate_sequence(
                            profile_dict['Profile'], distance_x, distance_y)
                        profile_dict['Translated_Midcurve_' + str(ix + 1) + str(iy + 1)] = translate_sequence(
                            profile_dict['Midcurve'], distance_x, distance_y)

                # Rotate
                for i, theta in enumerate(np.linspace(30, 370, 12)):
                    profile_dict['Rotated_Profile_' + str(i + 1)] = rotate_sequence(profile_dict['Profile'], theta)
                    profile_dict['Rotated_Midcurve_' + str(i + 1)] = rotate_sequence(profile_dict['Midcurve'], theta)

            json.dump(profiles_dict_list, fout)

    return profiles_dict_list


if __name__ == "__main__":
    # Generate 100x100 PNG pairs — shared by simple/cnn/dense/denoiser encoder-decoders
    print("Generating image pairs...")
    generate_images(IMAGE_PAIRS_DIR)

    # Generate combo images (side-by-side JPGs, train/val/test) — shared by pix2pix and img2img
    print("Generating images-combo dataset...")
    generate_pix2pix_dataset(
        inputdatafolder=IMAGE_PAIRS_DIR,
        pix2pixdatafolder=IMAGES_COMBO_DIR
    )

    # Generate UNet train/test split PNGs (previously missing here — Bug 11)
    print("Generating unet-splits dataset...")
    generate_unet_splits(
        inputdatafolder=IMAGE_PAIRS_DIR,
        unetsplitsfolder=UNET_SPLITS_DIR
    )

    # Generate sequence JSON for text-based approaches
    text_data_dir = os.path.join(SRC_DIR, 'text_based', 'data')
    os.makedirs(text_data_dir, exist_ok=True)
    sequences_filepath = os.path.join(text_data_dir, 'sequences.json')
    print("Generating sequences JSON...")
    sequences = generate_sequences(sequences_filepath=sequences_filepath, recreate_data=True)
    print(f"Generated {len(sequences)} sequences.")
