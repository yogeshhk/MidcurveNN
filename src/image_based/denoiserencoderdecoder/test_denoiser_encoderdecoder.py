"""
test_denoiser_encoderdecoder.py — unit tests for the 2-stage Denoiser approach.
Results written to results/test_results.txt

Run:
    cd src
    python -m pytest image_based/denoiserencoderdecoder/test_denoiser_encoderdecoder.py -v
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


class TestDenoiserData(unittest.TestCase):

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
class TestDenoiserModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from denoiserencoderdecoder.build_denoiser_encoderdecoder_model import denoiser_encoderdecoder
        from simpleencoderdecoder.build_simple_encoderdecoder_model import simple_encoderdecoder
        cls.denoiser = denoiser_encoderdecoder()
        cls.simple   = simple_encoderdecoder()

    def test_03_denoiser_instantiation(self):
        self.assertIsNotNone(self.denoiser)

    def test_04_simple_instantiation(self):
        self.assertIsNotNone(self.simple)

    def test_05_simple_predict_shape(self):
        imgs = np.random.rand(3, 100, 100).astype(np.float32)
        inp, out = self.simple.predict(imgs)
        self.assertEqual(inp.shape, out.shape)

    def test_06_denoiser_predict_shape(self):
        noisy = np.random.rand(3, 100, 100).astype(np.float32)
        inp, out = self.denoiser.predict(noisy)
        self.assertEqual(inp.shape, out.shape)

    def test_07_two_stage_pipeline(self):
        imgs = np.random.rand(4, 100, 100).astype(np.float32)
        _, noisy = self.simple.predict(imgs)
        inp, clean = self.denoiser.predict(noisy)
        self.assertEqual(inp.shape, clean.shape)

    def test_08_output_range(self):
        noisy = np.random.rand(3, 100, 100).astype(np.float32)
        _, out = self.denoiser.predict(noisy)
        self.assertTrue((out >= 0).all() and (out <= 1).all())


def run_and_save():
    import io
    suite  = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestDenoiserData),
        unittest.TestLoader().loadTestsFromTestCase(TestDenoiserModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {"approach": "denoiserencoderdecoder", "tf_available": _TF_AVAILABLE,
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
