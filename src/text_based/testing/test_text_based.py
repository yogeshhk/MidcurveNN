"""
test_text_based.py  --  MidcurveNN
=====================================
Smoke tests for the text-based (Phase II) data pipeline and finetuning modules.

Test groups
-----------
  TestRawDataFiles    -- shared .dat/.mid source files exist
  TestSequencesJSON   -- legacy sequences.json format (flat coord lists)
  TestBrepData        -- new BRep JSON shape files (data/brep/)
  TestCsvDatasets     -- CSV train/test/val splits (data/csvs/)
  TestUtilsImports    -- utils/ scripts importable (no model weights needed)
  TestFinetuningImports -- finetuning/metrics.py importable (no GPU needed)

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

# text_based/testing/  ->  text_based/  ->  src/
_HERE          = os.path.dirname(os.path.abspath(__file__))
_TEXT_BASED    = os.path.dirname(_HERE)               # text_based/
_SRC           = os.path.dirname(_TEXT_BASED)          # src/
sys.path.insert(0, _SRC)
sys.path.insert(0, _TEXT_BASED)

_TEXT_DATA_DIR  = os.path.join(_TEXT_BASED, 'data')
_SEQUENCES_FILE = os.path.join(_TEXT_DATA_DIR, 'sequences.json')
_BREP_DIR       = os.path.join(_TEXT_DATA_DIR, 'brep')
_CSVS_DIR       = os.path.join(_TEXT_DATA_DIR, 'csvs')
_RAW_DATA_DIR   = os.path.join(_SRC, 'data', 'raw')   # shared raw data

_BREP_SHAPES    = ['I', 'L', 'T', 'Plus']
_CSV_FILES      = [
    'midcurve_llm.csv',
    'midcurve_llm_train.csv',
    'midcurve_llm_test.csv',
    'midcurve_llm_val.csv',
]
_BREP_REQUIRED_KEYS = {'ShapeName', 'Profile', 'Midcurve', 'Profile_brep', 'Midcurve_brep'}
_BREP_SUB_KEYS      = {'Points', 'Lines', 'Segments'}


# ---------------------------------------------------------------------------
# Raw data tests
# ---------------------------------------------------------------------------

class TestRawDataFiles(unittest.TestCase):
    """Verify that the shared raw .dat/.mid source files exist."""

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
        self.assertGreater(len(dat_stems & mid_stems), 0,
                           "No matching .dat/.mid pairs found in data/raw/")


# ---------------------------------------------------------------------------
# Legacy sequences.json tests
# ---------------------------------------------------------------------------

class TestSequencesJSON(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        self.assertIsInstance(self._load(), list)

    def test_07_nonempty(self):
        self.assertGreater(len(self._load()), 0, "sequences.json is empty")

    def test_08_required_keys(self):
        for entry in self._load():
            for key in ('ShapeName', 'Profile', 'Midcurve'):
                self.assertIn(key, entry)

    def test_09_profile_is_list_of_pairs(self):
        for entry in self._load():
            for pt in entry['Profile']:
                self.assertEqual(len(pt), 2)

    def test_10_midcurve_is_list_of_pairs(self):
        for entry in self._load():
            for pt in entry['Midcurve']:
                self.assertEqual(len(pt), 2)

    def test_11_augmented_variants_present(self):
        data = self._load()
        if not data:
            self.skipTest("sequences.json is empty")
        aug_keys = [k for k in data[0] if k.startswith(('Scaled_', 'Rotated_', 'Translated_'))]
        self.assertGreater(len(aug_keys), 0,
                           "No augmented variants found — re-run prepare_data.py")


# ---------------------------------------------------------------------------
# BRep JSON shape files  (data/brep/)
# ---------------------------------------------------------------------------

class TestBrepData(unittest.TestCase):
    """Verify the 4 base BRep JSON shape files are present and well-formed."""

    def test_12_brep_dir_exists(self):
        self.assertTrue(os.path.isdir(_BREP_DIR),
                        f"BRep data directory not found: {_BREP_DIR}")

    def test_13_all_base_shapes_present(self):
        if not os.path.isdir(_BREP_DIR):
            self.skipTest("BRep dir missing")
        for name in _BREP_SHAPES:
            path = os.path.join(_BREP_DIR, f"{name}.json")
            self.assertTrue(os.path.isfile(path), f"Missing shape file: {name}.json")

    def test_14_brep_json_valid(self):
        if not os.path.isdir(_BREP_DIR):
            self.skipTest("BRep dir missing")
        for name in _BREP_SHAPES:
            path = os.path.join(_BREP_DIR, f"{name}.json")
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                shape = json.load(f)
            self.assertIsInstance(shape, dict, f"{name}.json is not a dict")

    def test_15_brep_top_level_keys(self):
        if not os.path.isdir(_BREP_DIR):
            self.skipTest("BRep dir missing")
        for name in _BREP_SHAPES:
            path = os.path.join(_BREP_DIR, f"{name}.json")
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                shape = json.load(f)
            missing = _BREP_REQUIRED_KEYS - shape.keys()
            self.assertEqual(missing, set(), f"{name}.json missing keys: {missing}")

    def test_16_brep_sub_dict_keys(self):
        if not os.path.isdir(_BREP_DIR):
            self.skipTest("BRep dir missing")
        for name in _BREP_SHAPES:
            path = os.path.join(_BREP_DIR, f"{name}.json")
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                shape = json.load(f)
            for sub_key in ('Profile_brep', 'Midcurve_brep'):
                missing = _BREP_SUB_KEYS - shape[sub_key].keys()
                self.assertEqual(missing, set(),
                                 f"{name}.json/{sub_key} missing keys: {missing}")

    def test_17_brep_points_are_pairs(self):
        if not os.path.isdir(_BREP_DIR):
            self.skipTest("BRep dir missing")
        for name in _BREP_SHAPES:
            path = os.path.join(_BREP_DIR, f"{name}.json")
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                shape = json.load(f)
            for sub_key in ('Profile_brep', 'Midcurve_brep'):
                for pt in shape[sub_key]['Points']:
                    self.assertEqual(len(pt), 2,
                                     f"{name}.json/{sub_key}/Points: bad point {pt}")


# ---------------------------------------------------------------------------
# CSV dataset files  (data/csvs/)
# ---------------------------------------------------------------------------

class TestCsvDatasets(unittest.TestCase):
    """Verify CSV split files are present and have the expected columns."""

    _REQUIRED_COLS = {'ShapeName', 'Profile', 'Midcurve', 'Profile_brep', 'Midcurve_brep'}

    def test_18_csvs_dir_exists(self):
        self.assertTrue(os.path.isdir(_CSVS_DIR),
                        f"CSV data directory not found: {_CSVS_DIR}")

    def test_19_all_csv_files_present(self):
        if not os.path.isdir(_CSVS_DIR):
            self.skipTest("CSVs dir missing")
        for fname in _CSV_FILES:
            path = os.path.join(_CSVS_DIR, fname)
            self.assertTrue(os.path.isfile(path), f"Missing CSV file: {fname}")

    def test_20_csv_columns_correct(self):
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        if not os.path.isdir(_CSVS_DIR):
            self.skipTest("CSVs dir missing")
        for fname in _CSV_FILES:
            path = os.path.join(_CSVS_DIR, fname)
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path, nrows=1)
            missing = self._REQUIRED_COLS - set(df.columns)
            self.assertEqual(missing, set(), f"{fname} missing columns: {missing}")

    def test_21_csv_nonempty(self):
        try:
            import pandas as pd
        except ImportError:
            self.skipTest("pandas not installed")
        if not os.path.isdir(_CSVS_DIR):
            self.skipTest("CSVs dir missing")
        for fname in _CSV_FILES:
            path = os.path.join(_CSVS_DIR, fname)
            if not os.path.isfile(path):
                continue
            df = pd.read_csv(path)
            self.assertGreater(len(df), 0, f"{fname} is empty")


# ---------------------------------------------------------------------------
# Utils imports smoke test  (no model weights, no GPU)
# ---------------------------------------------------------------------------

class TestUtilsImports(unittest.TestCase):
    """Verify that utils/ scripts can be imported without runtime errors."""

    def _add_utils_path(self):
        utils_path = os.path.join(_TEXT_BASED, 'utils')
        if utils_path not in sys.path:
            sys.path.insert(0, utils_path)

    def test_22_prepare_data_importable(self):
        self._add_utils_path()
        try:
            import prepare_data  # noqa: F401
        except ImportError as e:
            self.skipTest(f"prepare_data import failed (missing dep): {e}")

    def test_23_prepare_data_functions(self):
        self._add_utils_path()
        try:
            from prepare_data import (
                read_shape_json, read_all_shapes,
                scale_points, rotate_points, translate_points, mirror_points,
                apply_transform_to_shape,
            )
        except ImportError as e:
            self.skipTest(f"prepare_data functions unavailable: {e}")

    def test_24_create_brep_csvs_importable(self):
        self._add_utils_path()
        # When the full test suite runs, src/config.py (UNet config) may be cached
        # as 'config' from Phase I tests. It lacks the text_based constants
        # (BREP_FOLDER, SCALE_START, …) so we clear the stale cache entry so
        # that text_based/utils/config.py (which is at sys.path[0] after
        # _add_utils_path) is found on the next import.
        if 'config' in sys.modules and not hasattr(sys.modules['config'], 'BREP_FOLDER'):
            del sys.modules['config']
        if 'create_brep_csvs' in sys.modules:
            del sys.modules['create_brep_csvs']
        try:
            import create_brep_csvs  # noqa: F401
        except ImportError as e:
            self.skipTest(f"create_brep_csvs import failed (missing dep): {e}")


# ---------------------------------------------------------------------------
# Finetuning metrics smoke test  (no GPU, no model weights)
# ---------------------------------------------------------------------------

class TestFinetuningImports(unittest.TestCase):
    """Verify finetuning/metrics.py is importable and its functions callable."""

    def _add_finetuning_path(self):
        ft_path = os.path.join(_TEXT_BASED, 'finetuning')
        if ft_path not in sys.path:
            sys.path.insert(0, ft_path)

    def test_25_metrics_importable(self):
        self._add_finetuning_path()
        try:
            from metrics import GeometricMetrics  # noqa: F401
        except ImportError as e:
            self.skipTest(f"metrics import failed (missing dep): {e}")

    def test_26_chamfer_distance_computable(self):
        self._add_finetuning_path()
        try:
            from metrics import GeometricMetrics
        except ImportError as e:
            self.skipTest(f"metrics unavailable: {e}")
        set_a = [[0.0, 0.0], [1.0, 0.0]]
        set_b = [[0.0, 0.1], [1.0, 0.1]]
        dist = GeometricMetrics.chamfer_distance(set_a, set_b)
        self.assertIsInstance(dist, float)
        self.assertGreaterEqual(dist, 0.0)

    def test_27_hausdorff_metric_computable(self):
        self._add_finetuning_path()
        try:
            from metrics import GeometricMetrics
        except ImportError as e:
            self.skipTest(f"metrics unavailable: {e}")
        # hausdorff_metric expects BRep dicts (or JSON strings) with a "Points" key.
        pred = {"Points": [[0.0, 0.0], [2.0, 0.0]]}
        true = {"Points": [[0.0, 0.0], [2.0, 0.5]]}
        dist = GeometricMetrics.hausdorff_metric(pred, true)
        self.assertIsInstance(dist, float)
        self.assertGreater(dist, 0.0, "Hausdorff distance should be > 0 for distinct point sets")
        self.assertLess(dist, 100.0, "Hausdorff distance should not be the error sentinel 1000.0")


if __name__ == '__main__':
    unittest.main(verbosity=2)
