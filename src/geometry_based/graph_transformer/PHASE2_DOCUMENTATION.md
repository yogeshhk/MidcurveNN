# MidcurveNN – Phase II: Graph-to-Graph Transformer
## Technical Documentation

---

## 1. Overview

Phase II of MidcurveNN replaces the raster image representation used in Phase I with an explicit **geometric graph** representation. A 2D closed polygon (profile) is modelled as a graph whose nodes carry `(x, y)` coordinates and whose edges connect consecutive polygon corners. The task is to predict the midcurve — a polyline graph (open or branched) — from the profile graph.

This is formulated as a **graph coarsening / dimension-reduction** problem and solved with a **Graph Transformer encoder–decoder** architecture.

```
Profile Graph (input)         Midcurve Graph (output)
  N nodes, closed ring    →     M < N nodes, open / branched
  node features: (x, y)         node features: (x, y)
  edge features: length          edge features: length
```

---

## 2. Why Graphs?

| Property | Seq2Seq (Phase I approach) | Graph (Phase II) |
|---|---|---|
| Represents branches (Y, Plus) | ✗ | ✓ |
| Exact geometry (no rasterisation) | ✗ | ✓ |
| Variable number of nodes/edges | Needs padding | Native |
| Invariant to point-listing order | ✗ | ✓ (with PE) |
| Spatial (not just topological) | N/A | ✓ (node coords) |

Sequences cannot represent non-manifold outputs (branched midcurves). Graphs handle arbitrary topology naturally.

---

## 3. File Structure

```
midcurvenn_phase2/
├── data/
│   └── raw/                    ← .dat and .mid files go here
│       ├── I.dat, I.mid
│       ├── L.dat, L.mid
│       ├── T.dat, T.mid
│       └── Plus.dat, Plus.mid
│
├── graph_dataset.py            ← data loading, graph construction, augmentation
├── graph_transformer.py        ← model architecture and loss functions
├── train.py                    ← standalone training script (CLI)
├── evaluate.py                 ← standalone evaluation script (CLI)
├── main_graph_transformer.py   ← end-to-end pipeline (recommended entry point)
├── prepare_plots.py            ← all visualisation utilities (Phase I + II)
│
├── checkpoints/
│   ├── best_model.pt           ← saved after training
│   ├── last_model.pt
│   └── training_log.csv
│
└── results/
    ├── dataset_overview.png
    ├── augmentation_I.png  … augmentation_Plus.png
    ├── training_curves.png
    ├── I_prediction.png … Plus_prediction.png
    └── *_adj.png               ← adjacency heatmaps
```

---

## 4. Data Format

### Input: `.dat` file (profile polygon)
Each line is one vertex `x y` of the closed polygon, listed in order.  
The polygon is implicitly closed (last vertex connects back to first).

```
5 5        ← vertex 0
10 5       ← vertex 1
10 20      ← vertex 2
5 20       ← vertex 3
           ← closed: edge 3→0 added automatically
```

### Output: `.mid` file (midcurve polyline)
Each line is one point `x y` of the midcurve, listed in order.  
Consecutive listed points form edges. Repeated coordinates create branch nodes.

```
7.5 5      ← endpoint 0
7.5 20     ← endpoint 1  → edge 0–1
```

For branched shapes (T, Plus), the branch node appears as a repeated coordinate:
```
12.5 0     ← leg bottom
12.5 22.5  ← branch node (appears once; shared by three edges)
25.0 22.5  ← right end
0 22.5     ← left end
```

---

## 5. Graph Construction

### Profile Graph

| Element | Details |
|---|---|
| Nodes | One per polygon vertex; feature = normalised `(x, y)` |
| Edges | Closed ring: `0→1, 1→2, …, (n-1)→0` (undirected = both directions) |
| Edge feature | Euclidean segment length |

### Midcurve Graph

| Element | Details |
|---|---|
| Nodes | Unique `(x, y)` positions in the `.mid` file |
| Edges | Consecutive-pair rule on listed points; shared coords → branch node |
| Edge feature | Euclidean segment length |

### Normalisation
All coordinates are centred on the profile centroid and scaled so the largest absolute coordinate is ≤ 1. The same (centre, scale) transform is applied to the midcurve so both graphs live in the same coordinate frame.

---

## 6. Data Augmentation

Since only 4 base shapes are available, geometric augmentations are applied to the `(profile, midcurve)` pair **consistently** (same transform to both), yielding **136 samples** from 4 shapes.

| Transform | Variants |
|---|---|
| Rotation | 30°, 60°, …, 330° (11 angles) |
| Uniform scale | 0.5×, 0.75×, 1.5×, 2.0× |
| Translation | `dx ∈ {±10, ±20}` × `dy ∈ {±10, ±20}` (16 pairs) |
| Mirror X-axis | 1 variant |
| Mirror Y-axis | 1 variant |
| **Original** | 1 |
| **Total per shape** | 34 |

Augmentations are implemented via 2D affine transforms directly on the point lists — not image transforms — so exact geometry is preserved.

---

## 7. Architecture

```
                    ┌────────────────────────────────────────────────┐
Input Profile       │  ENCODER: GraphTransformerEncoder              │
x: [N, 2]   ──────►│                                                │
edge_index          │  1. Laplacian PE (k=4 eigenvectors)           │
edge_attr           │     Projects graph spectral features into      │
                    │     node embeddings → global positional sense  │
                    │                                                │
                    │  2. Input projection: Linear(2 → H)           │
                    │                                                │
                    │  3. L × (TransformerConv + LayerNorm + GELU)  │
                    │     Each layer: multi-head attention over      │
                    │     edges and edge features; residual          │
                    └──────────────────┬─────────────────────────────┘
                                       │ z: [N, H]
                    ┌──────────────────▼─────────────────────────────┐
                    │  BOTTLENECK: TopK Pooling                      │
                    │                                                │
                    │  Learns a score per node from z.               │
                    │  Keeps top ⌈ratio × N⌉ nodes.                 │
                    │  Old edges are discarded (decoder generates    │
                    │  entirely new topology).                       │
                    └──────────────────┬─────────────────────────────┘
                                       │ z_s: [k, H]
                    ┌──────────────────▼─────────────────────────────┐
                    │  DECODER: NonAutoregressiveDecoder             │
                    │                                                │
                    │  Per-node MLP:  z_s → coords_pred [k, 2]      │
                    │                                                │
                    │  Pairwise MLP:  [z_i ‖ z_j] → adj_logit [k,k]│
                    │  (matrix symmetrised; self-loops zeroed)       │
                    └────────────────────────────────────────────────┘
```

### Key design decisions

**Laplacian Positional Encoding (LPE)**  
Polygon graphs have no canonical node ordering. LPE injects spectral information (community structure, centrality, boundary shape) so the encoder can reason about global geometry even while operating locally.

**TransformerConv with edge features**  
Unlike standard GNN convolution which only uses node neighbour information, TransformerConv computes attention scores weighted by edge features (segment lengths here). This makes the encoder geometry-aware.

**TopK Pooling as bottleneck**  
The learned score function determines which polygon corners carry the most information about the midcurve. This is the geometric intuition: midcurve endpoints typically lie near polygon "waist" regions.

**Non-Autoregressive Decoding**  
The entire adjacency matrix is predicted in one shot (not edge-by-edge), which is critical for branched midcurves. The pairwise MLP on `[z_i ‖ z_j]` can represent both symmetric and asymmetric relationships; we symmetrise the output to enforce undirectedness.

---

## 8. Loss Function

```
L_total = λ_chamfer × L_chamfer  +  λ_adj × L_adj_BCE
```

| Component | Formula | Purpose |
|---|---|---|
| **Chamfer** | ½(mean_i min_j ‖p_i−g_j‖² + mean_j min_i ‖g_j−p_i‖²) | Penalises geometric mismatch between predicted and GT nodes; handles variable set sizes |
| **Adj BCE** | Binary cross-entropy on [k×k] adjacency with positive-class reweighting | Teaches the decoder which node pairs should be connected |

Default weights: `λ_chamfer = 1.0`, `λ_adj = 0.5`.  
The BCE loss uses a positive weight `= (k²−|E|) / |E|` to counteract the sparsity of midcurve adjacency matrices.

---

## 9. Quick Start

### Requirements
```
torch >= 2.0
torch_geometric >= 2.4
matplotlib
numpy
```

### Install
```bash
pip install torch torchvision
pip install torch_geometric
```

### Run end-to-end pipeline
```bash
cd midcurvenn_phase2
python main_graph_transformer.py
```

### Smoke test (10 epochs, no augmentation)
```bash
python main_graph_transformer.py --quick
```

### Train only
```bash
python train.py --epochs 300 --lr 3e-4 --hidden 128
```

### Evaluate a saved checkpoint
```bash
python evaluate.py --ckpt checkpoints/best_model.pt --threshold 0.45
```

---

## 10. Hyperparameters

| Parameter | Default | Meaning |
|---|---|---|
| `--hidden` | 64 | Embedding dimension H (must be divisible by heads) |
| `--num-layers` | 3 | Number of TransformerConv encoder layers |
| `--heads` | 4 | Attention heads per layer |
| `--lpe-k` | 4 | Laplacian eigenvectors for positional encoding |
| `--ratio` | 0.6 | TopK pooling ratio (fraction of nodes kept) |
| `--epochs` | 200 | Training epochs |
| `--lr` | 3e-4 | AdamW learning rate (cosine annealed to 1%) |
| `--lam-ch` | 1.0 | Chamfer loss weight |
| `--lam-adj` | 0.5 | Adjacency BCE loss weight |
| `--threshold` | 0.5 | σ(logit) threshold to declare an edge |
| `--batch-size` | 16 | Training batch size |

---

## 11. Visualisation API (`prepare_plots.py`)

All Phase II functions accept numpy arrays for portability.

```python
from prepare_plots import (
    plot_graph_pair,              # side-by-side profile + midcurve
    plot_graph_dataset_summary,   # grid of all dataset shapes
    plot_augmentation_gallery,    # variants of one shape
    plot_graph_prediction,        # profile | GT | prediction
    plot_training_curves,         # train/val loss from CSV
    plot_adjacency_matrix,        # predicted vs GT adjacency heatmap
    plot_node_degree_histogram,   # degree distribution
)
```

### Example
```python
import numpy as np
from prepare_plots import plot_graph_pair

profile_pts  = np.array([[5,5],[10,5],[10,20],[5,20]])
profile_edges = np.array([[0,1,2,3,1,2,3,0],[1,2,3,0,0,1,2,3]])
mid_pts   = np.array([[7.5,5],[7.5,20]])
mid_edges = np.array([[0,1],[1,0]])

fig = plot_graph_pair(profile_pts, profile_edges, mid_pts, mid_edges,
                      title="I-Shape", annotate=True)
fig.savefig("i_shape.png")
```

---

## 12. Output Figures

After running the pipeline:

| File | Content |
|---|---|
| `dataset_overview.png` | 2×2 grid: each shape with profile (blue) + midcurve (red) overlaid |
| `augmentation_{X}.png` | Gallery of up to 8 geometric variants of shape X |
| `training_curves.png` | Three subplots: total loss, Chamfer loss, adjacency BCE loss |
| `{shape}_prediction.png` | Three panels: input profile / GT midcurve / predicted midcurve |
| `{shape}_adj.png` | Heatmap: predicted adjacency probability vs ground truth |

---

## 13. Limitations and Future Work

| Limitation | Possible remedy |
|---|---|
| Only 4 base shapes → small dataset | Add more shapes; use larger augmentation space |
| TopK pool ratio is fixed | Adaptive ratio learned per graph via attention scoring |
| Branch nodes rely on coordinate coincidence in `.mid` format | Explicit branch-node annotation in data format |
| Coord prediction assumes normalised space | Richer decoder with graph-level context (global mean pooling) |
| No curvature in edges | Add arc-parameterised edge geometry for curved profiles |
| Single graph per batch in evaluation | Full mini-batch evaluation with PyG batch masking |

### Recommended next steps
1. Add more shape types (U, C, H, Z, custom imported from CAD)
2. Replace TopK with a differentiable soft-assignment (e.g. DiffPool or MinCutPool) for smoother gradients
3. Add a graph-matching loss (e.g. earth mover's distance on node sets) to complement Chamfer
4. Explore Variational Graph Auto-Encoders (VGAE) for generative capability

---

## 14. References

1. Shi et al., "Masked Label Prediction: Unified Message Passing Model for Semi-supervised Classification", 2021 – TransformerConv design.
2. Dwivedi & Bresson, "A Generalization of Transformers to Graphs", 2021 – Graph Transformer formulation.
3. Gama et al., "Graph Coarsening with Graph Convolutional Networks", 2019 – graph coarsening background.
4. Kipf & Welling, "Variational Graph Auto-Encoders", 2016 – adjacency reconstruction principle.
5. Fan et al., "A Point Set Generation Network for 3D Object Reconstruction", 2017 – Chamfer distance as point-set loss.
6. Kulkarni Y.H., "MidcurveNN: Encoder-Decoder Neural Network for Computing Midcurve of a Thin Polygon", ODSC 2019.
