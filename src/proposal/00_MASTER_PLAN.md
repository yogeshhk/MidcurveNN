# MidcurveNN upgrade: master plan (v2, three independent tracks)

Date: 2026-11-01. Status: PROPOSAL ONLY. Nothing in the repo has been changed except this folder.
Supersedes v1 (which merged the three approaches into one package; rejected by the user, since each
approach is a separate R&D line with its own paper).

Detail, code snippets and file:line evidence live in the sub-reports:

- `01_image_based_proposal.md` - image track, 17 items, PyTorch code for every trick
- `02_llm_based_proposal.md` - text/LLM track, phases A-F
- `03_graph_based_proposal.md` - graph track, 16 items, feasibility answer
- `04_standardization_proposal.md` - naming/driver ideas (only the per-approach parts still apply)
- `05_publications_triage.md` - what in `publications/` stays live and what gets zipped

Item ids from the sub-reports are cited as `[01-7]`, `[02-A-01]`, `[03-5]`, `[04-9]`.
Where a sub-report puts new code in a merged or differently named location, use the template in
section 2 of this file instead.

## 1. Principles (decided with the user)

1. **Three independent approaches**: `image_based/`, `text_based/`, `geometry_based/`. There is no
   shared code between them, and each approach has its own paper.
2. **Only the raw data is shared**, in `src/data/raw/`. Each approach turns it into its own form
   with its own `prepare_data.py`: images, JSON text, or a graph.
3. **Raw data gains explicit midcurve edges** (decided 2026-11-01). The `.mid` files list points
   only, which is why the graph code chains them wrongly for T and Plus. Add `<Shape>.edges` next
   to each `.mid`: ASCII, one `i j` pair per line, 0-based indices into the `.mid` points. The
   topology is taken from `text_based/data/brep/*.json` `Lines`. The `.dat` and `.mid` files stay
   untouched.
4. **Inside each approach, only the network differs.** Every model of that approach uses the same
   dataset file, the same split, the same loss options and the same evaluation.
5. **A cross-paper convention, not shared code.** Every approach splits by shape name (never by
   file), reads the split from one shared file `src/data/raw/splits.json`, and reports at least
   Chamfer and Hausdorff on the final midcurve polyline in raw units. That keeps numbers comparable
   across the three papers if ever needed.

## 2. The per-approach template (same names in all three)

```
<approach>_based/
  README.md            how to prepare data, train, evaluate; results table
  run.py               ONE driver: python run.py prepare|train|eval|predict --model <name> [--tag t] [--quick]
  prepare_data.py      raw (.dat/.mid/.edges + splits.json) -> data/dataset_v<N>.<ext>   (one file)
  dataset.py           loads that one file; returns (input, target, shape_name, split)
  evaluate.py          ONE metric set for this approach + the cross-paper Chamfer/Hausdorff
  models/
    __init__.py        REGISTRY = {"name": module}; each module exposes build_model(cfg)
    <model>.py         one file per network, short snake_case name
  data/
    dataset_v1.<ext>   the single training-data file for this approach
  runs/                git-ignored; runs/<model>__<tag>/{metrics.json, grid.png, log.csv, best.pt, args.json}
  tests/test_<approach>.py
  _legacy/             old folders moved here only after the new path reproduces them (per-item confirm)
```

| Approach | Dataset file | Models (file names) |
|---|---|---|
| image_based | `data/dataset_v1.npz` (inputs, targets, shape ids, split; rasterised in memory with OpenCV, no drawsvg) | `simple_ae`, `dense_ae`, `cnn_ae`, `denoiser_ae`, `unet`, `pix2pix` (img2img merged in), `skeleton` (classical baseline) |
| text_based | `data/dataset_v1.jsonl` (one row per sample: profile text, midcurve text, shape, split, transform) | `qwen_qlora`, `nemotron_qlora`, `codet5`, `fewshot_prompt`, `lmstudio_prompt` |
| geometry_based | `data/dataset_v1.json` (profile ring with closing edge, midcurve nodes + edges, shape, split) | `classical` (Voronoi baseline), `set_transformer` (new, recommended), `graph_transformer` (existing, kept as v1) |

Naming rules: lowercase snake_case, no framework or version words in model names, one role per
file, no module called `config.py` or `utils.py` inside the new files (this avoids the
`sys.modules` collisions recorded in CLAUDE.md).

## 3. Execution order

Global rules for the executor (paste into any subagent prompt):

- Never run any git command.
- Use the Edit and Write tools for every file change. No heredocs, no `sed`. Write longer scripts
  to a file first, then run them.
- Launch Python only via `conda run -n <env> python ...` from `D:/Yogesh/GitHub/MidcurveNN/src`.
- ASCII-only console output.
- Never run `utils/prepare_data.py` as a script (it deletes `images-combo/` and `unet-splits/`).
- No package installs, model downloads or GPU use without asking the user.
- Present each phase's plan and wait for the user's go-ahead. Items marked [CONFIRM] need their
  own confirmation.
- After each phase, run that approach's tests plus the legacy suite and report pass/fail against
  the baseline.
- Markdown images use `![alt](images/x.png)` followed by `*Image file: images/x.png*`.

### Phase 0 - shared raw data and trust fixes (about 3 h, no GPU)

- R-0.1 Baseline test counts into `src/proposal/baseline.txt` `[04-1]`. Check the env (torch,
  scipy, shapely, networkx, cv2, skimage, transformers, peft, trl) in `genai` and `midcurvenn`.
- R-0.2 Write `src/data/raw/{I,L,T,Plus}.edges` from the brep JSON `Lines`. First map brep point
  order to `.mid` point order by coordinates. Expected: I {0-1}, L {0-1, 1-2}, T {0-1, 1-2, 1-3},
  Plus {0-1, 1-2, 1-3, 1-4} `[03-4]`. Report any disagreement between the brep JSON and `.mid` to
  the user rather than picking one.
- R-0.3 Write `src/data/raw/splits.json`: shape -> role for the default fold (current
  `TEST_SHAPES=Plus`, `VAL_SHAPES=T`), plus the 4 leave-one-shape-out folds.
- R-0.4 Text quick fixes: repair the double-encoded CSVs with a backup `[02-A-01]`, make the parsers
  robust `[02-A-02]`, fix the few-shot prompter `[02-A-04]`.
- R-0.5 Note in `TODO.md` that the legacy headline numbers are leaked or unverified, and that the
  UNet "best" grid is collapsed.

### Track I - image_based (about 1 day of work + 3-6 h CPU)

- I-1 Create the template files (section 2). `prepare_data.py` rasterises from raw + `.edges` with
  3 input channels: outline, filled mask, distance transform `[01-3]`. On-the-fly pose
  augmentation in `dataset.py`.
- I-2 `evaluate.py`: pixel F1@2px after skeletonising + Chamfer/Hausdorff on the traced polyline
  `[01-5]`.
- I-3 Loss options: soft target + positive-weighted BCE + Dice `[01-4]`.
- I-4 `models/*.py` for all 7 names, with GroupNorm and batch size 1 tested `[01-6]`.
  pix2pix = UNet-lite generator + PatchGAN `[01-12]`.
- I-5 `run.py` + tests + overfit test `[01-7, 01-8]`.
- I-6 Experiments: pose-level runs for every model, the ablation, then leave-one-shape-out
  `[01-9..11]`. The `skeleton` baseline is the floor to beat.
- I-7 [CONFIRM] Move the old folders (`simpleencoderdecoder/` ... `img2img/`, `kaggle/`) to
  `image_based/_legacy/`.

### Track G - geometry_based (about 1.5 days + 1-3 h CPU)

- G-1 Template files. `prepare_data.py` builds graphs from raw + `.edges`. This fixes the wrong
  T/Plus edges and the PyG batching bug, because the new path uses plain torch with no PyG
  `[03-2, 03-7]`.
- G-2 `evaluate.py` with the graph metric set `[03-5]`; P1 check: the MST rule reproduces the
  `.edges` files `[03-4]`.
- G-3 `models/classical.py` (Voronoi baseline) `[03-6]`.
- G-4 `models/set_transformer.py` + Hungarian set loss `[03-8, 03-9]`. Edges come from the MST.
- G-5 Optional procedural generator `[03-3]`. It writes NEW raw files (`.dat/.mid/.edges`) into
  `src/data/raw/generated/`, so the other approaches can use the same shapes later without sharing
  code. [CONFIRM] before writing many files.
- G-6 Experiments and the P1-P5 table `[03-13]`.
- G-7 [CONFIRM] Retire `finetuned_graph_transformer/` and `gnnencoderdecoder/` to `_legacy/`
  `[03-15]`.

### Track T - text_based (about 2 days CPU; GPU only when asked)

- T-1 Template files. `prepare_data.py` builds `dataset_v1.jsonl` from raw + `.edges`, with
  canonical pose and the formats json / mcv1 (integer coordinates) / mcv2 (recipe)
  `[02-B-02, B-03, B-05, B-06]`.
- T-2 One prompt template shared by training and inference `[02-B-07]`. `evaluate.py` with the new
  metrics and baselines `[02-A-05, B-08]`.
- T-3 `models/lmstudio_prompt.py` + smoke test `[02-C-01..04]`. The user runs LM Studio, which
  gives the first trustworthy numbers with no training.
- T-4 [CONFIRM, GPU] `models/qwen_qlora.py` etc. with answer-only loss and the same precision for
  training and evaluation `[02-D-01..03]`.
- T-5 Result matrix `[02-F-01]`.
- T-6 [CONFIRM] Move `finetuning/`, `nemotron3/`, `codeT5/`, `ludwig/`, `prompt/` to `_legacy/`
  `[02-E]`.

### Phase P - publications

- P-1 [CONFIRM] Zip the archive list in `05_publications_triage.md` (dry run, then zip, then list
  the zip sizes).
- P-2 After the tracks have new results, update the live LaTeX items with them.

## 4. Decisions (2026-11-01)

- D1 Env: `genai`. `midcurvenn` does not exist.
  - Available in `genai`: torch 2.7.1+cu118 with CUDA, torchvision 0.22, scipy 1.15,
    networkx 3.2, cv2 4.11, skimage 0.25, TF 2.18, transformers 4.57, peft 0.18, trl 0.13,
    openai 2.32.
  - shapely is installed but FAILS to import (numpy DLL error), and drawsvg is missing. New code
    uses neither.
- D2 Order: the three tracks run IN PARALLEL (user, 2026-11-01), one agent per approach.
- D3 Image size 128.
- D4 LLM format and base model: open; ask before any GPU training.
- D5 Publications: three new papers, and the comprehensive paper is kept. See `05` for the archive
  and move decisions.
- Raw `.edges` + `splits.json` were written on 2026-11-01. The brep JSON midcurve points match the
  `.mid` files exactly, in the same order.
- `publications/prompts/` stays in MidcurveNN and becomes the text track's `check-model` tool.
