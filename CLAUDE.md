# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MidcurveNN** computes the midcurve (medial axis/skeleton) of 2D closed polygons using neural networks. It is a research project with three approach families:

- **Image-based (Phase I)**: Rasterize polygons to 100×100 or 256×256 bitmaps → encoder-decoder networks
- **Geometry-based (Phase III)**: Graph neural network approach — exact coordinates, handles branching natively
- **Text-based (Phase II)**: LLM/seq2seq approach using B-rep JSON text representations (implemented)

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
│   ├── data/                    # Shared generated image data (one copy, no duplication)
│   │   ├── image-pairs/         # PNG pairs (Profile+Midcurve) — used by simple/cnn/dense/denoiser
│   │   ├── unet-splits/         # UNet train/test split PNGs
│   │   │   ├── train/
│   │   │   └── test/
│   │   └── images-combo/        # Side-by-side combo JPGs — used by pix2pix and img2img
│   │       ├── train/
│   │       ├── val/
│   │       └── test/
│   ├── simpleencoderdecoder/    # 1 dense hidden layer (baseline)
│   ├── cnnencoderdecoder/       # 4-level Conv2D encoder-decoder
│   ├── denseencoderdecoder/     # Fully connected (flattened 10K dims)
│   ├── denoiserencoderdecoder/  # Denoising autoencoder variant
│   ├── unet/                    # 8-level UNet with 2-stage training (BEST)
│   ├── pix2pix/                 # Pix2Pix GAN (Keras)
│   ├── img2img/                 # Image-to-image (PyTorch)
│   └── kaggle/                  # Kaggle notebooks / dataset exports
│
├── geometry_based/              # Phase III — graph/geometric approaches
│   ├── data/                    # Graph datasets
│   ├── graph_transformer/       # Non-auto-regressive Graph Transformer (primary)
│   ├── finetuned_graph_transformer/  # Pretrained Graphormer fine-tuned on midcurve data
│   └── gnnencoderdecoder/       # Legacy GNN stub (reference only)
│
├── text_based/                  # Phase II — LLM/sequence approaches (implemented)
│   ├── data/
│   │   ├── sequences.json       # Legacy flat-coord dataset (from src/utils/prepare_data.py)
│   │   ├── brep/                # 4 base BRep JSON shapes (I, L, T, Plus)
│   │   ├── csvs/                # CSV train/test/val splits (993 rows, 80/10/10)
│   │   └── shapes2brep.csv      # Ludwig framework training data
│   ├── utils/                   # BRep data pipeline: config, prepare_data, create_brep_csvs, ...
│   ├── finetuning/              # QLoRA fine-tuning: train, inference, evaluate, metrics, server
│   │   └── results/             # evaluation_results.csv (populated by evaluate.py)
│   ├── codeT5/                  # CodeT5 fine-tuning notebooks (Gdrive + Kaggle)
│   │   └── results/             # evaluation_results_sample.csv (populated after training)
│   ├── ludwig/                  # Ludwig framework notebooks
│   └── prompt/                  # Few-shot prompting scripts + LLM comparison screenshots
│
├── image_based/testing/         # Phase I unit tests
│   └── test_image_based.py
├── geometry_based/testing/      # Phase III unit tests
│   └── test_geometry_based.py
├── text_based/testing/          # Phase II smoke tests
│   └── test_text_based.py
├── testing/                     # Cross-approach benchmark
│   └── benchmark.py
├── conftest.py                  # Pytest sys.path setup (auto-loaded by pytest)
└── pytest.ini                   # Test discovery config: maps `pytest` to all 3 test dirs
```

## Environment Setup

```bash
cd src
conda env create -f environment.yml
conda activate midcurvenn

# Extra dependency for finetuned_graph_transformer
pip install transformers>=4.35

# Extra dependencies for text_based/finetuning (QLoRA pipeline)
pip install peft>=0.7.0 trl>=0.7.0 bitsandbytes>=0.41.0 accelerate>=0.25.0 fastapi uvicorn pydantic
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
- PNG pairs → `src/image_based/data/image-pairs/` (shared by simple/cnn/dense/denoiser)
- UNet split PNGs → `src/image_based/data/unet-splits/train|test/`
- Pix2Pix combo JPGs → `src/image_based/data/images-combo/train|val|test/`
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

### Train — Geometry-based (Phase III)
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

### Train — Text-based / LLM (Phase II)
```bash
# Regenerate BRep CSV datasets from base shapes
cd src/text_based/utils
python create_brep_csvs.py

# Validate CSV data, then fine-tune with QLoRA
cd src/text_based/finetuning
python data_validator.py
python train.py
python evaluate.py --model_path Midcurve-Qwen-Coder-v1 --visualize

# Full pipeline in one command
python run_pipeline.py --full

# Serve predictions via FastAPI
python model_server.py --host 0.0.0.0 --port 8000
```

### Test / Infer
```bash
# UNet
cd src/image_based/unet && python test.py

# Graph Transformer
cd src/geometry_based/graph_transformer && python evaluate.py

# Fine-tuned Graphormer
cd src/geometry_based/finetuned_graph_transformer && python test.py

# LLM inference (after fine-tuning)
cd src/text_based/finetuning && python inference.py --single
```

### Run tests
```bash
cd src
python -m pytest                                              # all 3 suites (auto-discovered via pytest.ini)
python -m pytest image_based/testing/test_image_based.py -v  # Phase I
python -m pytest geometry_based/testing/test_geometry_based.py -v  # Phase III
python -m pytest text_based/testing/test_text_based.py -v    # Phase II
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
- `prepare_plots.py` — visualization utilities:
  - `save_results_grid_images(inputs, gts, preds, save_path, n=7)` — **3 rows × n cols** PNG (Row 0=Input, Row 1=GT, Row 2=Predicted); per-cell auto-scale so low-contrast predictions remain visible
  - `save_results_grid_geometry(profiles, gt_midcurves, pred_midcurves, ..., save_path)` — n×3 grid PNG for graph-based approach (samples as rows)
  - Each approach saves its grid to `<approach>/results/results_grid.png` after training/test
  - Result grids copied to `publications/Midcurve_LaTeX/images/` as `<approach>_results_grid.png`
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

## Known Gotchas

- **`src/utils/prepare_data.py` lazy imports**: TensorFlow and matplotlib are imported lazily (try/except at the top) so that geometry and text tests can import the module without those heavy deps installed. Do not move them to unconditional top-level imports — CI jobs will break.

- **`config` module name collision**: `src/config.py` and `src/text_based/utils/config.py` both register as `config` in `sys.modules`. When the full test suite runs, Phase I tests cache `src/config.py`; Phase II `create_brep_csvs` then picks up the wrong config. Test 24 (`test_24_create_brep_csvs_importable`) clears the stale cache entry before importing — do not remove that guard.

- **Image model `_build()` pattern**: All four image encoder-decoder classes (`simple`, `cnn`, `dense`, `denoiser`) build their Keras sub-models in `_build()` called from `__init__()`, not inside `train()`. This is required for `predict()` to work without training first (e.g. in tests). Do not inline model construction back into `train()`.

- **HuggingFace Graphormer is deprecated**: The `finetuned_graph_transformer` targets `clefourrier/graphormer-base-pcqm4mv2`. Newer `transformers` versions mark this deprecated and the `forward()` API has changed incompatibly. The two forward-pass tests gracefully `skipTest` on `IndexError/RuntimeError/TypeError` — this is intentional.

- **CI image-based job is import/data only**: `.github/workflows/ci.yml` runs the image tests with `-k "not model and not unet_import"` and only installs `numpy pillow pytest` — no TF or matplotlib. Keep visualisation and model tests behind the existing skip guards.

- **`unet/test.py` import ordering**: `unet/config.py` inserts `src/` at `sys.path[0]`, so `from utils.prepare_plots import save_results_grid_images` must be imported **before** `unet/` is inserted and before `from utils import get_coord_layers` runs. After the `prepare_plots` import, `sys.modules['utils']` must be evicted (`sys.modules.pop('utils', None)`) so that inserting `unet/` at position 0 and re-importing `utils` finds `unet/utils.py` rather than the cached `src/utils/` package. The fixed import block in `test.py` looks like:
  ```python
  from config import *                              # inserts src/ into sys.path
  from utils.prepare_plots import save_results_grid_images
  sys.modules.pop('utils', None); sys.modules.pop('utils.prepare_plots', None)
  sys.path.insert(0, _HERE)                        # unet/ before src/
  from utils import get_coord_layers               # finds unet/utils.py
  ```

- **Image model `models/` directories**: `cnn`, `dense`, and `denoiser` encoder-decoders save trained weights under `<approach>/models/`. The directory is created automatically via `os.makedirs(..., exist_ok=True)` in `__init__`. Model files use `.keras` extension (Keras 3 format).

- **Denoiser train() must call `process_images`**: `build_denoiser_encoderdecoder_model.py` `train()` must call `self.process_images()` on both X and Y before fitting, to reshape flat/2-D inputs to `(N, 100, 100, 1)`. Raw `midcurve_gray_objs` must be normalized to `[0, 1]` before being passed.

- **`finetuning/config_enhanced.py` and `metrics_enhanced.py`**: These are alias re-exports (`from config import Config` / `from metrics import GeometricMetrics`). They exist so older scripts that import `config_enhanced` / `metrics_enhanced` continue to work without change. Do not delete them.

- **`finetuning/evaluate.py` output path**: Default output is `results/evaluation_results.csv` (relative to the `finetuning/` directory). `os.makedirs` is called before saving to ensure the directory exists.

- **`unet/test.py` memory and performance**: `plt.close('all')` is called after each per-image save to prevent "Fail to allocate bitmap" crashes. The loop breaks after collecting `_GRID_N=7` samples so only 7 test images are processed instead of all 400+.

- **`unet/train.py` load path — no `model_from_json`**: Keras 3 removed `model_from_json`. The `load=True` code path in `train_stage1()` and `train_stage2()` now reconstructs the model by calling `unet_stage1()` / `unet_stage2()` (the same factory functions used during `init()`), then calls `load_weights()`. Do not reintroduce `model_from_json`.

- **`pix2pix` and `img2img` results grids**: Both `main_pix2pix.py` and `main_img2img_pytorch.py` now call `save_results_grid_images` after training. Pix2Pix loads test data via `data_loader.load_data(batch_size=7, is_testing=True)`; img2img converts PyTorch tensors (B, C, H, W) in [-1,1] to grayscale numpy arrays via `_tensor_to_gray_list()`. Results go to `<approach>/results/results_grid.png`.

## Research Context

- **Phase I** limitation: raster approximation loses exact geometry; post-processing needed to extract clean polylines from bitmaps
- **Phase III** (`graph_transformer/`) is the current best approach — handles exact geometry and branching natively
- **Phase III-b** (`finetuned_graph_transformer/`) adds transfer learning on top of Phase III
- **Phase II** (`text_based/`) is **implemented** — QLoRA fine-tuning pipeline (Qwen/Gemma/Mistral), CodeT5 and Ludwig notebooks, few-shot prompt scripts
- BRep JSON format solves the serialization challenge for branched midcurves via explicit `Lines`/`Segments` topology
- `text_based/data/brep/` — 4 base BRep JSON shapes; `text_based/data/csvs/` — 993-row train/test/val CSV splits
- `text_based/finetuning/` — full pipeline: QLoRA training, inference+repair, evaluation, FastAPI server, geometric metrics (Chamfer, Hausdorff)
