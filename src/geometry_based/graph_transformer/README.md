# Graph Transformer (Primary Geometry-Based Approach)

Non-auto-regressive Graph Transformer trained from scratch on exact polygon geometry. Handles branched midcurves natively without rasterization, using Chamfer distance and BCE as joint loss.

**Architecture:** Node feature embedding (x, y coords) → multi-head self-attention layers → node-wise coordinate regression + adjacency prediction

**Input:** Polygon graph — nodes are corner vertices with (x, y) features, edges encode adjacency
**Output:** Midcurve node coordinates + adjacency matrix

**Run:**
```bash
cd src/geometry_based/graph_transformer
python main_graph_transformer.py
python main_graph_transformer.py --epochs 300 --quick  # smoke test
```

Results grid (n samples × 3 cols: Profile / GT / Predicted) saved to `results/results_grid.png`.
