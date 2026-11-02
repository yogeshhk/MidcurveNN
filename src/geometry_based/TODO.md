# TODO (geometry_based), updated 2026-11-02 by agent B

Source of truth: `src/proposal/06_EXECUTION_PLAN.md` (Session 1, Track G). Results: `src/proposal/RESULTS_graph.md`.

## Done
- [x] `--resume` (checkpoint `last.pt` every epoch), `--holdout`, split `loso_real` (3-shape negative control); `--seed` redraws train/val data, test set fixed.

## Session 1 Track G (running as one sequential queue, CPU, 2 threads)
- [x] G1.1 set_transformer iid, 20000 samples, 100 epochs, tag e100: P3 FAIL (k_exact 0.905, deg-seq 0.904, H<=0.25w 0.981)
- [ ] G1.2 ood_deg4 e100
- [ ] G1.3 seeds 1 and 2 for iid (tags e100_s1, e100_s2)
- [ ] G1.4 ood_size e100 and loso_real folds (tags loso_Plus, loso_I, loso_L, loso_T)
- [ ] G1.5 rewrite RESULTS_graph.md, run tests

## Later
- Learned adjacency head only if the MST is shown to fail (it has not).
- Session 2 families (noisy, curved, holes) where the classical rule breaks.
- [CONFIRM] retire `finetuned_graph_transformer/` and `gnnencoderdecoder/` to `_legacy/` (not done).
