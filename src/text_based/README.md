# Text track (Phase II): midcurve with LLMs

Shape geometry is written as text (B-rep JSON and other serialisations) and a language model is asked
to produce the midcurve, either by prompting (local server) or by QLoRA fine-tuning.

Live plan: `../proposal/06_EXECUTION_PLAN.md` (Session 3). Task list: `TODO.md`.

## Status: NOT RUN (no results)

The new code and tests exist, but no evaluation has been completed. There is no `RESULTS_text.md`.
A check of an LM Studio model (`gemma-2-2b-it`) stalled with no output (about 19 s for a 5-token reply),
and the QLoRA training code has never been run. Nothing in this folder supports a performance claim yet.

The older headline figures (QLoRA Qwen2.5-7B MAE 0.78, PSR 98%; Nemotron-Mini-4B 2-shot PSR 85.7%) were
measured on a randomly shuffled split of augmented variants of four shapes, so train and test shared the
same shapes. Treat them as leaked, not as generalisation.

## What is built (new track)

```
text_based/
  run.py            driver: prepare | eval | check-model | train
  prepare_data.py   raw -> data/dataset_v1.jsonl (524 rows)
  dataset.py        views of each row; splits from src/data/raw/splits.json
  formats.py        serialisations: json, mcv1, mcv2, lines
  canonical.py      canonical pose handling
  prompts.py        prompt builders; prompts/*.txt (brep, description, fewshot, pointlist)
  recipes.py        prompt/format recipes
  evaluate.py       geometric and validity metrics
  models/           lmstudio_prompt, fewshot_prompt, qwen_qlora, nemotron_qlora, sft_common
  tests/            test_text_track.py (32 tests reported passing at handoff; re-run to confirm)
  data/csvs/        legacy CSVs (the double-encoding bug was fixed; backup in data/csvs/_backup_double_encoded/)
```

Legacy folders still present: `finetuning/`, `nemotron3/`, `codeT5/`, `ludwig/`, `prompt/`, `utils/`,
`testing/`. The legacy suite had one pre-existing failure (`test_34`, missing `nemotron3/results/`).

## Run (from `src/text_based`, env `genai`)

```
conda run -n genai python run.py prepare
conda run -n genai python run.py check-model --help
conda run -n genai python run.py eval --help
conda run -n genai python run.py train --help
```

Start the first real test as a timing probe: one prompt style, one shot, shape I, to measure seconds per
request before widening. Unload other LM Studio models and keep image jobs off the GPU while probing.
GPU QLoRA fine-tuning waits for a decision on model size and format.

## Results

None. Will be written to `../proposal/RESULTS_text.md` in Session 3.

## Tests

```
cd src
conda run -n genai python -m pytest text_based/tests -q
conda run -n genai python -m pytest text_based/testing/test_text_based.py -q   # legacy
```

## Key challenge

Branched midcurves (T, Plus) are not a single linear sequence. The B-rep format with `Lines` and
`Segments` carries the junction topology explicitly; a model must emit valid, correctly connected output.
Leave-one-shape-out evaluation is the planned way to make any claim here honest.
