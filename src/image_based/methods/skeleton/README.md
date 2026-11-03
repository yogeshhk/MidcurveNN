# Skeleton (classical baseline)

Non-learned baseline: skeletonize(filled mask). No parameters, no training.

## Implementation

skimage `skeletonize` wrapped as an nn.Module so it goes through the same evaluation path.

Code: `model.py` (`build_model(cfg)`). Driver: `src/image_based/run.py --model skeleton`. There is no older implementation
of this method, so there is no `enhanced/` folder.

## Commands

Run from `src/image_based`:

```
conda run -n genai python run.py train --model skeleton --split pose --tag h1
```

Run folders land in `runs/<split>__<tag>/` here.

## Results

| run (split__tag) | test F1@2px | chamfer (raw) | hausdorff (raw) | topology ok | n |
|---|---|---|---|---|---|
| [pose__base](runs/pose__base/metrics.json) | 0.850 | 0.361 | 2.44 | 0.09 | 256 |
| [pose__h1](runs/pose__h1/metrics.json) | 0.850 | 0.361 | 2.44 | 0.09 | 256 |

Discussion and caveats: `../../../proposal/RESULTS_image.md`.

## Status

Code done; a reference baseline (no learning). Tests: `../../tests/test_image_track.py`.
