# Denoiser Encoder-Decoder

Two-stage pipeline:
- **Stage 1:** Simple encoder-decoder (see `simpleencoderdecoder/`) produces a noisy midcurve prediction.
- **Stage 2:** This denoising autoencoder (Conv2D-based) takes the noisy Stage 1 output and cleans it.

**Architecture (Stage 2):** Conv2D(32) → MaxPool → Conv2D(32) → MaxPool | UpSampling → Conv2D(32) → UpSampling → Conv2D(1, Sigmoid)

**Input:** 100×100 noisy midcurve (Stage 1 output)
**Output:** 100×100 denoised midcurve

**Run (from `src/`):**
```bash
python image_based/denoiserencoderdecoder/main_denoiser_encoderdecoder.py
```

Trained weights saved to `models/denoiser_autoencoder_model.keras`. Results grid saved to `results/results_grid.png`.
