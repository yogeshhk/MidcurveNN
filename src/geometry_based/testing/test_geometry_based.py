"""
test_geometry_based.py  –  MidcurveNN
==========================================
Unit / smoke tests for geometry-based (Phase II) approaches:
  - graph_transformer  (non-auto-regressive, trained from scratch)
  - finetuned_graph_transformer (pretrained Graphormer fine-tuned)

Tests verify:
  - Raw data loading → graph construction
  - Dataset iteration
  - Model forward pass (random weights, CPU)
  - Loss computation

Run
---
    cd src
    python -m pytest testing/test_geometry_based.py -v
    python testing/test_geometry_based.py
"""

import os
import sys
import unittest
import torch

# geometry_based/testing/ → geometry_based/ → src/
_SRC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _SRC)

_RAW_DATA = os.path.join(_SRC, 'data', 'raw')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skip_if_no_pyg():
    try:
        import torch_geometric  # noqa
    except ImportError:
        return True
    return False


def _skip_if_no_transformers():
    try:
        import transformers  # noqa
    except ImportError:
        return True
    return False


# ---------------------------------------------------------------------------
# Dataset tests
# ---------------------------------------------------------------------------

class TestMidcurveGraphDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        sys.path.insert(0, os.path.join(_SRC, 'geometry_based', 'graph_transformer'))
        from graph_dataset import MidcurveGraphDataset
        cls.dataset = MidcurveGraphDataset(_RAW_DATA, augment=False)

    def test_dataset_nonempty(self):
        self.assertGreater(len(self.dataset), 0,
                           "Dataset is empty — check data/raw/ for .dat/.mid pairs")

    def test_data_fields(self):
        data = self.dataset.get(0)
        self.assertTrue(hasattr(data, 'x'),           "Missing node features x")
        self.assertTrue(hasattr(data, 'edge_index'),  "Missing edge_index")
        self.assertTrue(hasattr(data, 'y'),           "Missing midcurve target y")
        self.assertTrue(hasattr(data, 'mid_edge_index'), "Missing mid_edge_index")

    def test_node_feature_dim(self):
        data = self.dataset.get(0)
        self.assertEqual(data.x.size(1), 2, "Node features should be (N, 2) for (x, y)")

    def test_midcurve_feature_dim(self):
        data = self.dataset.get(0)
        self.assertEqual(data.y.size(1), 2, "Midcurve target should be (M, 2)")

    def test_normalised_coords(self):
        data = self.dataset.get(0)
        self.assertLessEqual(data.x.abs().max().item(), 1.5,
                             "Node coords should be normalised (approx within [-1.5, 1.5])")

    def test_augmented_dataset_larger(self):
        if _skip_if_no_pyg():
            self.skipTest("torch_geometric not installed")
        from graph_dataset import MidcurveGraphDataset
        ds_aug = MidcurveGraphDataset(_RAW_DATA, augment=True)
        self.assertGreaterEqual(len(ds_aug), len(self.dataset))


# ---------------------------------------------------------------------------
# Graph Transformer model tests
# ---------------------------------------------------------------------------

class TestGraphTransformerModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        sys.path.insert(0, os.path.join(_SRC, 'geometry_based', 'graph_transformer'))
        from graph_transformer import MidcurveGraphTransformer, midcurve_loss, chamfer_loss
        cls.Model = MidcurveGraphTransformer
        cls.loss_fn = midcurve_loss
        cls.chamfer_loss = chamfer_loss

    def _make_batch(self):
        """Tiny synthetic batch: 2 graphs, 4 nodes each."""
        from torch_geometric.data import Data, Batch
        graphs = []
        for _ in range(2):
            x = torch.rand(4, 2)
            ei = torch.tensor([[0, 1, 2, 3, 1, 2, 3, 0],
                                [1, 2, 3, 0, 0, 1, 2, 3]], dtype=torch.long)
            ea = torch.rand(8, 1)
            y = torch.rand(3, 2)
            mid_ei = torch.tensor([[0, 1], [1, 2]], dtype=torch.long)
            graphs.append(Data(x=x, edge_index=ei, edge_attr=ea,
                               y=y, mid_edge_index=mid_ei))
        return Batch.from_data_list(graphs)

    def test_forward_pass(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2)
        batch = self._make_batch()
        coords, adj, _, _ = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
        self.assertEqual(coords.shape[1], 2, "Output coords should have 2 columns (x, y)")

    def test_loss_computable(self):
        model = self.Model(node_in=2, edge_in=1, hidden=16, ratio=0.5,
                           num_layers=2, heads=2, lpe_k=2)
        batch = self._make_batch()
        coords, adj, _, _ = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
        loss, lc, la = self.loss_fn(coords, adj, batch.y, batch.mid_edge_index, 1.0, 0.5)
        self.assertFalse(torch.isnan(loss), "Loss is NaN")
        self.assertGreater(loss.item(), 0, "Loss should be positive")

    def test_chamfer_loss_zero_for_equal(self):
        pts = torch.rand(5, 2)
        loss = self.chamfer_loss(pts, pts)
        self.assertAlmostEqual(loss.item(), 0.0, places=5)


# ---------------------------------------------------------------------------
# Fine-tuned graph transformer tests (no pretrained weights needed)
# ---------------------------------------------------------------------------

class TestFinetunedGraphTransformer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if _skip_if_no_pyg():
            raise unittest.SkipTest("torch_geometric not installed")
        if _skip_if_no_transformers():
            raise unittest.SkipTest("transformers not installed")
        sys.path.insert(0, os.path.join(_SRC, 'geometry_based', 'finetuned_graph_transformer'))
        from model import MidcurveFinetuned, finetuned_loss
        cls.Model = MidcurveFinetuned
        cls.loss_fn = finetuned_loss

    def test_model_instantiation_no_pretrained(self):
        model = self.Model(max_nodes=8, freeze_epochs=2, pretrained=False)
        self.assertIsNotNone(model)

    def test_unfreeze(self):
        model = self.Model(max_nodes=8, freeze_epochs=2, pretrained=False)
        frozen = sum(1 for p in model.backbone.parameters() if not p.requires_grad)
        self.assertGreater(frozen, 0, "Backbone should be frozen initially")
        model.unfreeze()
        frozen_after = sum(1 for p in model.backbone.parameters() if not p.requires_grad)
        self.assertEqual(frozen_after, 0, "All backbone params should be unfrozen")

    def test_forward_pass_no_pretrained(self):
        model = self.Model(max_nodes=8, pretrained=False).eval()
        x = torch.rand(4, 2)
        ei = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long)
        batch = torch.zeros(4, dtype=torch.long)
        coords, adj_logits = model(x, ei, batch)
        self.assertEqual(coords.shape, (1, 8, 2),
                         f"Expected (1, 8, 2), got {coords.shape}")
        self.assertEqual(adj_logits.shape, (1, 8, 8))

    def test_loss_computable(self):
        model = self.Model(max_nodes=8, pretrained=False).eval()
        x = torch.rand(4, 2)
        ei = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]], dtype=torch.long)
        batch = torch.zeros(4, dtype=torch.long)
        coords, adj_logits = model(x, ei, batch)
        y = torch.rand(3, 2)
        mid_ei = torch.tensor([[0, 1], [1, 2]], dtype=torch.long)
        loss, lc, la = self.loss_fn(coords, adj_logits, y, mid_ei)
        self.assertFalse(torch.isnan(loss), "Loss is NaN")


if __name__ == '__main__':
    unittest.main(verbosity=2)
