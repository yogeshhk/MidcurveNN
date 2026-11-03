# Classical Voronoi baseline

Non-learned rule: Voronoi-based midcurve of the polygon. It is a strong floor on clean rectilinear shapes; the learned model is compared against it.

There is no older implementation of this method, so model.py, runs/ and tests sit at this folder's top level and there is
no `enhanced/` folder.

## Implementation

SciPy Voronoi diagram plus filtering and the shared inside-polygon edge rule. Code: `model.py` (`classical_midcurve`, `build_model`, `make_predictor`).

## Commands

Run from `src/geometry_based`:

```
conda run -n genai python run.py baseline --model classical --split iid --tag t
```

`--model` name for this method: `classical`. Run folders land in `runs/<split>__<tag>/` here (metrics.json, grid.png, log.csv,
args.json; `best.pt` and `last.pt` are git-ignored). Console logs of earlier runs are in `runs/logs/`.

## Results

Generated from the `metrics.json` files (synthetic test block; leakage-free generator splits, not the legacy data).
Discussion and caveats: `../../../proposal/RESULTS_graph.md`.

| run (split__tag) | synthetic test n | k exact | degree-sequence match | edge F1 (mean) | Hausdorff <= 0.25 w | real 4 shapes all ok |
|---|---|---|---|---|---|---|
| [iid__t](runs/iid__t/metrics.json) | 100 | 0.790 | 0.790 | 0.877 | 0.980 | yes |
| [iid__t1](runs/iid__t1/metrics.json) | 1000 | 0.816 | 0.813 | 0.901 | 0.974 | yes |
| [ood_deg4__t1](runs/ood_deg4__t1/metrics.json) | 1000 | 0.763 | 0.751 | 0.922 | 0.915 | yes |

## Status

Code done; baseline runs recorded above. Tests: `../../tests/test_graph_track.py`.
