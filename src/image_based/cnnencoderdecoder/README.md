# CNN Encoder-Decoder

4-level convolutional encoder-decoder with residual skip connections (Add layers). Progressively halves spatial resolution during encoding, restores it with Conv2DTranspose during decoding.

**Architecture:** 128→64→32→16 px (encoder, stride-2 Conv2D) → 32→64→128 px (decoder, Conv2DTranspose) + skip connections

**Input:** 128×128 grayscale PNG (profile polygon)
**Output:** 128×128 predicted midcurve PNG

**Run (from `src/`):**
```bash
python image_based/cnnencoderdecoder/main_cnn_encoderdecoder.py
```

Trained weights saved to `models/cnn_autoencoder_model.keras`. Results grid saved to `results/results_grid.png`.
