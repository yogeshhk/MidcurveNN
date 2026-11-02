## Image track: implementation and results (PARTIAL, experiments still running)

Status date 2026-11-01. The code, dataset and tests are complete. The experiment queue was still
running when this file was written (the GPU was shared with other jobs, 30 s/epoch became about 145
s/epoch, so the schedule was cut to 4-8 epochs of 100 steps). Only the rows listed in the table below are
measured; every other row is NOT yet measured. Re-generate the full table with the command at the end.

## What was built (all under `src/image_based/`, legacy folders untouched)

- `run.py` one driver: `prepare | train | eval`
- `prepare_data.py` raw `.dat/.mid/.edges` + `splits.json` to `data/dataset_v1.npz` (OpenCV rasteriser)
- `dataset.py` loads the one file, optional on-the-fly pose augmentation, 3 channels (outline, filled mask, distance transform)
- `evaluate.py` pixel F1/precision/recall at 2 px after threshold + skeletonise, Chamfer and Hausdorff in px and raw units, topology check, results grid PNG
- `losses.py` soft Gaussian target, pos-weighted BCE, Dice, focal option, plain BCE option
- `models/` `__init__.py` (REGISTRY), `_blocks.py`, `skeleton.py`, `simple_ae.py`, `dense_ae.py`, `cnn_ae.py`, `denoiser_ae.py`, `unet.py`, `pix2pix.py` (GroupNorm only)
- `tests/test_image_track.py` 25 tests, all pass (about 50 s CPU)
- `data/dataset_v1.npz` (1,408 samples: 4 shapes x (256 train + 32 val + 64 test) poses, 1.5 MB)
- `runs/<model>__<split>__<tag>/` outputs per run

## How to run (from `src/image_based`)

```
conda run -n genai python run.py prepare
conda run -n genai python run.py train --model unet --split pose --tag base --epochs 8 --steps 100
conda run -n genai python run.py eval  --model unet --split pose --tag base --tta
conda run -n genai python run.py train --model cnn_ae --split loso:Plus --tag base
conda run -n genai python run.py train --model unet --split pose --tag abl_in1 --in-ch 1
conda run -n genai python run.py train --model unet --split pose --tag abl_bce --loss bce
```
Models: skeleton simple_ae dense_ae cnn_ae denoiser_ae unet pix2pix. Splits: pose, default, loso:<Shape>.
Tests: `cd src; conda run -n genai python -m pytest image_based/tests/test_image_track.py -q`.

## Results measured so far (test part, F1 at 2 px, thr tuned on val)

| model | split | F1@2px | precision | recall | chamfer (raw) | hausdorff (raw) | sec/epoch |
|---|---|---|---|---|---|---|---|
| skeleton (no learning) | pose | 0.850 | 0.818 | 0.890 | 0.361 | 2.44 | n/a |
| unet (8 ep x 100 steps) | pose | 0.998 | 1.000 | 0.997 | 0.144 | 0.72 | about 145 (shared GPU; about 30 alone) |

Smoke runs (10 steps only, not results): unet 0.92, pix2pix 0.91, denoiser on skeleton 0.88, cnn_ae 0.19,
simple_ae 0.14, dense_ae 0.09.

NOT yet measured: simple_ae, dense_ae, cnn_ae, pix2pix full runs; unet with TTA; ablations (plain BCE,
1-channel input); leave-one-shape-out for unet and cnn_ae; denoiser. The queue is
`scratchpad/run_all.ps1` (log `run_all2.log`); finished runs appear in `runs/`.
Collect them with `scratchpad/table.py` (reads every `runs/*/metrics.json`).

## Comparison with the skeleton baseline

The skeleton of the filled mask already scores F1 0.85, with spurs at corners and ends visible in its grid.
The unet beats it clearly (0.998), mainly through precision (no spurs) and slightly higher recall.

## Caveats (honest)

- Only 4 shapes. The `pose` split is pose-level interpolation, not shape generalisation.
- The 3-channel input includes a distance transform whose ridge is the midcurve. The task is therefore
  close to trivial for a conv net (validation F1 was above 0.99 after 5 epochs). The 1-channel ablation
  is needed to know how much comes from the input representation; it has not run yet.
- The earlier unet run (40 epochs) was stopped at epoch 17 and discarded, so only the short run is reported.
- Epoch times are inflated by GPU sharing; do not quote them as model cost.
- Leave-one-shape-out: Plus held out has the only 4-way junction, expect it to be worst (not measured).

## Left to do

- Let the queue finish, regenerate the table, fill in the missing rows, add the ablation and loso tables.
- Optional [CONFIRM], not done: move legacy folders (`simpleencoderdecoder/` ... `img2img/`, `kaggle/`) to `image_based/_legacy/`.
- Add `runs/` to `.gitignore` (user manages git); update `image_based/README.md` after the layout is confirmed.
- More shape families (proposal 01 section 5.6) before any generalisation claim.
