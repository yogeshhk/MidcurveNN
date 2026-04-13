"""
test_unet.py — unit tests for the UNet 2-stage approach.
Results written to results/test_results.txt

Note: test.py in this folder is the inference/evaluation script for trained weights.

Run:
    cd src
    python -m pytest image_based/unet/test_unet.py -v
"""
import os, sys, unittest, json, datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)   # unet/ so `from config import *` resolves
sys.path.insert(0, _SRC)

RESULTS_DIR = os.path.join(_HERE, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

_TF_AVAILABLE = False
try:
    import tensorflow  # noqa
    _TF_AVAILABLE = True
except ImportError:
    pass


class TestUNetData(unittest.TestCase):

    def test_01_data_folder_exists(self):
        self.assertTrue(os.path.isdir(os.path.join(_HERE, 'data')),
                        "unet/data/ missing — run utils/prepare_data.py")

    def test_02_weights_stage1_dir(self):
        path = os.path.join(_HERE, 'weights', 'stage1')
        os.makedirs(path, exist_ok=True)
        self.assertTrue(os.path.isdir(path))

    def test_03_weights_stage2_dir(self):
        path = os.path.join(_HERE, 'weights', 'stage2')
        os.makedirs(path, exist_ok=True)
        self.assertTrue(os.path.isdir(path))

    def test_04_results_dir(self):
        self.assertTrue(os.path.isdir(RESULTS_DIR))


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestUNetModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from unet import unet_stage1, unet_stage2
        cls.stage1 = unet_stage1()
        cls.stage2 = unet_stage2()

    def test_05_stage1_builds(self):
        self.assertIsNotNone(self.stage1)

    def test_06_stage2_builds(self):
        self.assertIsNotNone(self.stage2)

    def test_07_stage1_two_outputs(self):
        self.assertEqual(len(self.stage1.outputs), 2,
                         "Stage1 should have 2 outputs (midcurve + reconstruction)")

    def test_08_stage1_input_shape(self):
        from config import IMG_SHAPE
        poly_input = self.stage1.inputs[1]
        self.assertEqual(poly_input.shape[1], IMG_SHAPE[0])
        self.assertEqual(poly_input.shape[2], IMG_SHAPE[1])

    def test_09_coordconv_importable(self):
        from utils import get_coord_layers, CoordConv
        self.assertIsNotNone(CoordConv)

    def test_10_coord_layers_shape(self):
        from utils import get_coord_layers
        from config import IMG_SHAPE
        coords = get_coord_layers(2, IMG_SHAPE)
        self.assertEqual(coords.shape[0], 2)
        self.assertEqual(coords.shape[3], 2)

    def test_11_weighted_loss_callable(self):
        from utils import weighted_cross_entropy
        loss_fn = weighted_cross_entropy(beta=0.1, balanced=False)
        self.assertTrue(callable(loss_fn))

    def test_12_datagenerator_importable(self):
        from datagenerator import datagen
        self.assertIsNotNone(datagen)


def run_and_save():
    import io
    suite  = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestUNetData),
        unittest.TestLoader().loadTestsFromTestCase(TestUNetModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {"approach": "unet", "tf_available": _TF_AVAILABLE,
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
