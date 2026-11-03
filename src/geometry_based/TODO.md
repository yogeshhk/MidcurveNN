# TODO (geometry_based), updated 2026-11-02 by agent B

Source of truth: `src/proposal/06_EXECUTION_PLAN.md` (Session 1, Track G). Results: `src/proposal/RESULTS_graph.md`.

## Done
- [x] 2026-11-03 layout reorganised (P4.1): `common/`, `methods/<method>/`, `docs/`, `tests/`; run folders now `methods/<method>/runs/<split>__<tag>/`; tests equal to baseline. `graph_transformer` is a frozen negative result; `finetuned_graph_transformer` and `gnn_encoder_decoder` are retired, kept in place under `methods/`.
- [x] `--resume` (checkpoint `last.pt` every epoch), `--holdout`, split `loso_real` (3-shape negative control); `--seed` redraws train/val data, test set fixed.

## Session 1 Track G (running as one sequential queue, CPU, 2 threads)
- [x] G1.1 set_transformer iid, 20000 samples, 100 epochs, tag e100: P3 FAIL (k_exact 0.905, deg-seq 0.904, H<=0.25w 0.981)
- [ ] G1.2 ood_deg4 e100
- [ ] G1.3 seeds 1 and 2 for iid (tags e100_s1, e100_s2)
- [ ] G1.4 ood_size e100 and loso_real folds (tags loso_Plus, loso_I, loso_L, loso_T)
- [ ] G1.5 rewrite RESULTS_graph.md, run tests

## GDL research (2026-11-03, see `src/proposal/07_GDL_RESEARCH_REPORT.md`)
- [x] First version of the report: symmetry audit, slot-collapse proof, EquiCollapse proposal. No training for the new method.
- [x] Second pass: options with pros and cons, literature check, overall verdict (report section 1 and section 12).
- [ ] HOLD G1.2 to G1.5: about 10% of synthetic labels have a spurious collinear node (`prepare_data.py:104`). Decide on the label fix first.
- [x] EquiCollapse implemented in `methods/equi_collapse/` (cell_complex.py, model.py, evaluate_extended.py, tests); `run.py` gained `--clean-labels`, `--rot-aug`, `--layers` (all default off). The generator label bug stays unfixed; `--clean-labels` corrects train and val labels only.
- [ ] Approved by the user 2026-11-03. Training queue running, one job at a time, CPU 4 threads. To resume, run these one at a time, skipping any whose `metrics.json` exists, each with `--epochs 80 --n-val 1000 --clean-labels --resume --threads 4`. Add `--lr 0.002 --batch-size 64` for `equi_collapse` (tags `n<N>_e80`) and `--rot-aug` for `set_transformer` (tags `clrot_n<N>_e80`): iid n8000, ood_deg4 n8000, iid n500, iid n2000, ood_size n8000, iid n8000 with `--seed 1` and `--seed 2` (tag suffix `_s1`, `_s2`).
- [x] Deck method slides written: `publications/Midcurve_LaTeX/midcurve_gdl_method.tex`, switches in `midcurve_switches.tex`, `seminar_midcurve_content.tex` uses them, references added. Not yet compiled.
- [ ] State when the session closed (2026-11-03): 9 of 14 runs have `metrics.json`; `set_transformer/ood_size__clrot_n8000_e80` was at about epoch 75 of 80; seeds s1 and s2 (4 runs) not started. Results not evaluated, no results slides. `\showGDLResults` is set to false in `midcurve_switches.tex` so the deck can compile without the missing results file; set it back to true once `midcurve_gdl_results.tex` exists.
- [ ] Then run `methods/equi_collapse/evaluate_extended.py`, write `src/proposal/RESULTS_gdl.md`, the method README and notebook, and `publications/Midcurve_LaTeX/midcurve_gdl_results.tex` (required by the deck while `\showGDLResultstrue`), reporting the results at whatever quality they have. Compile both drivers, run /verify-pdf, and update paths in `07_GDL_RESEARCH_REPORT.md` (`prepare_data.py` is now `common/prepare_data.py`).

## PENDING: finish EquiCollapse (restart checklist, written 2026-11-03; run in this order)
Env: `conda run -n genai python ...` from `src/geometry_based`. One heavy job at a time. No git (the user syncs). Do not quote figures that are not in a `metrics.json` or RESULTS file.

1. [ ] Check the training queue. Runs live in `methods/<method>/runs/<split>__<tag>/`; a run is finished when it has `metrics.json`. As of closing: 9 of 14 done. Done: equi iid n8000/n500/n2000, equi ood_deg4 n8000, equi ood_size n8000; ST (set_transformer) iid clrot n8000/n500/n2000, ST ood_deg4 clrot n8000. Unfinished: ST `ood_size__clrot_n8000_e80` (was at epoch ~75 of 80, `--resume` it), then equi and ST `iid` with `--seed 1` and `--seed 2` (tags `n8000_e80_s1`, `n8000_e80_s2`, `clrot_n8000_e80_s1`, `clrot_n8000_e80_s2`). Commands are in the "Approved" item above. Skip any run that already has `metrics.json`. If time is short, the seed runs may be dropped: say so in RESULTS.
2. [ ] Run `methods/equi_collapse/evaluate_extended.py` (writes `methods/equi_collapse/runs/extended_metrics.json`; compares classical, set_transformer e100, the clrot control, EquiCollapse; rotations 5/15/30/45, noise, deg-4, real shapes).
3. [ ] Write `src/proposal/RESULTS_gdl.md` from the metrics only, at whatever quality they have (user: "document that we have tried and this is the current state"). Report honestly if EquiCollapse does not beat the control or the classical baseline. Include data-efficiency (n500/n2000/n8000) and ood tables.
4. [ ] Method docs: `methods/equi_collapse/README.md` and a thin `notebook.ipynb` (nbformat 4). Update `geometry_based/README.md`, and the method lists in `MidcurveNN/CLAUDE.md` and `README.md` (add `equi_collapse`).
5. [ ] Deck, `publications/Midcurve_LaTeX/`: create `midcurve_gdl_results.tex` (real numbers; booktabs; `[fragile]` frames). Copy any figures to `images/` and list size/timestamp. Read the dataviz skill before any chart. Then set `\showGDLResultstrue` in `midcurve_switches.tex` (currently false, only so the deck compiles without the missing file).
6. [ ] Compile both drivers (Presentation and CheatSheet; `make.bat` uses `texify --engine=luatex -cp`; xelatex/latexmk also available). Check the Phase III legacy slides and CheatSheet still compile with the switches (`\ifshowImage` is false by design). Run /verify-pdf. Fix overflow. Deck was never compiled yet, so expect first-compile errors in `midcurve_gdl_method.tex`.
7. [ ] `src/proposal/07_GDL_RESEARCH_REPORT.md`: update paths to the new layout (`prepare_data.py` -> `common/prepare_data.py`, flat folders -> `methods/<method>/`), and replace "No trained EquiCollapse result exists" with a pointer to `RESULTS_gdl.md`.
8. [ ] Run the geometry tests (`cd src/geometry_based; conda run -n genai python -m pytest -q`): expect 33+ passed plus the equi_collapse tests, 2 skipped. Confirm no non-ignored file over 50 MB (weights *.pt are git-ignored).
9. [ ] Tick this file and `src/proposal/06_EXECUTION_PLAN.md` (GDL / EquiCollapse ledger line). Write a final summary for the user.

Open decisions (user's, not for the agent): fix the label generator bug (`common/prepare_data.py`, spurious collinear nodes in ~10% of samples) and then release the held G1.2 to G1.5 runs; stale note in `D:\Yogesh\GitHub\CLAUDE.md` saying MidcurveNN is absent locally.

## Later
- Learned adjacency head only if the MST is shown to fail (it has not).
- Session 2 families (noisy, curved, holes) where the classical rule breaks.
- [x] `finetuned_graph_transformer` and `gnn_encoder_decoder` are marked retired in their READMEs and stay under `methods/` (no `_legacy/` folder, user decision 2026-11-03).
