# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MidcurveNN** computes the midcurve (medial axis/skeleton) of 2D closed polygons using neural networks. It is a research project with three phases:

- **Phase I (Implemented)**: Image-to-image transformation — rasterize polygons to 100×100 or 256×256 bitmaps, then apply encoder-decoder networks
- **Phase II (Stub)**: Graph neural network approach (`src/gnnencoderdecoder/`) — geometric-aware representations, not yet implemented
- **Phase III (Emerging)**: LLM-based approach using B-rep JSON text representations with Hugging Face transformers

Input: 2D closed polygon (`.dat` file = profile points). Output: midcurve polyline (`.mid` file = skeleton points).

## Environment Setup

```bash
cd src
conda env create -f environment.yml
conda activate midcurvenn
```

The environment targets Python 3.10 with TensorFlow 2.13 (tensorflow-macos + tensorflow-metal for Mac GPU), PyTorch, Keras, and Hugging Face transformers.

## Common Commands

### Generate training data from raw `.dat`/`.mid` files
```bash
cd src
python utils/prepare_data.py
```
Reads ASCII coordinate files from `src/data/raw/`, rasterizes via DrawSVG, applies augmentations (rotation 0–350°, translation, mirroring), outputs paired PNG images to `src/data/input/`.

### Train a model
```bash
# Most advanced (UNet, 2-stage)
cd src/unet
python train.py

# Simpler baselines (run from src/)
python simpleencoderdecoder/main_simple_encoderdecoder.py
python cnnencoderdecoder/main_cnn_encoderdecoder.py
python denseencoderdecoder/main_dense_encoderdecoder.py
python denoiserencoderdecoder/main_denoiser_encoderdecoder.py
python pix2pix/main_pix2pix.py
python img2img/main_img2img_pytorch.py  # PyTorch variant
```

### Test / infer
```bash
cd src/unet
python test.py
```

## Code Architecture

### Configuration
- `src/config.py` — global config: `IMG_SHAPE` (100×100 vs 256×256), `TRAIN_SIZE`/`TEST_SIZE`, `TWO_STAGE`, `COORD_CONV`, loss functions (`STAGE1/2_LOSS`), weighted BCE betas
- `src/unet/config.py` — UNet-specific hyperparameters

### Data pipeline (`src/utils/`)
- `prepare_data.py` — reads `.dat`/`.mid` → DrawSVG rasterization → PNG pairs with augmentations
- `create_ds.py` — dataset creation helpers
- `prepare_plots.py` — visualization: side-by-side profile vs. predicted midcurve
- `metric_utils.py` — Keras callbacks, best-epoch tracking, training history

### Model architectures (Phase I)
Each subdirectory follows the same pattern:
- `build_*_model.py` — defines the Keras/PyTorch model
- `main_*.py` — loads data, trains, evaluates, plots

| Directory | Architecture |
|---|---|
| `simpleencoderdecoder/` | 1 dense hidden layer (100 units), baseline |
| `cnnencoderdecoder/` | 4-level Conv2D encoder + Conv2DTranspose decoder, skip connections |
| `denseencoderdecoder/` | Fully connected, input flattened to 10,000 dims |
| `denoiserencoderdecoder/` | Denoising autoencoder variant |
| `unet/` | 8-level UNet with auxiliary decoder, batch norm, LeakyReLU; best performer |
| `pix2pix/` | Pix2Pix GAN (Keras) |
| `img2img/` | PyTorch image-to-image |

### Data format
Raw data in `src/data/raw/`: named shapes (I, L, T, Plus, etc.)
- `.dat` = profile polygon points (ASCII, one `x y` coordinate per line)
- `.mid` = midcurve polyline points (same format)

Training data split: 70% train / 30% validation by default. Test set in `src/data/test/`.

### UNet details (`src/unet/`)
The most developed model. Key files:
- `unet.py` — architecture with configurable filter counts, coord conv channels
- `train.py` — two-stage training; stage 1 trains full network, stage 2 fine-tunes with weighted BCE
- `utils.py` — `CoordConv` layer implementation, custom loss functions
- `losses/` — weighted BCE and other custom losses
- `weights/` — saved model checkpoints
- `results/` — inference output images

## Research Context

- Phase I limitations: raster approximation loses exact geometry; post-processing needed to extract clean polylines
- Phase II (`gnnencoderdecoder/`) is scaffold only — `main_gnn_encoderdecoder.py` and `build_gnn_encoderdecoder_model.py` exist but are unfilled
- Phase III material was moved out of this repo (see commit history)
- `src/data/sequences.json` — JSON-format dataset used for LLM/sequence-to-sequence experiments
