"""
test_text_based.py  –  MidcurveNN
=====================================
Smoke tests for the text-based (Phase III) data pipeline.

Tests verify:
  - Raw .dat/.mid source files exist (shared data/raw/)
  - sequences.json can be loaded if it exists
  - JSON structure is valid (ShapeName, Profile, Midcurve keys present)
  - Coordinate sequences are non-empty lists of (x, y) pairs

Run
---
    cd src
    python -m pytest text_based/testing/test_text_based.py -v
    python text_based/testing/test_text_based.py
"""

import os
import sys
import json
import unittest

# text_based/testing/  →  text_based/  →  src/
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))   # src/
sys.path.insert(0, _SRC)

_TEXT_DATA_DIR  = os.path.join(_SRC, 'text_based', 'data')
_SEQUENCES_FILE = os.path.join(_TEXT_DATA_DIR, 'sequences.json')
_RAW_DATA_DIR   = os.path.join(_SRC, 'data', 'raw')   # shared raw data


# ---------------------------------------------------------------------------
# Raw data tests  (no TF needed — just file system checks)
# ---------------------------------------------------------------------------

class TestRawDataFiles(unittest.TestCase):
    """Verify that the raw .dat/.mid source files exist for the text pipeline."""

    def test_01_raw_data_dir_exists(self):
        self.assertTrue(os.path.isdir(_RAW_DATA_DIR),
                        f"Raw data directory not found: {_RAW_DATA_DIR}")

    def test_02_dat_files_present(self):
        if not os.path.isdir(_RAW_DATA_DIR):
            self.skipTest("Raw data dir missing")
        dat_files = [f for f in os.listdir(_RAW_DATA_DIR) if f.endswith('.dat')]
        self.assertGreater(len(dat_files), 0, "No .dat files found in data/raw/")

    def test_03_mid_files_present(self):
        if not os.path.isdir(_RAW_DATA_DIR):
            self.skipTest("Raw data dir missing")
        mid_files = [f for f in os.listdir(_RAW_DATA_DIR) if f.endswith('.mid')]
        self.assertGreater(len(mid_files), 0, "No .mid files found in data/raw/")

    def test_04_matching_dat_mid_pairs(self):
        if not os.path.isdir(_RAW_DATA_DIR):
            self.skipTest("Raw data dir missing")
        files = os.listdir(_RAW_DATA_DIR)
        dat_stems = {f[:-4] for f in files if f.endswith('.dat')}
        mid_stems = {f[:-4] for f in files if f.endswith('.mid')}
        paired = dat_stems & mid_stems
        self.assertGreater(len(paired), 0,
                           "No matching .dat/.mid pairs found in data/raw/")


# ---------------------------------------------------------------------------
# Sequences JSON tests  (skip gracefully if TF not installed)
# ---------------------------------------------------------------------------

class TestSequencesJSON(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Try to generate sequences.json if absent; skip if TF not available."""
        if not os.path.isfile(_SEQUENCES_FILE):
            try:
                from utils.prepare_data import generate_sequences
                os.makedirs(_TEXT_DATA_DIR, exist_ok=True)
                generate_sequences(sequences_filepath=_SEQUENCES_FILE, recreate_data=False)
            except ImportError as e:
                raise unittest.SkipTest(
                    f"sequences.json missing and cannot generate it: {e}. "
                    "Install TensorFlow and run: python utils/prepare_data.py")
        if not os.path.isfile(_SEQUENCES_FILE):
            raise unittest.SkipTest(
                f"sequences.json not found at {_SEQUENCES_FILE}. "
                "Run: python utils/prepare_data.py")

    def _load(self):
        with open(_SEQUENCES_FILE) as f:
            return json.load(f)

    def test_05_file_exists(self):
        self.assertTrue(os.path.isfile(_SEQUENCES_FILE))

    def test_06_valid_json(self):
        data = self._load()
        self.assertIsInstance(data, list)

    def test_07_nonempty(self):
        data = self._load()
        self.assertGreater(len(data), 0, "sequences.json is empty")

    def test_08_required_keys(self):
        for entry in self._load():
            for key in ('ShapeName', 'Profile', 'Midcurve'):
                self.assertIn(key, entry, f"Missing '{key}' in {entry.get('ShapeName', '?')}")

    def test_09_profile_is_list_of_pairs(self):
        for entry in self._load():
            profile = entry['Profile']
            self.assertIsInstance(profile, list)
            self.assertGreater(len(profile), 0)
            for pt in profile:
                self.assertEqual(len(pt), 2,
                                 f"Profile point should be (x,y), got {pt}")

    def test_10_midcurve_is_list_of_pairs(self):
        for entry in self._load():
            midcurve = entry['Midcurve']
            self.assertIsInstance(midcurve, list)
            self.assertGreater(len(midcurve), 0)
            for pt in midcurve:
                self.assertEqual(len(pt), 2,
                                 f"Midcurve point should be (x,y), got {pt}")

    def test_11_augmented_variants_present(self):
        data = self._load()
        if not data:
            self.skipTest("sequences.json is empty")
        first = data[0]
        aug_keys = [k for k in first if k.startswith(('Scaled_', 'Rotated_', 'Translated_'))]
        self.assertGreater(len(aug_keys), 0,
                           "No augmented variants — re-run prepare_data.py with recreate_data=True")


if __name__ == '__main__':
    unittest.main(verbosity=2)
