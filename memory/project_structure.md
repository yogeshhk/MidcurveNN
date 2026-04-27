---
name: MidcurveNN Project Structure
description: New type-based folder layout after 2026-04 refactor — image_based, geometry_based, text_based, testing
type: project
---

After a major refactoring (2026-04), MidcurveNN src/ is organized by data type:

- `src/data/raw/` — raw .dat/.mid files, shared by ALL approaches
- `src/image_based/` — all Phase I raster approaches: simpleencoderdecoder, cnnencoderdecoder, denseencoderdecoder, denoiserencoderdecoder, unet, pix2pix, img2img, kaggle
- `src/geometry_based/` — Phase III: graph_transformer (non-auto-regressive, from scratch), finetuned_graph_transformer (pretrained Graphormer HuggingFace), gnnencoderdecoder (legacy stub)
- `src/text_based/` — Phase II placeholder; data/sequences.json for LLM seq2seq
- `src/testing/` — test_image_based.py, test_geometry_based.py, test_text_based.py, benchmark.py
- `src/utils/` — shared utilities (stays at src level)
- `src/config.py` — global config (stays at src level)

**Why:** user wants approaches organized by data type they operate on (image/geometry/text), not by algorithm name.

**How to apply:** When navigating or editing code, always look in the appropriate type folder. When running commands from src/, prefix paths: `python image_based/unet/...` not `python unet/...`.
