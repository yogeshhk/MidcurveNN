# Changelog

All notable changes to MidcurveNN are recorded here.

## [Unreleased]

### Added
- `src/pytest.ini` and `src/conftest.py` for correct cross-approach test discovery.
- `src/image_based/README.md` and `src/geometry_based/README.md` folder overviews.
- `CONTRIBUTING.md` with setup, test, and contribution instructions.
- `.github/workflows/ci.yml` lightweight CI pipeline (text-based tests, no GPU).
- `CHANGELOG.md` (this file).

### Fixed
- `GeometricMetrics.chamfer_distance` now converts inputs to `np.ndarray` before indexing, fixing a `TypeError` crash when called with Python lists.
- `test_27_hausdorff_metric_computable` now passes a proper `{"Points": [...]}` dict so the function exercises the actual Hausdorff computation rather than silently returning the error sentinel `1000.0`.
- `benchmark_text()` updated from a legacy `sequences.json` placeholder to a live CSV-data validation that reports dataset row counts.
- Test run commands corrected in `README.md` and `CLAUDE.md` to match actual file locations.

### Changed
- `environment.yml`: replaced macOS-specific `tensorflow-macos` / `tensorflow-metal` / `apple` channel with cross-platform `tensorflow` for Windows/Linux compatibility.

---

## Phase III — LLM / Text-Based (2024)

- Full QLoRA fine-tuning pipeline: `train.py`, `inference.py`, `evaluate.py`, `metrics.py`.
- BRep JSON data format: explicit `Points / Lines / Segments` topology to handle branched midcurves.
- 993-row CSV dataset (I, L, T, Plus shapes, 80/10/10 split), geometric augmentation (scale, rotate, translate, mirror).
- FastAPI model server with `/predict`, `/health`, `/validate` endpoints.
- Geometric metrics: Chamfer distance, Hausdorff distance, MAE, RMSE, topology score.
- CodeT5 and Ludwig fine-tuning notebooks (Colab/Kaggle).
- Few-shot prompting comparison across Qwen, Gemma, Mistral.

## Phase II — Geometry-Based (2023)

- Non-auto-regressive Graph Transformer trained from scratch (`graph_transformer/`).
  - Custom LaplacianPE + TransformerConv + TopKPooling architecture.
  - Chamfer loss + BCE adjacency loss.
- Fine-tuned pretrained Graphormer (`finetuned_graph_transformer/`).
  - Two-phase training: frozen backbone → joint fine-tuning.
- `MidcurveGraphDataset` with coordinate normalisation and geometric augmentation.

## Phase I — Image-Based (2019–2022)

- Seven encoder-decoder variants: simple, CNN, dense, denoising, UNet, Pix2Pix (Keras), Pix2Pix (PyTorch).
- Best performer: 8-level UNet with 2-stage weighted BCE, auxiliary decoder, CoordConv.
- DrawSVG rasterization pipeline with rotation/translation/mirror augmentation.
- Initial publication at GMP 2021.
