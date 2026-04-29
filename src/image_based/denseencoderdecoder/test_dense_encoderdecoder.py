"""
test_dense_encoderdecoder.py — unit tests for the Dense Encoder-Decoder approach.
Results written to results/test_results.txt

Run:
    cd src
    python -m pytest image_based/denseencoderdecoder/test_dense_encoderdecoder.py -v
"""
import os, sys, unittest, json, datetime
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.dirname(_HERE))

RESULTS_DIR = os.path.join(_HERE, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

_TF_AVAILABLE = False
try:
    import tensorflow  # noqa
    _TF_AVAILABLE = True
except ImportError:
    pass


class TestDenseData(unittest.TestCase):

    def test_01_data_folder_exists(self):
        self.assertTrue(os.path.isdir(os.path.join(_HERE, '..', 'data', 'image-pairs')),
                        "image_based/data/image-pairs/ missing — run utils/prepare_data.py")

    def test_02_png_pairs_present(self):
        data_dir = os.path.join(_HERE, '..', 'data', 'image-pairs')
        if not os.path.isdir(data_dir): self.skipTest("image-pairs/ missing")
        files = os.listdir(data_dir)
        self.assertTrue(any('Profile'  in f for f in files))
        self.assertTrue(any('Midcurve' in f for f in files))


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestDenseModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from denseencoderdecoder.build_dense_encoderdecoder_model import dense_encoderdecoder
        cls.model = dense_encoderdecoder()

    def test_03_model_instantiation(self):
        self.assertIsNotNone(self.model)

    def test_04_input_is_flat_10000(self):
        self.assertEqual(self.model.autoencoder.input_shape[-1], 10000)

    def test_05_predict_returns_pair(self):
        imgs = np.random.rand(3, 100, 100).astype(np.float32)
        result = self.model.predict(imgs)
        self.assertEqual(len(result), 2)

    def test_06_output_shape_matches_input(self):
        imgs = np.random.rand(3, 100, 100).astype(np.float32)
        inp, out = self.model.predict(imgs)
        self.assertEqual(inp.shape, out.shape)

    def test_07_output_in_range(self):
        imgs = np.random.rand(3, 100, 100).astype(np.float32)
        _, out = self.model.predict(imgs)
        self.assertTrue((out >= 0).all() and (out <= 1).all())


def run_and_save():
    import io
    suite  = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestDenseData),
        unittest.TestLoader().loadTestsFromTestCase(TestDenseModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {"approach": "denseencoderdecoder", "tf_available": _TF_AVAILABLE,
               "timestamp": datetime.datetime.now().isoformat(),
               "tests_run": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "skipped": len(result.skipped),
               "success": result.wasSuccessful()}
    with open(os.path.join(RESULTS_DIR, 'test_results.txt'), 'w') as f: f.write(output)
    with open(os.path.join(RESULTS_DIR, 'test_results.json'), 'w') as f: json.dump(summary, f, indent=2)
    print(output)
    print(f"Results saved to: {RESULTS_DIR}/")
    return result.wasSuccessful()

if __name__ == '__main__':
    run_and_save()
