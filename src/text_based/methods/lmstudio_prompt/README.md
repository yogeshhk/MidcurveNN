# Prompting through an OpenAI-compatible server (LM Studio)

Client for any OpenAI-compatible server (LM Studio, llama.cpp, vLLM). Greedy by default; if the chat template rejects the system role the system text is merged into the first user turn and the call retried. Also drives `check-model`, the 'is this new LLM any good' probe.

There is no older implementation of this method, so `model.py`, `runs/` and tests sit at this folder's top level and there is
no `enhanced/` folder.

## Commands

Run from `src/text_based`:

```
conda run -n genai python run.py check-model --base-url http://localhost:1234/v1 --model gemma-2-2b-it
conda run -n genai python run.py eval --model lmstudio_prompt --model-id gemma-2-2b-it --format mcv2 --shots 4
```

Run folders land in `runs/<model-id>__<tag>/` here (raw.jsonl, metrics.json, summary.md).

## Results

Results: none. This method has not been run; there is no `metrics.json` for it and no `RESULTS_text.md`. Any older figures in the legacy folders were measured under train/test leakage and are not comparable.

## Status

Code and tests (against a local stub server) exist. A check of `gemma-2-2b-it` stalled earlier (about 19 s for a 5-token reply); no real run completed. Tests: `../../tests/test_text_track.py`.
