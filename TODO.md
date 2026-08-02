# TODO.md: Repo-Level Index

Index only, not a duplicate: points at where the real plans/status live so "what's next" from the
repo root gives a global picture without digging through every subfolder. First TODO.md for this
repo; no prior per-folder TODOs existed to link to, so entries below are grounded in each
approach's own `analysis_report.md` and the root `README.md`'s "Pending" section instead.

## By approach (long-term research project, three parallel phases)

| Phase | Folder | Status | Known issues / next steps |
|---|---|---|---|
| Phase I: Image-based | `src/image_based/` | Implemented, 7 encoder-decoder variants proposed; pix2pix's 3 bugs (sigmoid/tanh range mismatch, `np.float` crash, `load_batch` off-by-one) fixed 2026-08-02, not yet re-run end-to-end; img2img still crashes; denoiser still stops after ~2 of 500 epochs; UNet stable. See report for details. | See [`src/image_based/analysis_report.md`](src/image_based/analysis_report.md) |
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
