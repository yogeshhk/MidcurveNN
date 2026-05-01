"""
test_image_based.py  –  MidcurveNN
=====================================
Unit / smoke tests for all image-based (Phase I) approaches.

Tests verify:
  - Data folder exists and contains PNG pairs
  - Model can be built (forward pass without crash)
  - Output shape matches input

Run
---
    cd src
    python -m pytest testing/test_image_based.py -v
    # or standalone:
    python testing/test_image_based.py
"""

import os
import sys
import unittest
import numpy as np

# image_based/testing/ → image_based/ → src/
_SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.join(_SRC, 'image_based'))

_TF_AVAILABLE = False
try:
    import tensorflow  # noqa
    _TF_AVAILABLE = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Shared data dir constants (consolidated under image_based/data/)
# ---------------------------------------------------------------------------

_IMAGE_PAIRS_DIR = os.path.join(_SRC, 'image_based', 'data', 'image-pairs')
_UNET_SPLITS_DIR = os.path.join(_SRC, 'image_based', 'data', 'unet-splits')
_IMAGES_COMBO_DIR = os.path.join(_SRC, 'image_based', 'data', 'images-combo')


def _has_png_pairs(data_dir):
    if not os.path.isdir(data_dir):
        return False
    files = os.listdir(data_dir)
    has_profile  = any('Profile'  in f and f.endswith('.png') for f in files)
    has_midcurve = any('Midcurve' in f and f.endswith('.png') for f in files)
    return has_profile and has_midcurve


def _dummy_images(n=4, size=100):
    """Return (n, size, size) float array in [0, 1]."""
    return np.random.rand(n, size, size).astype(np.float32)


# ---------------------------------------------------------------------------
# Data presence tests
# ---------------------------------------------------------------------------

class TestDataFolders(unittest.TestCase):

    def test_image_pairs_exist(self):
        self.assertTrue(
            _has_png_pairs(_IMAGE_PAIRS_DIR),
            "image_based/data/image-pairs/ missing PNG pairs — run utils/prepare_data.py")

    def test_simple_data_exists(self):
        self.assertTrue(_has_png_pairs(_IMAGE_PAIRS_DIR),
            "image-pairs/ missing PNG pairs — run utils/prepare_data.py")

    def test_cnn_data_exists(self):
        self.assertTrue(_has_png_pairs(_IMAGE_PAIRS_DIR),
            "image-pairs/ missing PNG pairs — run utils/prepare_data.py")

    def test_dense_data_exists(self):
        self.assertTrue(_has_png_pairs(_IMAGE_PAIRS_DIR),
            "image-pairs/ missing PNG pairs")

    def test_denoiser_data_exists(self):
        self.assertTrue(_has_png_pairs(_IMAGE_PAIRS_DIR),
            "image-pairs/ missing PNG pairs")

    def test_unet_data_dir_exists(self):
        self.assertTrue(os.path.isdir(_UNET_SPLITS_DIR),
            f"image_based/data/unet-splits/ not found")


# ---------------------------------------------------------------------------
# Model build / forward-pass tests
# ---------------------------------------------------------------------------

@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestSimpleEncoderDecoder(unittest.TestCase):

    def setUp(self):
        from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
        self.model = simple_encoderdecoder()

    def test_model_created(self):
        self.assertIsNotNone(self.model)

    def test_predict_shape(self):
        imgs = _dummy_images(3, 100)
        inp, out = self.model.predict(imgs)
        self.assertEqual(inp.shape, out.shape)


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestCNNEncoderDecoder(unittest.TestCase):

    def setUp(self):
        from cnnencoderdecoder.build_cnn_encoderdecoder_model import cnn_encoderdecoder
        self.model = cnn_encoderdecoder(input_shape=(128, 128, 3))

    def test_model_created(self):
        self.assertIsNotNone(self.model)

    def test_predict_shape(self):
        # CNN expects (N, H, W, 3) — 2 coord channels + 1 image channel
        imgs = np.random.rand(3, 128, 128, 3).astype(np.float32)
        inp, out = self.model.predict(imgs, expand_dims=False)
        self.assertEqual(inp.shape[1:3], out.shape[1:3])


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestDenseEncoderDecoder(unittest.TestCase):

    def setUp(self):
        from denseencoderdecoder.build_dense_encoderdecoder_model import dense_encoderdecoder
        self.model = dense_encoderdecoder()

    def test_model_created(self):
        self.assertIsNotNone(self.model)

    def test_predict_shape(self):
        imgs = _dummy_images(3, 100)
        inp, out = self.model.predict(imgs)
        self.assertEqual(inp.shape, out.shape)


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestDenoiserEncoderDecoder(unittest.TestCase):

    def setUp(self):
        from denoiserencoderdecoder.build_denoiser_encoderdecoder_model import denoiser_encoderdecoder
        self.model = denoiser_encoderdecoder()

    def test_model_created(self):
        self.assertIsNotNone(self.model)

    def test_predict_shape(self):
        imgs = _dummy_images(3, 100)
        inp, out = self.model.predict(imgs)
        self.assertEqual(inp.shape, out.shape)


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestUNetImport(unittest.TestCase):

    def test_unet_import(self):
        sys.path.insert(0, os.path.join(_SRC, 'image_based', 'unet'))
        from unet import unet_stage1
        model = unet_stage1()
        self.assertIsNotNone(model)


# ---------------------------------------------------------------------------
# prepare_data utility test
# ---------------------------------------------------------------------------

class TestPrepareData(unittest.TestCase):

    def test_read_dat_files(self):
        from utils.prepare_data import read_dat_files
        profiles = read_dat_files()
        self.assertGreater(len(profiles), 0, "No .dat/.mid files found in data/raw/")
        first = profiles[0]
        self.assertIn('Profile',  first)
        self.assertIn('Midcurve', first)

    def test_get_training_data_missing_folder(self):
        from utils.prepare_data import get_training_data
        with self.assertRaises(Exception):
            get_training_data(datafolder='/nonexistent/path')


# ---------------------------------------------------------------------------
# Pix2Pix module existence / data smoke tests
# ---------------------------------------------------------------------------

class TestPix2PixFiles(unittest.TestCase):

    _PIX2PIX_DIR = os.path.join(_SRC, 'image_based', 'pix2pix')

    def test_main_script_exists(self):
        self.assertTrue(
            os.path.isfile(os.path.join(self._PIX2PIX_DIR, 'main_pix2pix.py')))

    def test_gan_module_exists(self):
        self.assertTrue(
            os.path.isfile(os.path.join(self._PIX2PIX_DIR, 'keras_gan_pix2pix.py')))

    def test_data_loader_exists(self):
        self.assertTrue(
            os.path.isfile(os.path.join(self._PIX2PIX_DIR, 'keras_gan_data_loader.py')))

    def test_combo_data_dir_exists(self):
        self.assertTrue(
            os.path.isdir(_IMAGES_COMBO_DIR),
            "image_based/data/images-combo/ not found — run utils/prepare_data.py")


# ---------------------------------------------------------------------------
# Img2Img (PyTorch) module existence smoke tests
# ---------------------------------------------------------------------------

class TestImg2ImgFiles(unittest.TestCase):

    _IMG2IMG_DIR = os.path.join(_SRC, 'image_based', 'img2img')

    def test_main_script_exists(self):
        self.assertTrue(
            os.path.isfile(os.path.join(self._IMG2IMG_DIR, 'main_img2img_pytorch.py')))

    def test_torch_available(self):
        try:
            import torch  # noqa
        except ImportError:
            self.skipTest("PyTorch not installed — img2img requires torch")
        self.assertTrue(True)

    def test_combo_data_dir_exists(self):
        self.assertTrue(
            os.path.isdir(_IMAGES_COMBO_DIR),
            "image_based/data/images-combo/ not found — run utils/prepare_data.py")


if __name__ == '__main__':
    unittest.main(verbosity=2)
