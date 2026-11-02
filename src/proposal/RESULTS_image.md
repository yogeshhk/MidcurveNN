## Image track: implementation and results (2026-11-02, leave-one-shape-out NOT finished)

Status: code, dataset, tests and all pose-split experiments are done. The leave-one-shape-out (loso)
runs, the TTA eval and the final test counts were NOT completed (session closed). Numbers below come from
`src/image_based/collect_results.py` reading every `runs/*/metrics.json` on 2026-11-02. Re-generate with:

```
cd src/image_based
conda run -n genai python collect_results.py
```

## What was built (all under `src/image_based/`, legacy folders untouched)

- `run.py` one driver: `prepare | train | eval` (`--in-ch 1|3`, `--loss`, `--no-aug`, `--tta`, `--skip-done`).
- `prepare_data.py` raw `.dat/.mid/.edges` + `splits.json` to `data/dataset_v1.npz` (1,408 samples, OpenCV rasteriser).
- `dataset.py`, `losses.py`, `evaluate.py` (pixel F1 at 2 px, Chamfer, Hausdorff, topology check, results grid), `collect_results.py`.
- `models/`: skeleton, simple_ae, dense_ae, cnn_ae, denoiser_ae, unet, pix2pix (GroupNorm only).
- `tests/test_image_track.py`; runs go to `runs/<model>__<split>__<tag>/`.

## Results: pose split, test part, 1-channel outline input unless noted

Schedule 30 epochs x 100 steps (tag `h1`) except where stated. Seconds/epoch measured on the 2 GB MX570 GPU
while other jobs were mostly absent (the `base` rows are the old shared-GPU, short-schedule runs).

| model | in_ch | schedule | sec/epoch | test F1@2px | chamfer (raw) | hausdorff (raw) | topology ok |
|---|---|---|---|---|---|---|---|
| skeleton (no learning) | 1 | n/a | n/a | 0.850 | 0.361 | 2.44 | 0.09 |
| simple_ae | 1 | 30 x 100 | 5.2 | 0.722 | 0.871 | 4.35 | 0.10 |
| dense_ae | 1 | 30 x 100 | 7.2 | 0.556 | 1.393 | 6.42 | 0.20 |
| denoiser_ae | 1 | 30 x 100 | 19.0 | 0.997 | 0.160 | 0.74 | 0.90 |
| cnn_ae | 1 | 30 x 100 | 18.0 | 0.999 | 0.142 | 0.64 | 0.99 |
| pix2pix | 1 | 30 x 100 | 25.1 | 0.999 | 0.147 | 0.68 | 0.96 |
| unet | 1 | 30 x 100 | 20.7 | 0.999 | 0.132 | 0.69 | 0.98 |

UNet ablations (pose split, 30 epochs): 3-channel input (`abl_in3`) F1 0.999, topology 0.99; plain BCE
(`abl_bce`) F1 0.999, chamfer 0.118, topology 0.80; no augmentation (`abl_noaug`, 30 x 64) F1 0.999, topology 0.98.
Old short runs (8 x 100, 3-channel, tag `base`): unet 0.998, cnn_ae 0.996, simple_ae 0.761.

Per-shape test F1 / topology ok for the 1-channel headline runs:

| run | I | L | T | Plus |
|---|---|---|---|---|
| unet h1 | 0.999 / 1.00 | 0.998 / 0.95 | 0.999 / 1.00 | 0.999 / 0.98 |
| cnn_ae h1 | 0.999 / 1.00 | 0.999 / 0.95 | 1.000 / 1.00 | 0.999 / 1.00 |
| pix2pix h1 | 0.999 / 1.00 | 0.998 / 0.86 | 0.999 / 1.00 | 0.999 / 0.98 |
| denoiser_ae h1 | 0.996 / 0.91 | 0.998 / 0.97 | 0.994 / 0.73 | 0.999 / 1.00 |
| dense_ae h1 | 0.711 / 0.44 | 0.410 / 0.03 | 0.488 / 0.05 | 0.614 / 0.27 |
| skeleton | 0.672 / 0.02 | 0.923 / 0.08 | 0.858 / 0.11 | 0.946 / 0.16 |

## What the numbers say

- The distance-transform channel is NOT what made the earlier 0.998 easy: the 1-channel UNet scores the same
  F1 (0.999) as the 3-channel one. With only four shapes the pose task is easy for any conv model.
- UNet, cnn_ae, pix2pix and denoiser are all at the ceiling (0.997-0.999 F1) on the pose split, so this split
  cannot rank them. Differences are only in topology (cnn_ae 0.99, unet 0.98, pix2pix 0.96, denoiser 0.90) and
  in plain-BCE UNet topology dropping to 0.80 (the Dice term helps topology).
- simple_ae and dense_ae are clearly worse than the no-learning skeleton baseline on F1 (0.72 and 0.56 against 0.85) and have very poor topology.
- The skeleton baseline has high F1 on L and Plus (0.92, 0.95) but fails on I (0.67); it scores topology 0.02-0.16 because of spurs.

## Caveats (honest)

- Only 4 shapes. The `pose` split tests new poses of the SAME shapes: this is interpolation, not shape generalisation.
- NOT measured: leave-one-shape-out for unet and cnn_ae (the only generalisation test; a `unet loso-I h1` run was at epoch 8 of 30 when the session closed), TTA, and the final test counts for the new and legacy image suites.
- Single seed everywhere; differences of 0.001 F1 are noise.
- The first `h1` runs in this table were run one at a time on the 2 GB GPU; do not read seconds/epoch as a model cost comparison across different batch/GPU states.

## Left to do

- Run the loso folds (`run.py train --model unet --split loso:Plus --tag h1 --skip-done`, same for I, L, T and for cnn_ae), then re-run `collect_results.py`.
- Run the image tests: `cd src; conda run -n genai python -m pytest image_based/tests/test_image_track.py -q` and the legacy `image_based/testing`.
- Optional [CONFIRM]: move legacy folders (`simpleencoderdecoder/` ... `img2img/`, `kaggle/`) to `image_based/_legacy/`.
- More shape families before any generalisation claim (Session 2 in `06_EXECUTION_PLAN.md`).
