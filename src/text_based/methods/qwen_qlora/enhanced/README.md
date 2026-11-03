# Qwen QLoRA: enhanced version

Qwen2.5-Coder QLoRA with answer-only loss (defaults: 8 epochs, lr 1.5e-4, LoRA r 32, 4-bit). Training code only: it needs a GPU and a model download and has never been run (ask the user first).
Base model default: Qwen/Qwen2.5-Coder-1.5B-Instruct (default).

This is the version registered in the text driver (`src/text_based/run.py`, `--model qwen_qlora`). The older implementation
(the former `finetuning/`) is at the top level of `../` (see `../README.md`); its figures were measured under train/test leakage.

## Commands

Run from `src/text_based`:

```
conda run -n genai python run.py train --model qwen_qlora --format mcv2 --confirm-gpu --max-steps 5
conda run -n genai python run.py eval  --model qwen_qlora --format mcv2 --adapter-dir <run dir>
```

Run folders land in `runs/` here. Adapter weights and checkpoints are git-ignored.

## Results

Results: none. This method has not been run; there is no `metrics.json` for it and no `RESULTS_text.md`. Any older figures in the legacy folders were measured under train/test leakage and are not comparable.

## Status

Code written, not run. Shared training code: `../../../common/sft_common.py`. Tests: `../../../tests/test_text_track.py`.
