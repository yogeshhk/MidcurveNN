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
  pytest.ini conftest.py
  common/           prepare_data.py (raw -> data/dataset_v1.json, generator), geom.py (point-in-polygon, MST edges,
                    snapping; no shapely), dataset.py, losses.py (Hungarian set loss), evaluate.py (node count,
                    degree sequence, Chamfer, Hausdorff, edge F1, grid)
  methods/          one folder per method (below); REGISTRY in methods/__init__.py
  tests/            test_graph_track.py (contract tests), test_legacy_geometry_based.py (old suite)
  data/             dataset_v1.json, synthetic preview
  docs/             analysis_report.md
```

Reorganised on 2026-11-03 (plan: `../proposal/08_REORG_PLAN.md`); `geom.py`, `dataset.py`, `losses.py`, `evaluate.py` and
`prepare_data.py` moved to `common/`. Run folders live in `methods/<method>/runs/<split>__<tag>/`.

| method folder | `--model` | state |
|---|---|---|
| [set_transformer](methods/set_transformer/README.md) | set_transformer | new; reduced-budget results |
| [classical_voronoi](methods/classical_voronoi/README.md) | classical | new; non-learned baseline |
| [equi_collapse](methods/equi_collapse/README.md) | equi_collapse | new (2026-11-03); equivariant dual-graph model; results in `../proposal/RESULTS_gdl.md` |
| [graph_transformer](methods/graph_transformer/README.md) | (script) | old implementation, frozen negative result |
| [finetuned_graph_transformer](methods/finetuned_graph_transformer/README.md) | (script) | old, retired |
| [gnn_encoder_decoder](methods/gnn_encoder_decoder/README.md) | (script) | old stub, retired |

The old implementations stay in place with their files, checkpoints and tests, unchanged apart from paths.

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

See `../proposal/RESULTS_graph.md` (set transformer, classical) and `../proposal/RESULTS_gdl.md` (EquiCollapse and its
rotation-augmented control). Neither is final: the label-generator bug (about 10% of synthetic samples carry a spurious
collinear node) is still open; new runs use `--clean-labels`.

## Tests

```
cd src/geometry_based
conda run -n genai python -m pytest -q        # tests/ (contract + legacy cross-method suite)
cd .. && conda run -n genai python run_all_tests.py   # all three approaches, one process each
```

## Caveats

- Synthetic ground truth and the classical rule both assume thin, rectilinear, flat-capped shapes.
  Curved, noisy, non-orthogonal or holed profiles are out of scope so far.
- Real-shape evidence is four samples; every claim about them is weak statistically.
