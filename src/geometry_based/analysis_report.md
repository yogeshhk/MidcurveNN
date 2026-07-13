# Phase III (geometry_based) - Code Analysis Report

Date: 2026-07-03
Scope: `src/geometry_based/` (graph_transformer, finetuned_graph_transformer,
gnnencoderdecoder, testing) plus shared dependencies it consumes
(`src/data/raw`, `src/utils/prepare_plots.py::save_results_grid_geometry`,
geometry parts of `src/benchmark.py`).

Intentional gotchas documented in CLAUDE.md (HuggingFace Graphormer
deprecation with skipTest guards, path auto-resolution, lazy imports) are NOT
reported as bugs here.

---

## 1. Overview

Phase III predicts midcurves directly in coordinate space. Two implemented
approaches share one dataset pipeline:

- Dataset (`graph_transformer/graph_dataset.py`): reads `.dat` (closed
  profile polygon) and `.mid` (midcurve polyline) pairs from `src/data/raw`,
  builds PyG `Data` objects. Profile: ring adjacency over N_p corner nodes,
  node features = normalized (x, y), edge features = segment length.
  Midcurve: consecutive listed points chained into edges; coordinates
  normalized with the PROFILE's centre/max-abs scale (correct - keeps both in
  one frame). Augmentation: 11 rotations (30 deg steps), 4 uniform scales,
  16 translations, 2 mirrors - applied identically to profile and midcurve
  (consistent).

- graph_transformer (primary): LaplacianPE -> 3x TransformerConv (4 heads,
  hidden 64, edge_dim 1, residual + LayerNorm + GELU) -> TopKPooling
  (ratio 0.6) -> non-autoregressive decoder: per-node MLP for (x, y) plus
  pairwise concat MLP for a k x k adjacency logit matrix (symmetrized).
  Loss = 1.0 * bidirectional squared Chamfer + 0.5 * adjacency BCE with
  pos_weight. Inference: sigmoid, zero diagonal, threshold 0.5,
  `dense_to_sparse`. Training: AdamW + cosine schedule, grad clip 1.0,
  random 75/15/10 split of the augmented dataset, best-val checkpointing.

- finetuned_graph_transformer (Phase III-b): HF Graphormer backbone
  (deprecated upstream; forward-pass tests skip gracefully by design). Coords
  are binned to 256 x 256 integer tokens; CLS embedding feeds two dense heads
  that emit a fixed (max_nodes, 2) coordinate block and a
  (max_nodes, max_nodes) adjacency block. Two-phase training: frozen backbone
  then joint fine-tuning at lr/10.

- Evaluation: per-shape squared Chamfer (normalized space) and adjacency BCE
  on the 4 original shapes; three-panel plots; `results/metrics.csv`;
  summary grid via shared `save_results_grid_geometry` (n rows x 3 cols,
  correct and straightforward). `benchmark.py` reloads checkpoints and
  reports mean Chamfer.

Current quality (from `graph_transformer/results/metrics.csv`): Chamfer
0.11-0.62 (normalized-squared units) and adjacency BCE ~1.1-1.2 (near
chance), i.e. node positions are roughly learned for T/Plus but topology is
not learned at all. The bugs below explain most of this.

---

## 2. Per-Approach Analysis

### 2.1 graph_transformer (primary)

Files: `graph_dataset.py`, `graph_transformer.py`, `train.py`,
`main_graph_transformer.py`, `evaluate.py`, `prepare_plots.py`,
`test_graph_transformer.py`.

Strengths:
- Clean separation of dataset / model / training / evaluation / plotting.
- Profile-frame normalization applied consistently to midcurve targets, with
  centre/scale stored per sample for denormalization.
- Augmentation transforms applied identically to profile and midcurve
  (rotation/scale/translation/mirror consistency is correct).
- Sensible optimizer setup (AdamW, cosine LR, grad clipping), CSV logging,
  best-val checkpointing.

Weaknesses (detailed in Bugs): batched loss mixes graphs; `mid_edge_index`
is mis-offset by PyG collation; adjacency supervision has no
predicted-to-GT node correspondence; TopK pooling fixes the output node
count to ceil(0.6 * N_p) regardless of the true midcurve size; the ring
graph plus only 3 message-passing hops means distant profile nodes never
exchange information; train/val/test split leaks heavily.

### 2.2 finetuned_graph_transformer

Files: `model.py`, `train.py`, `test.py`,
`test_finetuned_graph_transformer.py`.

The HF Graphormer API incompatibility itself is a documented, intentional
gotcha (tests skip on IndexError/RuntimeError/TypeError). Independent of
that, the module's own logic has real defects: the coordinate binning clamps
to [0, 1] although inputs live in [-1, 1] (half the plane collapses to bin
0); the batched loss broadcasts one (wrongly indexed) ground-truth adjacency
to every graph in the batch; Chamfer is computed across the flattened batch;
the LR scheduler never manages the backbone parameter group added at
unfreeze time. Design-wise, predicting all node coordinates and the full
adjacency from a single CLS embedding via dense heads discards per-node
information that `last_hidden_state[:, 1:, :]` already provides.

### 2.3 gnnencoderdecoder (status only)

Legacy stub, explicitly non-functional. `main_gnn_encoderdecoder.py` raises
NotImplementedError; `build_gnn_encoderdecoder_model.py` is documented as
non-compiling (bad DGL API calls, undefined variable). Tests only assert the
placeholder files exist. Status matches README - nothing to fix; candidate
for eventual removal once graph_transformer is mature.

### 2.4 testing/

`testing/test_geometry_based.py` and the two per-approach test files are
import/shape/loss smoke tests with proper skip guards for missing
torch_geometric/transformers. They pass even with the loss bugs present
because they only check "loss is finite and positive" - they cannot catch
the correctness issues below. No bugs in the tests themselves.

---

## 3. Bugs

Severity: High = corrupts training signal or invalidates results;
Medium = degrades quality or misleads; Low = cosmetic/doc/dead code.

### B1 [High] Batched loss mixes all graphs in a batch into one problem

- `graph_transformer/graph_transformer.py:307-312` (`midcurve_loss`),
  called from `train.py:74-81` and `main_graph_transformer.py:96-100` with
  batched PyG data.
- `chamfer_loss(coords_pred, data.y)` compares the concatenation of ALL
  pooled nodes in the batch against the concatenation of ALL ground-truth
  midcurve nodes in the batch. A predicted point can be "explained" by the
  nearest GT point of a DIFFERENT sample. With batch_size 16 and all shapes
  normalized around the origin, this systematically underestimates loss and
  blurs gradients toward the dataset-average midcurve.
- The decoder (`graph_transformer.py:162-168`) builds pairwise adjacency
  logits over the whole batch's pooled nodes (k_total x k_total) with no
  masking by `batch_out`, so cross-graph node pairs receive supervised
  logits. Cost is also O(k_total^2).
- Fix: compute both loss terms per graph using the `batch` vector
  (`batch_out` for predictions, a `y_batch` vector for targets), then
  average.

### B2 [High] `mid_edge_index` is wrongly re-indexed by PyG batching

- `graph_transformer/graph_dataset.py:138-150` uses a plain `Data` object.
  PyG's default `Data.__inc__` increments every attribute whose key contains
  "index" by `self.num_nodes`, which is the PROFILE node count (from `x`).
  But `y` (midcurve nodes) is concatenated with midcurve node counts. After
  `Batch.from_data_list`, `mid_edge_index` indices for graph i are offset by
  the cumulative profile sizes, while row/col positions in the GT adjacency
  built with `to_dense_adj(mid_edge_index, max_num_nodes=y.size(0))`
  (`graph_transformer.py:287-288`) assume cumulative midcurve sizes. The GT
  adjacency is garbage for every graph after the first in each batch.
- Fix: subclass `Data` and override `__inc__` so `mid_edge_index` increments
  by `self.y.size(0)` - or better, keep losses strictly per-graph (B1) and
  index locally.

### B3 [High] Ground-truth topology is wrong for branched midcurves

- `graph_transformer/graph_dataset.py:51-75` (`_build_polyline_edges`)
  assumes branch points appear multiple times in the `.mid` file and chains
  consecutive points. The actual data files list each point once:
  - `src/data/raw/Plus.mid` = (12.5,0), (12.5,22.5), (12.5,45), (0,22.5),
    (25,22.5). Chaining yields edge 2-3 = (12.5,45)-(0,22.5), a DIAGONAL
    that is not part of the midcurve, and the centre node never gets its
    degree-4 branch connectivity.
  - `src/data/raw/T.mid` = (12.5,0), (12.5,22.5), (25,22.5), (0,22.5).
    Edge 2-3 spans (25,22.5)-(0,22.5) across the centre instead of two
    edges meeting at node 1; node 1 has degree 2 instead of 3.
- Consequence: the adjacency head is trained on wrong targets for exactly
  the branched shapes that motivate Phase III, and "topology" metrics are
  computed against a wrong reference.
- Fix: derive GT edges structurally, e.g. star topology from the branch
  point (any point lying on the segment between two others splits that
  segment), or store `.mid` files as explicit edge lists / BRep JSON like
  Phase II does.

### B4 [High] No correspondence between predicted and GT nodes in the adjacency BCE

- `graph_transformer/graph_transformer.py:274-304` (`adjacency_bce_loss`)
  crops both matrices to `min(k, num_nodes)` and compares elementwise.
  Predicted node order is whatever TopKPooling's learned scores produce (a
  subset of profile-node order); GT node order is the `.mid` file listing
  order. Entry (i, j) of the prediction and entry (i, j) of the target refer
  to unrelated node pairs. The adjacency head can therefore only learn edge
  density, not structure - consistent with the near-chance adj_bce
  ~1.13-1.18 in `results/metrics.csv` and dots-only predicted graphs.
- Fix: match predicted coords to GT coords first (Hungarian /
  `scipy.optimize.linear_sum_assignment` on pairwise distances), permute the
  GT adjacency into matched order, and supervise only matched slots (see R1).

### B5 [High] Train/val/test split leaks; several augmentations are no-ops after normalization

- Split: `train.py:42-57` and `main_graph_transformer.py:54-61` randomly
  split the AUGMENTED dataset, so rotated/mirrored variants of the same
  shape sit in both train and test.
- Worse: per-sample normalization (`graph_dataset.py:125-128`: subtract
  mean, divide by max-abs) exactly cancels the translation (16 variants) and
  uniform-scale (4 variants) augmentations (`graph_dataset.py:194-204`).
  Each shape therefore contributes ~21 byte-identical normalized samples;
  the "test set" contains exact duplicates of training samples. Validation
  loss is close to training loss by construction and model selection is
  meaningless.
- Additionally, final evaluation (`main_graph_transformer.py:145-201`,
  `evaluate.py:222`) runs on the 4 original shapes, all of which were in
  training. All reported numbers are training-set numbers.
- Fix: deduplicate after normalization; split by BASE SHAPE
  (leave-one-shape-out or grouped split on the label prefix); replace
  translate/scale augmentations with ones that survive normalization
  (vertex jitter, anisotropic scaling, edge subdivision/resampling,
  arbitrary-angle rotation).

### B6 [High] Graphormer input binning destroys half the coordinate range

- `finetuned_graph_transformer/model.py:97`:
  `x_bin = (x_dense.clamp(0, 1) * (BINS - 1)).long()` - but inputs are
  normalized to approximately [-1, 1] by the shared dataset. Every negative
  coordinate collapses to bin 0; roughly half of each shape becomes
  indistinguishable before it reaches the backbone. (This is the project's
  own preprocessing, not the documented HF API gotcha.)
- Fix: map [-1, 1] -> [0, 1] first: `((x_dense + 1) / 2).clamp(0, 1)`.

### B7 [High] `finetuned_loss` broadcasts one wrong adjacency to the whole batch and flattens Chamfer across the batch

- `finetuned_graph_transformer/model.py:213-222`:
  - `chamfer_loss(coords_pred.view(-1, 2), coords_gt)` mixes all B *
    max_nodes predictions with all GT points of the batch (same defect as
    B1).
  - `ei = mid_edge_index.clamp(max=max_n - 1); adj_gt[:, ei[0], ei[1]] = 1`
    uses batch-global (and, per B2, mis-offset) indices, clamps anything
    >= 32 onto node 31 (creating spurious positive edges on slot 31), and
    assigns the SAME target adjacency to every graph in the batch.
- Fix: iterate per graph (or vectorize with masks); build each graph's GT
  adjacency from its local edge list; never clamp indices into range.

### B8 [Medium] LaplacianPE is invalid on batched graphs and unstable

- `graph_transformer/graph_transformer.py:57-81`: the PE is computed on the
  whole batch's block-diagonal Laplacian. A batch of B disconnected graphs
  has B zero eigenvalues; the code skips only ONE "constant" eigenvector
  (`eigvecs[:, 1:k+1]`), so for B > 1 the selected columns are mostly
  component-indicator vectors, not positional information. Eigenvector sign
  and ordering are also arbitrary between samples (no sign
  canonicalization), so the same shape can receive different PEs across
  epochs/batches. Also a full dense eigh runs on every forward pass.
- Fix: precompute PE per graph in the dataset with sign canonicalization
  (e.g. force first nonzero entry positive), or switch to random-walk PE
  (RWPE), which is sign-invariant and cheap.

### B9 [Medium] Output node count is hard-wired to the profile size

- `graph_transformer/graph_transformer.py:201` (TopKPooling ratio 0.6):
  k = ceil(0.6 * N_p) never equals the midcurve node count (I: 3 predicted
  vs 2 GT; Plus: 8 vs 5; see metrics.csv `n_pred_nodes` vs `n_gt_nodes`).
  Surplus nodes are only suppressed indirectly by zero-padded GT adjacency
  (which is itself broken per B4). There is no mechanism to emit fewer or
  more nodes than the ratio dictates.
- Fix: fixed max_nodes slots + per-node existence logit (DETR-style), see
  R2.

### B10 [Medium] Receptive field of the encoder cannot cover the polygon

- The profile graph is a ring; `TransformerConv` attends only over graph
  neighbours, so with `num_layers=3` information travels at most 3 hops.
  For Plus (12 profile nodes) opposite-side nodes - exactly the pairs whose
  mid-point is the midcurve - never exchange information.
  (`graph_transformer.py:100-120`, default `num_layers=3` at :193.)
- Fix: add a virtual global node, use full attention (treat the polygon as
  a fully-connected graph with ring encoded in edge features / PE), or
  increase depth to >= N_p / 2.

### B11 [Medium] Backbone param group added after scheduler creation is never scheduled

- `finetuned_graph_transformer/train.py:88-89` creates `CosineAnnealingLR`
  over the head-only optimizer; `train.py:105-109` adds the backbone group
  at unfreeze. The scheduler's `base_lrs` were captured at construction, so
  the new group's LR is not annealed (and on some PyTorch versions triggers
  errors about missing `initial_lr`).
- Fix: create the optimizer with both groups up front (backbone lr = 0 or
  requires_grad gating), or rebuild the scheduler at unfreeze.

### B12 [Medium] `benchmark.py` cannot run the finetuned approach standalone and hardcodes graph_transformer hyperparameters

- `src/benchmark.py:162-166`: for
  `--geometry-approach finetuned_graph_transformer`, only
  `geometry_based/finetuned_graph_transformer` is inserted into sys.path
  before `from graph_dataset import MidcurveGraphDataset` - that module
  lives in `graph_transformer/`, so a standalone run fails and is silently
  reported as "SKIP - dataset load failed". It only works when the
  graph_transformer benchmark ran first in the same process.
- `src/benchmark.py:174-175` rebuilds the model with hardcoded
  hidden=64/ratio=0.6/... instead of `ckpt['args']` (unlike
  `graph_transformer/evaluate.py:41-55`, which does it correctly). A
  checkpoint trained with non-default sizes fails to load and is skipped.

### B13 [Low] Squared distances reported as "Chamfer distance"

- `graph_transformer/graph_transformer.py:264-271` averages SQUARED
  nearest-neighbour distances but the value is logged/printed everywhere as
  "Chamfer" (`evaluate.py:87-96`, `benchmark.py:196`), and it is computed in
  normalized space while other phases report metrics in original units.
  Fine as a training loss; misleading as a benchmark metric.

### B14 [Low] Dead code / stale docs

- `graph_transformer/graph_dataset.py:43-44`: unused `src`/`dst` in
  `_build_polygon_edges` (the `_ud` variants are the ones returned).
- `graph_transformer/train.py:13-14`: docstring advertises a `--loo` flag
  that does not exist.
- `graph_transformer/graph_transformer.py:239-249`: `predict_graph`
  docstring claims numpy arrays are returned; tensors are returned.
- `finetuned_graph_transformer/train.py:71-74`: `idx[:n_test]` is reserved
  but a test set is never constructed or evaluated.

### B15 [Low] PhD shape data is silently ignored

- `graph_transformer/graph_dataset.py:232-236` uses non-recursive
  `os.listdir`; `src/data/raw/PhDdata/` (43 `.dat` files) and
  `src/data/raw/PhDShapes/` are never loaded. The model trains on 4 base
  shapes only. (Listed as Low because it may be intentional scoping, but it
  is the single cheapest source of more real data - see R4.)

---

## 4. Accuracy Improvement Recommendations (prioritized)

R1-R4 are expected to dominate; the rest are refinements.

### R1. Fix the supervision signal first (bugs B1-B5, B6-B7)

No architecture change will help while the loss compares wrong pairs.
Concretely: per-graph Chamfer and adjacency terms using batch masks; correct
`__inc__` (or local indexing) for `mid_edge_index`; structural GT edges for
T/Plus; grouped-by-shape splits with deduplication. This alone should turn
the adjacency BCE from ~1.15 (chance) into a learnable signal.

### R2. Set-prediction decoding with Hungarian matching (replaces B4/B9 band-aids)

Adopt the DETR recipe, which fits this problem exactly:
- Decoder: `max_nodes` learned query vectors cross-attending to encoder
  node embeddings (replace TopKPooling, which discards edges and ties k to
  N_p).
- Heads per query: (x, y) coordinates + existence probability; pairwise MLP
  over query embeddings for adjacency.
- Loss: Hungarian match queries to GT nodes on L2 coordinate cost
  (`scipy.optimize.linear_sum_assignment`); then (a) L1/L2 coordinate loss
  on matched pairs (exact correspondence beats Chamfer once matched),
  (b) BCE on existence (matched = 1, unmatched = 0), (c) BCE on the
  GT-permuted adjacency restricted to matched slots. Keep a small symmetric
  Chamfer term as a warm-up/regularizer.
This resolves variable-length output, node correspondence, and surplus-node
suppression in one consistent framework.

### R3. Give the encoder global context

Ring-graph message passing with 3 layers cannot relate opposite polygon
walls (B10). Options in increasing effort: (a) add a virtual node connected
to all profile nodes; (b) run full (dense) self-attention over all profile
nodes with the ring encoded via RWPE/LapPE and edge-length features; (c)
deepen to 6-8 layers with hidden 128-256 (the current model is ~100K params;
there is ample headroom on this data). Midcurve points are midpoints of
opposing wall pairs - the architecture must be able to form those pairs.

### R4. More and harder data

- Load `PhDdata/` recursively (43 real shapes) after verifying their `.mid`
  topology (B3 applies there too).
- Add a synthetic generator: random rectilinear/rounded polygons with
  known medial axes, variable vertex counts.
- Augmentations that survive normalization: arbitrary-angle rotation
  (already effective), anisotropic scaling (changes midcurve non-trivially -
  verify GT accordingly), vertex jitter (small noise on profile only,
  midcurve fixed - teaches robustness), and edge subdivision (insert
  collinear vertices so N_p varies without changing geometry - crucial so
  the model does not memorize "node count -> shape").
- Curriculum: I/L (unbranched) first, then T/Plus, then PhD/synthetic.

### R5. Loss shaping

- Use true (sqrt) Chamfer or Huber on distances; asymmetric weighting with
  pred->GT weighted higher than GT->pred to punish stray predicted points.
- After matching (R2): edge-length and edge-direction consistency loss on
  predicted vs GT edges; degree loss (predicted row-sums of sigmoid(adj)
  vs GT degrees) - directly targets branch points.
- Rebalance lambda_adj upward once adjacency targets are correct; monitor
  edge F1, not BCE.

### R6. Positional encodings done right

Precompute per-graph, sign-canonicalized LapPE in the dataset, or replace
with RWPE (k random-walk return probabilities) which is deterministic and
batch-safe; additionally feed simple geometric node features beyond (x, y):
interior angle at the vertex, adjacent edge lengths, and normalized
arc-length position along the polygon boundary. These are nearly free and
highly informative for medial-axis reasoning.

### R7. Post-processing for clean polylines

At inference: (a) merge predicted nodes closer than epsilon (in normalized
units); (b) drop nodes with existence < tau or degree 0; (c) extract a
spanning structure - maximum spanning tree over sigmoid(adj) weights, then
prune weak leaves - guaranteeing a connected, cycle-free midcurve;
(d) optionally snap each node to the local mid-point of the two nearest
opposing profile edges (a cheap geometric refinement that uses the profile
itself). Report metrics before and after post-processing.

### R8. Honest and richer evaluation

- Evaluate ONLY on held-out shapes (leave-one-shape-out over the 4 base
  shapes; later, held-out PhD shapes).
- Metrics: true Chamfer and Hausdorff in original units (denormalized),
  edge precision/recall/F1 after Hungarian matching, node-count error,
  branch-point detection rate, connectivity (single connected component
  yes/no). Mirror Phase II's metric suite so `benchmark.py` comparisons are
  apples-to-apples.
- Fix B12 so the benchmark actually exercises both approaches standalone.

### R9. finetuned_graph_transformer: fix or retire

If kept: fix B6/B7/B11, use per-node embeddings
(`last_hidden_state[:, 1:, :]`) instead of CLS-only heads, and feed real
shortest-path distances as `spatial_pos` (adjacency 0/1 collides with
Graphormer's padding semantics, `model.py:104`). Given that HF has
deprecated Graphormer and the forward API drifts (documented gotcha), the
pragmatic call is to freeze this directory as an experiment record and put
the transfer-learning effort into pretraining the from-scratch
graph_transformer on synthetic medial-axis data instead.

---

## 5. Summary Table

| Item | Where | Severity / Priority |
|---|---|---|
| B1 Batched loss mixes graphs (Chamfer + adjacency) | graph_transformer.py:307-312, :162-168 | High |
| B2 mid_edge_index mis-offset by PyG collation | graph_dataset.py:138-150 + graph_transformer.py:287 | High |
| B3 Wrong GT topology for branched shapes (T, Plus) | graph_dataset.py:51-75 + data/raw/*.mid | High |
| B4 No pred-GT node correspondence in adjacency BCE | graph_transformer.py:274-304 | High |
| B5 Split leakage; scale/translate augmentations are no-ops | train.py:42-57, graph_dataset.py:125-128,194-204 | High |
| B6 Graphormer coord binning clamps [-1,1] to [0,1] | finetuned .../model.py:97 | High |
| B7 finetuned_loss: broadcast adjacency + flat-batch Chamfer | finetuned .../model.py:213-222 | High |
| B8 LaplacianPE invalid on batches, sign-unstable | graph_transformer.py:57-81 | Medium |
| B9 Output node count fixed at ceil(0.6*N_p) | graph_transformer.py:201 | Medium |
| B10 3-hop ring receptive field too small | graph_transformer.py:100-120 | Medium |
| B11 Unfrozen backbone group not scheduled | finetuned .../train.py:88-109 | Medium |
| B12 benchmark.py finetuned import path + hardcoded hparams | benchmark.py:162-175 | Medium |
| B13 Squared Chamfer reported as Chamfer, normalized units | graph_transformer.py:264-271 | Low |
| B14 Dead code / stale docstrings / unused test split | multiple | Low |
| B15 PhDdata (43 shapes) never loaded | graph_dataset.py:232-236 | Low |
| R1 Fix supervision (per-graph losses, GT topology, splits) | - | Priority 1 |
| R2 DETR-style queries + Hungarian matching + existence head | - | Priority 1 |
| R3 Global context (virtual node / dense attention, bigger model) | - | Priority 2 |
| R4 PhD + synthetic data, normalization-surviving augmentation | - | Priority 2 |
| R5 Loss shaping (asymmetric Chamfer, edge/degree losses) | - | Priority 3 |
| R6 RWPE / canonical LapPE + geometric node features | - | Priority 3 |
| R7 Post-processing (merge, MST extraction, snapping) | - | Priority 3 |
| R8 Held-out evaluation + edge F1 / Hausdorff metrics | - | Priority 3 |
| R9 Fix-or-retire finetuned Graphormer | - | Priority 4 |
| gnnencoderdecoder | stub, non-functional by design | Status only |
