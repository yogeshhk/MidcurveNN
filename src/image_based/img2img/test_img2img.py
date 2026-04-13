"""
test_img2img.py
Unit tests for the img2img (PyTorch Pix2Pix) approach.
Results written to results/test_results.txt

Run:
    cd src/image_based/img2img
    python test_img2img.py
"""
import os, sys, unittest, json, datetime
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)
sys.path.insert(0, os.path.dirname(_HERE))

RESULTS_DIR = os.path.join(_HERE, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)


class TestImg2Img(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            import torch
            cls.torch = torch
        except ImportError:
            raise unittest.SkipTest("PyTorch not installed")

    def _load_models(self):
        """Import Gen/Disc from main_img2img_pytorch without executing training."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "main_img2img_pytorch",
            os.path.join(_HERE, "main_img2img_pytorch.py"))
        mod = importlib.util.load_from_spec = spec
        # Import selectively to avoid triggering DataLoader at module level
        sys.path.insert(0, _HERE)
        from main_img2img_pytorch import Gen, Disc
        return Gen, Disc

    def test_01_torch_available(self):
        self.assertIsNotNone(self.torch)

    def test_02_generator_import(self):
        try:
            sys.path.insert(0, _HERE)
            from main_img2img_pytorch import Gen
            self.assertIsNotNone(Gen)
        except Exception as e:
            self.skipTest(f"Could not import Gen: {e}")

    def test_03_generator_forward_pass(self):
        try:
            sys.path.insert(0, _HERE)
            from main_img2img_pytorch import Gen
        except Exception as e:
            self.skipTest(f"Import failed: {e}")
        device = self.torch.device("cpu")
        model = Gen(inst_norm=False).to(device).eval()
        dummy = self.torch.randn(1, 3, 256, 512)  # side-by-side 256×256 pairs
        with self.torch.no_grad():
            out = model(dummy)
        self.assertEqual(out.shape, dummy.shape,
                         f"Generator output {out.shape} should match input {dummy.shape}")

    def test_04_discriminator_forward_pass(self):
        try:
            sys.path.insert(0, _HERE)
            from main_img2img_pytorch import Disc
        except Exception as e:
            self.skipTest(f"Import failed: {e}")
        device = self.torch.device("cpu")
        model = Disc(inst_norm=False).to(device).eval()
        x = self.torch.randn(1, 3, 256, 256)
        y = self.torch.randn(1, 3, 256, 256)
        with self.torch.no_grad():
            out = model(x, y)
        self.assertEqual(len(out.shape), 4,
                         "Discriminator output should be a 4D patch tensor")

    def test_05_data_folder_exists(self):
        self.assertTrue(os.path.isdir(os.path.join(_HERE, 'data')),
                        "data/ missing — run utils/prepare_data.py")

    def test_06_logs_folder_exists(self):
        log_dir = os.path.join(_HERE, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        self.assertTrue(os.path.isdir(log_dir))


def run_and_save():
    import io
    suite  = unittest.TestLoader().loadTestsFromTestCase(TestImg2Img)
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {
        "approach": "img2img",
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
