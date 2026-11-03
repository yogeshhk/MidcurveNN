# Graph Transformer (Primary Geometry-Based Approach)

<!-- layout-note -->
> Status (2026-11-03): FROZEN NEGATIVE RESULT. This is the older implementation (non-autoregressive graph transformer), kept unchanged in the method folder with its checkpoints, results and tests; do not extend it. Its numbers, and the 'adjacency not learned' finding, were measured under train/test leakage on four shapes and are not comparable with the new track (`../set_transformer/`). Script paths were adjusted for the new folder depth.

Non-auto-regressive Graph Transformer trained from scratch on exact polygon geometry. Handles branched midcurves natively without rasterization, using Chamfer distance and BCE as joint loss.

**Architecture:** Node feature embedding (x, y coords) → multi-head self-attention layers → node-wise coordinate regression + adjacency prediction

**Input:** Polygon graph: nodes are corner vertices with (x, y) features, edges encode adjacency
**Output:** Midcurve node coordinates + adjacency matrix

**Run:**
```bash
cd src/geometry_based/methods/graph_transformer
python main_graph_transformer.py
python main_graph_transformer.py --epochs 300 --quick  # smoke test
```

Results grid (n samples × 3 cols: Profile / GT / Predicted) saved to `results/results_grid.png`.
