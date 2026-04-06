# gnnencoderdecoder — Phase II (Work in Progress)

This folder contains the stub for the Graph Neural Network (GNN) approach to midcurve prediction (Phase II of the MidcurveNN project).

**Status: Non-functional. Do not use or import this code.**

`build_gnn_encoderdecoder_model.py` contains incorrect API calls (`dgl.nn.Module`, `dgl.nn.MSELoss`) and references an undefined variable (`img`). It does not compile.

## Intent

The goal is to represent input profiles and output midcurves as graphs with coordinate-bearing nodes (x, y positions) and edges (line segments), then train an encoder-decoder using graph convolution layers (DGL / PyTorch Geometric) instead of image convolutions.

This avoids the rasterisation approximation of Phase I while preserving spatial structure.

## Challenges

- Standard GNN pooling aggregates topology but not spatial geometry. A geometric embedding that combines node coordinates with edge geometry is needed.
- Variable-sized graphs (different number of points per shape) require graph-level pooling strategies.
- No established baselines for graph-to-graph dimension reduction in the geometric domain.

## Next Steps

See [DGL VGAE example](https://github.com/dmlc/dgl/tree/master/examples/pytorch/vgae) for a starting point.
