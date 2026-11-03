# Set Transformer

Predicts the midcurve NODE SET: up to 12 query slots with an existence flag, trained with a Hungarian set loss. Edges are not learned; they are derived by an inside-polygon minimum spanning tree.

There is no older implementation of this method, so model.py, runs/ and tests sit at this folder's top level and there is
no `enhanced/` folder.

## Implementation

MidcurveSetNet (about 207k parameters at d=64, 3 encoder and 2 decoder layers). Code: `model.py` (`build_model`, `make_predictor`, `fit`, `load_best`); shared geometry in `../../common/`.

## Commands

Run from `src/geometry_based`:

```
conda run -n genai python run.py train --model set_transformer --split iid --tag t
```

`--model` name for this method: `set_transformer`. Run folders land in `runs/<split>__<tag>/` here (metrics.json, grid.png, log.csv,
args.json; `best.pt` and `last.pt` are git-ignored). Console logs of earlier runs are in `runs/logs/`.

## Results

Generated from the `metrics.json` files (synthetic test block; leakage-free generator splits, not the legacy data).
Discussion and caveats: `../../../proposal/RESULTS_graph.md`.

| run (split__tag) | synthetic test n | k exact | degree-sequence match | edge F1 (mean) | Hausdorff <= 0.25 w | real 4 shapes all ok |
|---|---|---|---|---|---|---|
| [iid__e100](runs/iid__e100/metrics.json) | 1000 | 0.905 | 0.904 | 0.934 | 0.981 | yes |
| [iid__e30](runs/iid__e30/metrics.json) | 1000 | 0.819 | 0.813 | 0.826 | 0.809 | yes |
| [iid__e80](runs/iid__e80/metrics.json) | 1000 | 0.895 | 0.891 | 0.919 | 0.947 | yes |
| iid__t1 | NOT MEASURED (no metrics.json) | | | | | |
| ood_deg4__e100 | NOT MEASURED (no metrics.json) | | | | | |
| [ood_deg4__e30](runs/ood_deg4__e30/metrics.json) | 1000 | 0.242 | 0.217 | 0.525 | 0.545 | yes |
| ood_deg4__e80 | NOT MEASURED (no metrics.json) | | | | | |

## Status

Code done. Experiments run on a reduced budget; see `../../../proposal/RESULTS_graph.md` (one seed, four real test shapes). Known open issue: about 10% of synthetic labels have a spurious collinear node (`common/prepare_data.py`); not fixed here, a separate decision. Tests: `../../tests/test_graph_track.py`.
