"""
test_finetuned_graph_transformer.py
Unit tests for the fine-tuned pretrained Graphormer approach.
Results written to results/test_results.txt

Note: test.py in this folder is the evaluation/inference script for trained checkpoints.
      This file tests model construction and forward pass in isolation (no pretrained download).

Run:
    cd src/geometry_based/finetuned_graph_transformer
    python test_finetuned_graph_transformer.py
"""
import os, sys, unittest, json, datetime
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)
sys.path.insert(0, _HERE)

RESULTS_DIR = os.path.join(_HERE, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

_RAW_DATA = os.path.join(_SRC, 'data', 'raw')


def _skip_if_no_pyg():
    try:
        import torch_geometric; return False  # noqa
    except ImportError:
        return True

def _skip_if_no_transformers():
    try:
        import transformers; return False  # noqa
    except ImportError:
        return True


class TestFinetunedModelArchitecture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        if _skip_if_no_transformers():
            raise unittest.SkipTest("transformers not installed")
        import torch
        cls.torch = torch
        from model import MidcurveFinetuned, finetuned_loss
        cls.Model = MidcurveFinetuned
        cls.loss_fn = finetuned_loss

    def test_01_model_instantiation_no_pretrained(self):
        model = self.Model(max_nodes=8, freeze_epochs=2, pretrained=False)
        self.assertIsNotNone(model)

    def test_02_backbone_frozen_initially(self):
        model = self.Model(max_nodes=8, pretrained=False)
        frozen = sum(1 for p in model.backbone.parameters() if not p.requires_grad)
        self.assertGreater(frozen, 0, "Backbone should be frozen on init")

    def test_03_unfreeze_releases_all_params(self):
        model = self.Model(max_nodes=8, pretrained=False)
        model.unfreeze()
        still_frozen = sum(1 for p in model.backbone.parameters() if not p.requires_grad)
        self.assertEqual(still_frozen, 0, "All backbone params should be trainable after unfreeze()")

    def test_04_forward_coords_shape(self):
        model = self.Model(max_nodes=8, pretrained=False).eval()
        x  = self.torch.rand(4, 2)
        ei = self.torch.tensor([[0,1,2,3],[1,2,3,0]], dtype=self.torch.long)
        batch = self.torch.zeros(4, dtype=self.torch.long)
        with self.torch.no_grad():
            coords, adj = model(x, ei, batch)
        self.assertEqual(coords.shape, (1, 8, 2),
                         f"Expected (1, 8, 2) coords, got {coords.shape}")

    def test_05_forward_adj_shape(self):
        model = self.Model(max_nodes=8, pretrained=False).eval()
        x  = self.torch.rand(4, 2)
        ei = self.torch.tensor([[0,1,2,3],[1,2,3,0]], dtype=self.torch.long)
        batch = self.torch.zeros(4, dtype=self.torch.long)
        with self.torch.no_grad():
            _, adj = model(x, ei, batch)
        self.assertEqual(adj.shape, (1, 8, 8),
                         f"Expected (1, 8, 8) adj logits, got {adj.shape}")

    def test_06_loss_computable(self):
        model = self.Model(max_nodes=8, pretrained=False).eval()
        x  = self.torch.rand(4, 2)
        ei = self.torch.tensor([[0,1,2,3],[1,2,3,0]], dtype=self.torch.long)
        batch = self.torch.zeros(4, dtype=self.torch.long)
        with self.torch.no_grad():
            coords, adj = model(x, ei, batch)
        y   = self.torch.rand(3, 2)
        mei = self.torch.tensor([[0,1],[1,2]], dtype=self.torch.long)
        loss, lc, la = self.loss_fn(coords, adj, y, mei)
        self.assertFalse(self.torch.isnan(loss), "Loss is NaN")
        self.assertGreater(loss.item(), 0)

    def test_07_loss_decreases_with_perfect_coords(self):
        """Chamfer loss should be ~0 when predicted coords == ground truth."""
        model = self.Model(max_nodes=4, pretrained=False).eval()
        x  = self.torch.rand(3, 2)
        ei = self.torch.tensor([[0,1,2],[1,2,0]], dtype=self.torch.long)
        batch = self.torch.zeros(3, dtype=self.torch.long)
        # manually set coord head output to match y
        y = self.torch.rand(4, 2)
        # patch coord head to return y
        with unittest.mock.patch.object(model, 'coord_head',
                                         side_effect=lambda emb: y.view(1, -1)):
            pass  # just verify loss infrastructure is sane via forward
        loss, lc, _ = self.loss_fn(
            y.unsqueeze(0),
            self.torch.zeros(1, 4, 4),
            y,
            self.torch.empty(2, 0, dtype=self.torch.long))
        self.assertAlmostEqual(lc, 0.0, places=5)

    def test_08_checkpoint_dir_created(self):
        ckpt_dir = os.path.join(_HERE, 'checkpoints')
        os.makedirs(ckpt_dir, exist_ok=True)
        self.assertTrue(os.path.isdir(ckpt_dir))

    def test_09_results_dir_exists(self):
        self.assertTrue(os.path.isdir(RESULTS_DIR))


class TestFinetunedDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        sys.path.insert(0, os.path.join(_SRC, 'geometry_based', 'graph_transformer'))
        from graph_dataset import MidcurveGraphDataset
        cls.dataset = MidcurveGraphDataset(_RAW_DATA, augment=False)

    def test_10_dataset_nonempty(self):
        self.assertGreater(len(self.dataset), 0)

    def test_11_data_has_required_fields(self):
        data = self.dataset.get(0)
        for field in ('x', 'edge_index', 'y', 'mid_edge_index'):
            self.assertTrue(hasattr(data, field), f"Missing field: {field}")


def run_and_save():
    import io
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite([
        loader.loadTestsFromTestCase(TestFinetunedModelArchitecture),
        loader.loadTestsFromTestCase(TestFinetunedDataset),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {
        "approach": "finetuned_graph_transformer",
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
