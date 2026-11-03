# Few-shot prompting with a local Hugging Face model

Greedy generation from a (base or tuned) causal LM loaded locally, with the shared prompt builder (`common/prompts.py`). No prompt truncation, explicit EOS. Nothing is downloaded unless generate() is called with an uncached model id.

There is no older implementation of this method, so `model.py`, `runs/` and tests sit at this folder's top level and there is
no `enhanced/` folder.

## Commands

Run from `src/text_based`:

```
conda run -n genai python run.py eval --model fewshot_prompt --model-id <hub id> --format mcv2 --shots 4
```

Run folders land in `runs/<model-id>__<tag>/` here (raw.jsonl, metrics.json, summary.md).

## Results

Results: none. This method has not been run; there is no `metrics.json` for it and no `RESULTS_text.md`. Any older figures in the legacy folders were measured under train/test leakage and are not comparable.

## Status

Code and tests exist; never run against a real model in this repository. Tests: `../../tests/test_text_track.py`.
