## Text track TODO

Source of truth for ordering: `../proposal/06_EXECUTION_PLAN.md` (Session 3). No `RESULTS_text.md` yet.

## Status

NOT RUN. Code and 32 new tests are in place; the LM Studio check stalled; QLoRA training code has never
been run. Legacy headline numbers (MAE 0.78, PSR 98%) were measured under train/test leakage.

## Session 3 (needs the user for model size and GPU decisions)

- [ ] S3.1 LM Studio timing probe: one prompt style, one shot, shape I; record seconds per request; try a smaller model if over 10 s.
- [ ] S3.2 `check-model` over the prompts as a standing "evaluate any new LLM on midcurve" probe, logged in a table.
- [ ] S3.3 Few-shot evaluation on leave-one-shape-out.
- [ ] S3.4 [CONFIRM] QLoRA (Qwen or Nemotron) on GPU with the loso split, only after image and graph runs are finished.
- [ ] S3.5 Write `../proposal/RESULTS_text.md`.

## Pending decisions

- [ ] [CONFIRM] archive legacy folders to `_legacy/`; move `publications/prompts/` to `prompts/research/` (P4.1, P4.2).
- [ ] Legacy items still open: analysis_report A3, B7, B10, and the failing `test_34`.

## Next step

S3.1 timing probe.
