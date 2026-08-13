# GitHub Issue Drafts -- 2026-08-13

Seven ready-to-paste issues: six covering everything still open in `src/text_based/` (Phase II),
plus one for the last two open `src/image_based/` bugs (Phase I). These are parked rather than
fixed because each needs either a Groq/LLM API budget, a training run, a missing dependency, or a
modelling judgement -- none of which were available in the 2026-08-13 close-out session.

Each body is written to stand alone: someone opening the issue cold, without this repo's session
history, should be able to act on it. Copy the block under each heading directly into the GitHub
issue form.

Suggested milestone for all six: **Phase II re-validation**.

---

## Issue 1

**Title:** `data/csvs/` is stale relative to its generator -- 200 translated rows where config implies 10,404

**Labels:** `bug`, `data`, `phase-2-text`, `priority-high`

**Body:**

The committed CSVs in `src/text_based/data/csvs/` were not produced by the current
`src/text_based/utils/create_brep_csvs.py`. They are the output of an older generator.

Measured composition of `data/csvs/midcurve_llm.csv` (992 data rows):

| Variant | Rows | Matches config? |
|---|---|---|
| `rotated` | 720 | Yes -- 180 angles x 4 shapes, matches `ROTATE_START/STOP/STEP` |
| `scaled` | 64 | Yes -- 16 factors x 4, matches `SCALE_START/STOP/STEP` |
| `mirrored` | 8 | Yes |
| `translated` | **200** | **No** -- config implies 10,404 |

`utils/config.py:52-58` sets `TRANSLATE_X/Y_START/STOP/STEP` to -50..50 step 2, i.e. 51 values per
axis. `create_brep_csvs.py:110-138` (`_translated_variants`) nests both loops, so the current code
would emit `51 * 51 * 4 = 10,404` translated rows. The 200 that actually exist work out to 50 per
shape, which is consistent with an older generator that varied only the diagonal (`dx == dy`) --
exactly the behaviour the current docstring at `create_brep_csvs.py:112-117` ("not just dx == dy
diagonal variants") says was deliberately changed.

Separately: zero rows carry a bare `ShapeName` (`I`, `L`, `T`, `Plus`), even though
`create_brep_csvs.py:338` builds `all_shapes = original_shapes + ...`. The untransformed base
shapes are missing from the dataset entirely.

**Two things need deciding before regenerating.**

1. **The dense grid is probably wrong anyway.** A 51x51 translation grid is a lot of near-identical
   rows. Translation invariance is close to free for a coordinate-regression LLM to pick up from a
   handful of examples, whereas rotation is the transform that actually changes the BRep JSON
   non-trivially. A dense translation grid buys very little and drowns out rotation in the training
   mix. Recommendation: cut to ~5-10 qualitatively different offsets per axis before regenerating,
   so the 10,404 never materializes.
2. Regeneration must happen in the same pass as the split fix (see the leave-one-shape-out issue),
   since both touch `create_brep_csvs.py` and both invalidate existing checkpoints.

**Acceptance:** `data/csvs/` is reproducible from `create_brep_csvs.py` in one command, row counts
match config for every variant type, and the base shapes appear as rows.

---

## Issue 2

**Title:** Train/val/test split leaks near-duplicate transformed variants -- adopt leave-one-shape-out

**Labels:** `bug`, `data`, `phase-2-text`, `priority-high`, `affects-published-metrics`

**Body:**

`utils/create_brep_csvs.py:270-280` (`save_dataset`) calls `random.shuffle(shuffled)` over the full
pool of transformed variants and then slices into train/test/val. There is no grouping by base
shape or by transform family.

Consequence: `T_rotated_44` can land in train while `T_rotated_45` lands in test. Those are one
degree apart -- essentially the same BRep JSON with coordinates shifted by hundredths. The model
can score well on the held-out split by near-memorization rather than by generalizing the
profile -> midcurve transformation. Both `finetuning/` and `nemotron3/` inherit this, since both
read `midcurve_llm_{train,test,val}.csv` directly.

This is the same root cause independently flagged in `geometry_based` (B5) and in the
`image_based` leakage findings. All three phases share the same 4 base shapes and the same
failure mode.

**Decided fix (2026-08-02): leave-one-shape-out.** Split by base shape identity, not by a flat
shuffle over augmented variants. Train on I/L/T, test entirely on Plus (rotating which shape is
held out). No augmented variant of the held-out shape appears in training at all.

*Rejected alternative:* held-out transform ranges (e.g. reserve rotations 150-180 degrees). Keeps
all 4 shapes in both splits but still risks family-level overfitting, since the model has seen the
shape itself, just not that exact transform. Leave-one-shape-out is the cleaner test of real
generalization.

**Read this part before starting.** Regenerating `data/csvs/` invalidates every existing
fine-tuned checkpoint's original split. The headline Phase II figures --

> QLoRA Qwen2.5-7B: MAE=0.78, RMSE=1.24, Hausdorff=2.1, PSR=98% on a 100-sample test set

-- were all measured under leakage and have to be re-measured afterwards. **They will very likely
get worse.** That is the point of the fix, not a regression. Whoever picks this up should plan for
a re-training run, not just a data edit, and should update every place those numbers are quoted
(`README.md`, `CLAUDE.md`, `analysis_report.md`, the papers under `publications/`).

Caveat worth stating in the writeup: with only 4 shapes, leave-one-shape-out means holding out 25%
of all topological families. That is statistically thin. It gets more meaningful once the shape
families are expanded (see the related issue).

**Do this in the same pass as the stale-CSV issue** -- both change `create_brep_csvs.py` and both
force a regeneration.

---

## Issue 3

**Title:** Only 4 topological families exist anywhere in the Phase II pipeline

**Labels:** `enhancement`, `data`, `phase-2-text`, `help-wanted`

**Body:**

`src/text_based/data/brep/` contains exactly `I.json`, `L.json`, `Plus.json`, `T.json`. There is
no ingestion path for richer shapes analogous to `src/data/raw/PhDdata/`.

Every one of the ~1,000 training rows is a rigid or scale transform of one of these 4 polygons.
The model can therefore only ever be tested on interpolations of four junction topologies: none,
L-corner, T-junction, and +-junction. Combined with the split leakage issue, the test set never
contains a topology the model has not already seen in some rotation or scale.

This is a ceiling on what any Phase II result can claim, and it caps how meaningful the
leave-one-shape-out split can be.

**This is content authoring, not a code fix** -- which is why it is parked rather than done.

Two workable routes:

- Run `create_brep_jsons.py` (already written, currently unused beyond the 4 seed shapes) against
  additional shape pairs from the Yogesh-method dataset.
- Synthesize new rectilinear polygons with known medial axes directly in BRep JSON.

Target: enough families that holding one out is a real generalization test rather than a 25% cut.
Good candidates are shapes with junction types absent today -- Y-junctions, multiple disjoint
branches, nested or concave features.

---

## Issue 4

**Title:** `combined_score` ignores MAE, RMSE, and vertex_count_accuracy

**Labels:** `enhancement`, `metrics`, `phase-2-text`, `priority-low`, `needs-decision`

**Body:**

In `finetuning/metrics.py:242-256` (`compute_all_metrics`), the metrics `mae`, `rmse`, and
`vertex_count_accuracy` are computed and returned in the metrics dict, but never enter
`combined_score`, which is:

```
combined_score = 0.4 * distance_score(hausdorff)
               + 0.3 * topology_score
               + 0.3 * connectivity_score
```

So a prediction with exactly the right point count and low MAE, but one middling Hausdorff
outlier, scores identically to a prediction with a wildly wrong point count. The headline number
the pipeline reports is blind to three metrics it already paid to compute.

Not a correctness bug -- nothing produces a wrong value. It is a design gap.

**Why this is parked rather than fixed:** picking new weights is a modelling judgement, not a
mechanical edit. Whoever takes it should decide deliberately how much vertex-count fidelity ought
to count against geometric distance, and record the reasoning in `analysis_report.md`. Changing
the weights also silently changes every previously reported `combined_score`, so any historical
comparison needs a note about which weighting produced it.

Related: `analysis_report.md` R3 pairs this with the (already fixed) MAE/RMSE symmetry bug B3.

---

## Issue 5

**Title:** `nemotron3/run_demo.py` near-duplicates `fewshot_prompter.py`

**Labels:** `refactor`, `phase-2-text`, `priority-low`, `good-first-issue`

**Body:**

`nemotron3/run_demo.py` (325 lines) re-implements, almost verbatim, what `FewShotPrompter` in
`nemotron3/fewshot_prompter.py` already does: the few-shot examples, the system prompt,
prompt-building, generation, JSON extraction and repair, and the evaluation loop.

Any future fix to the repair logic or the prompt wording has to be applied twice or the two drift
apart. They have already started to: `MAX_NEW_TOKENS=128` and `MAX_INPUT_LEN=512` are hardcoded
module constants at `run_demo.py:45-46`, but constructor defaults in `FewShotPrompter.__init__` at
`fewshot_prompter.py:77`.

**Fix:** make `run_demo.py` a thin CLI wrapper around
`FewShotPrompter(n_samples=7, ...).evaluate()`. Delete the duplicated logic rather than trying to
keep the two in sync.

Reasonable first contribution -- the target behaviour is already specified by the existing class,
and correctness is checkable by diffing the demo output before and after.

---

## Issue 6

**Title:** `test_34_nemotron3_results_placeholder_exists` fails -- `nemotron3/results/` does not exist

**Labels:** `bug`, `tests`, `phase-2-text`, `priority-low`, `good-first-issue`

**Body:**

A full `python -m pytest` run from `src/` on 2026-08-13 gives **81 passed, 1 failed, 2 skipped**.
The single failure is `test_34_nemotron3_results_placeholder_exists`, and it is not a regression --
it has been carried across several sessions.

Cause: `text_based/testing/test_text_based.py:419` asserts the presence of

```
src/text_based/nemotron3/results/evaluation_results_sample.csv
```

The entire `nemotron3/results/` directory does not exist on disk. It is a runtime output directory,
created only when `evaluate.py` or `run_demo.py` actually runs, and no placeholder is tracked.

`codeT5/results/` already ships exactly this placeholder file (`evaluation_results_sample.csv`), so
`nemotron3/` is the odd one out rather than the test being wrong -- the test was clearly written to
mirror the codeT5 convention.

**Fix, either way round:**

- Add `nemotron3/results/evaluation_results_sample.csv` with the same header row and a
  representative sample row as the codeT5 one, so the two approach folders behave identically.
  This is the consistent option and matches the test's evident intent.
- Or relax the test to assert the directory is creatable rather than that the file is present.

Prefer the first.

**Acceptance:** `python -m pytest` from `src/` is green with 0 failures on a clean checkout.

---

## Issue 7

**Title:** Phase I: augmentation leakage (Bug 7) and non-regenerable `unet-splits/` (Bug 11)

**Labels:** `bug`, `data`, `phase-1-image`, `priority-medium`, `affects-published-metrics`

**Body:**

The last two open items in `src/image_based/analysis_report.md`. Every other catalogued Phase I bug
is fixed (48/48 tests passing); these two were deferred together because they are one job, not two.

**Bug 7 -- augmentation-level leakage.** Train/test splits are made by a flat shuffle over
augmented variants of only 4 base shapes, so a held-out sample can be a rotated or translated
variant of a training shape. Note this is *not* the same as the already-fixed Bug 6 (which stopped
the models evaluating on their literal training data); the leakage survives that fix.

**Bug 11 -- `unet-splits/` cannot be regenerated.** The directory exists on disk but there is no
reproducible path from raw `.dat`/`.mid` files to its current contents.

**Decided fix (2026-08-02): leave-one-shape-out.** Group by base shape identity before splitting,
in `utils/prepare_data.py`, then regenerate `image-pairs/`, `unet-splits/` and `images-combo/` from
scratch. Regenerating through the fixed generator resolves Bug 11 as a side effect. This is the same
fix being applied to Phase II, and the root cause is shared across all three phases.

**Why this was not executed on 2026-08-13, in detail** -- three separate blockers, any one of which
is sufficient:

1. **Missing dependency.** `utils/prepare_data.py` rasterizes via DrawSVG. `drawsvg` is not
   installed in the `genai` environment that is now available (`pycairo` is present; `drawsvg` and
   `cairosvg` are not). The original `midcurvenn` environment no longer exists. There is also
   version drift to check before trusting any regeneration: the env has TensorFlow 2.18 and NumPy
   2.2.6, whereas `environment.yml` pins TensorFlow 2.13 on Python 3.10.
2. **The datasets are tracked in git.** `image-pairs/` (896 files), `unet-splits/` (3,000) and
   `images-combo/` (448) are all committed -- 4,344 files, none covered by `.gitignore`.
   Regenerating produces a diff touching every one of them.
3. **Regenerating without retraining makes the repo strictly worse.** All committed results,
   metrics and result grids were produced against the *current* splits. New splits invalidate every
   one of them. Retraining all seven image-based variants to restore consistency is a multi-hour
   GPU job, not a tail-end task. Half-doing this leaves datasets and published results that
   silently disagree -- worse than the current state, which is at least internally consistent and
   documented as leaky.

**So whoever picks this up should plan for the whole sequence in one go:** install `drawsvg`,
verify the environment against `environment.yml`, change the split logic, regenerate all three
dataset directories, retrain the variants, refresh the result grids, and update every quoted
metric. Anything less should not be merged.

**Acceptance:** `image-pairs/`, `unet-splits/` and `images-combo/` are all reproducible from
`python utils/prepare_data.py` alone; no augmented variant of a held-out shape appears in training;
`pytest image_based/` still green; reported metrics re-measured and re-labelled as
leave-one-shape-out.
