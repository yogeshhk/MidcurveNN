# Dense Encoder-Decoder

<!-- layout-note -->
> Layout (2026-11-03): this folder is the method folder. The text below describes the OLD Keras implementation, kept here unchanged. Its numbers were measured under train/test leakage. The standard PyTorch version is in [`enhanced/`](enhanced/README.md).

Fully connected encoder-decoder operating on the entire flattened image (10,000 dimensions). Separate encoder and decoder sub-models with a bottleneck representation.

**Architecture:** Input (10,000) → Dense bottleneck → Dense (10,000, Sigmoid)

**Input:** 100×100 grayscale PNG (profile polygon)
**Output:** 100×100 predicted midcurve PNG

**Run (from `src/`):**
```bash
python image_based/methods/dense_encoder_decoder/main_dense_encoderdecoder.py
```

Three model files saved to `models/` (autoencoder, encoder, decoder). Results grid saved to `results/results_grid.png`.
