# Graph track (Phase III): midcurve as node-set prediction

The model predicts the midcurve NODE SET (up to 12 query slots with an existence flag, trained with a
Hungarian set loss). Edges are not learned: they are derived by an inside-polygon minimum spanning
tree. No shapely, no PyTorch Geometric.

Live plan: `../proposal/06_EXECUTION_PLAN.md`. Results: `../proposal/RESULTS_graph.md` (figures are
not copied here). Task list: `TODO.md`.

## Status

- New code and tests: done.
- Experiments: run on a reduced budget; some criteria pass and one (P3) fails narrowly. See
  `RESULTS_graph.md` for the table and its caveats (single seed, 4 real test shapes, shared-CPU budget).
- A classical Voronoi baseline is included and is a strong floor on clean rectilinear shapes; the
  learned model has to be compared against it, not against zero.
- Legacy numbers and the old "adjacency not learned" finding come from `graph_transformer/` and were
  measured under train/test leakage on four shapes; they are not comparable with the new track.

## Layout

```
geometry_based/
  run.py            one driver: prepare | train | eval | baseline
  prepare_data.py   raw -> data/dataset_v1.json (4 gold graphs) + procedural shape generator
  geom.py           point-in-polygon, box unions, normalise, MST edges, snapping (no shapely)
  dataset.py        gold + synthetic samples
  losses.py         Hungarian set loss
  evaluate.py       node-count, degree-sequence, Chamfer, Hausdorff, edge F1, grid
  models/           classical (Voronoi baseline), set_transformer
  tests/            test_graph_track.py
  data/             dataset_v1.json, synthetic preview
  runs/             <model>__<split>__<tag>/ with metrics.json, grid.png, log.csv, args.json, best.pt
```

Legacy folders `graph_transformer/`, `finetuned_graph_transformer/`, `gnnencoderdecoder/` and
`testing/` are untouched. Retiring two of them to `_legacy/` is a pending decision (see `TODO.md`).

## Run

Environment is `genai` only. From `src/geometry_based`:

```
conda run -n genai python run.py prepare
conda run -n genai python run.py baseline --model classical --split iid --tag t1
conda run -n genai python run.py train --model set_transformer --split iid --tag e100 --epochs 100 --n-train 20000 --n-val 1000 --threads 2
```

Splits: `iid`, `ood_deg4` (train without degree-4 nodes), `ood_size`, and `loso_real` (negative control:
train on three real shapes, test on the held-out one; pass `--holdout I|L|T|Plus`). Add `--resume` to
continue a run from its `last.pt`. Graph jobs are CPU-only and small;
run one at a time and use `--threads 2` while an image job owns the machine.

## Results

See `../proposal/RESULTS_graph.md`.

## Tests

```
cd src/geometry_based
conda run -n genai python -m pytest tests -q
cd ..
conda run -n genai python -m pytest geometry_based/testing -q   # legacy
```

## Caveats

- Synthetic ground truth and the classical rule both assume thin, rectilinear, flat-capped shapes.
  Curved, noisy, non-orthogonal or holed profiles are out of scope so far.
- Real-shape evidence is four samples; every claim about them is weak statistically.
