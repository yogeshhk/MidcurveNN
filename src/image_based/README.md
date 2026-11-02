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

```
image_based/
  run.py            one driver: prepare | train | eval
  prepare_data.py   raw .dat/.mid/.edges + splits.json -> data/dataset_v1.npz
  dataset.py        loads the npz, optional pose augmentation
  losses.py         soft target, weighted BCE, Dice, focal, plain BCE
  evaluate.py       F1 at 2 px, Chamfer, Hausdorff, topology check, results grid
  models/           skeleton, simple_ae, dense_ae, cnn_ae, denoiser_ae, unet, pix2pix
  tests/            test_image_track.py
  data/             dataset_v1.npz (small, generated)
  runs/             <model>__<split>__<tag>/ with metrics.json, grid.png, log.csv, args.json, best.pt
```

The folders `simpleencoderdecoder/`, `cnnencoderdecoder/`, `denseencoderdecoder/`,
`denoiserencoderdecoder/`, `unet/`, `pix2pix/`, `img2img/`, `kaggle/` and `testing/` are the legacy
implementation. They still work but their numbers are leaked. Moving them to `_legacy/` is a pending
decision (see `TODO.md`).

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
cd src
conda run -n genai python -m pytest image_based/tests/test_image_track.py -q
conda run -n genai python -m pytest image_based/testing/test_image_based.py -q   # legacy
```

## Caveats

- Only four base shapes (I, L, T, Plus); the `pose` split is interpolation, `loso` is the only
  generalisation probe and even it is thin with four shapes.
- A high pixel F1 can hide wrong topology; the topology check is reported next to it.
