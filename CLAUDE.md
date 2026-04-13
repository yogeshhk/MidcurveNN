# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MidcurveNN** computes the midcurve (medial axis/skeleton) of 2D closed polygons using neural networks. It is a research project with three approach families:

- **Image-based (Phase I)**: Rasterize polygons to 100×100 or 256×256 bitmaps → encoder-decoder networks
- **Geometry-based (Phase II)**: Graph neural network approach — exact coordinates, handles branching natively
- **Text-based (Phase III)**: LLM/seq2seq approach using B-rep JSON text representations (planned)

Input: 2D closed polygon (`.dat` file = profile points). Output: midcurve polyline (`.mid` file = skeleton points).

## Directory Structure

```
src/
├── config.py                    # Global config (IMG_SHAPE, TRAIN_SIZE, loss settings)
├── environment.yml
├── data/raw/                    # Raw .dat/.mid coordinate files — shared by ALL approaches
├── utils/                       # Shared utilities (data prep, plotting, metrics)
│
├── image_based/                 # Phase I — raster/bitmap approaches
│   ├── data/                    # Generated PNG image pairs
│   ├── simpleencoderdecoder/    # 1 dense hidden layer (baseline)
│   ├── cnnencoderdecoder/       # 4-level Conv2D encoder-decoder
│   ├── denseencoderdecoder/     # Fully connected (flattened 10K dims)
│   ├── denoiserencoderdecoder/  # Denoising autoencoder variant
│   ├── unet/                    # 8-level UNet with 2-stage training (BEST)
│   ├── pix2pix/                 # Pix2Pix GAN (Keras)
│   ├── img2img/                 # Image-to-image (PyTorch)
│   └── kaggle/                  # Kaggle notebooks / dataset exports
│
├── geometry_based/              # Phase II — graph/geometric approaches
│   ├── data/                    # Graph datasets
│   ├── graph_transformer/       # Non-auto-regressive Graph Transformer (primary)
│   ├── finetuned_graph_transformer/  # Pretrained Graphormer fine-tuned on midcurve data
│   └── gnnencoderdecoder/       # Legacy GNN stub (reference only)
│
├── text_based/                  # Phase III — LLM/sequence approaches (planned)
│   ├── data/sequences.json      # B-rep JSON sequences generated from raw data
│   └── README.md                # Approach documentation and roadmap
│
└── testing/                     # Cross-approach tests and benchmarks
    ├── test_image_based.py      # Unit tests for all image-based approaches
    ├── test_geometry_based.py   # Unit tests for geometry-based approaches
    ├── test_text_based.py       # Smoke tests for text data pipeline
    └── benchmark.py             # Comparative benchmark across all approaches
```

## Environment Setup

```bash
cd src
conda env create -f environment.yml
conda activate midcurvenn

# Extra dependency for finetuned_graph_transformer
pip install transformers>=4.35
```

The environment targets Python 3.10 with TensorFlow 2.13, PyTorch, Keras, and Hugging Face transformers.

## Common Commands

### Generate training data from raw `.dat`/`.mid` files
```bash
cd src
python utils/prepare_data.py
```
Reads ASCII coordinate files from `src/data/raw/`, rasterizes via DrawSVG with augmentations
(rotation 0–350°, translation, mirroring). Outputs:
- PNG pairs → `src/image_based/<approach>/data/`
- Sequence JSON → `src/text_based/data/sequences.json`

### Train — Image-based (Phase I)
```bash
# Best performer (UNet, 2-stage training)
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

### Train — Geometry-based (Phase II)
```bash
# Non-auto-regressive Graph Transformer (trained from scratch)
cd src/geometry_based/graph_transformer
python main_graph_transformer.py
python main_graph_transformer.py --epochs 300 --quick   # smoke test

# Fine-tuned pretrained Graphormer
cd src/geometry_based/finetuned_graph_transformer
python train.py
python train.py --quick --no-pretrained                 # offline / CI
```

### Test / Infer
```bash
# UNet
cd src/image_based/unet && python test.py

# Graph Transformer
cd src/geometry_based/graph_transformer && python evaluate.py

# Fine-tuned Graphormer
cd src/geometry_based/finetuned_graph_transformer && python test.py
```

### Run tests
```bash
cd src
python -m pytest testing/ -v
python -m pytest testing/test_image_based.py -v
python -m pytest testing/test_geometry_based.py -v
python -m pytest testing/test_text_based.py -v
```

### Run benchmark
```bash
cd src
python testing/benchmark.py                           # all approaches
python testing/benchmark.py --approaches geometry     # geometry only
python testing/benchmark.py --geometry-approach graph_transformer
```

## Code Architecture

### Configuration
- `src/config.py` — global config: `IMG_SHAPE`, `TRAIN_SIZE`/`TEST_SIZE`, `TWO_STAGE`, `COORD_CONV`, loss functions
- `src/image_based/unet/config.py` — re-exports src/config.py for unet's local imports

### Data pipeline (`src/utils/`)
- `prepare_data.py` — reads `.dat`/`.mid` → DrawSVG rasterization → PNG pairs + sequences.json
- `prepare_plots.py` — visualization: side-by-side profile vs. predicted midcurve
- `metric_utils.py` — Keras callbacks, best-epoch tracking, training history

### Path conventions (important for imports)
All `main_*.py` files under `image_based/` compute `project_root` as **3 levels up** from
the script (reaching `src/`), and also add `image_based/` to `sys.path` for cross-approach
imports (e.g. `denoiser` imports from `simpleencoderdecoder`).

Geometry-based scripts auto-resolve `src/data/raw` relative to `__file__`.

### Image-based approaches (`src/image_based/`)

| Directory | Architecture | Image size |
|---|---|---|
| `simpleencoderdecoder/` | 1 dense hidden layer (100 units) | 100×100 |
| `cnnencoderdecoder/` | 4-level Conv2D encoder + Conv2DTranspose decoder | 128×128 |
| `denseencoderdecoder/` | Fully connected (10,000 dims) | 100×100 |
| `denoiserencoderdecoder/` | Denoising autoencoder (uses simple as first stage) | 100×100 |
| `unet/` | 8-level UNet, auxiliary decoder, CoordConv, 2-stage WBCE | 256×256 |
| `pix2pix/` | Pix2Pix GAN with discriminator (Keras) | 256×256 |
| `img2img/` | Pix2Pix GAN (PyTorch) | 256×256 |

### Geometry-based approaches (`src/geometry_based/`)

| Directory | Description |
|---|---|
| `graph_transformer/` | Non-auto-regressive Graph Transformer trained from scratch. Input: polygon graph (nodes=corners, features=(x,y)). Output: midcurve coords + adjacency. Loss: Chamfer + BCE. |
| `finetuned_graph_transformer/` | Pretrained `clefourrier/graphormer-base-pcqm4mv2` (HuggingFace) fine-tuned in two phases: frozen head-only → joint fine-tuning. |
| `gnnencoderdecoder/` | Legacy stub — not implemented, kept for reference. |

### Data format
Raw data in `src/data/raw/`:
- `.dat` = profile polygon points (ASCII, one `x y` per line, closed polygon)
- `.mid` = midcurve polyline points (same format, open/branched)

Shapes: I, L, T, Plus (simple); and many complex shapes under `PhDdata/` subdirectory.

## Research Context

- **Phase I** limitation: raster approximation loses exact geometry; post-processing needed to extract clean polylines from bitmaps
- **Phase II** (`graph_transformer/`) is the current best approach — handles exact geometry and branching natively
- **Phase II-b** (`finetuned_graph_transformer/`) adds transfer learning on top of Phase II
- **Phase III** (`text_based/`) is planned — key challenge: branched midcurves can't be serialized as simple sequences
- `src/text_based/data/sequences.json` — JSON-format dataset for LLM/seq2seq experiments
