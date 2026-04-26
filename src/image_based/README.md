# Phase I — Image-Based Approaches

This folder contains seven encoder-decoder variants that solve midcurve extraction by converting the problem into an image-to-image translation task.

## Concept

Polygon profiles and their midcurves are rasterized to PNG bitmaps. A neural network learns the pixel-level mapping: **input bitmap (closed polygon filled region) → output bitmap (midcurve strokes)**. Post-processing extracts the thin midcurve skeleton from the output.

**Limitation:** Raster approximation loses exact geometry; a separate vectorization step is needed to recover clean polylines.

## Approaches

| Directory | Architecture | Input size | Notes |
|---|---|---|---|
| `simpleencoderdecoder/` | 1 dense hidden layer (100 units) | 100×100 | Baseline |
| `cnnencoderdecoder/` | 4-level Conv2D encoder + Conv2DTranspose decoder | 128×128 | |
| `denseencoderdecoder/` | Fully connected (10 000 dims) | 100×100 | |
| `denoiserencoderdecoder/` | Denoising autoencoder (uses simple as stage 1) | 100×100 | |
| `unet/` | 8-level UNet, auxiliary decoder, CoordConv, 2-stage WBCE | 256×256 | **Best** |
| `pix2pix/` | Pix2Pix GAN with discriminator (Keras) | 256×256 | |
| `img2img/` | Pix2Pix GAN (PyTorch) | 256×256 | |

## Data Generation

Run from `src/`:

```bash
python utils/prepare_data.py
```

This reads `.dat`/`.mid` files from `src/data/raw/`, rasterizes them via DrawSVG with augmentations (rotation 0–350°, translation, mirroring), and writes PNG pairs into each approach's `data/` subdirectory.

## Training

```bash
# Best performer
cd src/image_based/unet
python train.py

# Simpler baselines (run from src/)
python image_based/simpleencoderdecoder/main_simple_encoderdecoder.py
python image_based/cnnencoderdecoder/main_cnn_encoderdecoder.py
python image_based/denseencoderdecoder/main_dense_encoderdecoder.py
python image_based/denoiserencoderdecoder/main_denoiser_encoderdecoder.py
python image_based/pix2pix/main_pix2pix.py
python image_based/img2img/main_img2img_pytorch.py
```

## Tests

```bash
cd src
python -m pytest image_based/testing/test_image_based.py -v
```

Tests cover: data folder presence, model build (forward pass), output shape matching, and the `read_dat_files` utility.
TensorFlow model tests are skipped automatically if TF is not installed.
