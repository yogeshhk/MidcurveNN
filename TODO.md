# TODO.md: Repo-Level Index

Index only, not a duplicate: points at where the real plans/status live so "what's next" from the
repo root gives a global picture without digging through every subfolder. First TODO.md for this
repo; no prior per-folder TODOs existed to link to, so entries below are grounded in each
approach's own `analysis_report.md` and the root `README.md`'s "Pending" section instead.

## By approach (long-term research project, three parallel phases)

| Phase | Folder | Status | Known issues / next steps |
|---|---|---|---|
| Phase I: Image-based | `src/image_based/` | Implemented, 7 encoder-decoder variants proposed; 3 variants currently non-functional (pix2pix/img2img crashes, denoiser stops after ~2 of 500 epochs); UNet stable. See report for details. | See [`src/image_based/analysis_report.md`](src/image_based/analysis_report.md) |
| Phase II: Text/LLM-based | `src/text_based/` | Implemented with caveats: reported metrics (QLoRA Qwen2.5-7B: MAE=0.78, PSR=98%) reflect train/test data leakage (near-duplicate augmented variants of same 4 base shapes); see report for generalization concerns. Nemotron-Mini-4B few-shot also working. | See [`src/text_based/analysis_report.md`](src/text_based/analysis_report.md) |
| Phase III: Geometry-based | `src/geometry_based/` | Implemented (from-scratch Graph Transformer + fine-tuned Graphormer variant); comprehensive evaluation still ongoing (preliminary status) | See [`src/geometry_based/analysis_report.md`](src/geometry_based/analysis_report.md) |

## Open problems (from root README's "Pending" section)

- Network-to-network encode/decode (not graph, since graphs are topological/connectivity-based, not spatial)
- Handling different input/output sizes
- Closed -> closed/open and manifold -> manifold/non-manifold transformations

## Not actively tracked here yet

`publications/` (paper/talk archives, including the Midsurface PhD work) and `references/` (prompt
templates, research notes) are supporting material, not active development threads.
