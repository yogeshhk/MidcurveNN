# 08 Reorganisation plan: one template for image_based, geometry_based, text_based

Date: 2026-11-03. Authorised by the user for this task only (the earlier rule "no file moves without confirmation" is
overridden here). Behaviour-preserving: no algorithm, loss, data or metric change; no training; the collinear-node label bug
in prepare_data is NOT fixed.

## Status (update after every sub-step)

- Done: baseline tests, plan, dry-run manifest (`08_moves.csv`, 96 rows, 0 collisions).
- Done: image_based (moves 41 rows in `08_moves_done.csv`, imports, run.py, collect_results, READMEs, notebooks, tests equal to baseline,
  checkpoint load OK for 6 methods).
- Done: geometry_based (moves, imports, run.py, READMEs, notebooks, tests equal to baseline, checkpoint load OK).
- Done: text_based (moves, imports, run.py, READMEs, notebooks, tests equal to baseline).
- Done: docs (approach README/TODO, root README, CLAUDE.md, TODO.md, RESULTS_image/graph, 06_EXECUTION_PLAN, .gitignore),
  `run_all_tests.py`, src `pytest.ini`/`conftest.py`, `benchmark.py` paths, `08_rollback.py` (dry run: 96 moves, 0 conflicts).
- Done: final verify (table below). ALL STEPS COMPLETE on 2026-11-03.
- Resume (not needed now): `08_moves_done.csv` lists the 96 moves (resumable: `08_mover.py exec <approach>` skips done rows).
  Roll back with `python proposal/08_rollback.py --dry-run` (dry-run first) then without the flag.
  Mover script copy: `proposal/08_mover.py` (same spec that produced `08_moves.csv`).

## Layout decisions (user, 2026-11-03; they replace the first draft of the brief)

1. Old code stays at each method's top level, unchanged apart from path and import fixes. Its README, notebooks, old results and
   old weights stay with it. There is no `legacy/` folder.
2. The "standard" version built in the last sessions goes in `methods/<method>/enhanced/`: `model.py` (from
   `<approach>/models/<x>.py`), `README.md`, `runs/<split>__<tag>/`, `tests/`. Future improvements of a method go inside that
   method. `img2img` (PyTorch pix2pix) goes to `methods/pix2pix/img2img/`.
3. Methods with no old implementation (set_transformer, classical_voronoi, skeleton, fewshot_prompt, lmstudio_prompt) keep
   `model.py`, `runs/`, `tests/` at the method top level, no `enhanced/`. graph_transformer, finetuned_graph_transformer and
   gnn_encoder_decoder are old code and stay at their own top level.
4. Text: `finetuning/` becomes the top level of `methods/qwen_qlora/`, `nemotron3/` the top level of `methods/nemotron_qlora/`;
   new versions in each one's `enhanced/`. The `config_enhanced.py` / `metrics_enhanced.py` alias files stay.
5. `REGISTRY` maps the CLI name (unchanged: `--model unet`, `simple_ae`, `set_transformer`, ...) to the module that holds the
   current driver (`methods.<name>.enhanced.model` or `methods.<name>.model`).
6. Old tests from `testing/` go to the owning method's `tests/`; tests that span methods go to `<approach>/tests/`.

## Template

```
src/<approach>/
  README.md  TODO.md  run.py  pytest.ini  conftest.py
  common/    shared code: dataset, evaluate, losses, prepare_data, geometry helpers, shared blocks
  data/      approach data (unchanged location)
  docs/      analysis_report.md and approach-level docs
  tests/     approach-level contract tests (and test_legacy_<approach>.py, the old cross-method suite)
  methods/
    __init__.py        REGISTRY
    <method>/          snake_case; README.md; old code, notebooks, results and weights at top level
      enhanced/        model.py, README.md, runs/<split>__<tag>/, tests/   (only where an old implementation exists)
      model.py, runs/, tests/   (methods that have only new code)
```

Rationale: one folder per method holds everything about it (old and new code, runs, tests, README); `models/` that held only
`.py` files, `tests/` next to `testing/`, and `runs/` next to `runs_smoke/` are gone; the three approaches look the same.

Deviations forced by the code (recorded here):

- Method-local legacy tests (`test_unet.py`, `test_pix2pix.py`, ...) stay beside the old code at the method top level: they
  are old code, unchanged except for paths, and their sys.path ordering (documented gotcha) depends on their folder.
- Smoke run folder name is `smoke__<split>` (the tag is always "smoke").
- `tests/` folders have no `__init__.py` (several `tests` packages would collide). Test file names are unique per approach.
- The new contract tests (`test_image_track.py`, `test_graph_track.py`, `test_text_track.py`) stay whole in `<approach>/tests/`:
  they iterate the registry or exercise `common/` and cannot be cleanly split by method without rewriting them.
- Empty `testing/__init__.py` files are kept as `tests/legacy_testing_init.py` (no deletions allowed).
- Run-folder naming: `methods/<m>/[enhanced/]runs/<split>__<tag>/`; the old `<model>__<split>__<tag>` is derived by `run.py`
  only for `--out` overrides.
- Import scheme: image/geometry `run.py` puts its own folder first on `sys.path` and imports `common.*` and `methods.*`
  as top-level packages; text keeps its package form (`text_based.common.*`, `text_based.methods.*`). Because the three
  approaches share the package names `common` and `methods`, each approach's tests run in its own process
  (`src/run_all_tests.py`).

## Method mapping

| approach | method folder | old code at top | enhanced/ or model.py |
|---|---|---|---|
| image | simple_encoder_decoder (+ kaggle/) | simpleencoderdecoder | enhanced (simple_ae) |
| image | dense_encoder_decoder | denseencoderdecoder | enhanced (dense_ae) |
| image | cnn_encoder_decoder | cnnencoderdecoder | enhanced (cnn_ae) |
| image | denoiser_encoder_decoder | denoiserencoderdecoder | enhanced (denoiser_ae) |
| image | unet | unet | enhanced (unet) |
| image | pix2pix (+ img2img/) | pix2pix | enhanced (pix2pix) |
| image | skeleton | none | model.py |
| geometry | set_transformer | none | model.py |
| geometry | classical_voronoi | none | model.py |
| geometry | graph_transformer | yes (frozen negative result) | none |
| geometry | finetuned_graph_transformer | yes (retired) | none |
| geometry | gnn_encoder_decoder | yes (retired stub) | none |
| text | fewshot_prompt, lmstudio_prompt | none | model.py |
| text | qwen_qlora | finetuning/ | enhanced |
| text | nemotron_qlora | nemotron3/ | enhanced |
| text | code_t5, ludwig, manual_prompt (was prompt/) | yes | none |

Common: image `common/` = dataset, evaluate, losses, prepare_data, collect_results, blocks (was `models/_blocks.py`).
geometry `common/` = geom, dataset, evaluate, losses, prepare_data. text `common/` = canonical, formats, recipes, prompts,
prompt_templates/ (was `prompts/`; renamed so it does not clash with `prompts.py`), dataset, evaluate, prepare_data, sft_common,
utils/ (the old BRep CSV pipeline; used only by its own scripts and the legacy tests).

## Per-approach before and after (folder level)

image_based before: cnnencoderdecoder/ denoiserencoderdecoder/ denseencoderdecoder/ simpleencoderdecoder/ unet/ pix2pix/
img2img/ kaggle/ models/ runs/ runs_smoke/ tests/ testing/ + dataset, evaluate, losses, prepare_data, collect_results, run.
after: common/ data/ docs/ tests/ methods/{simple_encoder_decoder, dense_encoder_decoder, cnn_encoder_decoder,
denoiser_encoder_decoder, unet, pix2pix(+img2img), skeleton} + run.py, README, TODO.

geometry_based before: graph_transformer/ finetuned_graph_transformer/ gnnencoderdecoder/ models/ runs/ tests/ testing/ + geom,
dataset, evaluate, losses, prepare_data, run. after: common/ data/ docs/ tests/ methods/{set_transformer, classical_voronoi,
graph_transformer, finetuned_graph_transformer, gnn_encoder_decoder}.

text_based before: finetuning/ nemotron3/ codeT5/ ludwig/ prompt/ prompts/ models/ utils/ tests/ testing/ + canonical, formats,
recipes, prompts, dataset, evaluate, prepare_data, run. after: common/ data/ docs/ tests/ methods/{fewshot_prompt,
lmstudio_prompt, qwen_qlora, nemotron_qlora, code_t5, ludwig, manual_prompt}.

The full folder-level move list is `08_moves.csv` (old_path, new_path, type). Not moved: `image_based/data/`, `text_based/data/`,
`geometry_based/data/`, `src/data/raw/`, `src/utils/`, `src/config.py`, `src/proposal/`. `src/models/` is empty and removed at
the end if truly empty.

## Baseline (before any move), `conda run -n genai python -m pytest <target> -q`, one process each

| suite (old path) | passed | failed | skipped / error | note |
|---|---|---|---|---|
| image_based/tests | 25 | 0 | 0 | |
| geometry_based/tests | 20 | 0 | 0 | |
| text_based/tests | 32 | 0 | 0 | |
| image_based/testing | 24 | 0 | 0 | |
| geometry_based/testing | 13 | 0 | 2 skipped | |
| text_based/testing | 46 | 1 | 0 | test_34 (nemotron3/results sample csv absent), pre-existing |
| unet/test_unet.py | 12 | 0 | 0 | |
| pix2pix/test_pix2pix.py | 6 | 0 | 0 | |
| img2img/test_img2img.py | 6 | 0 | 0 | |
| simpleencoderdecoder/test_simple_encoderdecoder.py | 8 | 0 | 0 | |
| finetuned_graph_transformer/test_finetuned_graph_transformer.py | 7 | 4 | 0 | test_04..07 (deprecated HF Graphormer API), pre-existing |
| graph_transformer/test_graph_transformer.py | 13 | 2 | 0 | test_12, test_13 (loss signature mismatch), pre-existing |
| finetuning/test_metrics.py | 0 | 0 | 1 collection error | `metrics_enhanced` not importable when run from src/; pre-existing |

| cnnencoderdecoder/test_cnn_encoderdecoder.py | 6 | 1 | 0 | test_04 (`autoencoder` attribute), pre-existing |
| denseencoderdecoder/test_dense_encoderdecoder.py | 7 | 0 | 0 | |
| denoiserencoderdecoder/test_denoiser_encoderdecoder.py | 8 | 0 | 0 | |

## After (2026-11-03, `run_all_tests.py`, one process per suite)

| suite (new path) | before | after |
|---|---|---|
| image_based/tests (new 25 + legacy 24) | 25 + 24 passed | 49 passed |
| geometry_based/tests (new 20 + legacy 15) | 20 passed; 13 passed, 2 skipped | 33 passed, 2 skipped |
| text_based/tests (new 32 + legacy 47) | 32 passed; 46 passed, 1 failed | 78 passed, 1 failed (same test_34) |
| methods/unet/test_unet.py | 12 passed | 12 passed |
| methods/pix2pix/test_pix2pix.py | 6 passed | 6 passed |
| methods/pix2pix/img2img/test_img2img.py | 6 passed | 6 passed |
| methods/simple_encoder_decoder/test_simple_encoderdecoder.py | 8 passed | 8 passed |
| methods/cnn_encoder_decoder/test_cnn_encoderdecoder.py | 6 passed, 1 failed | 6 passed, 1 failed (same test_04) |
| methods/dense_encoder_decoder/test_dense_encoderdecoder.py | 7 passed | 7 passed |
| methods/denoiser_encoder_decoder/test_denoiser_encoderdecoder.py | 8 passed | 8 passed |
| methods/graph_transformer/test_graph_transformer.py | 13 passed, 2 failed | 13 passed, 2 failed (same) |
| methods/finetuned_graph_transformer/test_finetuned_graph_transformer.py | 7 passed, 4 failed | 7 passed, 4 failed (same) |
| methods/qwen_qlora/test_metrics.py | collection error | collection error (same, `metrics_enhanced` not on path) |

No new failures. Checkpoint loads (read-only script, one forward pass): cnn, denoiser, dense, pix2pix, simple, unet (image)
and set_transformer (geometry). Text has no checkpoints. `run.py --help` works in all three approaches.

Known leftovers: the old tests create empty `models/` folders on the fly (legacy Keras code does `os.makedirs(.../models)`,
git-ignored by the `models/` rule); `benchmark.py` paths were updated but the script was not executed; the old `analysis_report.md`
files and the older proposals 00-05, `reports/` and `HANDOFF.md` are historical and still use the old folder names; the new
contract tests were not split per method (see Deviations).

## Risks

- Legacy scripts compute `src/` and `data/` by counting `dirname` levels; every moved legacy file needs +1 level
  (+2 for img2img). Fixed one by one and checked by the legacy test suites.
- Module-name collisions (`config`, `utils`, `common`, `methods`): one pytest process per approach and per legacy method suite.
- Existing run folders must still resolve: they are physically moved; `run.py eval` is not run on real runs. Checkpoints are
  checked with a read-only load script.
- Weights: `*.pt`, `*.keras`, `*.weights.h5` stay git-ignored; the old rule ignoring all `runs/` is replaced so that
  metrics.json, grid.png, log.csv and args.json can be committed; smoke runs are ignored.

## Checklist

- [x] Baseline recorded
- [x] Plan and dry-run manifest written
- [x] image_based: moves, imports and paths, run.py and registry, READMEs, tests vs baseline, checkpoint check, counts
- [x] geometry_based: same
- [x] text_based: same
- [x] Docs: approach README/TODO, root README, CLAUDE.md, TODO.md, RESULTS_*.md links, 06_EXECUTION_PLAN.md, .gitignore
- [x] run_all_tests.py, pytest.ini, conftest.py, benchmark.py consistent
- [x] Final verify, stale-reference grep, `run.py --help` per approach, rollback script dry-run
