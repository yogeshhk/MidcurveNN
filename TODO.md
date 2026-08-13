# TODO.md: Repo-Level Index

Index only, not a duplicate: points at where the real plans/status live so "what's next" from the
repo root gives a global picture without digging through every subfolder.

## Close-out -- 2026-08-13

**Active development on this repo has stopped.** Everything still open was either converted to a
GitHub issue or promoted to a research proposal. Nothing was left half-done on disk.

- **Phase I and Phase II remaining work: filed as GitHub issues.** Seven issue bodies are written
  out in [`reports/github_issues_2026-08-13.md`](reports/github_issues_2026-08-13.md), ready to
  paste. They cover the Phase II dataset/metric items (A1, A2, A3, B7, B10, plus the long-standing
  `nemotron3/results/` test failure) and the Phase I leakage pair (Bugs 7, 11). Each says
  explicitly why it was parked and what a complete fix has to include.
- **Phase III is now a supervised research topic, not a bug list.** Its blocker was always
  architectural rather than a defect. It is written up as a two-page proposal for MS/PhD students:
  [`publications/Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.tex`](publications/Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.tex)
  (compiles to exactly 2 pages, for back-to-back printing). A matching LinkedIn announcement draft
  is in [`reports/linkedin_post_2026-08-13.md`](reports/linkedin_post_2026-08-13.md).
- **Nothing was regenerated or retrained.** See issue 7 in the issues file for why regenerating the
  Phase I datasets without also retraining would have left the repo in a worse state than it is in
  now.

The standing caveat, unchanged and still important: **every headline accuracy figure in this repo
was measured under train/test leakage** and reflects interpolation over 4 base shapes rather than
generalization. This is documented consistently across all three `analysis_report.md` files.

## By approach (long-term research project, three parallel phases)

| Phase | Folder | Status | Known issues / next steps |
|---|---|---|---|
| Phase I: Image-based | `src/image_based/` | Implemented, 7 encoder-decoder variants; all cataloged bugs fixed 2026-08-02 except the augmentation-leakage/dataset-regeneration pair (Bugs 7, 11). 48/48 tests passing. **Bugs 7/11 filed as issue 7, 2026-08-13** -- blocked on a missing `drawsvg` dependency, 4,344 git-tracked data files, and the retraining that would have to accompany regeneration. | See [`src/image_based/analysis_report.md`](src/image_based/analysis_report.md) |
| Phase II: Text/LLM-based | `src/text_based/` | Implemented with caveats: 6 code-level bugs fixed 2026-08-02 (B1, B3, B5, B6, B8, B9), 44/45 tests passing. Reported metrics (QLoRA Qwen2.5-7B: MAE=0.78, PSR=98%) still reflect train/test leakage; fix decided (leave-one-shape-out), **filed as issues 1-6, 2026-08-13**, not executed. Nemotron-Mini-4B few-shot also working. | See [`src/text_based/analysis_report.md`](src/text_based/analysis_report.md) |
| Phase III: Geometry-based | `src/geometry_based/` | Implemented (from-scratch Graph Transformer + fine-tuned Graphormer variant). Node positions roughly learned; **topology not learned at all** (adjacency BCE ~1.15, i.e. chance). Hibernated 2026-08-02; **promoted 2026-08-13 to a written MS/PhD research topic** rather than a bug-fixing effort. | Proposal: [`publications/Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.tex`](publications/Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.tex); technical detail: [`src/geometry_based/analysis_report.md`](src/geometry_based/analysis_report.md) |

## Open problems (from root README's "Pending" section)

- Network-to-network encode/decode (not graph, since graphs are topological/connectivity-based, not spatial)
- Handling different input/output sizes
- Closed -> closed/open and manifold -> manifold/non-manifold transformations

## Not actively tracked here yet

`publications/` (paper/talk archives, including the Midsurface PhD work) is supporting material,
not an active development thread.

## Upgrade session -- 2026-08-02 (`/upgrade-repo-tech`)

6th review pass; see `reports/upgrade_13072026.md` for the prior one (structural hygiene, broken
links, stale CI docs, em-dash cleanup, personal-data relocations -- CODE_OF_CONDUCT.md/issue
templates were explicitly declined by the maintainer there and are not being re-proposed).

- [x] Fix pix2pix's 3 code-level bugs (range mismatch, `np.float` crash, `load_batch` off-by-one)
- [x] Update `src/image_based/analysis_report.md` and `CLAUDE.md` to reflect the pix2pix fixes
- [x] Fix README's stale `references/` paragraph (folder no longer exists at top level; its
      `prompts/` subfolder is now `publications/prompts/`)
- [x] Trim README's dead HTML-commented block: moved env-setup gotchas into `CLAUDE.md` Known
      Gotchas, moved the GAN-suitability design note into `analysis_report.md`, deleted the rest
      (stale training-data-prep notes, old Keras-install notes, pix2pix reference links, a
      "Pending" list duplicating this file, personal "Why Me?" notes)
- [x] Remove duplicate `publications/Midsurface_PhDThesis/publications/TwoPagerNotes/
      Presentation_defense.pptx` (14MB, byte-identical to the copy under `.../Presentation/`)
- [x] Move the Publications/Talks section higher in README.md (now right after the intro
      hook/image, before Repository Structure)
- [x] Legacy `publications/IntroToGeoMod/` ppt/pdf snapshots: zipped into
      `legacy_snapshots_archive.zip` (34.8MB, preserves the originals), 6 loose files removed.
- [x] README Disclaimer email removed, replaced with a link to GitHub Issues as the contact point.
- [x] GitHub repo Description/Topics set by the maintainer (2026-08-02, manual web UI step).

All items from the 2026-08-02 `/upgrade-repo-tech` session are complete.

## Remaining cataloged bugs -- working one by one (started 2026-08-02)

Going through `src/image_based/analysis_report.md`, then `src/geometry_based/analysis_report.md`,
then `src/text_based/analysis_report.md`, highest severity first within each file. Each item is
verified with a real test/script run where possible, not just a syntax check.

### `src/image_based/analysis_report.md`

- [x] Bugs 1, 2, 10 (pix2pix: range mismatch, `np.float` crash, off-by-one) -- fixed earlier
      2026-08-02, verified via `pytest image_based/pix2pix/test_pix2pix.py` (6/6 passed)
- [x] Bugs 3, 4, 13, 20 (img2img: `ImageFolder` crash, missing `import sys`, unused
      `weights_init`, broken progress-print format) -- fixed, verified via
      `pytest image_based/img2img/test_img2img.py` (6/6 passed)
- [x] Bug 22 (dead `_load_models` helper in `test_img2img.py`) -- deleted
- [x] Bug 25 (new, found while verifying Bug 3: img2img `Gen`/`Disc` class-name shadowing) --
      fixed by renaming instances to `generator`/`discriminator`
- [x] Bug 26 (new, found while verifying Bug 3: `test_pix2pix.py` missing `pix2pix/` on
      `sys.path`, breaking its bare sibling imports) -- fixed
- [x] Bug 5 (HIGH) -- denoiser `EarlyStopping(monitor='val_accuracy', min_delta=1)` stopped
      training after ~2 of 500 epochs -- fixed (`val_loss`, patience=20,
      restore_best_weights=True, optimizer adadelta->Adam(1e-3)); construction tests pass,
      full 500-epoch run not executed
- [x] Bug 6 (HIGH) -- all 4 encoder-decoder mains evaluated on training data -- fixed in all
      four by excluding sampled test indices from training; `simple` verified via a full real
      100-epoch training run (~66s), `dense` verified via a partial real run (25/100 epochs,
      no errors), `cnn`/`denoiser` verified via code review + passing construction tests
- [x] Bug 12 (MEDIUM) -- denoiser stale `__main__` trained on unnormalized raw arrays --
      deleted (the real entry point `main_denoiser_encoderdecoder.py` already normalizes
      correctly); also cleaned up imports that became unused
- [x] Bug 8 (MEDIUM) -- dense model saved last-epoch weights, not best -- fixed
      (`restore_best_weights=True`)
- [x] Bug 9 (MEDIUM) -- CNN callbacks monitored train loss instead of val loss -- fixed
      (both `EarlyStopping`/`ReduceLROnPlateau` now monitor `val_loss`)
- [x] Bug 14 (MEDIUM) -- CNN build-file `__main__` NameError + boolean-arg bug -- fixed by
      deleting the stale block (found the same superseded-`__main__` pattern in all 4
      plain-encoder-decoder build files while here; deleted all 4, not just CNN's -- see
      Bugs 8/12/14 notes in the report)
- [x] Bug 15 (LOW) -- pix2pix `binarize` only thresholded the dark side + slow Python loop --
      fixed (vectorized, two-sided threshold)
- [x] Bug 16 (LOW) -- pix2pix test sampling WITH replacement -- fixed (`replace=False`)
- [x] Bug 17 (LOW) -- `pix2pix/config.py` self-import (wrong path depth + fragile pattern) --
      fixed by mirroring `unet/config.py`'s proven `importlib`-based re-export
- [x] Bug 18 (LOW) -- UNet `Adam(decay=...)` breaks on Keras 3 -- fixed with an
      `InverseTimeDecay`-based `_make_adam()` helper reproducing the exact same schedule
- [x] Bug 27 (new, found while verifying Bug 18) -- `unet/test_unet.py` import-ordering bug
      (same class as the documented `unet/test.py` gotcha) -- fixed
- [x] Bug 28 (new, found while verifying Bug 18/27) -- `test_unet.py` asserted a `CoordConv`
      import that never existed in `unet/utils.py` -- fixed the test
- [x] All of image_based's HIGH/MEDIUM bugs and most LOW ones verified via
      `pytest image_based/unet/test_unet.py image_based/pix2pix/test_pix2pix.py
      image_based/img2img/test_img2img.py image_based/testing/test_image_based.py` (green)
- [x] Bug 19 (LOW) -- `unet/datagenerator.py` TRAIN_SIZE coupling + file order shuffled once --
      fixed (uses real `len(files)`, reshuffles every epoch)
- [x] Bug 21 (LOW) -- `unet/utils.py get_coord_layers` assumed square images, rebuilt per batch --
      fixed (per-axis normalization + `lru_cache`); verified for a non-square case manually
- [x] Bug 23 (LOW) -- `utils/metric_utils.py print_best_metrics` KeyError on empty best_metrics --
      fixed with a graceful early-return guard
- [x] Bug 24 (LOW) -- `utils/prepare_data.py` paired Profile/Midcurve files by independent sort --
      fixed (explicit filename-substitution pairing, warns and skips orphans)

**All of `src/image_based/analysis_report.md` is now resolved except Bugs 7 and 11**, both
deferred as a single larger, separate task (bigger infra change: split by base shape, regenerate
`image-pairs/`, `unet-splits/`, `images-combo/` from scratch). Every fix verified via
`pytest image_based/unet/test_unet.py image_based/pix2pix/test_pix2pix.py
image_based/img2img/test_img2img.py image_based/testing/test_image_based.py` (48/48 passed), plus
real end-to-end training runs for `simple`/`dense` and a manual non-square check for
`get_coord_layers`.

- [ ] Bug 7 (MEDIUM) -- augmentation-level leakage in all splits (shared root cause across all
      3 phases per the "Code Analysis Reports" note in `CLAUDE.md`) -- NOT fixed by Bug 6;
      held-out samples can still be rotated/translated variants of a training shape. **Split
      strategy decided 2026-08-02: leave-one-shape-out** -- see "Decided, ready to execute next
      session" below.
- [ ] Bug 11 (MEDIUM) -- `unet-splits/` cannot be regenerated from raw data -- related to Bug 7,
      same decided fix applies (regenerate together, once execution starts)

### `src/geometry_based/analysis_report.md` -- HIBERNATED (2026-08-02)

Per the maintainer: Phase III (geometry-based) is not ready at all right now. Not picking up
bug-fixing here until the maintainer explicitly says to revisit it -- don't propose this as
"next work" in the meantime.

### `src/text_based/analysis_report.md` -- in progress, started 2026-08-02

Bigger and higher-stakes than `image_based` (QLoRA fine-tuning of a 7B model, not small
Keras/PyTorch models) -- fixes here are code/logic-only and verified with synthetic data or
static checks, NOT with real training runs (impractical in this session). Split into "safe to
fix now" (pure code/logic, no training needed) vs. "needs a decision first" (dataset
regeneration, or design choices about wiring up unused config).

**Safe fixes -- done:**
- [x] Bug B1 (HIGH) -- `run_pipeline.py --full`/`--train` called nonexistent `train_enhanced.py`
      / referenced `inference_enhanced.py` -- fixed to `train.py`/`inference.py`; confirmed
      `inference.py` genuinely accepts `--single`/`--num_samples`
- [x] Bug B3 (HIGH) -- `metrics.py` MAE/RMSE were one-directional (not Chamfer-symmetric) for
      mismatched point counts, letting degenerate short predictions score artificially low --
      fixed (symmetric averaging, same approach as the existing `chamfer_distance`). Verified:
      a 1-point prediction matching one of 3 true points went from a "perfect" MAE of 0.0 to a
      correct 3.536.
- [x] Bug B5 (MEDIUM) -- `finetuning/inference.py`'s repair connected components pairwise in
      BFS-discovery order instead of by true nearest pair -- ported `nemotron3/inference.py`'s
      proven MST-style greedy-nearest-pair algorithm. Verified: a synthetic 3-component case
      dropped total connection length from ~137.9 (old) to 70.12 (new).
- [x] Bug B6 (MEDIUM) -- `run_pipeline.py`'s error-analysis step used bare relative filenames
      that only worked if manually copied into the CWD -- fixed to match `evaluate.py`'s and
      `config.py`'s real paths.
- [x] Bug B8 (LOW) -- `visualize.py::plot_results` always overwrote a stray `midcurve_result.png`
      in the CWD -- added an optional `save_path` param, defaults to not saving internally at
      all (the one real caller, `evaluate.py`, already does its own save+close). Verified: zero
      stray files produced.
- [x] Bug B9 (LOW) -- `data_validator.py::is_connected_graph` seeded BFS at a hardcoded node 0
      (wrong if point 0 is unreferenced) and had no bounds-check on line indices (KeyError risk)
      -- fixed both. Verified 3 synthetic cases (unreferenced-point-0, out-of-range index,
      genuinely-disconnected) all now behave correctly.
- [x] All 5 files syntax-checked; full suite re-run: `pytest text_based/testing/
      test_text_based.py` -- 44/45 passed. The 1 failure
      (`test_34_nemotron3_results_placeholder_exists`) is pre-existing and unrelated: the whole
      `nemotron3/results/` directory doesn't exist on disk, and nothing in `nemotron3/` was
      touched this session. Not fixed (out of today's scope).

**Still open, no decision yet:**
- [ ] Bug A3 (MEDIUM, dataset) -- only 4 topological families exist; expanding needs new shape
      authoring (content creation, not a code fix). Not brainstormed 2026-08-02; revisit later.
- [ ] Bug B7 (LOW) -- `combined_score` ignores MAE/RMSE/vertex_count_accuracy -- not yet
      addressed. Not purely mechanical: it needs a weighting decision on how much each metric
      should count, which is a modelling judgement rather than a bug fix.
- [ ] Bug B10 (LOW) -- `nemotron3/run_demo.py` duplicates `fewshot_prompter.py` almost verbatim
      -- not yet addressed (lower priority, left for a future pass).

## Decided, ready to execute (brainstormed 2026-08-02; items 3 and 4 executed 2026-08-07)

**Status: 3 and 4 are done. 1 and 2 remain, and are a session of their own.** Items 3 and 4 were
pure deletions verifiable against the test suite, so they were taken first: the dead callback and
nine unused config constants are gone, `pytest text_based/testing/test_text_based.py` still reports
44 passed with the one pre-existing `nemotron3/results/` failure, unchanged from before the edit.
Two details worth carrying forward: the open question about `use_cache` is answered (leave it, the
removed callback held the only `generate()` call in `train.py`, so that line is purely about
gradient checkpointing), and `VALIDATION_SAMPLES` had to go too, which the original decision did
not list, since the deleted callback was its only consumer.

Items 1 and 2 are deliberately not started. They regenerate `image-pairs/`, `unet-splits/`,
`images-combo/` and `data/csvs/`, which invalidates any existing checkpoint's split and means the
headline QLoRA figures (MAE 0.78, PSR 98%) have to be re-measured afterwards, most likely coming
out worse since they currently benefit from the leakage being removed. That is the point of the
fix, but it is not a tail-end job.


Four decisions made in a short brainstorm at the end of the 2026-08-02 session. Each is written
here as a self-contained, executable instruction so a future session can act on it directly
without re-deriving the reasoning or re-reading the full `analysis_report.md` entries.

### 1. Dataset split strategy: leave-one-shape-out

Applies to **both** `image_based` Bugs 7/11 and `text_based` Bugs A1/A2 -- the same underlying
fix, since all three phases share the same 4 base shapes and the same augmented-variant-leakage
failure mode (documented as a shared root cause in `CLAUDE.md`'s "Code Analysis Reports" note).

- Decision: split train/test/val by **base shape identity**, not by a flat shuffle over
  augmented variants. E.g. train on I/L/T, test entirely on Plus (or some rotation of which
  shape is held out); no augmented variant of the held-out shape appears in training at all.
- Rejected alternative: held-out transform ranges (e.g. reserve rotations 150-180 degrees) --
  keeps all 4 shapes in both splits but still risks family-level overfitting since the model has
  seen the shape itself, just not that exact transform. Leave-one-shape-out is the cleaner test
  of true generalization.
- To execute:
  - `image_based`: regenerate `image-pairs/`, `unet-splits/`, `images-combo/` from
    `utils/prepare_data.py`, grouping by base shape before splitting (fixes Bugs 7, 11).
  - `text_based`: regenerate `data/csvs/` from `utils/create_brep_csvs.py`, grouping by base
    shape before splitting (fixes Bug A2; do this together with item 2 below, which also touches
    `create_brep_csvs.py`, so both land in the same regeneration pass -- fixes Bug A1 too).
  - Caveat: with only 4 shapes total, leave-one-shape-out means holding out 1 of 4 (25% of
    families) for test -- small, but the report's own alternative (transform-range holdout) is
    weaker. Revisit if Bug A3 (more shape families) ever gets picked up -- more shapes make this
    split more statistically meaningful.

### 2. text_based Bug A1: thin the translation grid

- Decision: reduce `TRANSLATE_X_START/STOP/STEP` and `TRANSLATE_Y_START/STOP/STEP` in
  `text_based/utils/config.py` from the current 51x51 dense grid (-50..50 step 2 each axis) down
  to a handful of qualitatively different offsets per axis (~5-10 each), per the report's R1
  reasoning: translation invariance is nearly free for a coordinate-regression LLM to learn from
  a few examples, so a dense grid buys little and drowns out rotation (the transform that
  actually changes the BRep JSON non-trivially).
- Rejected alternative: keep the dense config but randomly subsample translated variants at
  CSV-build time in `create_brep_csvs.py` -- rejected in favor of just fixing the config directly
  (simpler, and keeps `config.py`'s ranges honest about what actually gets generated).
- To execute: edit `text_based/utils/config.py`'s translation range constants, then regenerate
  `data/csvs/` (same pass as item 1's `text_based` split-by-shape change -- both are config/data
  regeneration, do them together).
- Note: regenerating `data/csvs/` invalidates any existing fine-tuned checkpoint's original
  train/val/test split.

### 3. text_based Bug B2: remove `GeometricValidationCallback` -- DONE 2026-08-07

- Decision: delete the dead callback in `finetuning/train.py` (the per-epoch `try` block, roughly
  `train.py:28-91`, that calls `model.generate()` on up to 10 samples every epoch but never
  appends to `metrics_list`, so the `if metrics_list:` block never runs). Stops the wasted
  compute (a full generation pass every epoch with no result) immediately.
- Rejected alternative: implement it properly (wire to `GeometricMetrics.compute_all_metrics`) --
  rejected for now as more work than justified today; revisit together with Bug B4 if/when
  geometric-loss + curriculum learning ever gets implemented (R2), since a working per-epoch
  geometric validation metric is a prerequisite for Hausdorff-based early stopping anyway.
- To execute: delete the callback code in `train.py`; also check `train.py:163`'s
  `use_cache=False if USE_GRADIENT_CHECKPOINTING else True` line, since that was disabling the KV
  cache globally partly to support the (now-removed) per-epoch `generate()` calls -- confirm
  whether it's still needed for anything else before deciding whether to touch it too.

### 4. text_based Bug B4: strip unused config flags -- DONE 2026-08-07

- Decision: remove `USE_GEOMETRIC_LOSS`, `GEOMETRIC_LOSS_WEIGHT`, `TOKEN_LOSS_WEIGHT`,
  `USE_CURRICULUM`, `CURRICULUM_STAGES`, `EARLY_STOPPING_PATIENCE`, `EARLY_STOPPING_METRIC`, and
  `CHECKPOINT_METRICS` from `finetuning/config.py` (`config.py:46-62`), since none of them are
  referenced anywhere in `train.py` and they currently just document behavior that doesn't exist.
  Also note `EARLY_STOPPING_METRIC = "hausdorff_distance"` doesn't even match the real metric key
  name (`"hausdorff"`) `metrics.py` produces -- another reason not to leave it sitting there
  unimplemented.
- Rejected alternative: keep as an intentional documented roadmap marker -- rejected because it
  currently reads as implemented behavior, not a roadmap note; misleading as-is.
- Also rejected (for now): implementing it (wiring geometric loss + curriculum + Hausdorff-based
  early stopping into `train.py`) -- real design/engineering work, explicitly deferred to a
  future session, not stripped-and-forgotten. If that future work happens, do it together with
  Bug B2 (implement properly instead of removing) rather than after removal.
- To execute: delete the 8 unused config fields; grep `finetuning/` once more first to
  double check `augmentation.py` (which does use `AUGMENTATION_NOISE_LEVEL`/
  `AUGMENTATION_MULTIPLIER`, per the report -- those two are NOT part of this removal, only the
  8 geometric-loss/curriculum/early-stopping ones are).
