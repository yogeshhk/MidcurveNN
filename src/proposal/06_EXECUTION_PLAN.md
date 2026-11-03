# MidcurveNN: multi-session execution plan (written 2026-11-02)

Read `HANDOFF.md` first (state at 2026-11-01), then this file. This file is the single source of
truth for "what is next". Every session and every agent must tick items here AND in the matching
per-track `TODO.md` as soon as an item finishes, so an abrupt stop loses nothing.

Goal: make MidcurveNN a credible, unusual research repository: a small, well-defined geometry
problem (midcurve of thin 2D profiles) attacked by three independent method families (image, text/LLM,
graph), with honest, leakage-free evaluation, a classical baseline for each, negative results kept,
and everything reproducible from one `run.py` per track.

## 0. Decisions already made (do not re-ask)

- Three independent tracks; only `src/data/raw/` (+ `.edges`, `splits.json`) is shared.
- Image headline input = 1-channel outline. 3-channel (outline, mask, distance transform) = reported ablation.
- Graph: train longer first (20000 samples, 100+ epochs), then seeds, then `ood_size` and the 3-shape negative control.
- Text/LLM track: SKIPPED for now (next session at the earliest; start with a tiny timing probe).
- No file moves, zips or legacy-folder moves unattended. Those wait for the user (section 5, track P).
- Seminar `.tex` files are normal thin drivers (not damaged); the Phase I and III `\input` lines are commented out. Do not touch yet.
- No git commands, no CI, no CODE_OF_CONDUCT or issue templates (declined earlier).

## 1. Rules for every agent (paste into subagent prompts; they do not inherit CLAUDE.md)

- Never run any git command.
- Change files with Edit/Write only. No heredocs, no `sed`, no multi-line backslash shell commands. Longer scripts: write to a file, then run.
- Run Python only as `conda run -n genai python ...` from `D:/Yogesh/GitHub/MidcurveNN/src/<track>`. Windows 11, forward slashes in bash.
- ASCII-only console output.
- Never run `src/utils/prepare_data.py` (it deletes `images-combo/` and `unet-splits/`).
- No package installs or model downloads without asking.
- ONE heavy training job at a time per resource (see section 3). Check `Get-Process python` before starting one.
- Stay inside your track folder. Do not edit another track's files.
- Report outcomes faithfully: failing tests, skipped steps and unmeasured rows are stated, never hidden.
- After any multi-file edit run the track tests and report pass/fail.
- Markdown images: `![alt](images/x.png)` and, directly under it, `*Image file: images/x.png*`.
- Keep the status ledger (section 6) and the track `TODO.md` current after EVERY finished item.

## 2. Known open problems to resolve (from the review)

1. Image UNet 0.998 is untrustworthy: distance-transform channel leaks the answer; schedule was cut to 8x100 steps.
2. Image: cnn_ae F1 0.997 but topology only 84% (L 37%); simple_ae F1 0.76, topology 4%. dense_ae, pix2pix, denoiser not run. Check whether the numbers in each `metrics.json` are the test block or only `val_seen_shapes_new_poses`.
3. Every split so far = new poses of the same 4 shapes. Only leave-one-shape-out says anything about generalisation, and with 4 shapes even that is thin.
4. Graph: P3 missed (k_exact 0.895 vs 0.95); `ood_deg4` collapses on synthetic degree-4 shapes; `ood_deg4__e80` died at epoch 10; single seed; real-shape evidence = 4 samples.
5. Classical Voronoi baseline is exact on all 4 real shapes: learned methods must beat it where it breaks (noise, curves, holes, non-orthogonal).
6. Text: no results at all; the LM Studio probe hung (Gemma ~19 s per short reply).
7. Docs (README, CLAUDE.md, TODO.md) still describe the legacy layout and leaked numbers.
8. Papers: all published numbers are leaked; the three new papers need the clean results.

## 3. Parallelism and the machine

Yesterday three heavy jobs plus LM Studio's `llama-server` shared one GPU/CPU and epochs slowed 5x (30 s to 145-190 s); one run was killed and the harness raised a security warning. Rules:

- Image jobs own the GPU. Graph jobs run CPU-only with `--threads 2` (they are small) unless the GPU is idle.
- Unload models from LM Studio (or stop `llama-server`) before any image run.
- Safe in parallel with a heavy job: doc updates, README/TODO work, tests that are CPU-light, reading and analysis, writing paper skeletons, the dataset-expansion code (writing, not generating).
- Never two image trainings at once; never two graph trainings at once.
- Agents (all Sonnet): A = image experiments, B = graph experiments, C = docs/figures/paper skeletons. A and B run in parallel under the limits above; C is always safe.

## 4. Sessions

### Session 1 (next): trust the numbers, finish what exists  [unattended OK]

Track I (agent A):
- [x] I1.1 Confirm which block (test vs val) is reported in each `metrics.json`; make `evaluate.py` always write a `test` block and label both. Report the correction if the earlier figures were val-only.
- [x] I1.2 Add `--in-ch 1` as the default for the headline runs; keep 3-channel as `abl_in3`.
- [x] I1.3 Full-schedule runs (target 30+ epochs x 100 steps, one at a time): skeleton, simple_ae, dense_ae, cnn_ae, denoiser_ae, unet, pix2pix on `pose`, tag `h1` (1-channel).
- [x] I1.4 Ablations on unet: `abl_in3`, `abl_bce` (plain BCE), `abl_noaug`.
- [ ] I1.5 Leave-one-shape-out for unet and cnn_ae (4 folds each, 1-channel). Expect Plus worst.
- [ ] I1.6 TTA eval for the best model. Rewrite `RESULTS_image.md` (one table: test F1, Chamfer, Hausdorff, topology, schedule, seconds/epoch measured on an unshared GPU).
- [ ] I1.7 Run the image tests (new + legacy) and record counts.

Track G (agent B):
- [x] G1.1 (done: P3 FAIL, k_exact 0.905) `set_transformer` iid, 20000 samples, 100 epochs, tag `e100`. Check P3.
- [ ] G1.2 `ood_deg4` at the same budget (tag `e100`); a first resume-from-checkpoint is needed if the run dies (add `--resume` if missing).
- [ ] G1.3 Seeds 1 and 2 for the iid run (3 seeds total); report mean +/- std.
- [ ] G1.4 `ood_size` run and the 3-shape negative control (train on 3 real shapes, test the 4th).
- [ ] G1.5 Rewrite `RESULTS_graph.md` with the new P1-P5 table. Run graph tests.

Track D (agent C, docs):
- [x] D1.1 Update root `README.md`, `CLAUDE.md`, `TODO.md`: new per-track `run.py` commands, layout, "legacy numbers are leaked", status of each track (text = not run). No claims that are not in a RESULTS file.
- [x] D1.2 Per-track `README.md` (`image_based/`, `geometry_based/`, `text_based/`): how to prepare, train, evaluate, results table placeholder linking to RESULTS.
- [x] D1.3 Per-track `TODO.md` created/updated from section 6 below.
- [x] D1.4 Add `.gitignore` entry for `*/runs/*/best.pt` only (keep metrics.json, grid.png, log.csv, args.json small and committed so the results are inspectable). Do not run git.

### Session 2: harder, more honest data (the research core)  [plan with the user first]

The 4-shape dataset is the limit of every claim. Build a shared procedural shape-family generator
(the graph track already has one for rectilinear trees) and extend it per track:
- [ ] S2.1 Families: rectilinear trees (have), plus-with-arms of unequal width, tapered/non-orthogonal strips, curved (arc) strips, strips with noise, shapes with a hole (annulus-like), thick (non-thin) shapes where the midcurve is ill-defined.
- [ ] S2.2 Splits by FAMILY, not by pose or shape: train on rectilinear, test on curved. This is the unusual, publishable axis: does a learned midcurve extrapolate across geometry families, and where does the classical rule break?
- [ ] S2.3 A ground-truth rule per family (analytic midcurve), with a test that the rule reproduces I, L, T, Plus.
- [ ] S2.4 Re-run best image model and the graph model on the new family splits; report where classical beats learned and where it does not.
- [ ] S2.5 Decide with the user whether to publish the generator + dataset (Kaggle / Hugging Face) with a dataset card.

### Session 3: text/LLM track  [needs the user: model size and GPU decision]

- [ ] S3.1 LM Studio timing probe: one prompt style, one shot, shape I; record seconds per request; try a smaller/faster model if > 10 s.
- [ ] S3.2 `check-model` over the user's `publications/prompts/` as the "evaluate any new LLM on midcurve" tool: this is a standing probe that can be re-run on every new model release and logged in a table (unusual and cheap, good for the repo's identity).
- [ ] S3.3 Few-shot evaluation on leave-one-shape-out (fixes the leaked 98% PSR claim).
- [ ] S3.4 [CONFIRM] QLoRA (Qwen or Nemotron) on a GPU with the loso split, only after image/graph runs are finished.
- [ ] S3.5 `RESULTS_text.md`.

### Session 4: repo hygiene with the user present  [CONFIRM each, one at a time]

- [x] P4.1 DONE 2026-11-03, with a different layout than first written here (user decision): no `_legacy/` folders. Each approach now has `common/`, `methods/<method>/` (old code at the method's top level, `enhanced/` for the standard version), `docs/`, `tests/`. Plan, dry-run manifest, move log, rollback: `08_REORG_PLAN.md`, `08_moves.csv`, `08_moves_done.csv`, `08_rollback.py`. Imports, tests, `run.py`, `collect_results.py` and `benchmark.py` paths updated; `benchmark.py` itself was not executed. Moving the publications items stays in P4.2.
- [ ] P4.2 Publications triage moves from `05_publications_triage.md` (zip `Midsurface_PhDThesis/`, move `MediumBlogs/`, `IntroToGeoMod/`, the LinkedIn post, `prompts/` to `text_based/prompts/research/`, KaggleNotebooks distribution, TopoVal zip). Verify zip entry count before any delete; never delete without asking.
- [ ] P4.3 Seminar deck: decide whether the Phase I and III `\input` lines should come back; rebuild only after the new results exist; run `/verify-pdf`.

### Session 5: papers and the cross-approach story

- [ ] W5.1 `Main_Paper_MidcurveNN_Image.tex`, `_Graph.tex`, `_LLM.tex` from the RESULTS files (reuse `midcurve_intro.tex`, `midcurve_refs.tex`, `midcurve_impl_*.tex`). Lead with the negative/neutral findings: classical baselines, leakage correction, family-split generalisation.
- [ ] W5.2 Update the comprehensive paper last: relabel old numbers as leaked or replace them.
- [ ] W5.3 Update the seminar deck and cheat sheet.
- [ ] W5.4 `src/benchmark.py`: rewrite to read the three tracks' `runs/*/metrics.json` into one cross-approach table (Chamfer/Hausdorff in raw units, same loso folds).

### Session 6: make it a showcase repository

- [ ] R6.1 README: one-screen pitch, one results table with the clean numbers, one hero figure (input / ground truth / classical / learned for each family), links to the three papers, honest limitations section.
- [ ] R6.2 `CITATION.cff`, `CHANGELOG.md` entry, tagged release notes (user tags the release), repo topics.
- [ ] R6.3 `environment.yml` that really builds (`genai` is the only env today; `midcurvenn` does not exist) plus a 5-minute "smoke test" command per track.
- [ ] R6.4 Dataset and model cards (Kaggle/Hugging Face) if the user approves S2.5.
- [ ] R6.5 A short blog/LinkedIn post of the family-split result (user posts; do not publish for them).
- [ ] R6.6 Open GitHub issues for the remaining questions as an invitation to contributors (the MS/PhD topic already exists in the two-pager).

## 5. Research ideas (beyond the plan; pick later)

1. Family-split generalisation as the benchmark axis (S2.2): the main unusual contribution.
2. "Where does a rule break?" map: sweep noise, curvature, width/length ratio and hole count; plot classical vs learned error. A phase diagram, not a leaderboard.
3. Midcurve as set prediction (graph track) vs raster (image) vs text (LLM): same shapes, three representations; compare failure modes (topology errors vs blur vs invalid output).
4. Topology-aware metrics (degree sequence, branch count, cycle count) reported next to geometric ones; show high F1 with wrong topology (cnn_ae L: 0.996 F1, 37% topology).
5. Differentiable skeleton / medial-axis-transform loss for the image model; compare to the BCE+Dice loss.
6. Continuous-width midcurve: predict the radius with each node (full medial axis transform), allowing reconstruction of the profile as a round-trip test.
7. LLM probe as a living table (S3.2): every new model, same prompts, same split.
8. Hybrid: classical proposal + learned correction (residual on the Voronoi nodes).
9. Negative results page: what did not work and why (the legacy leakage, collapsed UNet grid, MST vs learned adjacency).

## 6. Status ledger (update after EVERY finished item; newest first)

Format: `date time | agent | item id | result in one line | files touched`

- 2026-11-03 | reorg agent | P4.1 | reorganised image_based, geometry_based, text_based into one template (common/, methods/<method>/[enhanced/], docs/, tests/); 96 folder-level moves logged in 08_moves_done.csv, no files deleted, no training, label bug NOT fixed; test results equal to the pre-move baseline (pre-existing failures unchanged, see 08_REORG_PLAN.md); checkpoints load in 6 image methods and set_transformer | src/*/methods, src/*/common, src/proposal/08_*
- 2026-11-03 | coordinator | GDL report | research report written, proposes EquiCollapse; found a collinear-node label bug in `prepare_data.py:104` affecting about 10% of synthetic samples, so hold G1.2-G1.5 until it is fixed; no code changed, no results for the new method | src/proposal/07_GDL_RESEARCH_REPORT.md, src/proposal/images/gdl_dual_complex.png
- 2026-11-03 | coordinator | EquiCollapse | PARTIAL: `methods/equi_collapse/` implemented and tested; 9 of 14 training runs done, training queue stopped by the user (resume with `--resume`); results not yet evaluated, no RESULTS_gdl.md, deck results slides not written, deck not compiled. Pending checklist: `src/geometry_based/TODO.md` section "PENDING: finish EquiCollapse" | src/geometry_based/methods/equi_collapse, publications/Midcurve_LaTeX/midcurve_gdl_method.tex
- 2026-11-03 (later) | session | EquiCollapse | DONE at the agreed quality, single seed: 10 of 14 runs finished; `evaluate_extended.py` run; `RESULTS_gdl.md`, method README and notebook, `midcurve_gdl_results.tex` written; both decks compiled (Presentation 105 pages) and checked with verify-pdf; generator label bug FIXED (`common/prepare_data.py`, regression test, geometry tests 45 passed 2 skipped). Seeds 1 and 2 not run (stopped so they would not train on a mixed generator). All runs are pre-fix and labelled as such. Still open: G1.2-G1.5 on the fixed generator, seeds, re-run of EquiCollapse and control on the fixed generator | src/proposal/RESULTS_gdl.md, src/geometry_based/methods/equi_collapse
- 2026-11-02 | agent C | D1.4 | .gitignore: best.pt already covered by existing `*.pt`; added a comment only, no duplicate pattern | .gitignore
- 2026-11-02 | agent C | D1.3 | created per-track TODO.md (image, graph, text=NOT RUN) from Session 1/3 items | src/image_based/TODO.md, src/geometry_based/TODO.md, src/text_based/TODO.md
- 2026-11-02 | agent C | D1.2 | rewrote per-track READMEs for run.py workflow; results link to RESULTS files, text marked NOT RUN | src/image_based/README.md, src/geometry_based/README.md, src/text_based/README.md
- 2026-11-02 | agent C | D1.1 | root README/CLAUDE.md/TODO.md describe per-track run.py, genai launch, track status, leaked legacy numbers, plan pointer | README.md, CLAUDE.md, TODO.md
- 2026-11-02 11:30 | agent A | I1.4 DONE | unet ablations test F1 all 0.999: abl_in3 topo 0.99 chamfer 0.133; abl_bce topo 0.80 chamfer 0.118; abl_noaug topo 0.98 chamfer 0.139 (vs h1 topo 0.98, chamfer 0.132). F1 does not separate variants; plain BCE hurts topology; distance-transform channel and augmentation make no measurable difference on this 4-shape pose split | src/image_based/runs/unet__pose__abl_*
- 2026-11-02 10:59 | agent A | I1.3 DONE | all 7 h1 runs (30x100, pose, 1-ch) test F1: skeleton 0.850, simple_ae 0.722, dense_ae 0.556, cnn_ae 0.999, denoiser_ae 0.997 (on skeleton stage 1), unet 0.999, pix2pix 0.999; topology ok 0.09/0.10/0.20/0.99/0.90/0.98/0.96 | src/image_based/runs/*__pose__h1
- 2026-11-02 10:28 | agent A | I1.3 (part 1) | unet h1 (30x100, 1-ch) test F1 0.999, topo 0.98, chamfer 0.132, ~21 s/epoch on unshared GPU; cnn_ae h1 test F1 0.999, topo 0.99, chamfer 0.142. Outline-only input is NOT the cause of near-perfect F1 (task is easy on 4 shapes). Other models still queued | src/image_based/runs/{unet,cnn_ae}__pose__h1
- 2026-11-02 | agent A | I1.1 + I1.2 | metrics.json always had BOTH blocks (`test` and `val_seen_shapes_new_poses`); the unet 0.998 / skeleton 0.850 figures in RESULTS_image.md were the TEST block; the plan's cnn_ae "0.997 / 84% / L 37%" were VAL figures (test is 0.996 / 86% / L 44%). evaluate path now writes blocks named `val` and `test` (old runs keep the old key; collector reads both). `--in-ch` default is now 1 (channels 1,2 zeroed; models still built for 3 channels); `--skip-done` added; `sec_per_epoch_median` added (cnn_ae base mean 1841 s was a sleep artefact, log.csv says about 20 s) | src/image_based/run.py, collect_results.py
- 2026-11-02 11:15 | agent B | G1.1 | iid e100 (20000 samples, 100 epochs, 3166 s): P3 FAIL (k_exact 0.905, deg-seq 0.904, H<=0.25w 0.981, ok_025w 0.893, n=1000); P4 pass, real Plus 5 nodes/4 edges | runs/set_transformer__iid__e100
- 2026-11-02 | agent B | G1 prep | added --resume (last.pt each epoch), --seed now redraws train/val data (test fixed), new split loso_real + --holdout (3-shape negative control); quick smoke + resume OK; queue started (iid e100 ~40 s/epoch at 2 CPU threads, 20000 samples, so ~67 min per 100-epoch run) | geometry_based/run.py, dataset.py, models/set_transformer.py
- 2026-11-02 | coordinator | plan written | this file created; Session 1 not started | src/proposal/06_EXECUTION_PLAN.md

## 7. Where things live

- Image results: `src/image_based/methods/<method>/[enhanced/]runs/<split>__<tag>/metrics.json`, summary `src/proposal/RESULTS_image.md`.
- Graph results: `src/geometry_based/methods/<method>/runs/<split>__<tag>/metrics.json`, summary `src/proposal/RESULTS_graph.md`.
- Text results: none yet; runs will go to `src/text_based/methods/<method>/[enhanced/]runs/`; `src/proposal/RESULTS_text.md` will be created in Session 3.
- Table helper for images: `src/image_based/common/collect_results.py` (scans all method run folders).
- Layout, move log and rollback: `src/proposal/08_REORG_PLAN.md`; tests: `src/run_all_tests.py` (one process per approach).
- New methods (for example the GDL / EquiCollapse method) go in `src/<approach>/methods/<name>/` with their own README, model.py, runs/, tests/.
