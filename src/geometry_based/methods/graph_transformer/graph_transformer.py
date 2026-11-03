"""
graph_transformer.py  –  MidcurveNN Phase III
=============================================
Graph Transformer Encoder → TopK Pool Bottleneck → Non-Autoregressive Decoder

Architecture
------------
                         ┌─────────────────────────────────────┐
  Profile Graph          │  ENCODER                            │
  x: [N_p, 2]   ──────► │  TransformerConv × L layers         │  z: [N_p, H]
  edge_index_p           │  + Laplacian Positional Encoding    │
  edge_attr_p            └──────────────┬──────────────────────┘
                                        │
                         ┌──────────────▼──────────────────────┐
                         │  BOTTLENECK (TopK Pooling)           │
                         │  Keeps top-k scored nodes           │  z_s: [k, H]
                         └──────────────┬──────────────────────┘
                                        │
                         ┌──────────────▼──────────────────────┐
                         │  DECODER                            │
                         │  MLP per node → coord prediction   │  y_hat: [k, 2]
                         │  Pairwise MLP → adj logits         │  A_hat: [k, k]
                         └─────────────────────────────────────┘

Loss
----
  L_total = λ_chamfer * L_chamfer  +  λ_adj * L_adj_bce

  L_chamfer : bidirectional nearest-neighbour distance between predicted
              node coords and ground-truth midcurve node coords.
  L_adj_bce : binary cross-entropy on predicted adjacency vs ground-truth
              midcurve adjacency (both expressed as k×k matrices).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import TransformerConv, TopKPooling
from torch_geometric.utils import get_laplacian, to_dense_adj, dense_to_sparse
import math


# ---------------------------------------------------------------------------
# Laplacian Positional Encoding
# ---------------------------------------------------------------------------

class LaplacianPE(nn.Module):
    """
    Adds k eigenvectors of the normalised graph Laplacian as extra node features.
    This gives the encoder a notion of global graph structure / position.
    """
    def __init__(self, k: int = 4, hidden: int = 16):
        super().__init__()
        self.k = k
        self.proj = nn.Linear(k, hidden)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        n = x.size(0)
        k = min(self.k, n - 1)   # can't exceed n-1 non-trivial eigenvectors

        # Build normalised Laplacian  L = I - D^{-1/2} A D^{-1/2}
        edge_index_lap, edge_weight_lap = get_laplacian(
            edge_index, normalization='sym', num_nodes=n)

        L = torch.zeros(n, n, device=x.device)
        L[edge_index_lap[0], edge_index_lap[1]] = edge_weight_lap

        # Eigendecomposition (CPU for stability; small graphs are fine)
        try:
            eigvals, eigvecs = torch.linalg.eigh(L.cpu())
            # Take k smallest non-trivial eigenvectors (skip constant eigvec)
            pe = eigvecs[:, 1:k + 1]           # [n, k]
        except Exception:
            pe = torch.zeros(n, k)

        pe = pe.to(x.device)
        if pe.size(1) < self.k:                # pad if graph too small
            pad = torch.zeros(n, self.k - pe.size(1), device=x.device)
            pe = torch.cat([pe, pad], dim=1)

        return x + self.proj(pe)               # residual addition


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------

class GraphTransformerEncoder(nn.Module):
    """
    Stack of TransformerConv layers (each with edge features) interleaved
    with layer-norm + residual connections. Laplacian PE applied before.
    """
    def __init__(self, in_dim: int, hidden: int, edge_dim: int,
                 num_layers: int = 3, heads: int = 4, lpe_k: int = 4):
        super().__init__()
        self.lpe = LaplacianPE(k=lpe_k, hidden=in_dim)

        self.input_proj = nn.Linear(in_dim, hidden)

        self.layers = nn.ModuleList()
        self.norms  = nn.ModuleList()
        for _ in range(num_layers):
            self.layers.append(
                TransformerConv(hidden, hidden // heads,
                                heads=heads, edge_dim=edge_dim,
                                concat=True, beta=True))
            self.norms.append(nn.LayerNorm(hidden))

        self.out_dim = hidden

    def forward(self, x, edge_index, edge_attr):
        # Laplacian positional encoding
        x = self.lpe(x, edge_index)
        x = self.input_proj(x)

        for conv, norm in zip(self.layers, self.norms):
            x_new = conv(x, edge_index, edge_attr)
            x = norm(x + x_new)       # residual + norm
            x = F.gelu(x)
        return x                       # [N, hidden]


# ---------------------------------------------------------------------------
# Non-Autoregressive Decoder
# ---------------------------------------------------------------------------

class NonAutoregressiveDecoder(nn.Module):
    """
    Given a reduced set of node embeddings z_s [k, H]:
      1. Predict (x, y) coordinates via per-node MLP.
      2. Predict adjacency via pairwise MLP on concatenated node pairs.
    """
    def __init__(self, hidden: int):
        super().__init__()
        self.coord_mlp = nn.Sequential(
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Linear(hidden // 2, 2),   # → (x, y)
        )
        self.edge_mlp = nn.Sequential(
            nn.Linear(hidden * 2, hidden),
            nn.GELU(),
            nn.Linear(hidden, hidden // 2),
            nn.GELU(),
            nn.Linear(hidden // 2, 1),   # → edge logit
        )

    def forward(self, z_s: torch.Tensor):
        """
        z_s : [k, H]
        Returns
        -------
        coords_pred  : [k, 2]       predicted midcurve node coordinates
        adj_logits   : [k, k]       raw logits for edge existence
        """
        k = z_s.size(0)

        # Node coordinate prediction
        coords_pred = self.coord_mlp(z_s)     # [k, 2]

        # Pairwise edge prediction
        zi = z_s.unsqueeze(1).expand(k, k, -1)  # [k, k, H]
        zj = z_s.unsqueeze(0).expand(k, k, -1)  # [k, k, H]
        pairs = torch.cat([zi, zj], dim=-1)      # [k, k, 2H]
        adj_logits = self.edge_mlp(pairs).squeeze(-1)  # [k, k]

        # Symmetrise (undirected graph)
        adj_logits = (adj_logits + adj_logits.T) / 2.0

        return coords_pred, adj_logits


# ---------------------------------------------------------------------------
# Full Model
# ---------------------------------------------------------------------------

class MidcurveGraphTransformer(nn.Module):
    """
    End-to-end Graph Transformer for midcurve extraction.

    Parameters
    ----------
    node_in   : int   – input node feature dimension (2 for x,y)
    edge_in   : int   – input edge feature dimension (1 for length)
    hidden    : int   – internal embedding dimension
    ratio     : float – TopK pooling ratio (fraction of nodes to keep)
    num_layers: int   – encoder depth
    heads     : int   – attention heads
    lpe_k     : int   – Laplacian PE eigenvectors
    """
    def __init__(self, node_in: int = 2, edge_in: int = 1,
                 hidden: int = 64, ratio: float = 0.6,
                 num_layers: int = 3, heads: int = 4, lpe_k: int = 4):
        super().__init__()
        assert hidden % heads == 0, "hidden must be divisible by heads"

        self.encoder = GraphTransformerEncoder(
            in_dim=node_in, hidden=hidden, edge_dim=edge_in,
            num_layers=num_layers, heads=heads, lpe_k=lpe_k)

        self.pool = TopKPooling(hidden, ratio=ratio)

        self.decoder = NonAutoregressiveDecoder(hidden)

    def forward(self, x, edge_index, edge_attr, batch=None):
        """
        Parameters
        ----------
        x          : [N, 2]     profile node coordinates (normalised)
        edge_index : [2, E]     profile graph connectivity
        edge_attr  : [E, 1]     profile edge lengths
        batch      : [N]        batch vector (None → single graph)

        Returns
        -------
        coords_pred  : [k, 2]   predicted midcurve node coordinates
        adj_logits   : [k, k]   edge existence logits
        batch_out    : [k]      batch assignment of kept nodes
        perm         : [k]      original node indices that were kept
        """
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

        # 1. Encode
        z = self.encoder(x, edge_index, edge_attr)         # [N, H]

        # 2. Pool (bottleneck)  – discards old edges
        z_s, _, _, batch_out, perm, score = self.pool(
            z, edge_index, batch=batch)                    # [k, H]

        # 3. Decode
        coords_pred, adj_logits = self.decoder(z_s)       # [k,2], [k,k]

        return coords_pred, adj_logits, batch_out, perm

    @torch.no_grad()
    def predict_graph(self, x, edge_index, edge_attr, adj_threshold=0.5):
        """
        Inference helper. Returns (predicted_coords, predicted_edge_index)
        as numpy arrays in the original (unnormalised) space – pass
        centre/scale separately for denorm.
        """
        self.eval()
        coords, adj_logits, _, _ = self.forward(x, edge_index, edge_attr)
        adj_prob = torch.sigmoid(adj_logits)
        # Remove self-loops and threshold
        adj_prob.fill_diagonal_(0.0)
        edge_index_new, _ = dense_to_sparse(adj_prob > adj_threshold)
        return coords, edge_index_new


# ---------------------------------------------------------------------------
# Loss functions
# ---------------------------------------------------------------------------

def chamfer_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """
    Bidirectional Chamfer distance between two point sets.
    pred   : [M, 2]
    target : [N, 2]
    """
    if pred.numel() == 0 or target.numel() == 0:
        return torch.tensor(0.0, requires_grad=True, device=pred.device)
    # Pairwise squared distances
    diff = pred.unsqueeze(1) - target.unsqueeze(0)    # [M, N, 2]
    dist2 = (diff ** 2).sum(-1)                       # [M, N]
    # Forward: each pred → nearest target
    loss_fwd = dist2.min(dim=1).values.mean()
    # Backward: each target → nearest pred
    loss_bwd = dist2.min(dim=0).values.mean()
    return (loss_fwd + loss_bwd) / 2.0


def adjacency_bce_loss(adj_logits: torch.Tensor,
                       mid_edge_index: torch.Tensor,
                       num_nodes: int) -> torch.Tensor:
    """
    Binary cross-entropy between predicted adjacency logits [k, k]
    and the ground-truth midcurve adjacency (built from mid_edge_index).
    k may differ from num_nodes (ground truth); we compare on the
    min-size square to allow gradient flow even with size mismatch.
    """
    k = adj_logits.size(0)

    # Build ground-truth adjacency [num_nodes, num_nodes]
    if mid_edge_index.numel() > 0:
        gt_adj_full = to_dense_adj(mid_edge_index,
                                   max_num_nodes=num_nodes).squeeze(0)  # [N_m, N_m]
    else:
        gt_adj_full = torch.zeros(num_nodes, num_nodes,
                                  device=adj_logits.device)

    # Crop / pad to [k, k]
    size = min(k, num_nodes)
    gt_adj = torch.zeros(k, k, device=adj_logits.device)
    gt_adj[:size, :size] = gt_adj_full[:size, :size]

    # Positive-weight to handle extreme sparsity
    pos_weight = torch.tensor(
        max(1.0, (k * k - gt_adj.sum().item()) / (gt_adj.sum().item() + 1e-6)),
        device=adj_logits.device)

    return F.binary_cross_entropy_with_logits(
        adj_logits, gt_adj, pos_weight=pos_weight)


def midcurve_loss(coords_pred, adj_logits, y, mid_edge_index,
                  lambda_chamfer=1.0, lambda_adj=0.5):
    """Combined training loss."""
    lc = chamfer_loss(coords_pred, y)
    la = adjacency_bce_loss(adj_logits, mid_edge_index, num_nodes=y.size(0))
    return lambda_chamfer * lc + lambda_adj * la, lc.item(), la.item()


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    torch.manual_seed(42)
    model = MidcurveGraphTransformer(hidden=64, ratio=0.6)
    print(model)

    x = torch.randn(8, 2)
    ei = torch.tensor([[0,1,2,3,4,5,6,7,1,2,3,4,5,6,7,0],
                        [1,2,3,4,5,6,7,0,0,1,2,3,4,5,6,7]], dtype=torch.long)
    ea = torch.randn(16, 1)
    coords, adj_logits, batch_out, perm = model(x, ei, ea)
    print("coords_pred:", coords.shape)
    print("adj_logits :", adj_logits.shape)
