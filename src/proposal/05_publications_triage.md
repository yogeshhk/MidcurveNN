# publications/ triage (draft, 2026-11-01)

Status: proposal only, nothing moved or zipped. Sizes are from a directory scan on 2026-11-01.
Rule (from the user): items already submitted or published are not reviewed. Running LaTeX items
stay live and get updated once the code produces new results. Everything old and not reusable gets
zipped and kept.

## Live (keep, update later with new results)

| Item | Notes |
|---|---|
| `Midcurve_LaTeX/Main_Paper_MidcurveNN_Comprehensive.tex` (72 KB) | All 3 phases in one paper. With three separate papers planned, this may split (decision D5). |
| `Midcurve_LaTeX/Main_Seminar_Midcurve_Presentation.tex` + `Main_Seminar_Midcurve_CheatSheet.tex` | Both driver files are 0 KB on disk, and so is `seminar_midcurve_content.tex`. The 7.4 MB PDF exists, so the sources may have been emptied by accident. Check before any rebuild. |
| `Midcurve_LaTeX/Main_TwoPager_MidcurveNN_GeometryResearch.tex` + `Main_Carousel_...` | Phase III research topic, written 2026-08-13. |
| `Midcurve_LaTeX/midcurve_*.tex`, `template_*.tex`, `images/` | Shared bodies used by the above. |

Papers decision (2026-11-01): add three new papers in `Midcurve_LaTeX/`, named
`Main_Paper_MidcurveNN_Image.tex`, `Main_Paper_MidcurveNN_LLM.tex` and
`Main_Paper_MidcurveNN_Graph.tex`. Each reuses the shared `midcurve_intro.tex` / `midcurve_refs.tex`
bodies and draws on the matching `midcurve_impl_*.tex`. Write them only after each track has new
results. The comprehensive paper stays as the overview and is updated last.

## Already archived (no action)

The 10 zips already in `publications/` (6 `MidcurveNN_*` talks and papers 2019-2025, 3
`MidcurveLLM_*` 2024, and `FBD_MastersThesis.zip`, about 130 MB in total).

DECIDED 2026-11-01:

- zip ONLY `Midsurface_PhDThesis/` (as `Midsurface_PhDThesis.zip`)
- move `MediumBlogs/` -> `D:/Yogesh/GitHub/Publications/Articles/MidcurveNN_MediumBlogs/`
- `prompts/` stays in MidcurveNN; it is NOT moved to Publications (user, 2026-11-01). The user
  feeds these to every new model as few-shot prompts. The text track builds them into a
  "check a new model" tool (`text_based/run.py check-model`, templates in `text_based/prompts/`).
  The originals move from `publications/prompts/` to `src/text_based/prompts/research/` after the
  user confirms.
- move `linkedin_post_2026-08-13.md` -> `D:/Yogesh/GitHub/Publications/Posts/`
- move `IntroToGeoMod/` -> `D:/Yogesh/GitHub/Publications/LaTeX/IntroToGeoMod/`

For each move: list the destination first, then move, then list the destination and confirm the
file count and size. Zip procedure: dry run
first. After zipping, verify the zip's entry count (3,585) and size before deleting the folder, and
ask the user before the delete.

## Proposed to zip (old, not live) - needs user confirmation per item

| Item | Size | Reason |
|---|---|---|
| `Midsurface_PhDThesis/` | 210 MB, 3,585 files | Finished thesis; largest folder. Earlier sessions already moved its Viva material out. |
| `MediumBlogs/` | 9 MB | Published blog PDFs. `nemotron3_midcurve_blog.md` may already be published too (the May 2026 Medium PDF exists). |
| `KaggleNotebooks/` | 0.5 MB | Do NOT zip; distribute into the approaches instead (see "KaggleNotebooks: move into the approaches" below). |
| `prompts/` | 0.2 MB | 2025 research prompts to ChatGPT/Gemini/Perplexity/Claude. |
| `linkedin_post_2026-08-13.md` | tiny | Posted announcement. |

## KaggleNotebooks: move into the approaches (checked 2026-11-01 by MD5 and size)

| File | Finding | Proposed destination |
|---|---|---|
| `MidcurveNN_simple_encoderdecoder.ipynb` | byte-identical to `src/image_based/simpleencoderdecoder/notebook_simple_encoderdecoder.ipynb` | drop the duplicate (keep it inside the zip only) |
| `midcurvellm-finetune-codet5.ipynb` | 45,777 B vs 45,785 B for `src/text_based/codeT5/Kaggle_Fine_tune_CodeT5_for_midcurve_generation.ipynb`; near-duplicate, diff before deciding | drop if the diff is trivial, else `text_based/codeT5/` |
| `midcurvellm-finetune-ludwig.ipynb` | no copy in `src/` | `src/text_based/ludwig/` |
| `MidcurveNN_Dataset_README.md/.png` | describes the published Kaggle image dataset | `src/image_based/data/` (as `KAGGLE_DATASET_README.md`) |
| `MidcurveLLM_Dataset_README.md/.png` | describes the published Kaggle text dataset | `src/text_based/data/` (as `KAGGLE_DATASET_README.md`) |
| `simpleencoder_decoder_batch5_epochs200_earlystop50.png` | old result plot | `src/image_based/simpleencoderdecoder/results/` |

## Unclear: not MidcurveNN, ask the user

| Item | Question |
|---|---|
| `IntroToGeoMod/` (48 MB) | Not MidcurveNN; CAD/geometric-modelling talks and notes. DECIDED 2026-11-01: move (not zip) to `Publications/LaTeX/IntroToGeoMod/`. Dry-run listing first, then list the destination and confirm the file count (159) and size (48.2 MB). |
| `Midsurface_LaTeX/` (TopoVal expanded v1 2026) + `Midcurve_LaTeX/Main_Paper_TopoVal_upgraded.tex` + `body_topoval_nonupgraded.tex` | DECIDED 2026-11-01: `Midsurface_LaTeX/` stays live. Zip `Main_Paper_TopoVal_upgraded.tex` + `body_topoval_nonupgraded.tex` (+ their PDF/aux if any, and images used only by them, checked by grep) out of `Midcurve_LaTeX/`, so that folder holds only MidcurveNN material. |
