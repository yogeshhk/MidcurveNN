# Denoising encoder-decoder: enhanced version

Second-stage refiner: takes a noisy midcurve estimate plus the outline and the filled mask and cleans it.

This is the standard PyTorch version used by the image driver (`src/image_based/run.py`, `--model denoiser_ae`). The older
implementation of the same method is at the top level of `../` (see `../README.md`); its numbers were measured under
train/test leakage and are not comparable.

## Architecture

UNetLite refiner trained on corrupted ground truth; at evaluation it is chained after a stage-1 predictor (a trained model, or the non-learned skeleton baseline) with `--stage1` (enhanced).

Code: `model.py` (`build_model(cfg)`; shared blocks in `../../../common/blocks.py`).

## Commands

Run from `src/image_based`:

```
conda run -n genai python run.py train --model denoiser_ae --split pose --tag h1 --epochs 30 --steps 100
conda run -n genai python run.py eval  --model denoiser_ae --split pose --tag h1 --tta
```

Run folders land in `runs/<split>__<tag>/` here (metrics.json, grid.png, log.csv, args.json; `best.pt` is git-ignored).
`run.py eval` overwrites `metrics_eval*.json` in a run folder, not `metrics.json`.

## Results

Test block of each `metrics.json` (split `pose` = new poses of shapes seen in training; `loso-X` = held-out shape X).
The table is generated from the files; see `../../../../proposal/RESULTS_image.md` for the discussion and caveats.

| run (split__tag) | test F1@2px | chamfer (raw) | hausdorff (raw) | topology ok | n |
|---|---|---|---|---|---|
| [pose__h1](runs/pose__h1/metrics.json) | 0.997 | 0.160 | 0.74 | 0.90 | 256 |

## Status

Code done. Experiments partial; see `../../../TODO.md`. Tests: contract tests in `../../../tests/`.
