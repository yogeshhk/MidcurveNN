"""
test_graph_transformer.py
Unit tests for the non-auto-regressive Graph Transformer approach.
Results written to results/test_results.txt

Note: evaluate.py in this folder is the full inference script for trained checkpoints.
      This file tests model architecture, dataset, and loss in isolation.

Run:
    cd src/geometry_based/graph_transformer
    python test_graph_transformer.py
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
        import torch_geometric  # noqa
        return False
    except ImportError:
        return True


class TestGraphTransformerDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        from graph_dataset import MidcurveGraphDataset
        cls.dataset_raw = MidcurveGraphDataset(_RAW_DATA, augment=False)
        cls.dataset_aug = MidcurveGraphDataset(_RAW_DATA, augment=True)

    def test_01_raw_data_dir_exists(self):
        self.assertTrue(os.path.isdir(_RAW_DATA),
                        f"Raw data not found at {_RAW_DATA}")

    def test_02_dataset_nonempty(self):
        self.assertGreater(len(self.dataset_raw), 0)

    def test_03_augmented_larger_or_equal(self):
        self.assertGreaterEqual(len(self.dataset_aug), len(self.dataset_raw))

    def test_04_node_features_are_2d(self):
        data = self.dataset_raw.get(0)
        self.assertEqual(data.x.size(1), 2, "Node features must be (N, 2) for (x, y)")

    def test_05_midcurve_target_is_2d(self):
        data = self.dataset_raw.get(0)
        self.assertEqual(data.y.size(1), 2, "Midcurve target must be (M, 2)")

    def test_06_edge_index_valid(self):
        import torch
        data = self.dataset_raw.get(0)
        n = data.x.size(0)
        self.assertTrue((data.edge_index >= 0).all())
        self.assertTrue((data.edge_index < n).all())

    def test_07_coords_are_normalised(self):
        data = self.dataset_raw.get(0)
        max_coord = data.x.abs().max().item()
        self.assertLessEqual(max_coord, 1.5,
                             "Normalised coords should be approximately within [-1.5, 1.5]")

    def test_08_label_attribute_present(self):
        data = self.dataset_raw.get(0)
        self.assertTrue(hasattr(data, 'label') and data.label,
                        "Each data object should have a non-empty label")


class TestGraphTransformerModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        import torch
        from torch_geometric.data import Data, Batch
        cls.torch = torch
        cls.Data  = Data
        cls.Batch = Batch
        from graph_transformer import MidcurveGraphTransformer, midcurve_loss, chamfer_loss
        cls.Model = MidcurveGraphTransformer
        cls.midcurve_loss = midcurve_loss
        cls.chamfer_loss  = chamfer_loss

    def _tiny_batch(self, n_graphs=2, n_nodes=4):
        graphs = []
        for _ in range(n_graphs):
            x  = self.torch.rand(n_nodes, 2)
            ei = self.torch.tensor([[0,1,2,3,1,2,3,0],[1,2,3,0,0,1,2,3]], dtype=self.torch.long)
            ea = self.torch.rand(8, 1)
            y  = self.torch.rand(3, 2)
            mei = self.torch.tensor([[0,1],[1,2]], dtype=self.torch.long)
            graphs.append(self.Data(x=x, edge_index=ei, edge_attr=ea, y=y, mid_edge_index=mei))
        return self.Batch.from_data_list(graphs)

    def test_09_model_instantiation(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2)
        self.assertIsNotNone(model)

    def test_10_forward_returns_4_values(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2).eval()
        batch = self._tiny_batch()
        with self.torch.no_grad():
            out = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
        self.assertEqual(len(out), 4,
                         "forward() should return (coords, adj_logits, pool_idx, attn)")

    def test_11_output_coords_dim_2(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2).eval()
        batch = self._tiny_batch()
        with self.torch.no_grad():
            coords, _, _, _ = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
        self.assertEqual(coords.size(1), 2)

    def test_12_loss_positive_not_nan(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2).eval()
        batch = self._tiny_batch()
        with self.torch.no_grad():
            coords, adj, _, _ = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
        loss, lc, la = self.midcurve_loss(coords, adj, batch.y, batch.mid_edge_index, 1.0, 0.5)
        self.assertFalse(self.torch.isnan(loss))
        self.assertGreater(loss.item(), 0)

    def test_13_chamfer_zero_for_identical(self):
        pts = self.torch.rand(5, 2)
        loss = self.chamfer_loss(pts, pts)
        self.assertAlmostEqual(loss.item(), 0.0, places=5)

    def test_14_checkpoint_dir_exists(self):
        ckpt_dir = os.path.join(_HERE, 'checkpoints')
        os.makedirs(ckpt_dir, exist_ok=True)
        self.assertTrue(os.path.isdir(ckpt_dir))

    def test_15_results_dir_exists(self):
        self.assertTrue(os.path.isdir(RESULTS_DIR))


def run_and_save():
    import io
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite([
        loader.loadTestsFromTestCase(TestGraphTransformerDataset),
        loader.loadTestsFromTestCase(TestGraphTransformerModel),
    ])
    buf    = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    output = buf.getvalue()
    summary = {
        "approach": "graph_transformer",
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
