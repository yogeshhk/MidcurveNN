# U-Net: enhanced version

Image-to-image U-Net from outline to midcurve mask.

This is the standard PyTorch version used by the image driver (`src/image_based/run.py`, `--model unet`). The older
implementation of the same method is at the top level of `../` (see `../README.md`); its numbers were measured under
train/test leakage and are not comparable.

## Architecture

UNetLite: 4 levels, GroupNorm, CoordConv, concat skips, bilinear upsampling, about 1.5M parameters (enhanced). The old Keras version is an 8-level U-Net with a 2-stage weighted BCE schedule.

Code: `model.py` (`build_model(cfg)`; shared blocks in `../../../common/blocks.py`).

## Commands

Run from `src/image_based`:

```
conda run -n genai python run.py train --model unet --split pose --tag h1 --epochs 30 --steps 100
conda run -n genai python run.py eval  --model unet --split pose --tag h1 --tta
```

Run folders land in `runs/<split>__<tag>/` here (metrics.json, grid.png, log.csv, args.json; `best.pt` is git-ignored).
`run.py eval` overwrites `metrics_eval*.json` in a run folder, not `metrics.json`.

## Results

Test block of each `metrics.json` (split `pose` = new poses of shapes seen in training; `loso-X` = held-out shape X).
The table is generated from the files; see `../../../../proposal/RESULTS_image.md` for the discussion and caveats.

| run (split__tag) | test F1@2px | chamfer (raw) | hausdorff (raw) | topology ok | n |
|---|---|---|---|---|---|
| loso-I__h1 | NOT MEASURED (no metrics.json) | | | | |
| [pose__abl_bce](runs/pose__abl_bce/metrics.json) | 0.999 | 0.118 | 0.60 | 0.80 | 256 |
| [pose__abl_in3](runs/pose__abl_in3/metrics.json) | 0.999 | 0.133 | 0.66 | 0.99 | 256 |
| [pose__abl_noaug](runs/pose__abl_noaug/metrics.json) | 0.999 | 0.139 | 0.67 | 0.98 | 256 |
| [pose__base](runs/pose__base/metrics.json) | 0.998 | 0.144 | 0.72 | 0.99 | 256 |
| [pose__h1](runs/pose__h1/metrics.json) | 0.999 | 0.132 | 0.69 | 0.98 | 256 |
| smoke__loso-I | smoke test run (not a result) | | | | |

## Status

Code done. Experiments partial; see `../../../TODO.md`. Tests: contract tests in `../../../tests/`.
