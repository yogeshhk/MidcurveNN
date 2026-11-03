# equi_collapse (EquiCollapse)

An E(2)-equivariant network on the dual graph of the polygon's interior Delaunay complex. For each cell it predicts an
invariant key probability and an equivariant position offset; the midcurve is obtained by contracting the dual graph on
the key cells (`cell_complex.decode`). Output nodes are indexed by input elements, not by learned query slots, so a
symmetry of the polygon permutes the outputs instead of pinning them (slot-collapse argument and full design:
`../../../proposal/07_GDL_RESEARCH_REPORT.md`). Pure PyTorch, no PyG, no shapely.

Results and caveats: `../../../proposal/RESULTS_gdl.md` (read the label caveat there before quoting any number).

## Files

- `cell_complex.py`: interior Delaunay complex, features, dual graph, `decode`.
- `model.py`: `EquiLayer`, `EquiCollapseNet`, training loop; registered as `--model equi_collapse`.
- `evaluate_extended.py`: loads existing `best.pt` files and compares classical, set transformer (e100 and rotation-augmented
  control) and EquiCollapse on published and corrected labels, rotations, test-time noise, degree-4 shapes and real shapes.
  Writes `runs/extended_metrics.json`.
- `tests/test_equi_collapse.py`: equivariance and decode tests.
- `notebook.ipynb`: loads `runs/extended_metrics.json` and prints the comparison table.
- `runs/<split>__<tag>/`: `metrics.json`, `grid.png`, `log.csv`, `args.json` committed; `best.pt` and `last.pt` ignored.

## Run

From `src/geometry_based`, env `genai`, one heavy job at a time:

```
conda run -n genai python run.py train --model equi_collapse --split iid --tag n8000_e80 --epochs 80 --n-train 8000 --n-val 1000 --clean-labels --lr 0.002 --batch-size 64 --resume --threads 4
conda run -n genai python methods/equi_collapse/evaluate_extended.py
```

`--clean-labels` removes spurious collinear nodes from train and val labels only. The generator bug in
`common/prepare_data.py` was fixed on 2026-11-03; every run in `runs/` predates the fix, so the flag is a no-op on new data. `--rot-aug` is for the set-transformer control, not for this model.

## Status

Trained at 500, 2000 and 8000 shapes (seed 0) and on `ood_deg4` and `ood_size`; seeds 1 and 2 are listed in `RESULTS_gdl.md`.
Evidence is synthetic hole-free rectilinear shapes plus four real ones; other geometry families are untested.
