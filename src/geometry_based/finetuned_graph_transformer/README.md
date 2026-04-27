# Phase III-b: Fine-tuned Pretrained Graph Transformer

## Overview

This approach **fine-tunes a pretrained Graphormer** (from HuggingFace Hub) on the
midcurve dataset, rather than training a Graph Transformer from scratch.

| | Non-auto-regressive GT (`graph_transformer/`) | Fine-tuned Graphormer (this folder) |
|---|---|---|
| Backbone | Trained from scratch | `clefourrier/graphormer-base-pcqm4mv2` |
| Parameters | ~50K | ~125M (backbone) + ~500K (heads) |
| Training | End-to-end from random init | 2-phase: frozen head-only → joint |
| Data need | Small OK (geometric augment) | Small OK (transfer from PCQM4Mv2) |
| Dependency | torch-geometric | transformers + torch-geometric |

## Motivation

The non-auto-regressive Graph Transformer trains from scratch, which is effective
given our geometric augmentation. The fine-tuned variant leverages molecular
graph pre-training (PCQM4Mv2, 3.8M molecules) to bring richer structural priors
that may improve generalisation on unseen shapes with fewer training samples.

## Setup

```bash
conda activate midcurvenn
pip install transformers>=4.35          # for GraphormerModel
pip install torch-geometric             # already in environment.yml
```

## Usage

### Training

```bash
cd src/geometry_based/finetuned_graph_transformer

# Full training (2-phase: 20 frozen + 80 joint fine-tune)
python train.py

# Quick smoke test (5 epochs, no augmentation)
python train.py --quick

# Offline / CI (no pretrained weights download)
python train.py --no-pretrained --quick
```

Key options:
- `--freeze-epochs N` — epochs to keep backbone frozen (default 20)
- `--epochs N` — total training epochs (default 100)
- `--lr F` — head learning rate; backbone uses lr/10 after unfreeze (default 1e-4)
- `--max-nodes N` — maximum output midcurve nodes (default 32)
- `--data PATH` — path to raw `.dat`/`.mid` files (default: `src/data/raw`)

### Evaluation

```bash
python test.py
python test.py --ckpt checkpoints/best_model.pt
```

## Architecture

```
Input: polygon graph (nodes=corners, edges=segments, features=(x,y))
        ↓
Graphormer backbone (12 layers, 768 hidden, 32 heads)
  • Node features (x,y) → binned to 256×256 tokens
  • Spatial encoding from adjacency matrix
  • Virtual CLS super-node (index 0)
        ↓
CLS embedding  (B, 768)
        ↓
Coordinate head: Linear(768→256) + ReLU + Linear(256→max_nodes×2)
        ↓  coords (B, max_nodes, 2)
Adjacency head: Linear(768→256) + ReLU + Linear(256→max_nodes²)
        ↓  adj logits (B, max_nodes, max_nodes)
```

## Loss

```
L = λ_ch · Chamfer(coords_pred, coords_gt) + λ_adj · BCE(adj_logits, adj_gt)
```

Default: λ_ch = 1.0, λ_adj = 0.5

## Training Protocol

1. **Phase 1 (frozen):** Only head parameters trained. Backbone frozen.
   Fast convergence, prevents catastrophic forgetting of pretrained features.
2. **Phase 2 (joint):** Backbone unfrozen with learning rate / 10.
   Allows domain adaptation while preserving pretrained representations.

## Outputs

- `checkpoints/best_model.pt` — best validation checkpoint
- `checkpoints/last_model.pt` — final epoch checkpoint
- `checkpoints/training_log.csv` — per-epoch metrics
- `results/<shape>_finetuned_prediction.png` — per-shape prediction visualisations
