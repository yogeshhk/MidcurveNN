# Phase III (graph-based) - Simplification and Feasibility Proposal

Date: 2026-11-01. Scope: `src/geometry_based/` plus the 2-pager. Static analysis only; nothing was run or edited.
Companion to the existing `src/geometry_based/analysis_report.md` (B1-B15, R1-R9), whose findings I re-verified
against the code and data and whose numbering I reuse. New findings are labelled N1-N8.

## 1. Bottom line

1. A variable-size graph-to-graph encoder-decoder is feasible, but NOT in the form currently coded. The current model fails
   for structural reasons (no node correspondence, wrong ground truth, leaked evaluation), not because the idea is infeasible.
2. The simplest formulation likely to work on I, L, T, Plus and extend beyond them is:
   **learn the NODE SET only (fixed K queries + existence flag + Hungarian matching), and derive the EDGES deterministically
   (minimum spanning tree restricted to segments that lie inside the profile polygon).**
   Learned adjacency becomes an optional later rung, not the starting point.
3. Before any network: build (a) a procedural generator that produces exact (profile, midcurve) pairs with known topology,
   which also removes the need for a classical algorithm as ground truth, and (b) a classical baseline and a metric suite.
   If those two cannot be made to agree with the 4 hand-made `.mid` files, no network result means anything.
4. Honest caveat: for thin rectilinear shapes the midcurve nodes are computable by a rule. A neural net earns its place only
   for what rules do badly (noisy, curved or non-rectilinear profiles, learned pruning, speed). The proposal therefore
   frames the NN result as "learned node proposals + guaranteed-valid topology", and keeps "learned topology" as the
   explicit research question for the later rungs.
5. Cut: `finetuned_graph_transformer/` (deprecated Graphormer, 7 High/Medium bugs), `gnnencoderdecoder/` (non-functional stub),
   the duplicated trainer in `main_graph_transformer.py`, PyG/TopK/LaplacianPE dependence for the baseline model.

## 2. What the current code does (verified)

Pipeline: `.dat/.mid` -> `graph_dataset.py` (PyG `Data`: profile ring graph, midcurve "chain" graph, 34 augmentations per shape)
-> `graph_transformer.py` (LaplacianPE -> 3x TransformerConv -> TopKPooling(0.6) -> per-node MLP for xy + pairwise MLP for a
k x k adjacency) -> loss = 1.0 * squared bidirectional Chamfer + 0.5 * adjacency BCE. Training in two near-duplicate places
(`train.py`, `main_graph_transformer.py:40-110`). Result (`graph_transformer/results/metrics.csv`): adjacency BCE 1.13-1.18
(chance), predicted node counts 3/4/8/5 vs ground truth 2/3/5/4 (I/L/Plus/T), predicted coordinates for I and L visibly wrong.

Bugs and risks, with locations (B-numbers from the existing report, re-verified; N-numbers new):

| ID | Where | Problem |
|---|---|---|
| B3 | `graph_dataset.py:51-75`; `data/raw/T.mid`, `Plus.mid` | Ground-truth edges wrong. `.mid` files list each point once; consecutive chaining makes T edge 2-3 = (25,22.5)-(0,22.5) (crosses the junction) and Plus edge 2-3 = (12.5,45)-(0,22.5) (a diagonal outside the shape). Verified from the files: T has 4 points, true edges are 0-1, 1-2, 1-3. The adjacency head is trained on wrong targets for exactly the branched shapes. |
| B2 | `graph_dataset.py:138-150` | `mid_edge_index` is incremented by PyG with the PROFILE node count, while `y` is concatenated with midcurve counts. Ground-truth adjacency is garbage for every graph but the first in a batch. |
| B1 | `graph_transformer.py:307-312, 162-168` | Chamfer and adjacency are computed over the whole batch as one point set; a prediction can be explained by another sample's target. |
| B4 | `graph_transformer.py:274-304` | Adjacency BCE compares entry (i,j) of predictions (TopK order) with entry (i,j) of the `.mid` listing order. No correspondence, so it can only learn edge density. This alone explains BCE ~ chance. |
| B5 | `train.py:42-57`; `graph_dataset.py:125-128, 194-204` | Random split of the augmented set; per-sample normalisation (subtract mean, divide max-abs) cancels all 4 scales and 16 translations, so each shape contributes about 21 identical samples. Evaluation is on the 4 training shapes. Every reported number is a training number. |
| B8 / N7 | `graph_transformer.py:57-81, 96` | LaplacianPE on the block-diagonal batch Laplacian (wrong eigenvectors, sign-unstable) and, new: it is projected to `in_dim=2` and ADDED to raw (x,y) coordinates (`x + self.proj(pe)`), corrupting the coordinate features. |
| B9 | `graph_transformer.py:201` | Output size fixed at ceil(0.6 * N_p) by TopKPooling; cannot output the true node count. |
| B10 | `graph_transformer.py:100-120` | Ring graph, 3 layers: opposite walls (the pairs whose midpoint IS the midcurve) never exchange information. |
| B13 | `graph_transformer.py:264-271` | Squared distances reported as "Chamfer", in normalised units. Also node-only Chamfer is blind to missing edges. |
| N1 | `graph_transformer.py:299-301` | `pos_weight` computed with `.item()` over k*k entries including the diagonal; unstable and not differentiable-safe under batching. |
| N2 | `train.py:195` | Optimizer passed to an eval-only call; harmless but shows the code was never read after writing. |
| N3 | `main_graph_transformer.py:40-110` vs `train.py:60-100` | Two independent training loops that can drift. |
| N4 | `graph_dataset.py:232-236` | Non-recursive `listdir`; `data/raw/PhDdata` (about 44 profiles) is never loaded. Note: those files' midcurves are in a free-form text format (`*_MidcurvesByYogeshMethod.txt`, blank lines, values like 494.58) - they are NOT usable as-is, so "just load PhDdata" is not a cheap win. |
| N5 | `finetuned_graph_transformer/model.py:97, 213-222` | B6/B7: negative coordinates collapse to bin 0; one wrong adjacency broadcast to the whole batch; indices clamped onto node 31. |
| N6 | `graph_transformer.py:127-170` | Decoder sees only TopK-surviving node embeddings (no queries); output coordinates are an MLP of a pooled embedding, not anchored to any geometry. |
| N8 | `testing/test_geometry_based.py` | Tests assert only "finite and positive loss"; they cannot catch any of the above. |

Root cause summary: the task has three entangled problems (variable node set, node correspondence, topology) and the
current design tries to learn all three jointly from a corrupted signal on 4 effective samples.

## 3. Feasibility analysis of options

Task restated: input = ordered ring of N_p (x,y) corners (N_p 4..~40); output = a graph with K nodes (K != N_p, K about 2..8 for
thin rectilinear shapes) and E edges (a tree for these shapes; branch degree up to 4).

Key facts that drive the recommendation:
- The output is a SET of nodes (order meaningless) plus a graph on them. Any loss needs either a matching (Hungarian), a
  permutation-invariant surrogate (Chamfer), or a canonical order.
- For tree-like thin shapes the edges are a deterministic function of (nodes, profile): MST under Euclidean weights, using only
  segments that stay inside the polygon. I checked by hand: I -> 1 edge, L -> 2, T -> 3 (junction degree 3), Plus -> 4
  (centre degree 4); the "collinear shortcut" (e.g. left end to right end through the T junction, 25 vs 12.5+12.5) is always
  longer than the two real edges, so MST never takes it. For right-angle arms the end-to-end distance is sqrt(a^2+b^2),
  longer than either arm, so it is safe; it can fail for arms meeting at under about 60 degrees, which the inside-polygon test
  mostly repairs. Cycles (holes, ring shapes) cannot be produced by an MST - out of scope for the first ladder.
- Only 4 real shapes exist, so any claim of generalisation requires a procedural dataset.

| Option | Variable size | Correspondence | Topology | Complexity | Verdict |
|---|---|---|---|---|---|
| (a) Fixed-K queries + existence + Hungarian (DETR-style), nodes only | yes (existence mask, K=12 >= max 8) | solved by matching | not learned | low (about 150 lines, pure PyTorch) | RECOMMENDED core |
| (b) mask + coords + adjacency logits (current) | only via fixed slots; currently via TopK | NOT solved (B4) | learned but unsupervised correctly | medium | Valid only if built on (a): adjacency supervised on matched slots. Make it rung 2b. |
| (c) Autoregressive node/edge generation | native | needs a canonical order (e.g. DFS from lowest-leftmost leaf), ambiguous for symmetric shapes | learned via parent pointers | medium-high (teacher forcing, exposure bias, ordering ambiguity, stop token) | Second choice; a small-model echo of Phase II. Revisit if (a)+(e) fails on cyclic shapes. |
| (d) Per-profile-vertex / per-edge prediction (classical-inspired: predict end-cap edges, wall pairings, derive nodes from profile geometry) | implicit | by construction (nodes tied to profile elements) | derived | high: re-implements the classical algorithm; junctions are not midpoints of any profile edge so need extra rules | Do not build; DO borrow its idea as input features (edge vectors, convex/reflex flag, short-edge cue). |
| (e) NN predicts only a point set; deterministic post-process builds the graph (inside-polygon MST) | yes | solved by (a) | guaranteed valid (connected tree) | very low | RECOMMENDED, combined with (a) |
| (f) Implicit field / occupancy (query point -> distance to midcurve) | free | none needed | extracted by thresholding + skeletonising | medium; needs dense queries | Not simplest: ends in the Phase I problem (noisy raster to clean polyline). Keep as a possible later comparison. |

Recommendation: **(a) + (e)**. Why it is the simplest that can work: it removes the two things that sank the current model
(correspondence and adjacency supervision) by (i) Hungarian matching on a fixed set of query slots and (ii) not learning the
edges at all. It is extensible: rung 2b adds an adjacency head on matched slots and measures whether learned topology beats MST;
rung 2c adds noise/curved profiles where rules fail.

What would count as proof of feasibility (all measured on held-out data, in original units, not on training shapes):
- P1 Oracle topology: `edges_from_nodes(GT nodes, profile)` reproduces the GT edge set on 100% of 2000 synthetic samples and
  the 4 real shapes. (Proves topology really is derivable; if it fails, option (e) is dead and (b)/(c) are needed.)
- P2 Generator fidelity: skeleton specs of I, L, T, Plus passed through the generator reproduce `I/L/T/Plus.dat` exactly
  (symmetric-difference area < 1e-6). (Proves the synthetic ground-truth convention equals the hand-made one.)
- P3 IID synthetic test: node-count exact match >= 95%, degree-sequence match >= 90%, Hausdorff <= 0.25 * wall width for >= 90%
  of samples.
- P4 Real 4 shapes (never in training; the generator draws continuous dimensions so the exact I/L/T/Plus are not in the set):
  all four give the right node count, right topology and Hausdorff <= 0.25 * width.
- P5 (stretch, the actual generalisation test) Train with every sample having a degree-4 node removed; the real Plus
  (centre degree 4) must still come out as 5 nodes / 4 edges.
- Negative control to report: training on only 3 real shapes with augmentation and testing on the held-out 4th will fail
  (3 effective samples). This justifies the procedural data and should be stated in the write-up, not hidden.

## 4. Baseline ladder

Rung 0 - classical (no learning), `classical.py` + `metrics.py`
- Ground truth for synthetic data comes from the generator (exact), not from this algorithm. The classical algorithm is a
  sanity baseline and a future label source for non-generated shapes.
- Algorithm: densify profile boundary (step = width/8), `scipy.spatial.Voronoi`, keep finite ridges whose both endpoints are
  inside the polygon, build a `networkx` graph, iteratively prune leaf branches shorter than `1.5 * local_half_width`
  (removes the corner spurs), contract degree-2 chains and Douglas-Peucker them (tolerance about 0.15 * width), extend each leaf
  along its last segment to the profile boundary (the repo's convention puts leaves on the end-cap midpoint, e.g. I.mid y=5 and 20),
  snap bends of near-90-degree pairs to the intersection of the two arm centrelines (convention of L.mid corner (7.5,32.5)).
- Expect it to match I/L/T/Plus to within a fraction of width but not exactly; record that residual as the "classical floor".
- shapely note: the base env has Shapely 1.8.5 (no `shapely.voronoi_diagram`, no vectorised API) - use scipy for Voronoi and
  only `Polygon`, `LineString`, `buffer`, `covers`, `distance`, `symmetric_difference`, which exist in 1.8 and 2.x.

Rung 1 - tiny PyTorch set model (pure torch, no PyG): vertex features -> `nn.TransformerEncoder` (2-3 layers, d=64, no
positional encoding; global attention solves B10) -> K=12 learned queries in `nn.TransformerDecoder` (2 layers) -> heads: xy (2),
existence logit (1). Loss: Hungarian match (cost = L1 distance - 0.5 * sigmoid(exist)), L1 on matched xy (weight 5), BCE on
existence (matched=1, rest=0, weight 0.5 on the empties as in DETR). Edges: inside-polygon MST on thresholded nodes.
Parameter count about 150k; trains on CPU in minutes.

Rung 2 (only if rung 1 meets P3-P4): (2a) arbitrary-angle rotation and anisotropic stretch; (2b) learned adjacency head on
matched slots, compared head-to-head with MST; (2c) noisy/curved profiles with classical labels; (2d) cycles/holes.

Rung 3 (only if 2b is needed): the existing GNN / graph transformer, reusing the same data, matching loss and metrics.
It is a drop-in encoder swap, not a new pipeline.

Metrics (all in units normalised by profile bbox half-extent, and ALSO divided by wall width w; success thresholds use w):
- Sampled-edge Chamfer (sqrt, mean of both directions) and Hausdorff between densified predicted and GT graphs (step 0.01).
  Node-only Chamfer is reported separately because it is blind to missing edges (B13).
- Node-count error (K_pred - K_gt) and exact-match rate.
- Degree-sequence match (sorted degrees equal), branch-point recall (GT nodes with degree >= 3 that have a predicted node within
  0.25 w), connected-yes/no, is-tree-yes/no.
- Edge precision/recall/F1 after Hungarian node matching with tolerance 0.25 w.

Split design (leave-one-shape-out made meaningful):
- `iid`: train/val/test from different RNG seeds of the generator (continuous dimensions, so no duplicates).
- `ood_deg4`: train excludes samples whose maximum node degree is 4; test includes them (and the real Plus).
- `ood_size`: train uses 1-5 skeleton edges; test 6-7.
- `real4`: I, L, T, Plus, always evaluation-only, never in training.
Never evaluate on augmented copies of a training sample; the old split is retired.

Procedural generator (the single most important new asset):
- Sample a random tree on a lattice (spacing 1): start at one node; repeat n_edges (1..7) times: pick an existing node with
  degree < 4 and an unused axis direction whose target lattice node is not yet in the tree and has exactly one tree neighbour
  (the parent). Merge degree-2 collinear nodes (canonical GT nodes = leaves, junctions, bends).
- Optional jitter: give every distinct x column and y row a random gap in [0.7, 1.5] (keeps axis alignment and topology).
- Width w uniform in [0.3, 0.6] (lattice units). Build the profile as the union of boxes, one per skeleton edge, each extended
  by w/2 at endpoints that have degree >= 2 (fills bends/junction corners), not extended at leaves (so leaf = end-cap midpoint,
  the repo's convention). `unary_union`, require a single valid Polygon with no holes; remove collinear vertices.
- Reject if two non-adjacent skeleton edges are closer than 1.5 w (stops touching strips and accidental holes).
- Profile orientation random (CW/CCW), random start vertex, optional collinear-vertex insertion (so N_p varies without changing
  geometry; stops the model from keying on vertex count), random mirror and 90-degree rotation at load time.
- Check that it reproduces the repo's hand data: I w=5, nodes (7.5,5),(7.5,20); L w=5, nodes (7.5,5),(7.5,32.5),(35,32.5);
  T w=5, nodes (12.5,0),(12.5,22.5),(25,22.5),(0,22.5) edges (0,1),(1,2),(1,3); Plus w=5, nodes (12.5,0),(12.5,22.5),(12.5,45),
  (0,22.5),(25,22.5) edges (0,1),(1,2),(1,3),(1,4). I checked these against the `.dat` files: all four are exactly the union of
  flat-capped rectangles of width 5 around these skeletons.
- Do not write the generated data to git-tracked files (lesson from the Phase I datasets); generate on the fly from a seed.

## 5. What to cut or freeze

- Retire `src/geometry_based/finetuned_graph_transformer/` (deprecated HF Graphormer, API drift, bugs B6/B7/B11/N5, tests skip). Move to
  `src/geometry_based/_retired/` (this repo's convention for retired material); remove its sections from `README.md`,
  `geometry_based/README.md`, `src/benchmark.py` (lines 151-237 handle it), the tests that import it, the two-pager text that
  mentions it (leave the .tex alone until the user asks; list as follow-up).
- Retire `src/geometry_based/gnnencoderdecoder/` (stub that raises NotImplementedError and does not compile).
- Freeze `graph_transformer/` as the "v1 negative result": do not fix B1-B10 there; keep checkpoints/results because the
  2-pager and paper cite them. Delete the duplicated trainer in `main_graph_transformer.py` only when the user agrees (it is
  frozen code with its own tests).
- Do not make the new model depend on PyG, Laplacian eigendecomposition, TopKPooling or HF.
- Do not touch Phase I/II, `publications/`, or the `.dat/.mid` raw files.

## 6. Action list for Sonnet

General rules for the executor: no git commands. Use the Edit/Write tools for files (no heredocs, no sed). Python via
`conda run -n <env> python ...`; first find an env that has torch, scipy, shapely, networkx
(`conda run -n midcurvenn python -c "import torch,scipy,shapely,networkx"`; if that fails try `genai`) and use the same env
throughout. ASCII output only. Work from `D:/Yogesh/GitHub/MidcurveNN/src`. After each step run the stated check and stop on
failure instead of improvising. The new package is `src/geometry_based/midcurve_set/`; use relative imports inside it
(`from . import geom`) so the `config` module-name collision noted in CLAUDE.md cannot occur. Ask the user before step 15.

1. Baseline snapshot (read-only). Run `python -m pytest geometry_based -q` from `src/`. Record pass/fail counts as a comment at the
   top of the new test file in step 12. Check: command finishes; counts noted. Effort: 5 min.

2. Create `src/geometry_based/midcurve_set/__init__.py` (empty) and `geom.py` containing exactly these functions:
   `read_pts(path)`; `polygon(pts)` (shapely Polygon, fix orientation to CCW); `remove_collinear(pts, tol=1e-9)` (drop vertices
   whose cross product with neighbours is below tol, cyclically); `normalize(profile, nodes)` returning
   `(profile_n, nodes_n, centre, half_extent)` with centre = bbox centre, half_extent = max bbox half-side (isotropic);
   `edges_from_nodes(nodes, poly, eps_rel=1e-6)`: build all pairs, keep pair (i,j) only if
   `poly.buffer(eps_rel*extent).covers(LineString([pi, pj]))`, run `scipy.sparse.csgraph.minimum_spanning_tree` on those
   weights, return sorted list of `(i,j)` with i<j; if the graph is disconnected return the minimum spanning forest and let
   callers check connectivity; `degrees(n, edges)`; `densify(nodes, edges, step)` (points along edges, plus the nodes; if no
   edges return the nodes). Check: `python -c "from geometry_based.midcurve_set import geom"` from `src/`. Effort: 1 h.

3. Create `procedural.py` implementing `from_skeleton(nodes, edges, w)` -> dict(profile[N,2] CCW with collinear removed, nodes,
   edges, w) as specified in section 4 (boxes, extension by w/2 at degree>=2 endpoints, `unary_union`, single Polygon, no holes,
   non-adjacent-edge distance >= 1.5 w else raise `Rejected`); `sample_skeleton(rng, n_edges, allow_deg4, jitter=True)`;
   `make_sample(rng, min_edges=1, max_edges=7, allow_deg4=True)` that loops until accepted and adds meta `deg_max`, `n_edges`;
   `make_dataset(n, seed, **kw)`; constant `REAL_SPECS` holding the four skeleton specs from section 4. Use
   `numpy.random.default_rng(seed)`. Check (acceptance for P2): a test that for each of I, L, T, Plus builds `from_skeleton`
   and asserts `Polygon(profile).symmetric_difference(Polygon(read_pts(.dat))).area < 1e-6` and vertex counts 4, 6, 8, 12;
   and that `make_dataset(2000, seed=0)` finishes with no exception, `nodes <= 8` for all, and mean acceptance rate (accepted /
   attempted) is logged (must be above 20%; if lower, loosen only the lattice-neighbour rule, not the 1.5 w rule). Effort: 3 h.

4. Verify P1 inside the same test file: for the 2000 synthetic samples and for the 4 real shapes (nodes from `.mid` with expected
   edge lists I:{(0,1)}, L:{(0,1),(1,2)}, T:{(0,1),(1,2),(1,3)}, Plus:{(0,1),(1,2),(1,3),(1,4)}), assert
   `geom.edges_from_nodes(nodes, Polygon(profile)) == sorted(gt_edges)` for 100%. If any synthetic sample fails, print its
   skeleton and stop and report to the user (this is a finding, not a bug to patch silently). Effort: 1 h.

5. Create `metrics.py` with: `chamfer(a, b)` (sqrt mean nearest distance, symmetric), `hausdorff(a, b)`, `graph_metrics(pred_nodes,
   pred_edges, gt_nodes, gt_edges, w)` returning a dict with keys `chamfer_edge, hausdorff_edge, chamfer_node, k_err, k_exact,
   deg_seq_match, branch_recall, connected, is_tree, edge_precision, edge_recall, edge_f1, hausdorff_over_w, ok_025w`
   (ok_025w = hausdorff_over_w <= 0.25 and k_exact and deg_seq_match). Node matching via
   `scipy.optimize.linear_sum_assignment` with tolerance 0.25 w. Use `densify(step=0.01)` after normalisation. Check: unit
   tests: identical graphs give zeros / F1 = 1 / ok_025w True; a graph with one node dropped gives k_err = -1 and ok_025w False.
   Effort: 2 h.

6. Create `classical.py` with `classical_midcurve(profile, w_hint=None)` per section 4 (Voronoi of densified boundary, keep
   interior ridges, prune short leaf branches, contract and simplify, extend leaves to the boundary, snap near-90-degree bends).
   Create `eval_classical.py` that runs it on the 4 real shapes and on 500 synthetic samples (`seed=123`), writes
   `midcurve_set/results/classical.csv` (one row per sample, columns from step 5) and prints mean/median per metric and the
   fraction with `ok_025w`. Check: the file exists, row count 504, no crash. Do NOT tune the algorithm to hit a number; report
   the figures. If classical `ok_025w` < 50% on synthetic, report which stage (pruning, leaf extension, bend snapping) causes
   most failures. Effort: 4 h (this is the riskiest step; a crude version that only handles axis-aligned arms is acceptable
   if documented in the module docstring).

7. Create `data.py`: `to_example(sample, rng, augment)` -> dict of tensors: apply augmentation (random 90-degree rotation, mirror,
   random cyclic start, random reversal, optional collinear vertex insertion of 0-3 vertices per edge with prob 0.3) to profile
   and GT together, then `geom.normalize`. Per-vertex features (7 dims): x, y, prev-edge vector (dx,dy), next-edge vector
   (dx,dy), convex/reflex flag (sign of cross product). Pad to NMAX=40 with a boolean mask (drop samples with N_p > 40 at
   generation time). GT nodes padded to K=12 with a mask. Provide `make_loader(samples, batch_size, shuffle, augment)` using a
   plain `torch.utils.data.Dataset`; no PyG. Check: one batch has shapes (B,40,7), (B,40), (B,12,2), (B,12) and rotating a sample
   by 90 degrees rotates its GT nodes identically (assert on a fixed seed). Effort: 2 h.

8. Create `model.py`: class `MidcurveSetNet(d=64, heads=4, enc_layers=3, dec_layers=2, k=12)`: `nn.Linear(7,d)`,
   `nn.TransformerEncoder` with `src_key_padding_mask`, `nn.Embedding(k,d)` queries, `nn.TransformerDecoder`, heads
   `nn.Linear(d,2)` for xy and `nn.Linear(d,1)` for existence logit; `forward(feats, mask)` returns `xy[B,K,2], logit[B,K]`.
   Use `batch_first=True`, no BatchNorm. Check: forward on a batch of 1 and a batch of 8 both work; parameter count printed
   (expected 100k-300k). Effort: 1 h.

9. Create `loss.py`: `set_loss(xy, logit, gt_xy, gt_mask)`: per sample, cost matrix = L1(xy_q, gt_j) - 0.5*sigmoid(logit_q);
   `linear_sum_assignment` (on CPU numpy); loss = 5.0 * mean L1 over matched pairs + BCE-with-logits on all K slots (targets 1 for
   matched, 0 otherwise; weight 0.5 on target-0 slots); average over the batch; return total and the two parts. No batch-level
   mixing anywhere (this is the fix for B1). Check: unit test where predictions equal GT in a shuffled order gives matched L1 = 0.
   Effort: 1.5 h.

10. Create `train.py` (argparse: `--split {iid,ood_deg4,ood_size}`, `--n-train 20000`, `--n-val 2000`, `--epochs 100`,
    `--batch-size 128`, `--lr 1e-3`, `--seed 0`, `--out midcurve_set/checkpoints`). Data: `make_dataset` with seeds 0/1/2 for
    train/val/test; for `ood_deg4` pass `allow_deg4=False` for train and keep val IID without deg-4 but test with deg-4 allowed;
    for `ood_size` train `max_edges=5`, test `min_edges=6`. AdamW + cosine schedule, grad clip 1.0, save the best-val model
    and a CSV log. Every 10 epochs run `metrics.graph_metrics` on the val set (threshold exist > 0.5, merge nodes closer than
    0.02, `edges_from_nodes`) and print `k_exact`, `deg_seq_match`, `ok_025w`. Check: a 3-epoch smoke run (`--epochs 3
    --n-train 512`) finishes and writes the checkpoint and log. Effort: 2 h.

11. Create `evaluate.py`: loads a checkpoint, evaluates on (a) the held-out synthetic test set of the chosen split, (b) `real4`
    (I, L, T, Plus from `data/raw`, normalised with the same function, w = 5), writes
    `midcurve_set/results/<split>_metrics.csv`, and also writes the P1-P5 pass/fail summary as a small text file with the
    thresholds from section 3. Include a plotting helper that saves one PNG per real shape (profile, GT, prediction). ASCII only
    in printed output. Check: runs on the smoke checkpoint. Effort: 2 h.

12. Create `src/geometry_based/testing/test_midcurve_set.py` (pytest.ini already collects `geometry_based/testing`) with the tests
    from steps 3, 4, 5, 7, 9. Mark nothing as skip except `torch` import guard. Check: `python -m pytest
    geometry_based/testing/test_midcurve_set.py -q` all pass, runtime < 60 s. Effort: 1 h.

13. Run the experiments (user reviews numbers; do not tune beyond these knobs): `train.py --split iid --epochs 100`; then
    `evaluate.py`. If P3 fails, try only: epochs 300, d 128, enc_layers 4, n_train 50000, one at a time, and report each. Then
    `train.py --split ood_deg4` and `evaluate.py` for P5. Check: result CSVs exist; report a table of P1-P5 pass/fail with the
    measured numbers and the classical floor from step 6. Effort: 3 h compute and reporting.

14. Update docs (small edits only): `src/geometry_based/README.md` (replace the approaches table by: `midcurve_set/` primary,
    `graph_transformer/` frozen v1 negative result, retired items listed; add the run commands), append a dated section to
    `src/geometry_based/analysis_report.md` ("2026-11-01 simplification: verified B-numbers, N1-N8, pointer to
    `src/proposal/03_graph_based_proposal.md`"), and add one line to `TODO.md` under Phase III pointing to the proposal.
    Do not edit the .tex files. Check: links resolve (files exist). Effort: 45 min.

15. (Needs explicit user confirmation first, because it is a multi-file move.) Retire: move
    `geometry_based/finetuned_graph_transformer/` and `geometry_based/gnnencoderdecoder/` to `geometry_based/_retired/`;
    in `testing/test_geometry_based.py` delete the finetuned and gnn test classes (finetuned tests start near line 160, gnn
    placeholder tests near line 215); in `src/benchmark.py` remove the finetuned branch (`benchmark_geometry` lines 151-237
    keep only `graph_transformer`) and fix B12's hardcoded hyperparameters by reading `ckpt['args']`; in `src/README.md` and
    `CLAUDE.md` update the directory listing lines that mention the two folders (README lines about 149-153 and 225).
    Check: `python -m pytest geometry_based -q` passes, `python benchmark.py --approaches geometry` still runs or reports a clean
    SKIP. Present the exact list of edits to the user before applying. Effort: 1.5 h.

16. Final report to the user: table of P1-P5 results, the classical floor, what failed, and an explicit statement of whether
    learned topology (rung 2b) is still needed. Effort: 20 min.

Total effort estimate: about 3 working days, of which step 6 (classical baseline) and step 13 (experiments) are the only ones with
real uncertainty.

## 7. Risks and open questions

- The generator covers only thin rectilinear tree shapes. The real PhD shapes (curves, holes, non-orthogonal) are out of scope until
  rung 2c/2d; the research claim must be worded accordingly.
- The MST rule makes edges non-learned. If the supervisor wants "learned topology" as the headline, rung 2b is the experiment and
  the MST result is its baseline to beat; having a strong deterministic baseline is a strength, not a weakness.
- Existence + Hungarian can produce duplicate near-coincident nodes early in training; the merge step (0.02 normalised) is part of
  the evaluation protocol, applied identically to every model.
- Normalising by bbox half-extent loses absolute scale; metrics divided by w keep the numbers comparable across shapes.
- The 4 real shapes all have the same width (5) and axis alignment; arbitrary-angle rotation is deferred to rung 2a on purpose.
- Python/shapely versions: base Python 3.10 has Shapely 1.8.5, scipy 1.15, torch 2.7.1; the project env may differ - verify first
  (step header).
