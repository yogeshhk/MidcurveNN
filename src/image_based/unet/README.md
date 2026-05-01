# U-Net (Best Image-Based Approach)

8-level U-Net with CoordConv coordinate channels and optional 2-stage weighted binary cross-entropy (WBCE) training. Handles class imbalance (sparse midcurve pixels) via WBCE loss weighting.

**Architecture:** 8 encoder levels (256→128→...→1 px) + 8 symmetric decoder levels with skip connections; auxiliary decoder output for Stage 1 supervision.

**Input:** 256×256 grayscale PNG (from `data/unet-splits/train/` and `test/`)
**Output:** 256×256 binary midcurve mask

**Train:**
```bash
cd src/image_based/unet
python train.py
```

**Test / generate results:**
```bash
python test.py
```

Weights saved to `weights/stage1/` and `weights/stage2/`. Results grid saved to `results/results_grid.png`.
