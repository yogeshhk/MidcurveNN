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

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.join(_SRC, 'image_based'))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _data_dir(approach):
    return os.path.join(_SRC, 'image_based', approach, 'data')


def _has_png_pairs(approach):
    d = _data_dir(approach)
    if not os.path.isdir(d):
        return False
    files = os.listdir(d)
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

    def test_simple_data_exists(self):
        self.assertTrue(
            _has_png_pairs('simpleencoderdecoder'),
            "simpleencoderdecoder/data/ missing PNG pairs — run utils/prepare_data.py")

    def test_cnn_data_exists(self):
        self.assertTrue(
            _has_png_pairs('cnnencoderdecoder'),
            "cnnencoderdecoder/data/ missing PNG pairs — run utils/prepare_data.py")

    def test_dense_data_exists(self):
        self.assertTrue(
            _has_png_pairs('denseencoderdecoder'),
            "denseencoderdecoder/data/ missing PNG pairs")

    def test_denoiser_data_exists(self):
        self.assertTrue(
            _has_png_pairs('denoiserencoderdecoder'),
            "denoiserencoderdecoder/data/ missing PNG pairs")

    def test_unet_data_dir_exists(self):
        d = _data_dir('unet')
        self.assertTrue(os.path.isdir(d), f"unet/data/ not found at {d}")


# ---------------------------------------------------------------------------
# Model build / forward-pass tests
# ---------------------------------------------------------------------------

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


if __name__ == '__main__':
    unittest.main(verbosity=2)
