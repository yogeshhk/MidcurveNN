"""
test_pix2pix.py — unit tests for the Pix2Pix GAN (Keras) approach.
Results written to results/test_results.txt

Run:
    cd src
    python -m pytest image_based/pix2pix/test_pix2pix.py -v
"""
import os, sys, unittest, json, datetime

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


class TestPix2PixData(unittest.TestCase):

    def test_01_data_dir_exists(self):
        self.assertTrue(os.path.isdir(os.path.join(_HERE, 'data')),
                        "pix2pix/data/ missing — run utils/prepare_data.py")

    def test_02_train_subdir(self):
        train_dir = os.path.join(_HERE, 'data', 'train')
        if not os.path.isdir(os.path.join(_HERE, 'data')): self.skipTest("data/ missing")
        self.assertTrue(os.path.isdir(train_dir),
                        "pix2pix/data/train/ missing")


@unittest.skipUnless(_TF_AVAILABLE, "TensorFlow not installed — skipping model tests")
class TestPix2PixModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import tensorflow as tf
        from pix2pix.keras_gan_pix2pix import Pix2Pix
        cls.tf  = tf
        cls.gan = Pix2Pix()

    def test_03_model_created(self):
        self.assertIsNotNone(self.gan)

    def test_04_data_loader_import(self):
        from pix2pix.keras_gan_data_loader import DataLoader
        loader = DataLoader('pix2pix', img_res=(256, 256))
        self.assertIsNotNone(loader)

    def test_05_generator_output_shape(self):
        dummy = self.tf.random.normal((1, 256, 256, 1))
        out = self.gan.generator(dummy, training=False)
        self.assertEqual(out.shape[1:3], (256, 256))

    def test_06_discriminator_output_shape(self):
        img_a = self.tf.random.normal((1, 256, 256, 1))
        img_b = self.tf.random.normal((1, 256, 256, 1))
        out = self.gan.discriminator([img_a, img_b], training=False)
        self.assertEqual(len(out.shape), 4)


def run_and_save():
    import io
    suite  = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(TestPix2PixData),
        unittest.TestLoader().loadTestsFromTestCase(TestPix2PixModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {"approach": "pix2pix", "tf_available": _TF_AVAILABLE,
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
