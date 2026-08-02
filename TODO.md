# TODO.md: Repo-Level Index

Index only, not a duplicate: points at where the real plans/status live so "what's next" from the
repo root gives a global picture without digging through every subfolder. First TODO.md for this
repo; no prior per-folder TODOs existed to link to, so entries below are grounded in each
approach's own `analysis_report.md` and the root `README.md`'s "Pending" section instead.

## By approach (long-term research project, three parallel phases)

| Phase | Folder | Status | Known issues / next steps |
|---|---|---|---|
| Phase I: Image-based | `src/image_based/` | Implemented, 7 encoder-decoder variants; all cataloged bugs fixed 2026-08-02 except the augmentation-leakage/dataset-regeneration pair (Bugs 7, 11), deliberately deferred as a larger task. 48/48 tests passing. | See [`src/image_based/analysis_report.md`](src/image_based/analysis_report.md) |
| Phase II: Text/LLM-based | `src/text_based/` | Implemented with caveats: reported metrics (QLoRA Qwen2.5-7B: MAE=0.78, PSR=98%) reflect train/test data leakage (near-duplicate augmented variants of same 4 base shapes); see report for generalization concerns. Nemotron-Mini-4B few-shot also working. | See [`src/text_based/analysis_report.md`](src/text_based/analysis_report.md) |
| Phase III: Geometry-based | `src/geometry_based/` | Implemented (from-scratch Graph Transformer + fine-tuned Graphormer variant); comprehensive evaluation still ongoing (preliminary status) | See [`src/geometry_based/analysis_report.md`](src/geometry_based/analysis_report.md) |

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
      held-out samples can still be rotated/translated variants of a training shape. Deferred.
- [ ] Bug 11 (MEDIUM) -- `unet-splits/` cannot be regenerated from raw data -- related to Bug 7,
      deferred alongside it

### `src/geometry_based/analysis_report.md` -- HIBERNATED (2026-08-02)

Per the maintainer: Phase III (geometry-based) is not ready at all right now. Not picking up
bug-fixing here until the maintainer explicitly says to revisit it -- don't propose this as
"next work" in the meantime.

### `src/text_based/analysis_report.md` -- in progress, started 2026-08-02
