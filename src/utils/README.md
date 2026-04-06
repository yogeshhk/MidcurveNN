# utils — Shared Utilities

Utilities shared across all model experiments.

| File | Purpose |
|------|---------|
| `prepare_data.py` | **Canonical data loader.** Reads `.dat`/`.mid` files, rasterises via DrawSVG, generates augmented PNG pairs, and provides `get_training_data()` for all models. |
| `prepare_plots.py` | Visualisation: `plot_results()` for side-by-side profile/midcurve comparison, B-rep plotting, and line-comparison subplots. |
| `metric_utils.py` | Keras `MetricsHistory` callback, `print_best_metrics()`, and multi-model comparison plots. |
| `create_ds.py` | **Standalone alternative dataset generator** using OpenCV. Draws shapes (T, I, L, C, E, F) programmatically. Not integrated with the main pipeline. Has a hardcoded `BASE_DIR` path that must be updated before use. |

## Import convention

All model modules should import from:
- `utils.prepare_data` — for `get_training_data`, `read_input_image_pairs`, `generate_images`
- `utils.prepare_plots` — for `plot_results` and geometry visualisers
- `utils.metric_utils` — for `MetricsHistory`, `print_best_metrics`
