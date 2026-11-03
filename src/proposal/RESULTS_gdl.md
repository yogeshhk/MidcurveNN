# RESULTS_gdl.md: EquiCollapse (geometric deep learning for the graph-based midcurve)

Status: written 2026-11-03 from `metrics.json` files and `methods/equi_collapse/runs/extended_metrics.json`.

**All runs here used the generator BEFORE the 2026-11-03 fix** (spurious collinear nodes in about 10% of samples), with
`--clean-labels` on train and val labels. The generator is fixed now; these results were deliberately not re-run (user
decision) and are labelled as pre-fix. Seeds 1 and 2 were started and stopped before finishing, so there is one seed only.
Runs on the fixed generator (seeds, `ood_deg4`, `ood_size`, `loso_real`) are still to do.
Method background: `07_GDL_RESEARCH_REPORT.md`. Code: `src/geometry_based/methods/equi_collapse/`.

## What was compared

- `equi_collapse`: the new model (cell-complex message passing, outputs indexed by input elements).
- `set_transformer` control (tag `clrot_*`): the earlier model, retrained with the same cleaned training labels
  and continuous rotation augmentation (`--rot-aug`). This is the fair baseline for a rotation-equivariant model.
- `classical_voronoi`: the rule-based medial-axis baseline (no training).
- `set_transformer` e100: the earlier run with published labels and 90-degree turns only (reference).

All new runs: 80 epochs, `--clean-labels` (train and val labels only), 1000 validation and 1000 test shapes, seed 0,
CPU. `equi_collapse` uses `--lr 0.002 --batch-size 64`.

## Label caveat (read first)

About 10% of generated synthetic samples have a spurious collinear ground-truth node (generator bug, not fixed;
`common/prepare_data.py`). The standard `iid` test set keeps those labels, so no model can exceed about 0.90 on it
(EquiCollapse scores 0.904). The extended evaluation therefore reports `iid_published` and `iid_corrected` separately.
The 4 real shapes are unaffected.

## Table 1: standard test sets (published labels), correct graph within 0.25w (`ok_025w`)

| Model | iid n=8000 | ood_deg4 (test_in / test) | ood_size n=8000 |
|---|---|---|---|
| EquiCollapse | 0.904 | 0.897 / 0.877 | 0.836 |
| Set transformer control (clrot) | 0.810 | 0.809 / 0.716 | 0.293 |

Mean Hausdorff over wall width (lower is better), same runs: iid 0.006 vs 0.126; ood_deg4 test 0.031 vs 0.152;
ood_size 0.012 vs 0.756.

## Table 2: data efficiency (iid, published labels, `ok_025w`)

| Training shapes | EquiCollapse | Set transformer control |
|---|---|---|
| 500 | 0.901 | 0.299 |
| 2000 | 0.904 | 0.559 |
| 8000 | 0.904 | 0.810 |

EquiCollapse is already at the label ceiling with 500 shapes.

## Table 3: extended evaluation (`extended_metrics.json`; corrected labels unless stated; `ok_025w`)

| Test | Classical | ST e100 (published labels) | ST control n8000 | EquiCollapse n8000 |
|---|---|---|---|---|
| iid_published | 0.813 | 0.893 | 0.810 | 0.904 |
| iid_corrected | 0.862 | 0.920 | 0.896 | 1.000 |
| rot 5 deg | 0.880 | 0.370 | 0.907 | 1.000 |
| rot 15 deg | 0.880 | 0.007 | 0.880 | 1.000 |
| rot 30 deg | 0.880 | 0.000 | 0.890 | 1.000 |
| rot 45 deg | 0.880 | 0.000 | 0.877 | 1.000 |
| noise 0.01w | 0.293 | 0.000 | 0.000 | 0.683 |
| noise 0.02w | 0.200 | 0.000 | 0.000 | 0.510 |
| noise 0.05w | 0.073 | 0.000 | 0.000 | 0.217 |
| noise 0.1w | 0.003 | 0.000 | 0.000 | 0.083 |
| real4 (n=4) | 1.000 | 1.000 | 1.000 | 1.000 |
| real4 rotated 37 deg (n=4) | 1.000 | 0.000 | 1.000 | 1.000 |
| deg-4-only shapes | 0.841 | 0.852 | 0.939 | 1.000 |

Degree-4-only shapes, models trained WITHOUT any degree-4 shape (`ood_deg4` runs): ST control 0.798, EquiCollapse 1.000.
Noise: walls are subdivided up to 40 vertices and each vertex jittered by s times the wall width; at test time only,
no model was trained on noisy shapes.

## What this does and does not show

- On this synthetic family EquiCollapse matches the labels exactly (1.000 on corrected labels) at every rotation, with
  500 training shapes, and on a degree it never saw in training. The control does not; it also shows the data hunger the
  equivariant design was meant to remove.
- Caution: the family is hole-free rectilinear trees, where the classical rule itself reaches 0.86 and a spanning tree
  recovers every edge given the true nodes. A score of 1.000 here says the model learned this family's construction; it is
  not evidence of generalisation to other geometry families (curved, holes, thick shapes), which are untested (Session 2).
- Noise robustness is limited for every method. EquiCollapse is best (0.68 at 0.01w against 0.29 classical and 0 for the
  set transformers) but still degrades quickly; this is test-time noise only.
- ood_size is the weakest EquiCollapse result (0.836); failures are shapes larger than the training range.
- The real-shape test has 4 shapes, so it carries almost no statistical weight.
- Single seed (0) for all numbers above. Differences against the control are large, but there is no variance estimate yet.

## Seeds

Not run. The queue was stopped (about epoch 16 of 80 on the first seed-1 job) when the generator was fixed, so that
seeds would not be trained on mixed data. There is no variance estimate: every number above is seed 0.
