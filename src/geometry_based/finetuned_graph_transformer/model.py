"""
model.py  –  MidcurveNN Phase III-b
====================================
Fine-tunable Graph Transformer for midcurve prediction.

Strategy
--------
Load a pretrained Graphormer backbone (clefourrier/graphormer-base-pcqm4mv2
via HuggingFace transformers), replace the task-specific regression head with
a midcurve coordinate regression head, and fine-tune on our small dataset using
the geometric augmentation pipeline from graph_transformer/.

Architecture
------------
Pretrained backbone  →  Graphormer encoder (12 layers, 768 hidden, 32 heads)
                     →  Fine-tune head: Linear(768 → 256) + ReLU + Linear(256 → 2*max_nodes)
                                        (predicts x,y per output node)
                     →  Adjacency head: Linear(768 → max_nodes^2) → sigmoid → thresholded edges

The backbone is frozen for the first `freeze_epochs` epochs, then unfrozen for
joint fine-tuning with a lower learning rate.

Usage
-----
    from model import MidcurveFinetuned
    model = MidcurveFinetuned(max_nodes=32, freeze_epochs=10)
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F

# Attempt to import HuggingFace Graphormer; fall back gracefully so the module
# can be imported even when transformers is not installed.
try:
    from transformers import GraphormerModel, GraphormerConfig
    _HF_AVAILABLE = True
except ImportError:
    _HF_AVAILABLE = False

# Add src/ to path so we can reuse graph_transformer utilities
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)

from geometry_based.graph_transformer.graph_transformer import chamfer_loss  # reuse loss


# ---------------------------------------------------------------------------
# Pretrained backbone wrapper
# ---------------------------------------------------------------------------

class GraphormerBackbone(nn.Module):
    """
    Thin wrapper around HuggingFace Graphormer.
    Converts our (x,y) node features + edge_index into Graphormer's dict input.
    """

    PRETRAINED_MODEL = "clefourrier/graphormer-base-pcqm4mv2"

    def __init__(self, pretrained: bool = True):
        super().__init__()
        if not _HF_AVAILABLE:
            raise ImportError(
                "Install transformers>=4.35: pip install transformers")

        if pretrained:
            self.backbone = GraphormerModel.from_pretrained(self.PRETRAINED_MODEL)
        else:
            cfg = GraphormerConfig()
            self.backbone = GraphormerModel(cfg)

        self.hidden_size = self.backbone.config.hidden_size  # 768

    def forward(self, x, edge_index, batch):
        """
        x          : (N, 2)  normalised (x, y) node coords
        edge_index : (2, E)  COO edge indices (global node ids)
        batch      : (N,)    graph-membership per node
        Returns: (B, hidden_size) — one embedding per graph (CLS token pooled)
        """
        from torch_geometric.utils import to_dense_batch, to_dense_adj

        # Dense node features (B, max_nodes, 2)
        x_dense, mask = to_dense_batch(x, batch)
        B, max_n, _ = x_dense.shape

        # Dense adjacency (B, max_nodes, max_nodes)
        adj = to_dense_adj(edge_index, batch, max_num_nodes=max_n)  # (B, N, N)

        # Graphormer expects integer atom types; project our (x,y) → embedding dim
        # via its input_nodes embedding by converting coords to a single int index
        # (a simplification — coords are binned to 256 buckets per axis).
        BINS = 256
        x_bin = (x_dense.clamp(0, 1) * (BINS - 1)).long()     # (B, N, 2)
        node_ids = x_bin[..., 0] * BINS + x_bin[..., 1]       # (B, N) flatten to 1D token
        node_ids = node_ids.unsqueeze(-1)                      # (B, N, 1) — HF Graphormer expects 3D input_nodes

        # Spatial pos encoding from adjacency (shortest-path distances)
        # Graphormer's built-in spatial encoder expects attn_bias & spatial_pos.
        # We pass the adjacency as spatial_pos (1 = connected, 0 = not) clamped to int.
        spatial_pos = adj.long()  # (B, N, N)

        # attn_bias shape: (B, N+1, N+1) — HF Graphormer adds the head dim internally
        # via .unsqueeze(1).repeat(1, num_heads, 1, 1), so we must NOT include it here.
        attn_bias = torch.zeros(B, max_n + 1, max_n + 1, device=x.device)

        # attn_edge_type: per-hop edge type features (B, N, N, num_edge_dist)
        # We have no multi-type edges, so pass zeros with 1 feature dim.
        edge_zeros = torch.zeros(B, max_n, max_n, 1, dtype=torch.long, device=x.device)
        outputs = self.backbone(
            input_nodes=node_ids,
            input_edges=edge_zeros,
            attn_bias=attn_bias,
            in_degree=adj.sum(-1).long(),
            out_degree=adj.sum(-2).long(),
            spatial_pos=spatial_pos,
            attn_edge_type=edge_zeros,
            on_the_fly_graph_features=None,
        )
        # outputs.last_hidden_state: (B, max_n+1, hidden)
        # Index 0 is the virtual "CLS" node
        graph_embedding = outputs.last_hidden_state[:, 0, :]  # (B, hidden)
        return graph_embedding, outputs.last_hidden_state[:, 1:, :], mask


# ---------------------------------------------------------------------------
# Fine-tuning head
# ---------------------------------------------------------------------------

class MidcurveFinetuned(nn.Module):
    """
    Pretrained Graphormer backbone + midcurve-specific regression head.

    Parameters
    ----------
    max_nodes    : maximum number of output midcurve nodes
    freeze_epochs: number of epochs to keep backbone frozen (call unfreeze() after)
    pretrained   : load pretrained HF weights (set False for offline / unit tests)
    """

    def __init__(self, max_nodes: int = 32, freeze_epochs: int = 10,
                 pretrained: bool = True):
        super().__init__()
        self.max_nodes = max_nodes
        self.freeze_epochs = freeze_epochs

        self.backbone = GraphormerBackbone(pretrained=pretrained)
        hidden = self.backbone.hidden_size

        # Coordinate head: predict (x, y) per output node
        self.coord_head = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Linear(256, max_nodes * 2),
        )

        # Adjacency head: predict max_nodes x max_nodes edge probabilities
        self.adj_head = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Linear(256, max_nodes * max_nodes),
        )

        # Freeze backbone initially
        self._freeze_backbone()

    def _freeze_backbone(self):
        for p in self.backbone.parameters():
            p.requires_grad = False

    def unfreeze(self):
        """Call after freeze_epochs to enable joint fine-tuning."""
        for p in self.backbone.parameters():
            p.requires_grad = True

    def forward(self, x, edge_index, batch):
        """
        Returns
        -------
        coords_pred : (B, max_nodes, 2)  predicted midcurve node coordinates
        adj_logits  : (B, max_nodes, max_nodes)  raw adjacency logits
        """
        graph_emb, _, _ = self.backbone(x, edge_index, batch)   # (B, hidden)

        coords_flat = self.coord_head(graph_emb)                 # (B, max_nodes*2)
        coords_pred = coords_flat.view(-1, self.max_nodes, 2)    # (B, max_nodes, 2)

        adj_flat = self.adj_head(graph_emb)                      # (B, max_nodes^2)
        adj_logits = adj_flat.view(-1, self.max_nodes, self.max_nodes)

        return coords_pred, adj_logits


# ---------------------------------------------------------------------------
# Loss
# ---------------------------------------------------------------------------

def finetuned_loss(coords_pred, adj_logits, coords_gt, mid_edge_index,
                   lam_ch: float = 1.0, lam_adj: float = 0.5):
    """
    Combined Chamfer + adjacency BCE loss for the fine-tuning head.

    coords_pred  : (B, max_nodes, 2)
    adj_logits   : (B, max_nodes, max_nodes)
    coords_gt    : (N_gt_total, 2)  ground-truth midcurve coords (flat across batch)
    mid_edge_index: (2, E_gt)       ground-truth midcurve edges
    """
    B = coords_pred.size(0)

    # Chamfer on batch-mean (flatten batch dim for simplicity — same as graph_transformer)
    ch = chamfer_loss(coords_pred.view(-1, 2), coords_gt)

    # Adjacency BCE
    max_n = adj_logits.size(-1)
    adj_gt = torch.zeros_like(adj_logits)
    if mid_edge_index.numel() > 0:
        ei = mid_edge_index.clamp(max=max_n - 1)
        adj_gt[:, ei[0], ei[1]] = 1.0
    adj_loss = F.binary_cross_entropy_with_logits(adj_logits, adj_gt)

    return lam_ch * ch + lam_adj * adj_loss, ch.item(), adj_loss.item()
