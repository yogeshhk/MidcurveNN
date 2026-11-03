# Image track TODO (source of truth: src/proposal/06_EXECUTION_PLAN.md, Session 1 Track I)

Run from `src/image_based`: `conda run -n genai python run.py train --model unet --split pose --tag h1 --epochs 30 --steps 100 --skip-done`
Table: `conda run -n genai python common/collect_results.py`
Layout: reorganised 2026-11-03 into `common/`, `methods/<method>/[enhanced/]`, `docs/`, `tests/` (see `../proposal/08_REORG_PLAN.md`).

- [x] P4.1 image_based layout: methods/, common/, run folders moved, run.py and collect_results updated, tests equal to baseline
- [ ] Split `tests/test_image_track.py` per method (kept whole: it iterates the registry)
- [ ] `methods/unet/enhanced/runs/loso-I__h1` has best.pt and log.csv but no metrics.json (incomplete before the move)

- [x] I1.1 test vs val blocks confirmed; evaluate path writes labelled `val` and `test` blocks
- [x] I1.2 `--in-ch 1` is the default; 3-channel runs are ablation `abl_in3`
- [x] I1.3 h1 runs (30 ep x 100 steps, pose, 1-channel): unet, cnn_ae, skeleton, simple_ae, dense_ae, denoiser_ae, pix2pix
- [x] I1.4 unet ablations: abl_in3, abl_bce, abl_noaug
- [ ] I1.5 leave-one-shape-out (I, L, T, Plus) for unet and cnn_ae
- [ ] I1.6 TTA eval of best model; collect_results.py (done); rewrite RESULTS_image.md
- [ ] I1.7 test counts
