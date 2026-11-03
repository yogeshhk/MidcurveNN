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

Reorganised on 2026-11-03 (plan: `../proposal/08_REORG_PLAN.md`); same template as `image_based/` and `geometry_based/`.

```
text_based/
  run.py            driver: prepare | eval | check-model | train
  pytest.ini conftest.py
  common/           prepare_data.py (raw -> data/dataset_v1.jsonl, 524 rows), dataset.py, formats.py (json, mcv1,
                    mcv2, lines), canonical.py, prompts.py + prompt_templates/*.txt (was prompts/), recipes.py,
                    evaluate.py, sft_common.py, utils/ (old BRep CSV pipeline)
  data/             dataset_v1.jsonl, brep/, csvs/ (legacy CSVs; double-encoding bug fixed, backup in data/csvs/_backup_double_encoded/)
  docs/             analysis_report.md
  tests/            test_text_track.py (32), test_legacy_text_based.py (old suite)
  methods/          REGISTRY in methods/__init__.py
```

| method folder | `--model` | old implementation (top level) | enhanced version |
|---|---|---|---|
| [fewshot_prompt](methods/fewshot_prompt/README.md) | fewshot_prompt | none | `model.py` |
| [lmstudio_prompt](methods/lmstudio_prompt/README.md) | lmstudio_prompt | none | `model.py` |
| [qwen_qlora](methods/qwen_qlora/README.md) | qwen_qlora | former `finetuning/` | [enhanced](methods/qwen_qlora/enhanced/README.md) |
| [nemotron_qlora](methods/nemotron_qlora/README.md) | nemotron_qlora | former `nemotron3/` | [enhanced](methods/nemotron_qlora/enhanced/README.md) |
| [code_t5](methods/code_t5/README.md) | (notebooks) | former `codeT5/` | none |
| [ludwig](methods/ludwig/README.md) | (notebooks) | former `ludwig/` | none |
| [manual_prompt](methods/manual_prompt/README.md) | (manual) | former `prompt/` | none |

The legacy suite has one pre-existing failure (`test_34`, missing `nemotron3/results/` sample CSV).

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
cd src/text_based
conda run -n genai python -m pytest -q                      # tests/ (new + legacy suite)
cd .. && conda run -n genai python run_all_tests.py         # all three approaches, one process each
```

## Key challenge

Branched midcurves (T, Plus) are not a single linear sequence. The B-rep format with `Lines` and
`Segments` carries the junction topology explicitly; a model must emit valid, correctly connected output.
Leave-one-shape-out evaluation is the planned way to make any claim here honest.
