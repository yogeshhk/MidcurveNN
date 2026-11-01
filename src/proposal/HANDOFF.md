# Handoff to the next session (written 2026-11-01)

Read this first, then `00_MASTER_PLAN.md` (v2, three independent tracks) and
`05_publications_triage.md`. The sub-reports `01`-`04` hold the detailed reasoning; you do not
need to re-derive anything.

## Live status log (newest first; updated by the coordinating session)

- 15:08: Harness raised a security warning on the image agent ("Interfere With Workloads", details
  not given). Observed: its earlier 40-epoch `unet__pose__base` run (epoch 18) disappeared and
  was replaced by a SHORT run (`--epochs 8 --steps 100`). Graph runs and the Gemma check were
  unaffected. Treat the image UNet numbers as short-schedule; rerun with the full schedule later
  and check that RESULTS_image.md states the schedule honestly.

- 15:07 (2026-11-01): no RESULTS_*.md written yet. LM Studio reachable. Running: Gemma check-model
  (24 min), graph `set_transformer` ood_deg4 e30 (epoch 17) and iid e80 (epoch 18). Finished:
  graph `set_transformer__iid__e30` (metrics.json exists), classical baselines (iid, ood_deg4),
  image `skeleton__pose__base`. Image: the earlier `unet__pose__base` run folder is gone (the
  image agent evidently restarted it); the image agent is still active, no unet metrics yet.
  The `set_transformer__iid__t1` folder is a partial run that was stopped on purpose.

## State at handoff

- Shared raw data (done): `src/data/raw/{I,L,T,Plus}.edges` (midcurve edges, from brep JSON
  `Lines`; points match `.mid` order exactly) and `src/data/raw/splits.json` (`pose`, `default`,
  `loso` folds).
- Env: `genai` only (`midcurvenn` does not exist). shapely fails to import and drawsvg is missing;
  the new code uses neither. Launch with `conda run -n genai python ...`.
- Three tracks were built in parallel by agents. Each follows the same template inside its own
  folder: `run.py`, `prepare_data.py`, `dataset.py`, `evaluate.py`, `models/`, `tests/`, `runs/`.
  Each agent writes `src/proposal/RESULTS_<track>.md` when it finishes. If a file is missing, that
  track did not finish; check its `runs/` folder.

| Track | Built | At handoff |
|---|---|---|
| image (`src/image_based/`) | run.py, prepare_data.py (npz, 128x128, 3 channels), dataset.py, losses.py, evaluate.py, models: simple_ae, dense_ae, cnn_ae, denoiser_ae, unet, pix2pix, skeleton | skeleton baseline done; unet pose run in progress; cnn/dense/simple/pix2pix runs and loso/ablation probably NOT run |
| geometry (`src/geometry_based/`) | run.py, prepare_data.py (+ procedural generator), geom.py (no shapely), dataset.py, losses.py (Hungarian), evaluate.py, models: classical, set_transformer | P1 and P2 PASS; classical baseline: real4 exact, synthetic ok_025w 0.81; set_transformer e30 run near done; ood_deg4 next. The 100-epoch `t1` run was stopped by the user's choice (partial folder `runs/set_transformer__iid__t1`) |
| text (`src/text_based/`) | CSV double-encoding fixed (backup in `data/csvs/_backup_double_encoded/`), parsers fixed, fewshot_prompter fixed; run.py, prepare_data.py (jsonl, 524 rows), formats.py, canonical.py, recipes.py, prompts.py, evaluate.py, prompts/*.txt, models: lmstudio_prompt, fewshot_prompt, qwen_qlora, nemotron_qlora (training code NOT run) | check-model on LM Studio `gemma-2-2b-it` in progress (slow, ~19 s per short reply); eval run and optional `qwen/qwen3-1.7b` check pending |

Test counts reported by the agents (re-run to confirm):
- text: new 32/32; legacy 46 passed and 1 failed (pre-existing `test_34`)
- geometry: new 18 passed; legacy 13 passed and 2 skipped
- image: see `RESULTS_image.md`

## Next steps (in order)

1. Collect `RESULTS_image.md`, `RESULTS_graph.md`, `RESULTS_text.md`. Summarise them for the user
   in one table.
2. Finish any unrun experiments with each track's `run.py`, running one heavy training job at a
   time (CPU contention slowed everything). Use the GPU where the code supports it (CUDA is
   available in `genai`).
3. Ask the user the [CONFIRM] items ONE AT A TIME, each with a recommendation:
   - move legacy image folders to `image_based/_legacy/`
   - retire `finetuned_graph_transformer/` and `gnnencoderdecoder/` to `geometry_based/_legacy/`
   - archive the legacy text folders to `text_based/_legacy/`
   - move `publications/prompts/` to `src/text_based/prompts/research/`
   - GPU QLoRA fine-tuning (ask about model size and format first)
   - the publications moves and the zip in `05_publications_triage.md`
4. After the moves: update the root README.md, CLAUDE.md and TODO.md (new per-approach `run.py`
   commands; note that the legacy headline numbers were leaked or unverified).
5. Later: write the three new papers (`Main_Paper_MidcurveNN_{Image,LLM,Graph}.tex`) from the new
   results, then update the comprehensive paper and the seminar deck.

## Open issue to raise with the user

`publications/Midcurve_LaTeX/Main_Seminar_Midcurve_Presentation.tex`,
`Main_Seminar_Midcurve_CheatSheet.tex` and `seminar_midcurve_content.tex` are 0 KB on disk, while
the 7.4 MB presentation PDF exists. The sources may have been emptied by accident; check before
any rebuild.

## Rules (from the user's CLAUDE.md; paste into any subagent prompt)

- No git commands.
- Use Edit/Write tools only (no heredocs, no sed).
- Run Python via `conda run -n genai python`.
- ASCII output.
- Never run `src/utils/prepare_data.py` as a script.
- Ask decisions one at a time, with a recommendation.
- Dry-run before any move or zip; list the destination before and after; confirm file count and
  size.
- No CI.
