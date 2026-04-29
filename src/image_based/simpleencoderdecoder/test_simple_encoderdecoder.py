"""
test_simple_encoderdecoder.py — unit tests for the Simple Encoder-Decoder approach.
Results written to results/test_results.txt and results/junit.xml

Run:
    cd src
    python -m pytest image_based/simpleencoderdecoder/test_simple_encoderdecoder.py -v
    python image_based/simpleencoderdecoder/test_simple_encoderdecoder.py
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


# ── Data tests (no TF required) ────────────────────────────────────────────

class TestSimpleEncoderDecoderData(unittest.TestCase):

    def test_01_data_folder_exists(self):
        self.assertTrue(os.path.isdir(os.path.join(_HERE, '..', 'data', 'image-pairs')),
                        "image_based/data/image-pairs/ missing — run utils/prepare_data.py")

    def test_02_profile_pngs_present(self):
        data_dir = os.path.join(_HERE, '..', 'data', 'image-pairs')
        if not os.path.isdir(data_dir): self.skipTest("image-pairs/ missing")
        self.assertTrue(any('Profile' in f for f in os.listdir(data_dir)),
                        "No Profile PNG files found")

    def test_03_midcurve_pngs_present(self):
        data_dir = os.path.join(_HERE, '..', 'data', 'image-pairs')
        if not os.path.isdir(data_dir): self.skipTest("image-pairs/ missing")
        self.assertTrue(any('Midcurve' in f for f in os.listdir(data_dir)),
                        "No Midcurve PNG files found")


# ── Model tests (requires TensorFlow) ─────────────────────────────────────

@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestSimpleEncoderDecoderModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
        cls.model = simple_encoderdecoder()

    def test_04_model_instantiation(self):
        self.assertIsNotNone(self.model)

    def test_05_model_has_keras_model(self):
        self.assertTrue(hasattr(self.model, 'autoencoder'))

    def test_06_predict_returns_tuple(self):
        imgs = np.random.rand(3, 100, 100).astype(np.float32)
        result = self.model.predict(imgs)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_07_output_shape_matches_input(self):
        imgs = np.random.rand(4, 100, 100).astype(np.float32)
        inp, out = self.model.predict(imgs)
        self.assertEqual(inp.shape, out.shape)

    def test_08_output_range(self):
        imgs = np.random.rand(4, 100, 100).astype(np.float32)
        _, out = self.model.predict(imgs)
        self.assertTrue((out >= 0).all() and (out <= 1).all())


def run_and_save():
    import io
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite([
        loader.loadTestsFromTestCase(TestSimpleEncoderDecoderData),
        loader.loadTestsFromTestCase(TestSimpleEncoderDecoderModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {
        "approach": "simpleencoderdecoder", "tf_available": _TF_AVAILABLE,
        "timestamp": datetime.datetime.now().isoformat(),
        "tests_run": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "success": result.wasSuccessful(),
    }
    with open(os.path.join(RESULTS_DIR, 'test_results.txt'), 'w') as f: f.write(output)
    with open(os.path.join(RESULTS_DIR, 'test_results.json'), 'w') as f: json.dump(summary, f, indent=2)
    print(output)
    print(f"Results saved to: {RESULTS_DIR}/")
    return result.wasSuccessful()


if __name__ == '__main__':
    run_and_save()
