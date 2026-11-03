# Simple Encoder-Decoder

<!-- layout-note -->
> Layout (2026-11-03): this folder is the method folder. The text below describes the OLD Keras implementation, kept here unchanged (code, notebooks, `kaggle/` notebook, results, weights). Its numbers were measured under train/test leakage. The standard PyTorch version is in [`enhanced/`](enhanced/README.md). Scripts here still run; paths were adjusted for the new depth.

Baseline approach: a single dense hidden layer (100 units) encodes the flattened 100×100 profile image to a latent vector, then a dense decoder reconstructs the 100×100 midcurve image.

**Architecture:** Input (10,000) → Dense(100, ReLU) → Dense(10,000, Sigmoid)

**Input:** 100×100 grayscale PNG (profile polygon)
**Output:** 100×100 predicted midcurve PNG

**Run (from `src/`):**
```bash
python image_based/methods/simple_encoder_decoder/main_simple_encoderdecoder.py
```

Trained weights saved to `models/`. Results grid (3 rows × 7 cols: Profile / GT / Predicted) saved to `results/results_grid.png`.
