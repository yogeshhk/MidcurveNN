# Standardization proposal: naming, dataset, driver, environment, packaging

Scope: structure only (folder naming, dataset layout and split manifest, one driver, environment, package layout).
No model-level fixes. Static analysis only; nothing was moved or changed. All numbers below were counted on disk.

## 0. Key findings that shape the proposal

- 110 `.py` files under `src/`; 17 `__init__.py`; `config.py` x6, `train.py` x5, `prepare_plots.py` x5,
  `prepare_data.py` x4, `evaluate.py` x3, `metrics.py`/`inference.py`/`dataset_loader.py` x2. These
  same-name modules are the root of the `sys.modules['config']` and `utils` collisions.
- 94 `sys.path` manipulations across the repo (`conftest.py`, `benchmark.py`, every `main_*.py`, `test_*.py`,
  unet, nemotron3, finetuning). None of them is needed once the code is an installable package.
- Raw data in `src/data/raw/` is 201 files: 4 base shapes as `.dat`/`.mid` pairs (I, L, T, Plus), `PhDdata/`
  (173 entries: `.dat` plus Bayazit/Yogesh decomposition `.txt`), `PhDShapes/` (20 PNGs).
  `src/config.py` points `JSON_FOLDER` to `data/raw/Jsons`, which does not exist.
- Data is derived four separate ways from the same 4 shapes:
  - image: `image_based/data/` = image-pairs 896 + images-combo 448 + unet-splits 3000 = 4,344 files (the git-tracked count);
  - text: `text_based/data/brep/*.json` (4 hand-authored BRep files, the effective true source for text) -> `csvs/midcurve_llm*.csv`
    (the CLAUDE.md mentions "shapes2brep.csv" and sequences.json as well);
  - geometry: `graph_dataset.MidcurveGraphDataset("data/raw")` reads `.dat/.mid` directly and augments in memory;
  - `text_based/utils/config.py` sets `RAW_DATA_FOLDER = text_based/data/brep` (a different meaning of "raw").
- A base-shape split already exists but only for image data: `utils/prepare_data.py` has `BASE_SHAPES`,
  `TEST_SHAPES=('Plus',)`, `VAL_SHAPES=('T',)`, `split_indices_by_base_shape()`. It is not shared by text or geometry.
  This is the seed of the shared manifest (reuse it, do not reinvent).
- Frameworks: TF/Keras only in simple/cnn/dense/denoiser/pix2pix/unet and `utils/`; PyTorch in img2img, all geometry,
  all text. `environment.yml` (name `midcurvenn`, py3.10, numpy 1.24, TF>=2.13 + keras 2.13.1 + torch + PyG + HF + peft/trl/bnb +
  drawsvg) vs the `genai` env used in practice (drawsvg missing); a third `image_based/unet/env/environment.yml` exists.
  `text_based/finetuning/requirements.txt` is a fourth dependency list.
- No CI, none to be added (standing preference). Tests: 3 central suites (`*/testing/`, wired in `pytest.ini`) plus
  per-folder `test_*.py` files that `pytest.ini` does NOT collect (testpaths lists only the 3 `testing/` dirs).

## 1. Current-state inventory

| Folder | Purpose | Issues |
|---|---|---|
| `src/config.py` | Global UNet/image config, `RAW_DATA_FOLDER` | Name collides with 5 other `config.py`; dead `JSON_FOLDER`; mixes UNet hyperparameters with data paths |
| `src/benchmark.py` | Cross-approach benchmark | 6+ `sys.path.insert`; per-approach `if` ladder; own argparse; duplicate metric code (iou, chamfer) also in `text_based/*/metrics.py` |
| `src/data/raw/` | Canonical raw `.dat/.mid` + `PhDdata`, `PhDShapes` | Only I/L/T/Plus have trainable pairs; PhD files are a different format family (decomposition txt); no manifest of shapes |
| `src/utils/` | `prepare_data` (DrawSVG, augment, split), `prepare_plots`, `metric_utils` (Keras), `create_ds` | Name `utils` shadowed by `unet/utils.py` and `text_based/utils/`; TF/matplotlib lazy-import workaround; image-specific code in a "shared" folder; `create_ds.py` is a legacy synthetic generator (draw_T, draw_I...) |
| `image_based/` | Phase I | `data/` inside the approach folder (4,344 tracked files) |
| `image_based/{simple,cnn,dense,denoiser}encoderdecoder/` | 4 Keras AEs | Names: no separators, long, suffix `encoderdecoder`; files `build_*_model.py` + `main_*.py` + `test_*.py` + notebook + stray PNGs in folder root; `.gitignore` per folder |
| `image_based/unet/` | UNet 2-stage | Different layout (`train.py`, `test.py`, `unet.py`, own `config.py`, `utils.py`, `env/`, `training_run.log`, `run_stage2_only.py`); `test.py` is an evaluation script, not a test (confusing for pytest); import-order hack |
| `image_based/pix2pix/`, `img2img/` | GAN Keras / PyTorch | Own `config.py`; names are algorithms not task; `img2img` is also Pix2Pix (PyTorch) so the two are the same family split by framework; `images/`, `logs/` at root |
| `image_based/kaggle/` | notebook only | Not code-structured; orphan |
| `image_based/testing/` | Phase I tests | Plus per-folder tests that are not collected |
| `geometry_based/graph_transformer/` | Phase III primary | Own `prepare_plots.py`, `train.py`, `evaluate.py`, loose PNGs, `PHASE2_DOCUMENTATION.md` (name says Phase 2, code is Phase III), `training_run.log`, `checkpoints/` |
| `geometry_based/finetuned_graph_transformer/` | Graphormer FT | Very long name; `test.py` and `test_*.py` both; sys.path hacks |
| `geometry_based/gnnencoderdecoder/` | Stub | Legacy, unimplemented; uses `main_*`/`build_*` naming unlike its siblings |
| `text_based/finetuning/` | Qwen QLoRA pipeline | Describes a stage not a model; 22 flat files; alias files `config_enhanced.py`/`metrics_enhanced.py`; own `requirements.txt`; `pipeline_output/` |
| `text_based/nemotron3/` | Nemotron-Mini | Duplicate `config/dataset_loader/inference/evaluate/metrics` of `finetuning/`; version-suffixed name; `train.py` + `train_unsloth.py` + trainers |
| `text_based/codeT5/`, `ludwig/`, `prompt/` | Notebooks and prompt scripts | Mixed case (`codeT5`), notebook-only folders, typo filenames (`Ludiwg`), PNG assets in root |
| `text_based/utils/` | BRep JSON/CSV pipeline | Second `utils`, second `config`, second `prepare_data`, second `prepare_plots`; `backup/` with `hub`, `orig` (stale code) |
| `text_based/data/` | brep JSON, csvs, sequences.json, shapes2brep.csv | Derived views live beside a hand-authored source (`brep/`) |
| `*/testing/` + pytest.ini | 3 central suites | Collide on `config`; need guard test 24; per-folder tests uncollected |
| `src/environment.yml` | Env | See section 5 |
| `reports/`, `publications/` | Docs / papers | Out of scope except path references |

## 2. Naming convention (target rules)

1. Folders: lowercase, snake_case, no version numbers or framework words, nouns for models: `<family>/<arch>/`.
2. Family folders keep the existing `*_based` names (they are in README, papers, and CLAUDE.md); shorten only if the user wants a bigger break (option below).
3. Arch folder names: `simple_ae`, `dense_ae`, `cnn_ae`, `denoiser_ae`, `unet`, `pix2pix` (merge `img2img` in as `pix2pix/torch` variant, see 4.2), `graph_transformer`, `graphormer_ft`, `gnn_ae`, `qlora_qwen`, `nemotron`, `codet5`, `ludwig`, `prompting`.
4. Every arch folder has the same file names: `README.md`, `__init__.py`, `model.py`, `train.py`, `evaluate.py`, `predict.py` (optional), `test_<arch>.py` (or tests under the family `tests/`), `notebooks/` for ipynb, `results/` (gitignored except one `results_grid.png`).
5. Registry entry point per arch: `train(cfg)`, `evaluate(cfg)` functions. This is the only thing the driver calls.
6. No loose PNG/logs in arch roots: images go to `results/` or `docs/images`, logs to `results/logs` (gitignored).
7. Test files named `test_<family>.py` in `src/tests/<family>/`.

Minimal-overhaul option (recommended): keep the `*_based` family names and apply rules 3-6 only to arch folders. Alternative (bigger): rename families to `image/`, `text/`, `graph/`; not recommended, it touches README, 6 papers, issues and CLAUDE.md.

## 3. Target layout

```
MidcurveNN/
  pyproject.toml                 # makes `midcurve` installable (pip install -e src) ; or setup.cfg
  environment.yml                # ONE env (moved from src/), name midcurvenn
  README.md  CLAUDE.md  TODO.md  CHANGELOG.md  CONTRIBUTING.md
  src/
    midcurve/                    # the package (no sys.path hacks)
      __init__.py
      cli.py                     # python -m midcurve  (or src/run.py thin shim)
      config.py                  # paths + global constants ONLY (no hyperparameters)
      registry.py                # {(family, arch): module path}
      data/
        __init__.py
        raw/                     # canonical source (moved from src/data/raw, unchanged contents)
        manifest.json            # shape list, base-shape groups, split roles, content hash
        splits.py                # leave-one-shape-out logic (lift from utils/prepare_data.py)
        loaders.py               # read_shape(name) -> {profile, midcurve, brep}
        views/                   # build_image_view, build_text_view, build_graph_view
        derived/                 # gitignored generated views (image/, text/, graph/)
      common/
        metrics.py               # one chamfer/hausdorff/iou/topology implementation
        plots.py                 # merged prepare_plots (results grid)
        brep.py                  # BRep helpers from text_based/utils
      image_based/  simple_ae/ dense_ae/ cnn_ae/ denoiser_ae/ unet/ pix2pix/
      geometry_based/ graph_transformer/ graphormer_ft/ gnn_ae/
      text_based/   qlora_qwen/ nemotron/ codet5/ ludwig/ prompting/
    run.py                       # `python run.py ...` thin wrapper calling midcurve.cli.main
    tests/
      conftest.py  test_driver.py  test_data.py  image_based/  geometry_based/  text_based/
      pytest.ini (or in pyproject)
  scripts/                       # one-off helpers (create_ds legacy)
  reports/  publications/
```

Package name `midcurve` (not `src`) so `from midcurve.data import splits` never collides with anything. Because every module is namespaced, the 6 `config.py` files and 4 `prepare_data.py` files can coexist unchanged by name.

## 4. Specific standards

### 4.1 Dataset: one source, derived views, one manifest

- Canonical source = `data/raw/<Shape>.dat` + `<Shape>.mid` (existing, 4 trainable shapes). The hand-authored BRep JSONs in `text_based/data/brep/` carry topology (Lines/Segments) that `.dat/.mid` lacks, so declare them the second canonical file set: `data/raw/brep/<Shape>.json`. A `data.check` command verifies that the JSON Points agree with `.dat/.mid`.
- `PhDdata/` and `PhDShapes/` stay under `data/raw/` but are listed in the manifest as `role: "unused_for_training"` (decision for the user).
- `manifest.json` fields: schema_version, shapes[{name, files, sha256, n_profile_pts, n_mid_pts, family}], splits{test:[...], val:[...], train:[...]}, folds (the 4 leave-one-shape-out folds: hold out each of I/L/T/Plus in turn), views{image:{img_size, aug params, n_files}, text:{...}, graph:{...}}.
- Split rule: assignment is made on the base-shape name only, never on a file. Default fold equals the current `TEST_SHAPES=('Plus',)`, `VAL_SHAPES=('T',)` (so nothing changes until the user picks), with `--fold k` for the other 3 rotations. Every view builder takes the manifest; every training loader filters by `base_shape(file)` from the manifest. Add a test: no base shape in two roles, and no derived file whose prefix is in test when loading train.
- Derived views are written to `src/midcurve/data/derived/<view>/` (gitignored in the end state), each with a `VIEW.json` stamp {builder version, manifest hash, drawsvg version}. The current 4,344 tracked files stay exactly as they are during migration (see 4.1.1).
- 4.1.1 Do not regenerate casually: the build commands are dry-run by default (`data build --view image` prints the plan and file counts, writes nothing); writing requires `--write` and refuses when `drawsvg` cannot be imported or when it would overwrite tracked files unless `--allow-overwrite-tracked`. First-stage migration only repoints loaders at the existing folders via `config.py` paths (no data movement). The git-tracked-files decision (untrack with `git rm --cached` vs keep) is for the user to run; this analysis does not run git.
- Image view geometry (PNG sizes 100 vs 256) is an `ImageViewSpec` dataclass in the manifest instead of scattered `IMG_SHAPE` constants.

### 4.2 Merge candidates (user decision)
`img2img` (PyTorch) and `pix2pix` (Keras) implement the same model. Proposal: one `pix2pix/` folder with `keras.py` and `torch.py`, so TF has fewer entry points. `finetuning/` (Qwen) and `nemotron/` share config/dataset/metrics/inference shapes; unify by moving shared code to `text_based/common/` and leave trainer-specific files in each.

### 4.3 One driver: `python src/run.py <cmd>`

Subcommands:

| Command | Behavior | Wraps today |
|---|---|---|
| `data check` | validate raw vs manifest vs derived stamps | new |
| `data build --view image\|text\|graph [--write]` | dry-run by default | `utils/prepare_data.py`, `text_based/utils/create_brep_*.py` |
| `data split --fold k` | print/write split roles | `split_indices_by_base_shape` |
| `train --approach image\|text\|graph --arch X [--quick] [--fold k]` | calls `registry[(approach, arch)].train(cfg)` | each `main_*.py`/`train.py` |
| `eval --approach ... --arch X` | calls `.evaluate(cfg)`, writes `results/metrics.json` in a common schema | each `evaluate.py`/`test.py` |
| `benchmark [--approaches ...]` | reads `metrics.json` files produced by `eval` and prints the table | `benchmark.py` |
| `test [--family f] [--quick]` | runs pytest subsets | pytest.ini |
| `list` | prints the registry (families, archs, framework, deps) | new |

Integration:
- Registry (`registry.py`) maps names to module path strings, lazily imported, so `list`/`data` work without TF or torch (preserves the lazy-import constraint in CLAUDE.md).
- Phase 1 of the driver is argv-forwarding: each registry entry stores the existing script path and the driver runs `runpy`/`subprocess` with the current cwd conventions. No model code is edited. Phase 2 (after package move) replaces that with function calls.
- `benchmark.py` becomes `midcurve/benchmark.py`: the per-approach functions turn into thin readers of the common `metrics.json`; metric functions come from `common/metrics.py`; kept `python benchmark.py` shim for README compatibility.
- `config.py`: split into `midcurve/config.py` (paths, seeds, fold) and per-arch `Config` dataclasses living in each arch folder (UNet hyperparameters leave global config). The driver passes `cfg` objects; CLI overrides use `--set key=value`.
- Tests: driver test checks `list` runs with no TF/torch, `data build` is a dry run by default, and each registry entry imports (skip-guarded when deps missing). Keep the lightweight subset `-k "not model and not unet_import"` working.

### 4.4 Common result schema
`results/metrics.json`: {approach, arch, fold, split, n, chamfer, hausdorff, topology_acc, notes, manifest_hash, leakage_free: bool}. The `leakage_free` flag is true only if the run used the manifest split. This directly supports the CLAUDE.md warning about leaked headline numbers.

## 5. Environment

Current: `midcurvenn` yml (TF>=2.13, keras==2.13.1 pinned, numpy 1.24, torch, PyG, HF stack, drawsvg) plus a `genai` env in practice plus `unet/env/environment.yml` plus `finetuning/requirements.txt`.

Proposal:
1. One `environment.yml` at the repo root, name `midcurvenn`. Delete the 3 stray lists after confirmation (move to `reports/` archive, not delete).
2. Split into two optional environments rather than one monster: `environment.yml` (core: numpy, pandas, pillow, matplotlib, scipy, torch, pytest, drawsvg, tqdm) and `environment-llm.yml` (adds transformers, peft, trl, bitsandbytes, accelerate, fastapi, uvicorn, wandb). Reason: LLM stack pins conflict with TF/numpy 1.24; keeps the GPU/bitsandbytes pieces optional, and lets `genai` be retired or declared as the LLM env.
3. Consolidate to PyTorch where cheap. Cost by arch:
   - img2img already PyTorch: becomes the single `pix2pix` (cheap, delete Keras pix2pix after parity check; the pix2pix Keras data loader and 3 Colab notebooks are retired to notebooks/).
   - simple/dense/cnn/denoiser AEs: small models, port is low-medium effort each (~50-150 lines); they are the first candidates after the driver exists. Their `_build()` pattern maps to `nn.Module.__init__`.
   - unet: 8-level UNet + CoordConv + custom WBCE losses + two-stage; port is high effort and changes headline numbers; do NOT port in this standardization (leave TF as the one optional TF island, extra `environment-tf.yml`) or the user decides later.
   - Outcome: core env is torch-only, TF becomes an optional extra for unet/AEs until ported. Order: pix2pix merge, then AEs, last unet.
4. Pin `drawsvg` in core yml and also note GTK/cairo requirement (known Windows `libcairo-2` error). Add `python -m midcurve doctor` printing which of drawsvg, torch, tf, peft, cairo import OK, since the drawsvg absence in `genai` is currently invisible until a data build fails.
5. Do not use pip/venv; per user rules launch with `conda run -n midcurvenn python ...`.

## 6. Removing the `config` and `utils` hacks

Root cause: top-level, non-namespaced modules (`config`, `utils`, `prepare_plots`...) imported via `sys.path` insertion. Under `midcurve/` every import becomes absolute and unique:

- `from midcurve.config import ...` vs `from midcurve.text_based.nemotron.config import Config`: no `sys.modules['config']` clash; the stale-cache guard in test 24 and the `unet/test.py` `sys.modules.pop('utils')` block are deleted.
- `unet/utils.py` becomes `midcurve/image_based/unet/coord.py` (rename, content unchanged); `get_coord_layers` imports from there.
- `utils/prepare_plots.py`, `geometry_based/graph_transformer/prepare_plots.py`, `text_based/utils/prepare_plots.py` (3 plus 2 more): diff and merge into `common/plots.py` where equal; keep arch-specific plotters under their arch with unique names (`plots_graph.py`).
- `text_based/finetuning/config_enhanced.py` and `metrics_enhanced.py` alias files: the CLAUDE.md says never delete; keep them as shims at the new location, or leave a deprecation comment (user decision).
- Package install: `pip install -e .` inside the conda env (pyproject at repo root with `package-dir = src`), so `conftest.py` sys.path logic disappears. If the user dislikes pip -e under conda, fall back to a single `conftest.py` path insert of `src/` only (one line, not 94).

Intermediate, lower-risk step available before the full move (stage A): keep folders where they are and only add `src/midcurve_compat` ... not recommended; skip. Instead use stage order in section 8.

## 7. Rename / move map (old -> new) and what it breaks

| Old path | New path | Breaks |
|---|---|---|
| `src/config.py` | `src/midcurve/config.py` (+ UNet constants to `image_based/unet/config.py`) | `from config import *` in unet/pix2pix/tests; CLAUDE.md "config collision" paragraph; test 24 |
| `src/benchmark.py` | `src/midcurve/benchmark.py` (+ shim `src/benchmark.py`) | README/CLAUDE commands `python benchmark.py`; its 6 sys.path lines |
| `src/conftest.py`, `src/pytest.ini` | `src/tests/conftest.py`, `pyproject.toml [tool.pytest]` | CLAUDE.md "Run tests" commands (paths change to `src/tests/...`) |
| `src/environment.yml` | `environment.yml` (+ `environment-llm.yml`) | README setup section, CLAUDE.md "Environment Setup", unet/README |
| `src/data/raw/` | `src/midcurve/data/raw/` | `RAW_DATA_FOLDER` users: `utils/prepare_data.py`, graph_dataset, text config, docs mention `src/data/raw`; large-ish git rename but content identical |
| `src/utils/prepare_data.py` | `midcurve/data/views/image.py` + `data/splits.py` (split fn) | `from utils.prepare_data import ...` in image tests/main files; lazy-import guard note |
| `src/utils/prepare_plots.py` | `midcurve/common/plots.py` | unet/test.py, 7 main_*.py, tests; CLAUDE.md prepare_plots docs |
| `src/utils/metric_utils.py` | `midcurve/image_based/_keras_callbacks.py` | image AE trainers |
| `src/utils/create_ds.py` | `scripts/create_ds_legacy.py` | nothing known (verify by grep) |
| `src/image_based/data/*` | `midcurve/data/derived/image/*` (stage 2, only if user approves moving 4,344 tracked files) | all image loaders; datasets listed in issue 7; keep in place in stage 1 and point config at them |
| `image_based/simpleencoderdecoder` | `image_based/simple_ae` | its tests, README, notebooks, CLAUDE.md table, analysis_report, publications mention |
| `image_based/denseencoderdecoder` | `image_based/dense_ae` | same |
| `image_based/cnnencoderdecoder` | `image_based/cnn_ae` | same; also saved `models/` dirs path |
| `image_based/denoiserencoderdecoder` | `image_based/denoiser_ae` | imports from simple (`from simpleencoderdecoder...`) |
| `build_<x>_encoderdecoder_model.py` / `main_<x>_encoderdecoder.py` | `model.py` / `train.py` | all imports; test files |
| `image_based/img2img` + `pix2pix` | `image_based/pix2pix/{torch_impl,keras_impl}` (optional merge) | tests, `_tensor_to_gray_list`, grids path docs |
| `image_based/unet/{train,test}.py` | `unet/train.py`, `unet/evaluate.py` (rename test.py) | CLAUDE.md "unet/test.py" gotchas; pytest collection ambiguity removed |
| `image_based/unet/utils.py` | `unet/coord.py` | `from utils import get_coord_layers` |
| `image_based/kaggle/` | `image_based/simple_ae/notebooks/` | none known |
| `image_based/testing/`, `geometry_based/testing/`, `text_based/testing/` | `src/tests/<family>/` | pytest.ini testpaths; CLAUDE.md test commands; test 24 guard |
| `geometry_based/graph_transformer` | unchanged name; loose PNGs -> `results/`; `PHASE2_DOCUMENTATION.md` -> `README` section | docs links |
| `geometry_based/finetuned_graph_transformer` | `geometry_based/graphormer_ft` | README table, CLAUDE.md, TODO.md, carousel/paper mentions |
| `geometry_based/gnnencoderdecoder` | `geometry_based/gnn_ae` (or delete stub; user decision) | none functional |
| `text_based/finetuning` | `text_based/qlora_qwen` | CLAUDE.md commands (`cd src/text_based/finetuning`), run_pipeline paths, README, TODO |
| `text_based/nemotron3` | `text_based/nemotron` | gitignore entries for `nemotron3/results/...`; CLAUDE.md; test 34 |
| `text_based/codeT5` | `text_based/codet5` | case-only rename: needs two-step rename on Windows (git is case-insensitive here) |
| `text_based/ludwig`, `prompt` | `text_based/ludwig`, `text_based/prompting` | README references |
| `text_based/utils/*` | `midcurve/common/brep.py`, `data/views/text.py` | `from config import RAW_DATA_FOLDER`, create_brep_* scripts |
| `text_based/utils/backup` | `reports/archive/` or delete (user) | none |
| `text_based/data/brep/*.json` | `data/raw/brep/*.json` | text config, dataset loaders |
| `text_based/data/{csvs,sequences.json,shapes2brep.csv}` | `data/derived/text/` | training scripts' default CSV paths |
| `text_based/finetuning/requirements.txt`, `unet/env/environment.yml` | `reports/archive/` | docs mentioning them |

## 8. Safe migration order

Principle: add first, move later; each stage leaves tests passing and is independently committable by the user. Test baseline before starting: record the current pass counts (Phase I 48/48, Phase II 44/45, Phase III per its suite).

1. Stage 0: baseline and dry-run report (read-only).
2. Stage 1: add the `data/manifest.json` + `splits.py` + `common/metrics.py` as NEW files, nothing existing changed. Add driver `run.py` with `list`, `data check`, `test`, `benchmark` forwarding to existing scripts.
3. Stage 2: package skeleton `midcurve/` with `pyproject.toml`; `pip install -e` in env; point driver at old locations via registry paths. Tests unchanged.
4. Stage 3: move non-model shared code (config, utils, benchmark, tests dir) and fix imports; delete sys.path hacks in the same step per file; update pytest config.
5. Stage 4: rename arch folders (one family per step: text, then geometry, then image), with `__init__` shims? No shims; update imports, READMEs, CLAUDE.md in the same step.
6. Stage 5: move raw data and (if approved) derived data; point manifest views at them.
7. Stage 6: env consolidation (yml files), torch ports (pix2pix merge, AEs) as separate later tasks.
8. Stage 7: docs sweep: README, CLAUDE.md (remove obsolete gotchas), TODO.md, analysis_report links, CHANGELOG.

## 9. Sonnet-executable action list

Legend: B = bulk operation (multi-file move/rename/edit) -> present plan and wait for user confirmation for THAT step, per the user's working rules. Effort in Sonnet-hours (S <1h, M 1-3h, L >3h). No git commands anywhere; user commits between steps. Always use Edit/Write tools; write long scripts to a file then run.

1. Baseline. Run `cd src && conda run -n genai python -m pytest -q` (and `midcurvenn` if different), record counts into `src/proposal/baseline.txt`. Accept: counts recorded. S. Not bulk.
2. Create `src/data/manifest.json` (new file) listing shapes I, L, T, Plus with file names and sha256 (computed by a throwaway script in the scratchpad), default split from `TEST_SHAPES`/`VAL_SHAPES`, and the 4 folds. Accept: JSON loads; hashes match `certutil`/`hashlib`. S. Not bulk.
3. Add `src/midcurve/data/splits.py` with `load_manifest()`, `base_shape(path)`, `split_roles(fold)`; copy logic from `utils/prepare_data.py` lines 55-112 (do NOT delete the original yet; make the original import from the new one in a later step). Add `src/tests/test_splits.py` (3 tests: disjoint roles, prefix parsing for the 4 shapes plus a rotated PNG name, default fold equals current constants). Accept: new tests pass and old suites unchanged. S. Not bulk.
4. Add `src/midcurve/common/metrics.py` consolidating chamfer/hausdorff/iou (read `benchmark.py`, `text_based/finetuning/metrics.py`, `nemotron3/metrics.py` and keep numerics identical; add a test comparing old and new on random arrays). Do not replace old callers yet. Accept: parity test passes. M. Not bulk.
5. Write `src/run.py` (argparse subcommands `list`, `data check`, `data split`, `test`, `benchmark`, `train`, `eval`) and `src/midcurve/registry.py` with registry entries pointing at existing scripts (phase 1 forwarding via `subprocess` with `cwd` equal to each script's folder to match the documented commands). Accept: `python run.py list` works without TF or torch; `python run.py benchmark --approaches geometry` reproduces `python benchmark.py --approaches geometry`; `python run.py data build --view image` prints a plan and writes nothing (verify via directory listing and file count still 4,344). M. Not bulk (new files only).
6. Add `src/pyproject.toml` (or root) making `midcurve` installable; run `conda run -n midcurvenn pip install -e .` only after user says OK (changes the env). Accept: `python -c "import midcurve"` OK. S. Ask user (env change).
7. Fix `src/config.py` dead `JSON_FOLDER`; add `MANIFEST_PATH`, `DERIVED_ROOT` constants only (no moves). Accept: tests unchanged. S. Not bulk.
8. B. Move tests: relocate `*/testing/` to `src/tests/<family>/`, update `pytest.ini` testpaths, `conftest.py`, doc test commands. Accept: same pass counts as baseline (48, 44/45, geometry unchanged). M.
9. B. Replace `sys.path.insert` hacks with package imports, one family at a time (text first, image last), per file list from `grep -rl sys.path`. After each family: run its suite. Remove test 24 guard and unet import-order block only when the full suite passes. Accept: `grep -rn "sys.path" src --include=*.py` returns only the benchmark shim (if kept). L per family.
10. B. Rename arch folders per section 7, one family per sub-step, updating imports, per-folder README, family README, CLAUDE.md directory tree and Common Commands, analysis_report path mentions, TODO.md, `.gitignore` nemotron3 lines. Case-only rename `codeT5 -> codet5` via a temp name. Accept: suites pass; `grep -rn "encoderdecoder\|nemotron3\|finetuning/" ` finds only historical docs (CHANGELOG, reports). M-L per family.
11. B (optional, needs user choice): merge `img2img` into `pix2pix`; unify `finetuning` and `nemotron` shared modules. Accept: suites pass and `eval` outputs match previous numbers within tolerance. L.
12. B (needs per-step confirmation, touches 4,344 tracked files): move `image_based/data` to `data/derived/image/` and `text_based/data` derived files to `data/derived/text/`; update loaders via config constants only. Dry-run first: list source, destination contents, file counts; after the move list destination and confirm count 4,344 and sizes. Accept: image tests pass; file counts identical; user runs git. M.
13. B. Make view builders honor the manifest: `utils/prepare_data.py` -> `data/views/image.py` (dry-run default, `--write`, drawsvg check, refusal to overwrite tracked data); text and graph builders likewise. Hook split loaders in train/eval of each arch to `split_roles(fold)` ONLY for the data-selection line (model code untouched; other analysts own model fixes). Accept: `data build` dry-runs; a test asserts no test-shape file reaches train. M-L. Coordinate with the issue-7 retraining requirement: do not use `--write` until the user decides.
14. Environment: write root `environment.yml` (core, torch + drawsvg) and `environment-llm.yml`; archive the other 3 dependency lists to `reports/archive/`; add `python run.py doctor`. Accept: `conda env create --dry-run` (or `conda env export` diff) shows no conflict; doctor lists import status. M. Ask the user before archiving and before creating any env.
15. Torch ports (separate, later, per arch): pix2pix Keras retire, then simple/dense/cnn/denoiser. Each: port `model.py`, run old and new on the same fold, compare IoU/Chamfer in `metrics.json`. unet excluded. L each.
16. Common results schema: make every `evaluate` write `results/metrics.json`; rewrite `benchmark` to read them. Accept: `run.py benchmark` prints one table covering all three families without importing TF/torch. M.
17. Docs sweep: README (setup, commands, layout), CLAUDE.md (new tree, drop collision gotchas, add driver/manifest section, keep "do not regenerate datasets" and "no CI" notes), TODO.md, CONTRIBUTING.md, each arch README header block. Accept: link checker script (write to scratchpad) finds no broken relative links; grep for old paths clean outside `reports/` and CHANGELOG. M.
18. Final: re-run full suites, record counts vs baseline, write summary into `CHANGELOG.md`. Accept: counts >= baseline. S.

Bulk steps needing per-step user confirmation: 8, 9, 10, 11, 12, 13 (and 14 for archiving, 6 for env). Steps 1-5, 7, 15-16 add or edit single areas and can proceed after one overall go-ahead, but the user's working-style rule applies if the user prefers each phase confirmed.

## 10. Decisions to ask the user, one at a time (each with a recommendation)

1. Package name and install style: `midcurve` + `pip install -e` (recommended) / conftest one-line path / keep as is.
2. Family folder names: keep `*_based` (recommended) / rename to image,text,graph.
3. Merge `img2img` into `pix2pix` (recommended yes) and nemotron/finetuning shared code (recommended later).
4. Move the 4,344 derived files, or leave in place and only repoint (recommended: leave in place until a retraining pass happens, since issue 7 couples regeneration with retraining).
5. Default leave-one-shape-out fold and whether reporting should average all 4 folds (recommended: report all 4 folds, headline = mean).
6. PhDdata/PhDShapes role: out of the training manifest (recommended) / include as extra eval-only set.
7. Env split core vs LLM (recommended) and TF as optional extra until unet is ported.

## 11. Risks and non-goals

- Windows: case-only rename (`codeT5`), long paths, forward slashes in docs, `libcairo` for drawsvg.
- Renaming arch folders invalidates saved `models/` and `weights/` paths and any Colab/Kaggle notebooks with hard-coded paths; notebooks are listed but not auto-fixed.
- Publications and zipped archives reference old names; leave as historical.
- All headline metrics stay marked as leaked until runs are redone under the manifest split; the driver's `leakage_free` flag makes that explicit rather than fixing it.
- No CI will be added (standing preference); `run.py test` is local only.
- Out of scope: model bug fixes, retraining, regenerating datasets, git operations.
