# Handoff to the next session (written 2026-11-01)

Read this first, then `00_MASTER_PLAN.md` (v2, three independent tracks) and
`05_publications_triage.md`. The sub-reports `01`-`04` hold the detailed reasoning; you do not
need to re-derive anything.

## PARKED 2026-11-03 (read this first when resuming)

The user is parking the project after a git sync. State: EquiCollapse closed out at agreed quality (see
`RESULTS_gdl.md`, one seed, pre-fix generator); the label generator is fixed; nothing is training; no background jobs.
Resume order: (1) re-run EquiCollapse and the control on the fixed generator, seeds 0-2, then G1.2-G1.5 (list in
`geometry_based/TODO.md`); (2) image track: 1-channel ablation first, then full-schedule UNet and leave-one-shape-out
(`image_based/TODO.md`); (3) text track: LM Studio timing probe (one style, one shot, shape I), then few-shot on
leave-one-shape-out (`text_based/TODO.md`); (4) [CONFIRM] items one at a time: publications moves and zips (P4.2),
`publications/prompts/` move, GPU QLoRA, seminar deck Phase I/III inputs (P4.3). Papers, `benchmark.py`, README/CITATION and
`environment.yml` come last (06_EXECUTION_PLAN.md sections W5 and R6). Outside this repo: `D:\Yogesh\GitHub\CLAUDE.md` still
says MidcurveNN is absent locally (the user's file; update it yourself).

SHELVED later the same day (2026-11-03): the user stopped the UNet leave-one-shape-out run and shelved the project. No
background jobs. Close-out files added: `RESULTS_text.md` (built, not run), `src/environment_genai.yml` (untested recipe).
Decisions taken: graph re-runs, publications moves/zips, and the three new papers stay tracked TODO; the seminar deck keeps
the Image slides off (`\showImagefalse`); image loso, text probes and QLoRA are open, none started.

## Live status log (newest first; updated by the coordinating session)

- 19:40 FINAL SYNC: all three agents have finished. Status loop stopped.
  - GRAPH: `RESULTS_graph.md` written (read it). P1 PASS, P2 PASS, P3 FAIL (close: iid k_exact
    0.895, ok_025w 0.865 at 80 epochs, vs classical 0.813; looks under-trained, 8000 samples),
    P4 PASS (all 4 real shapes), P5 PASS for the real Plus (30-epoch run) BUT the model collapses
    on synthetic degree-4-only shapes (ok_025w 0.155), so P5 is weak evidence. Rerun ood_deg4 at
    80+ epochs, add seeds, run ood_size and the 3-shape negative control.
  - IMAGE: `RESULTS_image.md` PARTIAL (see the 19:36 entry). Run the 1-channel ablation before
    quoting 0.998. A leftover queue (cnn_ae run with empty log) may still be running; check
    `src/image_based/runs/` and the scratchpad `run_all2.log` before starting anything.
  - TEXT: NO RESULTS_text.md and no Gemma numbers. The check-model run was hung (no output after
    ~5 h wall time; LM Studio was reachable). Next session: restart with one prompt style, one
    shot, one shape to measure time per request, then widen. Text code + 32 new tests are in place.
  - Still to do (all [CONFIRM] one at a time): legacy folder moves, publications moves/zip,
    GPU QLoRA, docs updates (README/CLAUDE.md/TODO.md). See "Next steps" below.

- 19:36: Image agent final (partial) report received; `RESULTS_image.md` now exists, marked
  PARTIAL. The text agent finished WITHOUT RESULTS_text.md and with no run folder (Gemma check
  process gone); graph 80-epoch ood_deg4 process is no longer running either.
  - Image tests: new suite 25/25, legacy image suite 24/24. Dataset: `data/dataset_v1.npz`
    (1408 samples).
  - Image numbers so far (pose split, test, F1@2px): skeleton baseline 0.850; unet (8 epochs x 100
    steps) 0.998 (chamfer 0.144, hausdorff 0.72 raw). Smoke runs of 10 steps only (NOT results):
    pix2pix 0.91, denoiser 0.88, cnn_ae 0.19, simple_ae 0.14, dense_ae 0.09.
  - CAUTION: the distance-transform input channel nearly gives the answer away (unet val F1 above
    0.99 after ~5 epochs). The 1-channel ablation is NOT run yet, so 0.998 is not a fair
    comparison with the legacy models or with the other tracks. Run the 1-channel ablation before
    quoting any image number.
  - The agent killed the 40-epoch UNet plan because the GPU was shared with other jobs (a
    llama-server process and the other agents' training; epochs went from 30 s to 145-190 s) and
    restarted with 4-8 epoch runs. This explains the earlier security warning.
  - A queue script (scratchpad/run_all.ps1, log scratchpad/run_all2.log) was left running; it was on
    cnn_ae with an EMPTY log.csv. Remaining in that queue: simple_ae, dense_ae, pix2pix, unet+TTA,
    ablations (plain BCE, 1-channel), leave-one-shape-out (unet, cnn_ae), denoiser. Collect
    results with `conda run -n genai python <scratchpad>/table.py`.

- 19:32: wall clock jumped 4 h since the 15:28 entry (the PC probably slept; nothing was written
  between 15:32 and 19:32). Still no RESULTS_*.md. LM Studio reachable (HTTP 200).
  - Graph: `set_transformer__iid__e80` DONE (metrics.json, grid.png). `ood_deg4__e30` done.
    `ood_deg4__e80` running (epoch 13 of 80, resumed after the sleep). Classical baselines done.
    RESULTS_graph.md NOT written.
  - Image: `unet__pose__base` DONE (short 8 x 100 schedule; metrics.json + grid.png at 15:30).
    `cnn_ae__pose__base` started 15:30 but its log.csv is EMPTY (0 bytes) after 4 h wall time:
    stalled or very slow. dense/simple/denoiser/pix2pix not started. RESULTS_image.md NOT written.
  - Text: Gemma `check-model` has run 289 min wall time; its console log (scratchpad
    check_gemma.log) is 0 bytes and no run folder exists: treat as HUNG/stalled. Needs the user to
    decide (restart with a smaller `--n`/fewer prompt styles, or use a faster model; Gemma took
    ~19 s for a 5-token reply). Eval run and RESULTS_text.md NOT done.
  - Suggested restart order for the next session: finish graph e80 + RESULTS_graph.md; rerun
    cnn_ae with `--quick` first to see why log.csv stays empty; restart the text check with a
    single prompt style and 1 shot on I only to measure time.

- 15:28: still no RESULTS_*.md. LM Studio reachable (HTTP 200).
  - Graph: `set_transformer` iid e30 and ood_deg4 e30 both have metrics.json; iid e80 at epoch 73
    of 80 (running); classical baselines done. The agent still has to write RESULTS_graph.md.
  - Image: `unet__pose__base` (short schedule, 8 epochs x 100 steps) at epoch 7 of 8; skeleton
    baseline done. cnn/dense/simple/pix2pix not started.
  - Text: the Gemma check-model run is at 45 min with no output folder yet in
    `text_based/runs/`; Gemma is slow, but if still nothing at the next sync it may be hung
    (per-request timeout is 240 s). Eval run and RESULTS_text.md pending.

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
