## Text track: built, NOT RUN (2026-11-03)

There are no results for the text track. No figure in this file is a measurement.

## What exists

- `src/text_based/run.py` with `prepare | eval | check-model | train`; shared code in `common/` (canonical, formats, recipes,
  prompts, evaluate); methods `lmstudio_prompt`, `fewshot_prompt`, `qwen_qlora`, `nemotron_qlora`.
- CSV double-encoding and parser bugs fixed; `prepare` writes a 524-row jsonl.
- New tests 32 passed; legacy suite 46 passed and 1 failed (`test_34`, pre-existing, the `nemotron3/results/` folder does not exist).
  Counts are from the 2026-11-01 agent report, not re-run in this close-out.
- The QLoRA training code was never run.

## Why nothing ran

- The first `check-model` run (LM Studio, `gemma-2-2b-it`) produced no output and no run folder after about 5 hours of wall
  time and was treated as hung. Gemma took about 19 s for a 5-token reply, and each request is allowed up to 240 s.
- QLoRA needs the GPU, which was used by the image track.

## Legacy claims (do not quote)

The old QLoRA Qwen2.5-7B figures (MAE 0.78, PSR 98%) and Nemotron-Mini-4B 2-shot (PSR 85.7%) were measured with train/test
leakage on four base shapes and have not been reproduced under a clean split.

## Restart recipe (in order)

1. Timing probe, one style, one shot, one shape, short timeout:
   `cd src/text_based` then `conda run -n genai python run.py check-model --base-url http://localhost:1234/v1 --model <served-id> --styles fewshot-mcv2 --shots 1 --n 1 --timeout 60`.
   If a request takes over about 10 s, use a smaller or faster model.
2. Few-shot evaluation on leave-one-shape-out folds (`--fold loso_<Shape>`) to replace the leaked 98% PSR claim.
3. QLoRA on the GPU only after the image and graph work is done, and only with the user's confirmation (`--confirm-gpu`).

Tracked as S3.1 to S3.5 in `06_EXECUTION_PLAN.md` and `text_based/TODO.md`.
