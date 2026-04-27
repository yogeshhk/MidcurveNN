# Phase III — Geometry-Based Approaches

This folder contains graph neural network approaches that operate directly on polygon coordinates, avoiding the rasterization approximation of Phase I.

## Concept

Each closed polygon is represented as a **graph**: nodes are corner points (features = `(x, y)`), edges connect adjacent corners. The network predicts midcurve coordinates and adjacency, handling branched midcurves (T, Plus shapes) natively via the graph structure.

Losses combine **Chamfer distance** (point-cloud matching) and **binary cross-entropy** on the adjacency matrix.

## Approaches

| Directory | Description | Status |
|---|---|---|
| `graph_transformer/` | Non-auto-regressive Graph Transformer trained from scratch. Custom LaplacianPE + TransformerConv + TopKPooling architecture. | **Primary** |
| `finetuned_graph_transformer/` | Pretrained `clefourrier/graphormer-base-pcqm4mv2` (HuggingFace) fine-tuned in two phases: frozen head-only → joint fine-tuning. | Active |
| `gnnencoderdecoder/` | Legacy GNN stub — not implemented, kept as reference. | Reference only |

## Training

```bash
# Non-auto-regressive Graph Transformer
cd src/geometry_based/graph_transformer
python main_graph_transformer.py
python main_graph_transformer.py --epochs 300 --quick   # smoke test

# Fine-tuned pretrained Graphormer
cd src/geometry_based/finetuned_graph_transformer
python train.py
python train.py --quick --no-pretrained                 # offline / CI
```

## Evaluation

```bash
cd src/geometry_based/graph_transformer
python evaluate.py

cd src/geometry_based/finetuned_graph_transformer
python test.py
```

## Tests

```bash
cd src
python -m pytest geometry_based/testing/test_geometry_based.py -v
```

Tests cover: dataset loading, node/edge field presence, coordinate normalisation, augmentation size, model forward pass (random weights, CPU), loss computation, and the Chamfer identity check.
PyTorch Geometric tests are skipped automatically if `torch_geometric` is not installed.

## Data Format

Input comes from `src/data/raw/`:
- `.dat` — profile polygon points (ASCII, `x y` per line, closed)
- `.mid` — midcurve polyline points (same format, open/branched)

`MidcurveGraphDataset` reads these files, normalizes coordinates to `[-1, 1]`, and builds PyG `Data` objects with optional geometric augmentation.
