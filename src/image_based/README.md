# Image track (Phase I): midcurve as image-to-image translation

Polygon outline in, midcurve bitmap out. A network learns the pixel mapping, then the output is
thresholded and skeletonised to a thin polyline. The raster approximation is the known limitation.

Live plan: `../proposal/06_EXECUTION_PLAN.md`. Results: `../proposal/RESULTS_image.md` (figures are
not copied here so they cannot go stale). Task list: `TODO.md`.

## Status

- New code, dataset and tests: done (`run.py` workflow below).
- Experiments: PARTIAL. See `RESULTS_image.md` for the rows that are actually measured.
- All legacy headline numbers (the old per-folder scripts) were measured under train/test leakage:
  augmented variants of the same four shapes were shuffled across splits. They show interpolation, not
  generalisation.
- An earlier UNet F1 of 0.998 used a leaky 3-channel input (outline, filled mask, distance transform;
  the distance-transform ridge is the midcurve) and a cut-down schedule. It is being re-measured with the
  1-channel outline input, the planned headline setting. Do not quote it.

## Layout

Reorganised on 2026-11-03 (plan: `../proposal/08_REORG_PLAN.md`). One folder per method; the same template is used by
`geometry_based/` and `text_based/`.

```
image_based/
  run.py            one driver: prepare | train | eval   (--model keeps the old names)
  pytest.ini conftest.py
  common/           prepare_data.py, dataset.py, losses.py, evaluate.py, blocks.py, collect_results.py
  data/             approach data (dataset_v1.npz, image-pairs/, unet-splits/, images-combo/)
  docs/             analysis_report.md
  tests/            test_image_track.py (contract tests), test_legacy_image_based.py (old cross-method suite)
  methods/
    __init__.py     REGISTRY: --model name -> module
    <method>/       README.md; OLD implementation at the top level (code, notebooks, weights, results, old tests)
      enhanced/     standard PyTorch version: model.py, README.md, notebook.ipynb, runs/<split>__<tag>/
```

| method folder | `--model` | old implementation (top level) | enhanced version |
|---|---|---|---|
| [simple_encoder_decoder](methods/simple_encoder_decoder/README.md) | simple_ae | Keras, notebooks, `kaggle/` | [enhanced](methods/simple_encoder_decoder/enhanced/README.md) |
| [dense_encoder_decoder](methods/dense_encoder_decoder/README.md) | dense_ae | Keras | [enhanced](methods/dense_encoder_decoder/enhanced/README.md) |
| [cnn_encoder_decoder](methods/cnn_encoder_decoder/README.md) | cnn_ae | Keras | [enhanced](methods/cnn_encoder_decoder/enhanced/README.md) |
| [denoiser_encoder_decoder](methods/denoiser_encoder_decoder/README.md) | denoiser_ae | Keras | [enhanced](methods/denoiser_encoder_decoder/enhanced/README.md) |
| [unet](methods/unet/README.md) | unet | Keras, 8-level, weights | [enhanced](methods/unet/enhanced/README.md) |
| [pix2pix](methods/pix2pix/README.md) | pix2pix | Keras GAN, `img2img/` (PyTorch variant) | [enhanced](methods/pix2pix/enhanced/README.md) |
| [skeleton](methods/skeleton/README.md) | skeleton | none (classical baseline) | `model.py` at the top |

The old implementations still work but their numbers were measured under leakage. Run folders live in
`methods/<method>/[enhanced/]runs/<split>__<tag>/`.

## Run

Environment is `genai` only. From `src/image_based`:

```
conda run -n genai python run.py prepare
conda run -n genai python run.py train --model unet --split pose --tag h1 --epochs 30 --steps 100
conda run -n genai python run.py eval  --model unet --split pose --tag h1 --tta
conda run -n genai python run.py train --model cnn_ae --split loso:Plus --tag h1
```

Models: skeleton, simple_ae, dense_ae, cnn_ae, denoiser_ae, unet, pix2pix.
Splits: `pose` (new poses of the same shapes), `default`, `loso:<Shape>` (leave one shape out).
Use `--in-ch 1` for the 1-channel outline input; the `--in-ch` and `--loss` options drive the ablations.
`--epochs`/`--steps` set the schedule; check `args.json` of a run for the exact values.

Run one image training at a time; it uses the GPU. Do not run the legacy `utils/prepare_data.py`
(it deletes `images-combo/` and `unet-splits/`).

## Results

See `../proposal/RESULTS_image.md` (single source of truth for the table).

## Tests

```
cd src/image_based
conda run -n genai python -m pytest -q                      # tests/ (contract + legacy cross-method suite)
cd .. && conda run -n genai python run_all_tests.py         # all three approaches, one process each
```

Method-local legacy suites (for example `methods/unet/test_unet.py`) are run one file per process; `run_all_tests.py`
lists them.

## Caveats

- Only four base shapes (I, L, T, Plus); the `pose` split is interpolation, `loso` is the only
  generalisation probe and even it is thin with four shapes.
- A high pixel F1 can hide wrong topology; the topology check is reported next to it.
