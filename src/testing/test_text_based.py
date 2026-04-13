"""
test_text_based.py  –  MidcurveNN
=====================================
Smoke tests for the text-based (Phase III) data pipeline.

Phase III model code is not yet implemented; these tests verify:
  - sequences.json can be generated from raw .dat/.mid data
  - JSON structure is valid (ShapeName, Profile, Midcurve keys present)
  - Coordinate sequences are non-empty lists of (x, y) pairs

Run
---
    cd src
    python -m pytest testing/test_text_based.py -v
    python testing/test_text_based.py
"""

import os
import sys
import json
import unittest

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SRC)

_TEXT_DATA_DIR = os.path.join(_SRC, 'text_based', 'data')
_SEQUENCES_FILE = os.path.join(_TEXT_DATA_DIR, 'sequences.json')
_RAW_DATA_DIR   = os.path.join(_SRC, 'data', 'raw')


class TestSequencesJSON(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Generate sequences.json if it doesn't exist."""
        if not os.path.isfile(_SEQUENCES_FILE):
            from utils.prepare_data import generate_sequences
            os.makedirs(_TEXT_DATA_DIR, exist_ok=True)
            generate_sequences(sequences_filepath=_SEQUENCES_FILE, recreate_data=False)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(_SEQUENCES_FILE),
                        f"sequences.json not found at {_SEQUENCES_FILE}")

    def test_valid_json(self):
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)

    def test_nonempty(self):
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        self.assertGreater(len(data), 0, "sequences.json is empty")

    def test_required_keys(self):
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        for entry in data:
            self.assertIn('ShapeName', entry, f"Missing 'ShapeName' in {entry}")
            self.assertIn('Profile',   entry, f"Missing 'Profile' in {entry}")
            self.assertIn('Midcurve',  entry, f"Missing 'Midcurve' in {entry}")

    def test_profile_is_list_of_pairs(self):
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        for entry in data:
            profile = entry['Profile']
            self.assertIsInstance(profile, list)
            self.assertGreater(len(profile), 0)
            for pt in profile:
                self.assertEqual(len(pt), 2, f"Profile point should be (x, y), got {pt}")

    def test_midcurve_is_list_of_pairs(self):
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        for entry in data:
            midcurve = entry['Midcurve']
            self.assertIsInstance(midcurve, list)
            self.assertGreater(len(midcurve), 0)
            for pt in midcurve:
                self.assertEqual(len(pt), 2, f"Midcurve point should be (x, y), got {pt}")

    def test_augmented_variants_present(self):
        """At least one augmented variant (Scaled/Rotated/Translated) should exist."""
        with open(_SEQUENCES_FILE) as f:
            data = json.load(f)
        if not data:
            self.skipTest("sequences.json is empty")
        # Check if any augmented key exists in the first entry
        first = data[0]
        aug_keys = [k for k in first if
                    k.startswith('Scaled_') or
                    k.startswith('Rotated_') or
                    k.startswith('Translated_')]
        self.assertGreater(len(aug_keys), 0,
                           "No augmented variants found — re-run prepare_data.py with recreate_data=True")


class TestRawDataFiles(unittest.TestCase):
    """Verify that the raw .dat/.mid source files exist for text pipeline."""

    def test_raw_data_dir_exists(self):
        self.assertTrue(os.path.isdir(_RAW_DATA_DIR),
                        f"Raw data directory not found: {_RAW_DATA_DIR}")

    def test_dat_files_present(self):
        files = os.listdir(_RAW_DATA_DIR)
        dat_files = [f for f in files if f.endswith('.dat')]
        self.assertGreater(len(dat_files), 0,
                           "No .dat files found in data/raw/")

    def test_mid_files_present(self):
        files = os.listdir(_RAW_DATA_DIR)
        mid_files = [f for f in files if f.endswith('.mid')]
        self.assertGreater(len(mid_files), 0,
                           "No .mid files found in data/raw/")

    def test_matching_dat_mid_pairs(self):
        files = os.listdir(_RAW_DATA_DIR)
        dat_stems = {f[:-4] for f in files if f.endswith('.dat')}
        mid_stems = {f[:-4] for f in files if f.endswith('.mid')}
        paired = dat_stems & mid_stems
        self.assertGreater(len(paired), 0,
                           "No matching .dat/.mid pairs found in data/raw/")


if __name__ == '__main__':
    unittest.main(verbosity=2)
