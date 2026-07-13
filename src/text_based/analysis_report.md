# Phase II (text_based) - Code Analysis Report

Date: 2026-07-03
Scope: `src/text_based/` (utils, data, finetuning, nemotron3, codeT5, ludwig, prompt,
testing) plus the shared dependency it consumes for plotting
(`src/utils/prepare_plots.py::save_results_grid_brep`).

Intentional design choices documented in CLAUDE.md (config_enhanced.py /
metrics_enhanced.py alias re-exports, config-module-name collision guard in
test 24) are NOT reported as bugs here.

---

## 1. Overview

Phase II represents shapes as BRep JSON (`Points`/`Lines`/`Segments` for both
`Profile` and `Midcurve`) and asks a fine-tuned LLM to map profile-BRep text
to midcurve-BRep text. Two parallel, largely independent pipelines share one
dataset:

- **Dataset pipeline** (`utils/`): 4 hand-authored base shapes
  (`data/brep/{I,L,T,Plus}.json`) are the single source of truth.
  `create_brep_csvs.py` applies scale/rotate/translate/mirror transforms
  (ranges from `utils/config.py`) to produce `data/csvs/midcurve_llm*.csv`
  (80/10/10 train/test/val). Unlike the geometry_based `.mid`-file chaining
  bug (B3 in that report), the BRep JSON topology here is authored correctly
  by hand for T/Plus (explicit star topology at the junction point) - a
  genuine strength of this representation.
- **`finetuning/`**: QLoRA fine-tuning of Qwen2.5-Coder-7B (or
  Gemma/Mistral) via PEFT + TRL `SFTTrainer`, with an evaluation harness
  (`GeometricMetrics`: Hausdorff, Chamfer, MAE/RMSE, topology accuracy,
  connectivity), a FastAPI server, a data validator, an augmentation module,
  an error-analysis module, and a `run_pipeline.py` orchestrator.
- **`nemotron3/`**: a smaller, later, and noticeably more carefully written
  pipeline for `nvidia/Nemotron-Mini-4B-Instruct` (HF SFTTrainer, Unsloth,
  and few-shot variants), targeting 4 GB VRAM. It reuses `finetuning/metrics.py`
  when importable and falls back to an inline copy otherwise.
- **`codeT5/`, `ludwig/`, `prompt/`**: notebooks / exploratory scripts, not
  actively maintained code paths (status noted, not bug-audited in depth).

Both LLM pipelines train and evaluate on the **same** `data/csvs/` CSVs
produced by `utils/create_brep_csvs.py`, so the dataset-level issues in
Section 3 (A1-A3) affect `finetuning/`, `nemotron3/`, and (if ever run)
`codeT5/` identically.

---

## 2. Per-Component Analysis

### 2.1 utils/ (dataset pipeline)

Files: `config.py`, `prepare_data.py`, `create_brep_jsons.py`,
`create_brep_csvs.py`, `prepare_plots.py`.

Strengths: 3x3 homogeneous-matrix transforms are correct and reused
consistently; `apply_transform_to_shape` keeps flat `Profile`/`Midcurve`
lists in sync with `BRep["Points"]`; `Lines`/`Segments` are never touched,
which is valid for this transform set; `create_brep_jsons.py`'s onboarding
converter derives midcurve topology structurally from the Yogesh method's
segment list rather than by re-chaining points, so branch points do not
silently become diagonals (contrast with geometry_based B3).

Weaknesses: the checked-in `data/csvs/` is measurably out of sync with what
`create_brep_csvs.py` + the current `config.py` would produce today (A1),
and `save_dataset()`'s train/test/val split is a flat shuffle over
transformed variants with no shape-level grouping (A2), so the two LLM
pipelines evaluate on leaked data.

### 2.2 finetuning/

Files: `config.py`, `dataset_loader.py`, `train.py`, `inference.py`,
`evaluate.py`, `metrics.py`, `data_validator.py`, `augmentation.py`,
`error_analysis.py`, `model_comparison.py`, `model_server.py`,
`run_pipeline.py`, `visualize.py`.

This is the most feature-rich pipeline (curriculum learning, geometric
loss weighting, augmentation, early stopping all appear in `Config`) but
most of that surface is unwired: `train.py` runs a plain token-level SFT
run and ignores `USE_GEOMETRIC_LOSS`, `GEOMETRIC_LOSS_WEIGHT`,
`TOKEN_LOSS_WEIGHT`, `USE_CURRICULUM`, `CURRICULUM_STAGES`,
`EARLY_STOPPING_PATIENCE`, `EARLY_STOPPING_METRIC`, and
`CHECKPOINT_METRICS` entirely (B4). The per-epoch
`GeometricValidationCallback` runs `model.generate()` on 10 samples every
epoch but never records a metric (B2) - pure wasted compute. The
documented one-command entry point, `run_pipeline.py --full`, cannot
complete because it shells out to a script (`train_enhanced.py`) that does
not exist in the repo (B1). `metrics.py`'s MAE/RMSE degrade silently for
mismatched point counts (B3), and `mae`/`rmse`/`vertex_count_accuracy` are
computed but excluded from `combined_score` (B7).

### 2.3 nemotron3/

Files: `config.py`, `dataset_loader.py`, `hf_sft_trainer.py`,
`unsloth_trainer.py`, `fewshot_prompter.py`, `train.py`, `train_unsloth.py`,
`run_demo.py`, `inference.py`, `evaluate.py`, `metrics.py`.

Cleaner than `finetuning/`: every advertised config flag is actually used;
`inference.py`'s `_repair()` performs genuine nearest-component MST-style
connectivity repair (iteratively connects the closest unvisited node to the
visited set, recomputing components) - materially better than
`finetuning/inference.py`'s single-pass adjacent-pair repair
(`repair_connectivity`, `finetuning/inference.py:97-160`), which only
connects consecutively-discovered components in BFS order and never
reconsiders once linked (may not choose the globally nearest pair,
though it does still guarantee connectivity). `fewshot_prompter.py` and
`run_demo.py` are near-duplicate implementations of the same few-shot
logic (B10, low severity - a maintenance/drift risk, not a correctness
bug). Shares the dataset-level issues (A1-A3) with `finetuning/`.

### 2.4 codeT5/, ludwig/, prompt/ (status only)

Notebook-based or exploratory; not exercised by `testing/test_text_based.py`
beyond file-existence checks. `prompt/midcurve_generator.py` is a leftover
LangChain script with the actual LLM-invocation loop commented out (only
the matplotlib comparison plot at the bottom still runs) and uses the
deprecated `langchain.llms` import path - candidate for removal or a
"historical/reference only" label, same treatment as
`gnnencoderdecoder/` in the geometry_based report.

### 2.5 testing/

`testing/test_text_based.py` (45 tests) is thorough for existence/shape/
importability checks across every subfolder, including a
`TestFewShotPrompterLogic` class that unit-tests the pure-Python JSON
repair helpers without a GPU. It does not - and structurally cannot, as a
smoke suite - catch the split-leakage (A2), the unwired config flags (B4),
or the missing `train_enhanced.py` (B1), since none of those are exercised
by an existence/import check.

---

## 3. Dataset-Level Findings (affect both finetuning/ and nemotron3/)

### A1 [High] `data/csvs/` is stale relative to `utils/config.py` and `create_brep_csvs.py`

- Measured composition of `data/csvs/midcurve_llm.csv` (992 data rows):
  720 `rotated` (= 180 angles x 4 shapes, matches `ROTATE_START/STOP/STEP`
  exactly), 64 `scaled` (= 16 factors x 4, matches `SCALE_START/STOP/STEP`
  exactly), 8 `mirrored` (matches), but only **200** `translated` rows.
- `utils/config.py:52-58` configures independent X and Y translation
  (`TRANSLATE_X/Y_START/STOP/STEP` = -50..50 step 2, 51 values each), and
  `create_brep_csvs.py:110-138` (`_translated_variants`) nests both loops,
  which would produce `51 * 51 * 4 = 10,404` translated rows - not 200.
  200 / 4 shapes = 50, consistent with an **older** version of the
  translation generator that varied only the diagonal (`dx == dy`), which
  is exactly the behaviour the current docstring
  (`create_brep_csvs.py:112-117`: "not just dx == dy diagonal variants")
  says was deliberately changed.
- Additionally, zero rows have a bare `ShapeName` (`I`, `L`, `T`, `Plus`)
  even though `create_brep_csvs.py:338` (`all_shapes = original_shapes +
  variants`) includes the untransformed originals - confirming the
  checked-in CSVs predate that line too.
- Consequence: (a) the numbers in CLAUDE.md/README ("993-row... dataset")
  describe an artifact that no longer matches the code that is documented
  as generating it; (b) anyone following the README
  ("`cd utils && python create_brep_csvs.py`") to regenerate data gets an
  11,200-row dataset that is ~93% translation variants (10,404 of 11,200),
  a severe augmentation-type imbalance not present in the currently
  shipped 992-row set, and will silently invalidate any existing
  fine-tuned adapter's train/val/test split.
- Fix: regenerate and re-commit `data/csvs/` from the current pipeline (or
  pin the translation grid down - see R1), and keep a data-version stamp
  (e.g. a hash of `config.py`'s transform ranges) in the CSV or a sidecar
  file so drift like this is caught automatically.

### A2 [High] Train/val/test split leaks near-duplicate transformed variants

- `utils/create_brep_csvs.py:270-280` (`save_dataset`) does
  `random.shuffle(shuffled)` over the full pool of transformed variants
  (rotations/scales/translations/mirrors of only 4 base shapes) and then
  slices into train/test/val. There is no grouping by base shape or by
  transform family.
- Consequence: e.g. `T_rotated_44` can land in train while `T_rotated_45`
  (1 degree apart, essentially the same BRep JSON with coordinates shifted
  by a few hundredths) lands in test. This is the same failure mode as
  geometry_based B5 and the image_based leakage findings - the model can
  score well on the held-out split by near-memorization rather than by
  generalizing the profile -> midcurve transformation. Both `finetuning/`
  and `nemotron3/` inherit this because both read
  `midcurve_llm_{train,test,val}.csv` directly.
- Combined with A3 (below), the test set also never contains a topology the
  model hasn't seen in some rotation/scale during training - there are
  only 4 topological families (I, L, T, Plus) in the entire dataset.
- Fix: split by base-shape identity (leave-one-shape-out, or hold out
  entire transform ranges, e.g. rotations 150-180 degrees reserved for
  test) so test measures generalization to unseen geometry, not
  interpolation between near-identical training rows. This is the single
  highest-leverage fix for making the CLAUDE.md-reported MAE/Hausdorff/PSR
  numbers trustworthy.

### A3 [Medium] Only 4 topological families exist anywhere in the pipeline

- `data/brep/` has exactly `I.json`, `L.json`, `Plus.json`, `T.json`. There
  is no PhD/synthetic-shape ingestion analogous to `src/data/raw/PhDdata/`
  (used - or rather, not used - by geometry_based). Every one of the
  ~1,000-11,000 training rows is a rigid/scale transform of one of these 4
  polygons, so the model can only ever be tested on interpolations of 4
  junction topologies (none, L-corner, T-junction, +-junction).
- Fix: see R1 (data expansion) - the highest-value schema-compatible move
  is running `create_brep_jsons.py` (already written and unused beyond the
  4 seed shapes) against additional Yogesh-method shape pairs, or
  synthesizing new rectilinear polygons with known medial axes directly in
  BRep JSON.

---

## 4. Bugs

Severity: High = wrong results, crash on a documented path, or invalidates
reported metrics; Medium = degrades quality or misleads; Low =
cosmetic/dead code.

(A1-A3 above are dataset-level and apply to both pipelines; B1-B10 below are
component-specific.)

### B1 [High] `run_pipeline.py --full` / `--train` shells out to a script that does not exist

- `finetuning/run_pipeline.py:126-129` runs `python train_enhanced.py` (and
  the "next steps" banner at `:246` prints
  `python inference_enhanced.py --single`). Neither `train_enhanced.py` nor
  `inference_enhanced.py` exists anywhere in the repo - the real files are
  `train.py` and `inference.py`.
- `run_command()` (`run_pipeline.py:13-27`) uses `os.system()`, which on a
  missing script prints a shell "not found" message and returns a non-zero
  exit code; `run_pipeline.py:132` records the step as failed but (for
  `--full`) does not `return`, so evaluation then runs against
  `Config.NEW_MODEL_NAME` (`Midcurve-Qwen-Coder-v1`), which was never
  produced - `evaluate.py`'s `PeftModel.from_pretrained` fails with
  "adapter not found." The documented single-command pipeline is broken
  end-to-end.
- Fix: change the two `os.system()` calls to invoke `train.py` /
  `inference.py`, or add the missing `_enhanced` wrapper scripts if a
  distinct "enhanced" entry point was actually intended.

### B2 [High] `GeometricValidationCallback` is dead code that still costs a full generation pass every epoch

- `finetuning/train.py:28-91`: the per-sample `try` block
  (`train.py:53-75`) calls `model.generate()` for up to
  `Config.VALIDATION_SAMPLES` (10) examples every epoch, but the comment
  at `train.py:58-59,71` says "This is simplified/placeholder - in
  practice, need proper parsing/extraction" and never appends anything to
  `metrics_list`. The `if metrics_list:` block (`train.py:77-89`) is
  therefore always skipped - no geometric validation is ever logged to
  stdout or wandb, despite `Config.EARLY_STOPPING_METRIC =
  "hausdorff_distance"` and `Config.CHECKPOINT_METRICS` implying it drives
  model selection. Meanwhile `model = AutoModelForCausalLM.from_pretrained(
  ..., use_cache=False if USE_GRADIENT_CHECKPOINTING else True)`
  (`train.py:163`) disables the KV cache globally, so every one of these
  no-op `generate()` calls runs without cache reuse - purely wasted
  wall-clock time, worse the longer `MAX_SEQ_LENGTH`/output length is.
- Fix: either implement the extraction (`GeometricMetrics.compute_all_metrics`
  is already available and does exactly what's needed) or remove the
  callback until it does something; if kept, temporarily flip
  `model.config.use_cache = True` around the `generate()` calls.

### B3 [High] `finetuning/metrics.py` MAE/RMSE degrade silently to a one-directional nearest-neighbour distance when point counts differ

- `finetuning/metrics.py:53-84` (`mae_metric`, `rmse_metric`): when
  `len(pred_points) != len(true_points)`, the code computes
  `dist_matrix = norm(pred[:, None] - true[None, :])` and
  `min_dists = np.min(dist_matrix, axis=1)` - i.e. for every PREDICTED
  point, the distance to its nearest TRUE point, then averages. This is
  only half of a Chamfer-style distance: it never penalizes true points
  that have no nearby predicted point.
- Consequence: a degenerate prediction with very few points (e.g. the
  model emits a single point) can score an artificially LOW (good) MAE/RMSE
  as long as that one point happens to be close to some true point,
  because the metric never "sees" the true points that were never
  matched. This directly rewards under-generation, which is exactly the
  failure mode expected from a model still learning to close JSON braces
  correctly (`json_validity` can also be high on truncated-but-parseable
  partial output).
- `hausdorff_metric` (`metrics.py:39-50`) does NOT have this asymmetry (it
  correctly takes `max(directed_hausdorff(a,b), directed_hausdorff(b,a))`),
  so MAE/RMSE and Hausdorff can disagree sharply on the same degenerate
  prediction - worth cross-checking before trusting a low MAE.
- Fix: symmetrize (`mean(min_dist(pred->true)) + mean(min_dist(true->pred))`,
  as `chamfer_distance` already does two functions above it in the same
  file), or report both directions separately.

### B4 [Medium] Config flags for geometric loss, curriculum learning, and metric-based early stopping are entirely unused

- `finetuning/config.py:46-62` defines `USE_GEOMETRIC_LOSS`,
  `GEOMETRIC_LOSS_WEIGHT`, `TOKEN_LOSS_WEIGHT`, `USE_CURRICULUM`,
  `CURRICULUM_STAGES`, `EARLY_STOPPING_PATIENCE`, `EARLY_STOPPING_METRIC`,
  and `CHECKPOINT_METRICS`. None of these names appear anywhere in
  `train.py` (grep confirms zero references outside `config.py`,
  `README.md`, and `augmentation.py` for the augmentation pair).
  `train.py:207-211` hardcodes `metric_for_best_model="eval_loss"` (plain
  token cross-entropy) with no `EarlyStoppingCallback` registered at all,
  so `EARLY_STOPPING_PATIENCE`/`EARLY_STOPPING_METRIC` are pure
  documentation that does not reflect training behaviour.
- Also note `EARLY_STOPPING_METRIC = "hausdorff_distance"` and
  `CHECKPOINT_METRICS = ["hausdorff_distance", ...]` don't even match the
  actual metric key names produced by `metrics.py` (`"hausdorff"`, not
  `"hausdorff_distance"`) - if someone wires these up later without
  noticing, the lookup will KeyError or silently no-op depending on how
  it's read.
- `AUGMENTATION_NOISE_LEVEL`/`AUGMENTATION_MULTIPLIER` (`config.py:56-57`)
  are used only by the standalone `augmentation.py` script, which is never
  invoked by `train.py` and is invoked by `run_pipeline.py` only as an
  optional separate `--augment` step whose output file
  (`TRAIN_FILE.replace(".csv", "_augmented.csv")`,
  `augmentation.py:158-161`) is never read back by anything - i.e. even
  when run, its output is orphaned.
- Fix: either wire these into `train.py` (curriculum staging by epoch,
  Hausdorff-based `EarlyStoppingCallback` via a custom
  `TrainerCallback.on_evaluate`, a combined loss term) or remove them from
  `Config` so the file documents actual behaviour.

### B5 [Medium] `finetuning/inference.py` repair only connects BFS-discovered components pairwise, not by true nearest pair overall

- `finetuning/inference.py:97-160` (`repair_connectivity`): after finding
  connected components via BFS, it connects component `i` to component
  `i+1` (in component-discovery order) using the nearest point PAIR
  between exactly those two components. If there are 3+ components, it
  never considers whether component 0 is actually closer to component 2
  than to component 1 - the repaired graph can end up longer/more
  contorted than necessary, and if discovery order is unlucky, distant
  components may be joined before nearer ones.
- Contrast with `nemotron3/inference.py:159-192` (`_repair`), which
  recomputes the visited-component frontier after every added edge and
  always joins the globally nearest (visited, unvisited) pair - a proper
  greedy MST-style repair. `finetuning/` would benefit from the same
  approach.
- Fix: port `nemotron3/inference.py::_repair`'s algorithm (or the
  underlying idea) into `finetuning/inference.py`.

### B6 [Medium] `run_pipeline.py` error-analysis step reads paths relative to the wrong working directory

- `run_pipeline.py:150-163` checks `os.path.exists("evaluation_results.csv")`
  and then invokes
  `python error_analysis.py --results_file evaluation_results.csv --test_file midcurve_llm_test.csv`
  - both bare filenames, not the paths actually used elsewhere in the
  pipeline (`evaluate.py`'s default output is
  `finetuning/results/evaluation_results.csv` per `evaluate.py:345-347`,
  and the test CSV lives in `data/csvs/midcurve_llm_test.csv` per
  `config.py:22`). Even after fixing B1, this step will print "Skipping
  Error Analysis" or fail with a `FileNotFoundError` unless the user has
  manually copied both files into the current working directory first.
- Fix: use `Config`-derived absolute paths, consistent with how
  `evaluate.py --output_file` and `Config.TEST_FILE` are defined elsewhere.

### B7 [Low] `metrics.py` `combined_score` ignores half the computed metrics

- `finetuning/metrics.py:242-256` (`compute_all_metrics`): `mae`, `rmse`,
  and `vertex_count_accuracy` are computed and returned in the metrics
  dict but never enter `combined_score`, which is
  `0.4*distance_score(hausdorff) + 0.3*topology_score + 0.3*connectivity_score`.
  A prediction with the exactly right point count and low MAE but a
  middling Hausdorff outlier scores the same as one with wildly wrong
  point count. Not a bug in the sense of wrong output, but a design gap
  given the metric is used for "best/worst" ranking in
  `evaluate.py::analyze_results` and `visualize_predictions`.
- Fix: fold `vertex_count_accuracy` (and optionally MAE) into the weighted
  sum, e.g. `0.3*distance + 0.25*topology + 0.25*connectivity +
  0.2*vertex_count_accuracy`.

### B8 [Low] `visualize.py::plot_results` always overwrites a stray file in the current directory

- `finetuning/visualize.py:57` unconditionally
  `plt.savefig('midcurve_result.png')` before returning, on top of whatever
  path the caller later saves to (`evaluate.py:303`:
  `plt.savefig(f"{output_dir}/{category}_{i+1}_{...}.png")`). Every call
  during `visualize_predictions`'s loop (best/worst/median x
  `num_samples`) clobbers the same `midcurve_result.png` in whatever the
  process's CWD happens to be - harmless but wasteful I/O and confusing
  clutter when debugging output locations. It also never calls
  `plt.close()`, so figures accumulate across the loop (same
  "Fail to allocate bitmap" risk class that unet/test.py already had to
  fix, per CLAUDE.md; `evaluate.py:304` does close, but only after the
  double save).
- Fix: accept an optional `save_path` parameter and only save once, at the
  caller's chosen location.

### B9 [Low] `data_validator.py::is_connected_graph` starts BFS from a hardcoded node index that may not be part of the graph

- `finetuning/data_validator.py:71-73`: `queue = [0]; visited.add(0)`
  regardless of whether point index 0 is referenced by any `Line`. If a
  sample's `Points` list happens to have an unreferenced point at index 0
  (e.g. a hallucinated extra point a model might emit, though this
  function is mainly used offline on the curated dataset), the function
  can report `False` even when every point that IS referenced by `Lines`
  forms one connected component, because BFS never leaves node 0's
  (possibly empty) component. It also KeyErrors if a `Line` references an
  out-of-range index (no bounds check at `data_validator.py:64-67`, unlike
  `metrics.py:129-135` which guards with `p1 < len(points)`).
  `GeometricMetrics.connectivity_score` in `metrics.py` /
  `nemotron3/metrics.py` does not have the seeding issue (it tries every
  unvisited node as a new BFS root).
- Fix: seed BFS from any point index that appears in `Lines`, bounds-check
  line indices, or iterate all unvisited indices as `connectivity_score`
  already does.

### B10 [Low] `nemotron3/run_demo.py` and `nemotron3/fewshot_prompter.py` are near-duplicate implementations

- `run_demo.py` (325 lines) re-implements `FewShotPrompter`'s few-shot
  examples, system prompt, prompt-building, generation, JSON
  extraction/repair, and evaluation loop almost verbatim instead of
  calling into `fewshot_prompter.py`. Any future fix to the repair logic
  or prompt wording has to be applied in two places or they drift apart
  (e.g. `MAX_NEW_TOKENS=128`/`MAX_INPUT_LEN=512` are hardcoded module
  constants in `run_demo.py:45-46` but constructor defaults in
  `FewShotPrompter.__init__` at `fewshot_prompter.py:77`).
- Fix: make `run_demo.py` a thin CLI wrapper around
  `FewShotPrompter(n_samples=7, ...).evaluate()`.

---

## 5. Accuracy Improvement Recommendations (prioritized)

### R1. Fix the dataset before touching the model (A1, A2, A3)

Nothing downstream is trustworthy while the CSVs are stale (A1) and the
split leaks (A2). Concretely: regenerate `data/csvs/` from the current
`utils/create_brep_csvs.py`; cap or thin the translation grid so it does
not dominate the dataset 93%-to-7% (e.g. reduce to a handful of
qualitatively different offsets - translation invariance is a nearly free
thing for a coordinate-regression LLM to learn once a few offsets are
seen, so a dense 51x51 grid buys little and drowns out rotation, the
transform that actually changes the JSON non-trivially); split by
base-shape identity or by held-out transform ranges instead of a flat
shuffle; and grow beyond 4 topological families using
`create_brep_jsons.py` on additional real (Yogesh-method) shapes or
synthetic rectilinear polygons with known medial axes (mirrors
geometry_based R4's PhDdata recommendation - the two phases could even
share an expanded raw-shape corpus).

### R2. Wire up the already-designed geometric loss and curriculum (B4)

`Config.USE_GEOMETRIC_LOSS`/`GEOMETRIC_LOSS_WEIGHT` and
`USE_CURRICULUM`/`CURRICULUM_STAGES` describe a sensible plan (blend
token-level CE with a geometry-aware term; train on I/L before T/Plus)
that simply isn't implemented. A practical version: after each eval epoch,
decode a validation batch, compute `GeometricMetrics.compute_all_metrics`,
and log `combined_score`/`hausdorff` (this reuses the machinery B2 already
half-built); use a Hausdorff-based `metric_for_best_model` via a custom
callback instead of `eval_loss` alone, since token-level loss does not
track geometric correctness (a syntactically-plausible but geometrically
wrong JSON can have low CE loss). For curriculum, sort the training
dataset by shape family (I/L first) and use a `Sampler` or staged
`Dataset` swap keyed on `state.epoch`.

### R3. Fix the MAE/RMSE asymmetry and enrich `combined_score` (B3, B7)

Symmetrize MAE/RMSE the same way `chamfer_distance` already is, and fold
`vertex_count_accuracy` into `combined_score`. Together these stop the
evaluation harness from rewarding degenerate short predictions and stop
"best predictions" rankings from hiding wrong-node-count outputs.

### R4. Constrained / repaired decoding at inference time

Both pipelines already do useful post-hoc repair (`_ensure_lines`,
`_repair` in `nemotron3/inference.py`; `repair_connectivity` in
`finetuning/inference.py`) - keep and strengthen this rather than relying
on the model to emit perfect JSON:
- Port `nemotron3/inference.py::_repair`'s greedy-nearest-pair MST repair
  into `finetuning/inference.py` (B5) so both pipelines guarantee a
  minimal-length connected fix rather than an order-dependent one.
- Consider constrained/grammar-guided decoding (e.g. `outlines`,
  `lm-format-enforcer`, or HF's constrained beam search) to force valid
  JSON syntax during generation rather than only validating after the
  fact - this removes an entire failure category (`json_validity == 0`)
  instead of catching it post-hoc.
- Snap predicted `Points` to the true medial-axis position given the
  profile (nearest equidistant point between the two facing walls) as a
  cheap geometric refinement pass, similar to R7 in the geometry_based
  report.

### R5. Make `run_pipeline.py --full` actually runnable (B1, B6)

Fix the `train_enhanced.py`/`inference_enhanced.py` script-name mismatch
and the relative-path mismatch in the error-analysis step. This is cheap
(a few small edits) and currently blocks the one documented "just run
this" entry point end-to-end, which matters for reproducibility of any
reported numbers.

### R6. Prompt and format design

- `MAX_NEW_TOKENS` (512 in `finetuning/config.py:65` and
  `nemotron3/config.py:30`, but only **128** in
  `nemotron3/fewshot_prompter.py:77` and `run_demo.py:45`) is comfortable
  for the current 4-shape/12-point-max dataset, but should scale with
  R1's data expansion - a Plus-like shape with more branches or an
  expanded PhD-shape corpus produces longer BRep JSON, and 128 tokens is
  tight even for the existing Plus midcurve plus any conversational
  padding the base model adds. Raise it proportionally when R1 lands, per
  the standing guidance to keep max_tokens generous and avoid truncated
  JSON.
- JSON-parsing robustness is a genuine strength here: all main call sites
  (`finetuning/inference.py:38-48`, `finetuning/metrics.py:8-24`,
  `nemotron3/inference.py:109-118`,
  `nemotron3/fewshot_prompter.py:178-208`) do `json.loads` ->
  `ast.literal_eval` fallback, and nemotron3 additionally has proper
  brace-matching + markdown-fence extraction (`_extraction_candidates`).
  Preserve this pattern in new call sites - specifically, prefer
  nemotron3's `_extraction_candidates`/`_try_parse` over the simpler
  `index('{')`/`rindex('}')` slice used in
  `finetuning/inference.py:56-63` and `model_server.py:329-332`, which
  breaks if any stray `{`/`}` appears in surrounding prose before/after
  the real JSON object.
- Port nemotron3's per-family topology hints into `finetuning`'s system
  prompt: `nemotron3/fewshot_prompter.py:57-71` explicitly states "I/bar:
  2 points 1 Line; L: 3 points 2 Lines; Plus/T: central junction with 4/3
  branches", whereas `finetuning/config.py:76-94`'s `SYSTEM_PROMPT` states
  the junction rule only abstractly. Explicit branch-count anchoring is a
  cheap way to reduce topology errors on T/Plus, the shapes that motivate
  the BRep format in the first place.

### R7. Evaluation rigor

- Report metrics separately for "seen shape family, unseen transform" vs.
  "unseen shape family" once R1's split changes land - the current single
  aggregate number conflates interpolation with generalization.
  `evaluate_by_complexity` (`finetuning/evaluate.py:190-215`) already
  groups by shape family; extend it to also group by transform type
  (rotation/scale/translation/mirror), which `error_analysis.py:38-47`
  already extracts via `_get_transform_type` but `evaluate.py` does not
  use. (Note `error_analysis.py:20-23` joins `results_df` and `test_df`
  positionally via `.apply` on the other frame's column - only valid when
  the two CSVs are row-aligned; joining on the `index`/`shape_name`
  columns would be robust to any row drop in evaluation.)
- Cross-check MAE/RMSE against Hausdorff per-sample (B3) as a diagnostic
  during evaluation - a large gap flags degenerate/under-generated
  predictions that the current MAE would otherwise hide.
- Mirror geometry_based's suggested metric suite (edge precision/recall,
  branch-point detection rate) using the already-available `Lines`
  adjacency, so Phase II and Phase III numbers in `benchmark.py` are
  comparable on the same basis.

### R8. Hyperparameters

- `finetuning/config.py`'s `NUM_EPOCHS = 3` with `EARLY_STOPPING_PATIENCE`
  defined-but-unused (B4) means training always runs the full 3 epochs
  regardless of validation trend; wire up early stopping once a geometric
  metric is available (R2) so training doesn't over/under-shoot on a fixed
  epoch count.
- `nemotron3` (`BATCH_SIZE=1`, `GRAD_ACC_STEPS=16`) and `finetuning`
  (`BATCH_SIZE=4`, `GRAD_ACC_STEPS=4`) both reach an effective batch of
  16, which is fine; just note that nemotron3's numbers in CLAUDE.md come
  from a 4B model on a 4 GB-VRAM budget while finetuning's come from a 7B
  model - keep the comparison caveated when reporting cross-pipeline
  results.

---

## 6. Summary Table

| Item | Where | Severity |
|---|---|---|
| A1 `data/csvs/` stale vs. current `config.py`/`create_brep_csvs.py` | utils/create_brep_csvs.py + data/csvs/ | High |
| A2 Train/val/test split leaks near-duplicate transformed variants | utils/create_brep_csvs.py:270-280 | High |
| A3 Only 4 topological families exist anywhere in the dataset | data/brep/ | Medium |
| B1 `run_pipeline.py --full` calls nonexistent `train_enhanced.py` | finetuning/run_pipeline.py:126-129,246 | High |
| B2 `GeometricValidationCallback` is dead code, wastes a generate() pass/epoch | finetuning/train.py:28-91,163 | High |
| B3 MAE/RMSE one-directional (not Chamfer-symmetric) for mismatched point counts | finetuning/metrics.py:53-84 | High |
| B4 Geometric-loss/curriculum/early-stopping config flags entirely unused | finetuning/config.py:46-62 + train.py | Medium |
| B5 `finetuning` repair connects components pairwise, not globally-nearest | finetuning/inference.py:97-160 | Medium |
| B6 `run_pipeline.py` error-analysis step uses bare relative filenames | finetuning/run_pipeline.py:150-163 | Medium |
| B7 `combined_score` ignores MAE/RMSE/vertex_count_accuracy | finetuning/metrics.py:242-256 | Low |
| B8 `plot_results` always overwrites stray CWD file, never closes figure | finetuning/visualize.py:57 | Low |
| B9 `is_connected_graph` BFS seeded at hardcoded node 0, no bounds check | finetuning/data_validator.py:64-73 | Low |
| B10 `run_demo.py` duplicates `fewshot_prompter.py` almost verbatim | nemotron3/run_demo.py | Low |
| R1 Regenerate/rebalance/regroup dataset; expand beyond 4 shape families | - | Priority 1 |
| R2 Wire up geometric loss + curriculum + Hausdorff-based early stopping | - | Priority 1 |
| R3 Symmetrize MAE/RMSE; enrich combined_score | - | Priority 2 |
| R4 Strengthen repair (MST-style) and/or constrained JSON decoding | - | Priority 2 |
| R5 Fix run_pipeline.py script-name and path mismatches | - | Priority 2 |
| R6 Scale MAX_NEW_TOKENS with data growth; unify JSON extraction; per-family prompt hints | - | Priority 3 |
| R7 Split metrics by seen/unseen transform and shape family | - | Priority 3 |
| R8 Wire early stopping into epoch budget once geometric metric exists | - | Priority 3 |
| codeT5/, ludwig/ | notebooks, tested for existence only | Status only |
| prompt/midcurve_generator.py | exploratory, LLM-call loop commented out | Status only |
