# Phase II (text / LLM based) - static analysis and improvement proposal

Date: 2026-11-01. Scope: `src/text_based/` (utils, finetuning, nemotron3, codeT5, ludwig, prompt,
data/brep, data/csvs, testing), read-only. Nothing was trained, run against a model, or downloaded.
Only tiny pure-Python checks on the checked-in CSVs and on `finetuning/metrics.py` were run.
All paths below are relative to `src/text_based/` unless stated.

## 0. Executive summary (read this first)

The weak results are explained mostly by the DATA and the EVALUATION, not by the choice of LLM.

Top findings, in order of impact:

1. The checked-in CSVs are DOUBLE-ENCODED JSON. Every `Profile_brep` / `Midcurve_brep` cell is a
   JSON string literal that wraps the JSON (starts with a literal `"`, inner quotes written as `\"`).
   `str(row['Profile_brep'])` therefore begins `"{\"Points\": [[...`. Models are trained to emit that
   escaped form, and `GeometricMetrics.parse_brep` (`finetuning/metrics.py:9-24`) cannot read it:
   `json.loads` returns a `str`, `.get` raises, the `except` returns `(None, [])`. Measured: scoring
   the ground truth against itself gives `json_validity=0, hausdorff=1000, combined_score=0`.
   So either the reported numbers (MAE 0.78, PSR 98%) came from an older, clean CSV, or the
   evaluation is currently meaningless. Either way nothing in `data/csvs/` can be trusted as is.
2. Training loss is computed over the whole sequence (system prompt + profile + answer), not only the
   answer (`finetuning/dataset_loader.py:22-27`, `finetuning/train.py:156-165`,
   `nemotron3/dataset_loader.py:21-24`, `nemotron3/hf_sft_trainer.py:121-127`). About 70-80% of the
   loss tokens are prompt tokens the model need not learn. Gradient signal on the part that matters
   (coordinates of the midcurve) is diluted.
3. The task as posed asks an LLM to do float arithmetic on arbitrary-pose coordinates
   (rotation 1..180 deg, scale 2..6, translation -50..50, 2 decimal places) for only 4 base shapes.
   Midcurve coordinates are means of profile coordinates; the model must learn to add and halve
   multi-digit decimals digit by digit. This is the hardest possible way to present the problem.
4. The prompt and the JSON are very verbose. Roughly 300 tokens of constant system prompt plus
   about 400-450 tokens of JSON per sample against `MAX_SEQ_LENGTH=1024`. Little margin; the answer
   (and EOS) sits at the END of the sequence, so any truncation removes exactly what we train on.
5. Train / test leakage (known: A1, A2, A3 in `analysis_report.md`). Measured here in addition:
   the test split is 69% rotations by an integer degree and 23% translations, all of 4 shapes.
   The "nearest training neighbour" of a test row is typically 1 degree away.
6. The metric `combined_score` (`finetuning/metrics.py:247-258`) is nearly constant for any
   connected output: a connected prediction with the right junction count scores >= 0.6 even if
   Hausdorff is 30 units (shape size is about 25-150). The `> 0.7` "high quality" threshold
   (`finetuning/evaluate.py:151`) is passed at Hausdorff 30. For I and L shapes (no junctions)
   topology and connectivity are trivially 1.0.
7. Three divergent copies of the same pipeline (`finetuning/`, `nemotron3/`, notebooks in
   `codeT5/` and `ludwig/`) with four different system prompts, three different data formats
   (BRep JSON, tuple lists, line lists), different decoding and different repair.

The recommended path (details in sections 4-8):
(a) fix the data encoding and the metric first (hours, makes everything measurable);
(b) change the representation: canonical pose + compact integer text + index recipes;
(c) generate many more shapes procedurally with analytic ground truth (shapely);
(d) train on completion only, with a group-aware split;
(e) add an OpenAI-compatible harness so LM Studio models can be evaluated in minutes;
(f) merge the duplicated pipelines into one package with one driver.

## 1. Pipeline trace with file:line

### 1.1 Data creation (`utils/`)

- 4 hand-authored shapes `data/brep/{I,L,T,Plus}.json`. Each has `Profile`, `Midcurve`,
  `Profile_brep`, `Midcurve_brep` (Points / Lines / Segments). Midcurve convention (consistent in all
  four): vertices at the midpoints of terminal end edges, plus the junction at the centre of the
  crossing rectangle (T: `[12.5,22.5]` is the mean of profile corners 0 and 2).
- `utils/config.py:36-58`: scale 2.0..5.75 step 0.25 (16 values; the unscaled original never appears),
  rotation 1..180 integer degrees (no 181-359), translation x,y in -50..50 step 2 (51 x 51), mirror x,y.
- `utils/create_brep_csvs.py:61-185`: variants of each base shape; `:239-289` `save_dataset`
  shuffles ALL variants flat and slices 80/10/10 (leakage, A2).
  `:338` `all_shapes = original_shapes + variants` (originals present in code, absent from the
  stale CSV, A1).
- `utils/prepare_data.py:227-239` `_apply_transform` rounds to 2 decimals after every transform, so
  rotated "midcurve" points are only equal to the true midpoints within about 0.005 (fine), but the
  numbers have irregular digit patterns (e.g. `-17.48`, `-15.93`).
- `utils/prepare_data.py:246-293`: Lines / Segments never change (valid). Mirror flips polygon
  orientation (CW vs CCW) silently; the model sees both orientations but only 8 mirrored rows.
- Checked-in CSV measured: 992 rows (train 793 / val 100 / test 99), families I 200+, L 188,
  T 207, Plus 198 in train. Compositions: rotated 720, translated 200, scaled 64, mirrored 8.
  Max cell sizes: profile 394 chars, midcurve 184 chars.
- CSV encoding defect: see finding 1. The writer in `utils/create_brep_csvs.py:192-213` does
  `json.dumps(dict)` once, which pandas then quotes correctly; the checked-in file was therefore
  produced by an older writer that dumped twice. `data/shapes2brep.csv` (Ludwig) is single-encoded.
  Test 20/21 in `testing/test_text_based.py` only check columns and non-emptiness, so they do not
  catch this.

### 1.2 Prompt / chat template

- Training text: `finetuning/dataset_loader.py:15-27` and `nemotron3/dataset_loader.py:16-24`:
  system = `Config.SYSTEM_PROMPT`, user = raw BRep JSON string, assistant = raw BRep JSON string,
  rendered with `apply_chat_template(..., add_generation_prompt=False)` into one `text` field.
- System prompts: `finetuning/config.py:75-93` (about 1400 chars, about 300 tokens, includes the
  vague rule "approximately equidistant"), `nemotron3/config.py:34-53` (slightly different),
  `nemotron3/fewshot_prompter.py:57-71` (third variant with per-family hints),
  `ludwig/prompt.txt` and `prompt/midcurve_prompt.txt` (tuple / line-list formats, a fourth and
  fifth format). Training and inference within one pipeline agree (same function builds both), but
  across pipelines they do not, so comparisons between pipelines are not like-for-like.
- `finetuning/config.py:95-101` `FEW_SHOT_EXAMPLES` is defined and never used.

### 1.3 Tokenization / length

- `MAX_SEQ_LENGTH = 1024` (`finetuning/config.py:35`, `nemotron3/config.py:26`, `unsloth_trainer.py:48`).
  `finetuning/train.py:56` smoke test sets it to 128, which truncates every sample before the answer.
- Rough budget per sample (estimate: digits are single tokens in Qwen): system 300 + profile 200-250 +
  midcurve 100-130 + template 20 = 620-700 tokens typical, up to about 800-900 for rotated Plus with
  negative coordinates. Margin to 1024 is thin and tokenizer dependent (Nemotron / CodeT5 tokenise
  digits differently). A length audit script is in the action list (A-03); nothing guarantees today
  that the final `}` and EOS survive.
- `codeT5/Kaggle_...ipynb`: `max_input_length=256`, `max_target_length=128` with `truncation=True`
  and padding to max length: a Plus profile (394 chars) very likely exceeds 256 BPE tokens and its
  midcurve (182 chars) may exceed 128, so the targets are silently cut. Needs the same audit.

### 1.4 Loss masking

- All four trainers use `SFTTrainer(dataset_text_field="text")` on the full chat string:
  `finetuning/train.py:156-165`, `nemotron3/hf_sft_trainer.py:121-127,151-154`,
  `nemotron3/train.py` (same), `nemotron3/unsloth_trainer.py`/`train_unsloth.py`.
  No `DataCollatorForCompletionOnlyLM`, no `response_template`, no `assistant_only_loss`.
  Consequence: the model also learns to reproduce the constant system prompt and the profile JSON.
  The profile is about 60% of the variable tokens, so most of the gradient teaches copying the input.
- `pad_token = eos_token` (`finetuning/train.py:70`, `nemotron3/hf_sft_trainer.py:65`,
  `unsloth_trainer.py:98`). For Qwen-Instruct the EOS is `<|im_end|>`. Depending on the TRL
  version, the collator masks every position equal to `pad_token_id`, which also masks the real
  end-of-answer token, so the model may never learn to stop. Symptom to look for: outputs that
  continue past the closing brace (hence the `index('{')`/`rindex('}')` slicing in
  `finetuning/inference.py:56-63`). Verify with the label dump in action item B-04.
- TRL version: the Python here reports `trl 0.13.0`. `finetuning/train.py:156-165` passes
  `tokenizer=`, `max_seq_length=`, `dataset_text_field=` directly to `SFTTrainer` and a plain
  `TrainingArguments`; these moved into `SFTConfig` / `processing_class` in 0.12-0.14 and later
  versions reject them. `nemotron3/*` has try/except shims, `finetuning/train.py` does not.
  Also `train.py:98` defaults `attn_implementation="flash_attention_2"` (`config.py:39`), which
  needs the `flash-attn` wheel and fails on a stock Windows install.

### 1.5 LoRA / optimisation

- r=16, alpha=32, dropout 0.05, all attention + MLP projections (`finetuning/train.py:107-115`;
  nemotron3 uses `"all-linear"`). Reasonable.
- LR 2e-4, cosine (with restarts in finetuning, `train.py:132`; restarts are pointless for 3 epochs),
  warmup 3%, `max_grad_norm=0.3`, batch 4x4 = 16 (finetuning) or 1x16 (nemotron3), 3 epochs.
  793 rows / 16 = about 50 steps per epoch, about 150 optimiser steps in total. That is very few
  steps to learn digit-level arithmetic. 4-bit NF4 base with 8-bit paged AdamW adds noise to numeric
  fidelity.
- Best checkpoint chosen by `eval_loss` on a leaked val set (`train.py:144-145`): it picks the
  checkpoint that memorises best.
- Train / inference quantisation mismatch: training uses a 4-bit NF4 base
  (`finetuning/train.py:83-99`); `finetuning/inference.py:23-33` and `finetuning/evaluate.py:30-41`
  reload the base in fp16 and `merge_and_unload()` the adapter. Merging a QLoRA adapter into a
  different-precision base is a known source of small numeric drift, which matters when the output
  is exact digits. `nemotron3/inference.py:61-73` keeps the 4-bit base and does not merge (consistent).

### 1.6 Decoding / evaluation

- `finetuning/config.py:64-67`: greedy (`DO_SAMPLE=False`), `TEMPERATURE=0.1` is ignored when
  not sampling (HF warns), `MAX_NEW_TOKENS=512`, no `eos_token_id` / stop strings, no constrained
  decoding.
- Retry logic is ineffective in two places. `nemotron3/inference.py:94-100,198-225`: `do_sample=False`
  on every attempt so the 3 retries return the identical string. `finetuning/inference.py:166-173`:
  attempt 0 greedy, later attempts sampled at temperature 0.1-0.3, which is fine, but a
  `max_retries` loop on parse failure only helps for syntax errors, not for wrong numbers.
- Repair step masking errors (cases where repair hides model failures):
  - `finetuning/inference.py:129,144`: connectivity is always seeded from node 0 and repaired by
    adding the nearest edge. A prediction with 5 floating, unrelated points becomes a "connected"
    tree and then scores `connectivity_score=1.0`. Repair success is reported as `success=True`
    (`:195-199`) and mixed into the same metrics as unrepaired outputs. Report raw vs repaired.
  - `nemotron3/inference.py:149-157` `_ensure_lines` fabricates a polyline through the points in
    emission order when `Lines` is empty. This can turn a topologically wrong T into a plausible
    path. `fewshot_prompter.py:210-218` does the same.
  - `nemotron3/inference.py:160-192` `_repair` indexes `adj[ln[0]]` without a bounds check
    (KeyError on any out-of-range index in a model output); the `finetuning` version guards it
    (`:114`), so behaviour differs by pipeline.
  - `finetuning/inference.py:85-90`: the "out of range" check uses profile ranges (x 2) and flags
    only; it never rejects.
- Few-shot path (`nemotron3/fewshot_prompter.py`):
  - `:77` `max_new_tokens=128` too short for a 5-point Plus midcurve in JSON (about 100-140
    tokens) - truncated JSON then fails parse.
  - `:160-162` `truncation=True, max_length=512` on the PROMPT. The prompt is system (about 220
    tokens) + 2 examples (about 250) + query (up to 250) which can exceed 512. With the default
    right-side truncation the end of the prompt, including `Midcurve:` and the generation prompt,
    is cut off, so the model continues the profile instead of answering. Silent and nasty.
  - `:171` `repetition_penalty=1.1` penalises repeated digits, `], [` and repeated coordinates -
    exactly the repetitive structure of the answer. It actively corrupts numeric output.
  - `:172` `temperature=1.0` with `do_sample=False` is a no-op warning.
  - `:42-55` the two few-shot examples are rows from the training CSV (the first is the first
    train row `I_rotated_72`) and only cover I and L; the system prompt describes T and Plus but no
    example demonstrates a junction. Only 7 test rows are evaluated (`n_samples=7`, `:77`), so the
    published "85.7% PSR" is 6/7 and has a 95% interval of roughly 49%-97%.

### 1.7 Metrics (`finetuning/metrics.py`, copy in `nemotron3/metrics.py`)

- All geometry metrics (Hausdorff, Chamfer, MAE, RMSE) are computed on the VERTEX set only
  (`:45-50`, `:34-37`), never on the polylines. A midcurve is a set of segments; vertex-only
  distance ignores edges entirely: a T with the right 4 vertices but the wrong edges (a path
  instead of a star) scores perfect geometry.
- `topology_accuracy` (`:91-119`) only compares the COUNT of degree>2 vertices: wrong edges with
  the same count score 1.0; I and L (0 junctions both) are always 1.0.
- `connectivity_score` returns `1/components` (`:160`); isolated extra vertices lower it only mildly.
- `combined_score` (`:247-258`) = 0.4/(1+H/10) + 0.3 topology + 0.3 connectivity. With the two
  trivial terms equal to 1 this is >= 0.6 for ANY output that parses and is connected. B7 in the
  old report understated this; it is the main reason the headline numbers look good.
- MAE / RMSE with equal point counts compare points by index (`:71,89`) - correct only if the model
  also keeps the ground-truth vertex ORDER, which is an arbitrary authoring convention (hub is
  index 1 in T, index 4 or 1 in Plus). A correct midcurve emitted in another order is penalised;
  with unequal counts the metric silently switches to Chamfer, so the metric is discontinuous.
- Errors are in raw units, not normalised by shape size. Scale 2..6 and translation +-50 make a
  Hausdorff of 2.1 mean very different things on different rows.
- `json_validity` is 1 for any dict, even `{}` or without `Points`. Failures return 1000.0 /
  inf into `hausdorff` / `chamfer` means, so the mean is dominated by outliers (no median / trimmed
  report except `median_hausdorff` in `evaluate.py:183`).
- No baseline. A trivial baseline (copy the midcurve of the nearest training shape, rescaled by
  bounding box) would show how much of the score comes from memorisation. No confidence intervals.
- `finetuning/evaluate.py:190-200` `evaluate_by_complexity` groups by substring tests such as
  `'I_' in name`; these are fragile (any new shape name containing such a substring would be
  misgrouped). Use an explicit `family` column instead.

### 1.8 Duplication inventory

| Concern | `finetuning/` | `nemotron3/` | other |
|---|---|---|---|
| config | `config.py` (Qwen) | `config.py` (Nemotron) | `config_enhanced.py` alias shim |
| dataset formatting | `dataset_loader.py` | `dataset_loader.py` (about 50 diff lines) | ludwig yaml template, codeT5 prefix |
| train (HF QLoRA) | `train.py` | `train.py` AND `hf_sft_trainer.py` (same job, function vs class) | codeT5 Lightning, ludwig yaml |
| train (Unsloth) | - | `train_unsloth.py` AND `unsloth_trainer.py` (same job) | - |
| inference + repair | `inference.py` (MST repair, retries) | `inference.py` (own repair) | `model_server.py` third copy of generate |
| few-shot | - | `fewshot_prompter.py` AND `run_demo.py` (324 lines duplicate) | `prompt/midcurve_generator.py` (LangChain, loop commented out) |
| metrics | `metrics.py` (269 lines) | `metrics.py` (142 lines, subset) | `test_metrics.py` |
| evaluate | `evaluate.py` | `evaluate.py` | `error_analysis.py`, `model_comparison.py` |

## 2. Why the results are poor: ranked diagnosis

| Rank | Cause | Evidence | Confidence |
|---|---|---|---|
| 1 | Double-encoded CSV -> unparseable targets and zero-valued metrics | section 1.1 / 1.7, measured | certain (verified) |
| 2 | Metric cannot discriminate (combined_score floor 0.6) and vertex-only | `metrics.py:247-258` | certain |
| 3 | Leakage: 4 shapes, 1-degree neighbours across splits; no baseline | A1-A3, plus measured composition | certain |
| 4 | Loss on prompt tokens; EOS possibly masked | `dataset_loader.py`, `train.py:70,156` | high |
| 5 | Representation: absolute pose, 2-dp floats, verbose JSON, arithmetic by digits | section 1.1, 1.3 | high |
| 6 | Few shot prompt truncated at 512 tokens, 128 new tokens, repetition penalty | `fewshot_prompter.py:77,160-172` | certain (code) |
| 7 | Too few optimiser steps (about 150) and checkpoint picked on leaked val loss | `config.py:28-35` | medium |
| 8 | QLoRA train vs fp16 merge at eval | `inference.py:23-33` vs `train.py:83` | medium |
| 9 | Retry/repair hides failures and inflates success | section 1.6 | high |
| 10 | Only 4 topologies: cannot generalise; no test for generalisation | A3 | certain |

Note on item 5: an LLM does not need to generate coordinates at all for this task. See the
"recipe" format in section 4.3: if every midcurve vertex is expressed as the mean of a few profile
vertex indices, the output is a handful of small integers and all pose / scale / rotation issues
vanish exactly (affine equivariance), with no arithmetic required of the model.

## 3. What should be preserved (genuine strengths)

- BRep topology authoring in `data/brep/*.json` is correct (explicit star topology at junctions).
- Transform code (`utils/prepare_data.py`) is correct and reusable for tests.
- `nemotron3/fewshot_prompter.py:178-208` JSON extraction (fence + brace matching) is the best of the
  parsers; reuse it. Greedy MST repair is fine as an OPTIONAL post step if reported separately.
- The old `analysis_report.md` fixes (B1, B3, B5, B6, B8, B9) remain valid.

## 4. Proposed fixes, ranked by impact / effort

Legend: impact H/M/L, effort S (under 1 h) / M (1-3 h) / L (half day or more).

| # | Fix | Impact | Effort |
|---|---|---|---|
| F1 | Un-double-encode CSVs, make parsers unwrap strings, add a data-encoding test | H | S |
| F2 | Replace `combined_score` with normalised, polyline-based metrics + baselines + CIs | H | M |
| F3 | Completion-only loss with explicit label masking, EOS kept, own collator | H | M |
| F4 | Fix few-shot prompter (no truncation, 768 tokens, no repetition penalty, held-out examples) | M | S |
| F5 | Canonical pose (translate / scale / rotate / start vertex / orientation) | H | M |
| F6 | Compact integer text format (vertex list + edge list), tiny system prompt | H | M |
| F7 | Procedural shape generator with analytic midcurve (shapely) | H | L |
| F8 | Group-aware splits (instance, family, hardest = held-out topology) | H | M |
| F9 | Recipe format (vertex = mean of profile vertex indices), coordinates computed by code | H | M |
| F10 | Constrained decoding (JSON schema in LM Studio / llama.cpp grammar / outlines for HF) | M | S-M |
| F11 | Curriculum (I, L -> T, Plus -> multi-branch / unequal widths) | M | S |
| F12 | LM Studio / OpenAI-compatible evaluation harness + smoke test | H (for iteration speed) | M |
| F13 | One package, one driver, archive the rest | M (maintenance) | L |
| F14 | Smaller model (Qwen2.5-Coder 1.5B / 3B) and more steps; match train/eval precision | M | S |

### 4.1 Canonicalisation (F5)

Goal: the model sees one pose. Steps (all invertible; store the inverse in the dataset row):
1. Orientation: force CCW (signed area > 0); if mirrored, reverse vertex order.
2. Rotation: for rectilinear and near-rectilinear shapes, rotate so the longest edge is horizontal
   (angle of longest edge, snapped to the nearest multiple of 90 degrees when within 1 degree).
   Result: the 1..180 rotation augmentation becomes unnecessary; test-time rotated input is
   normalised the same way. For generic shapes keep principal-axis alignment (minimum-area
   rectangle via shapely `minimum_rotated_rectangle`).
3. Translation: subtract bbox min so the shape sits at the origin.
4. Scale: divide by the longer bbox side and multiply by 1000, round to integers (quantisation
   error 0.1% of size). Keep `scale` and `offset` in the row to undo.
5. Start vertex: the vertex with the smallest (y, x) after steps 1-4; list CCW from there.
6. Midcurve vertex order: DFS from the vertex nearest the start in canonical order; edges as
   sorted `i-j` pairs with `i<j`. This removes the arbitrary index convention that makes MAE by
   index unfair.

Dataset augmentation after canonicalisation should be SHAPE augmentation (new widths / lengths /
arm counts, F7) plus cheap dihedral symmetries (8 flips / 90 deg turns), re-canonicalised so the
model keeps seeing canonical pose but with different start vertices. Do not use independent noise
on profile and midcurve (as `finetuning/augmentation.py:36-52` does): it destroys the exact
relation between them. Non-uniform scaling (`augmentation.py:54-64`) is valid for rectilinear
shapes only if widths and lengths are both scaled consistently (it changes wall thickness, so the
midcurve is still the centreline only for axis-aligned arms); keep it behind the generator, not as
a post-hoc row transform.

### 4.2 Compact text format (F6)

Current: about 420 characters of JSON per pair plus 1400 characters of prompt.
Proposed format "mcv1" (one line per field, integers on a 0..1000 grid):

Prompt (user message only, system message of about 40 tokens or none):
```
profile n=8
0,1000 1000,1000 1000,800 600,800 600,0 400,0 400,800 0,800
```
Completion:
```
midcurve n=4 e=3
500,0 500,900 1000,900 0,900
1-0 1-2 1-3
```
Rules: coordinates are `x,y` integers separated by spaces; second block is vertex list (index =
position); third line is edges `a-b` with `a` hub-first, then sorted. No Segments (derivable:
each edge is its own segment for midcurves; one loop for profiles). Provide `encode_mcv1()` and
`decode_mcv1()` plus a converter to the legacy BRep dict so metrics, plots and tests keep working.
Expected effect: roughly 5x fewer tokens per sample, no JSON escape problems, no
unbalanced-brace failure mode, easy regex parsing (add the fallback regex as the global rules
require), `max_seq_length=512` is then safe.

### 4.3 Recipe format (F9) - removes numeric generation entirely

Observation, verified by hand on the four base shapes: every midcurve vertex equals the mean of one,
two or four profile vertices (I: ends are means of the two end-cap vertices; L: bend =
mean of profile vertices 2 and 5 `[(38,58),(33,63)] -> (35.5,60.5)`; T hub = mean of vertices 0 and
2 `[(0,25),(25,20)] -> (12.5,22.5)`). Format "mcv2" completion:
```
v0 = mean(4,5)
v1 = mean(0,2)
v2 = mean(1,2)
v3 = mean(0,7)
e 1-0 1-2 1-3
```
Pros: output is a few small integers (tiny vocabulary of tokens), exact affine equivariance
(no canonicalisation needed for correctness), coordinates computed deterministically by code, the
LLM only decides topology and which profile vertices pair up - the part that is genuinely
"reasoning". Cons: the generator must find a recipe for each vertex (search subsets of size 1-4,
tolerance 1e-6); where no subset matches (unequal arm widths at a junction) fall back to explicit
coordinates `v3 = (437,812)` or exclude those shapes from the recipe training set. Evaluate mcv1
vs mcv2 head to head; mcv2 is the likely winner and also the easiest for few-shot prompting with
a general LM Studio model.

### 4.4 Procedural data with analytic ground truth (F7, F8)

Generate skeleton first, polygon second (so ground truth is exact and unlimited):
- Skeleton: random tree on an integer grid with axis-aligned arms (phase 1), arms 2-5 per hub,
  1-3 hubs, arm lengths in [3w, 12w], widths per arm in {2,3,4,5,6,8} (phase 1: single width per
  shape; phase 2: per-arm widths).
- Polygon: for each skeleton edge build `LineString.buffer(w/2, cap_style=2)` (flat) for leaf ends;
  at degree-2 bends extend the two edges by the other edge's half width (cap_style square on that
  end only) so the outer corner is sharp; at hubs (degree >= 3) no extension (each of the hub
  square's quadrants is covered by an arm; verified on T and Plus). `unary_union`, then
  `.simplify(0)` / drop collinear vertices, assert `Polygon.is_valid`, single exterior ring,
  no holes (O-shapes need two loops: out of scope in v1; note in README).
- Ground truth = the skeleton graph (nodes of degree 2 that are collinear are dropped, leaf ends
  at the cap midpoints) - this reproduces the convention in `data/brep/*.json`. Reject generated
  shapes whose pixel-exact dims match the hand-authored gold shapes.
- Quality gate: for every generated pair check `skeleton.buffer(w/2, cap_style=2)` vs polygon
  symmetric-difference area below 1% and the I/L/T/Plus gold shapes are reproduced exactly by the
  generator when given their parameters (unit test).
- Phase 2: arbitrary-angle arms (Y, X, skew L), arms of unequal widths (hub recipe fails -> use
  explicit coordinates), tapered arms, curved arcs approximated by polylines, shapes with a hole.
- Splits (F8), by a `group_id` column, never row-shuffle:
  - `train` / `val`: instances from families seen in training, disjoint `group_id`.
  - `test_inst`: unseen instances (new dims) of seen families.
  - `test_family`: families never seen (e.g. Z, U, H, E, 5-arm star): measures real generalisation.
  - `gold`: the 4 hand-authored shapes in canonical pose plus their hand-checked rotations
    (never used for training or model selection; report separately).
  Size target for a first meaningful run: 4,000-8,000 train rows of the new compact format;
  roughly 100 tokens each, a full epoch is cheap even on a small GPU.

### 4.5 Decoding (F10)

- LM Studio / llama.cpp: pass `response_format` JSON schema for the JSON variants; for mcv1/mcv2
  use a GBNF grammar if the server supports it, otherwise rely on fine-tuning + regex parser.
- HF: `outlines` or `lm-format-enforcer`; or simpler, `stop` strings and `max_new_tokens=256`
  with the compact format. Always set explicit `eos_token_id` (`<|im_end|>` for Qwen).
- Greedy for eval, `temperature=0`; sample only for best-of-n experiments. Do not call retries a
  success: report `parse_ok_first_try` separately.
- Keep the MST connectivity repair only as an optional post-process; report both raw and repaired
  numbers in every table.

### 4.6 Training (F3, F14)

- Own tokenisation: `prompt_ids = apply_chat_template(messages_without_answer, add_generation_prompt=True)`,
  `completion_ids = tokenizer(answer + eos_text, add_special_tokens=False)`, `labels = [-100]*len(prompt) + completion_ids`.
  Use plain `transformers.Trainer` with `DataCollatorForSeq2Seq(label_pad_token_id=-100)`. This
  avoids TRL version drift (0.13 here) and gives full control over EOS. Log the first decoded
  label sequence on startup (acceptance check: it must start at the answer and end with the EOS).
- Start with Qwen2.5-Coder-1.5B-Instruct or 3B (LoRA r=32 all-linear, LR 1e-4..2e-4, 6-10 epochs
  over the larger dataset, effective batch 16-32); keep 7B only if the small model underfits.
  Train and evaluate with the same precision (either keep the 4-bit base unmerged, as
  `nemotron3/inference.py` does, or train bf16 LoRA and merge into bf16).
- Model selection: validation on `val` with a geometric metric (normalised Chamfer) computed on
  64 generated samples at the end of each epoch, not only eval loss.
- Curriculum (F11): sort/stage by number of arms: epoch 1 I/L only (mix 20% T), epoch 2 + T/Plus,
  epoch 3+ all families. Implement as a sampler list built before training, not a callback.

## 5. Evaluation design

### 5.1 Metrics (all computed on decoded polylines, in canonical units, normalised by the
profile's bbox diagonal)

| Metric | Definition | Why |
|---|---|---|
| parse_ok | decoder returns vertices + edges, indices in range, no self loops | syntax |
| chamfer_n | symmetric mean nearest distance between points sampled every 1% of diagonal along all edges | geometry incl. edges |
| hausdorff_n | max of the two directed values on the same samples | worst error |
| edge_f1@tol | an edge matches if both endpoints are within tol (2% of diagonal) of a GT edge's endpoints; F1 over edges | topology + geometry |
| graph_exact | node count, edge count, sorted degree sequence, component count equal | topology |
| branch_acc | number of vertices with degree >= 3 equal AND positions within tol | junctions |
| exact_match | decoded strings equal GT (after quantisation) | strictest, esp. mcv2 |
| wrong_but_valid | parse_ok and not graph_exact | most useful failure rate |

Report mean, median and a 95% bootstrap CI per (split, family) cell. Always include these
baselines in the same table: (B0) always-empty (floor), (B1) nearest-train-shape copy rescaled by bbox,
(B2) shapely `centroid`-line heuristic if available, (B3) the unfine-tuned base model few-shot.
If B1 is close to the fine-tuned model, the model memorised.

### 5.2 Required slices
- by family, by number of arms, by split name (inst / family / gold), by repaired vs raw.
- never aggregate `gold` with `test_inst`.

### 5.3 LM Studio / local OpenAI-compatible harness (F12)

Why: lets you test any GGUF in minutes (zero-shot, few-shot, your merged fine-tune) without
wiring HF / bitsandbytes on Windows.

Design (single script `scripts/lmstudio_eval.py`, library code in `midcurve_text/models/openai_client.py`):
- Config via env or CLI: `LMSTUDIO_URL` (default `http://localhost:1234/v1`), `--model` (default:
  first id from `GET /v1/models`), `--format {json,mcv1,mcv2}`, `--shots K` (0,2,4), `--split`,
  `--n`, `--temperature 0`, `--max-tokens 1024`, `--schema/--no-schema`, `--seed 0`, `--timeout 120`.
- Client: the `openai` package (2.32 already installed in the Python on this machine; check the
  conda env) with `api_key="lm-studio"`, `base_url=LMSTUDIO_URL`, `client.chat.completions.create(...)`;
  fallback to `requests.post(url + "/chat/completions")` if the package is missing.
- Prompt builder is the SAME function used for training data (`prompts.build_messages(example, fmt, shots)`),
  so there is one prompt definition. Shots are retrieved from `train` only, family-balanced, never
  from the evaluated item's group.
- Structured output: when `--schema`, send `response_format={"type":"json_schema","json_schema":{"name":"brep","strict":True,"schema":BREP_SCHEMA}}`
  (LM Studio enforces it for llama.cpp models; if the server rejects the field, retry without and
  log `schema_unsupported`).
- Output: `results/lmstudio/<model>_<format>_<shots>shot_<split>/{raw.jsonl, metrics.csv, summary.md}`
  where `raw.jsonl` has prompt hash, raw completion, finish_reason, prompt/completion tokens,
  latency. Summary uses the section 5.1 table with baselines.
- Smoke test `python scripts/mc.py lmstudio-smoke` (under 1 minute, no dataset needed beyond
  4 gold shapes):
  1. `GET /v1/models` succeeds and lists at least one model; print ids.
  2. Echo test: ask for the string `OK` at temperature 0; expect `OK` in the reply.
  3. Gold shape I and T, zero-shot, then 2-shot, in mcv1 and JSON; decode and score.
  4. Schema-mode call; report whether the server accepted `response_format`.
  5. Print tokens/second and a PASS / FAIL line per step; exit code 0 only if steps 1-3 pass.
- Serving the fine-tune in LM Studio later: merge the LoRA into the bf16 base (`merge_and_unload`),
  convert with llama.cpp `convert_hf_to_gguf.py`, quantise to Q8_0 or Q5_K_M, load in LM Studio.
  Evaluate the GGUF with the same harness (this also measures quantisation damage).

## 6. Target layout (consolidation, F13)

One installable package, one driver, one config system, no module named `config` (removes the
`sys.modules['config']` collision documented in the root `CLAUDE.md`; keep the test-24 guard until
the old folders are archived).

```
src/text_based/
  README.md                      # short, points to this layout
  TODO.md                        # statuses
  configs/
    data.yaml                    # generator ranges, split sizes, seeds
    format.yaml                  # active format: json | mcv1 | mcv2, grid=1000
    train_qwen15b.yaml
    train_qwen7b.yaml
    train_nemotron4b.yaml
    eval.yaml                    # metrics tolerances, bootstrap n
  midcurve_text/
    __init__.py
    settings.py                  # paths, loads yaml (replaces both config.py)
    geometry/
      transforms.py              # moved from utils/prepare_data.py (rotate, scale, ...)
      canonical.py               # canonicalise() / decanonicalise()
      generator.py               # procedural skeleton -> polygon (shapely)
      recipes.py                 # find_recipe(profile, midcurve_vertex)
    formats/
      brep_json.py               # legacy BRep dict <-> text
      mcv1.py                    # encode / decode compact
      mcv2.py                    # encode / decode recipe
      registry.py                # name -> codec
    data/
      build_dataset.py           # writes data/generated/<version>/{train,val,test_inst,test_family,gold}.jsonl
      splits.py
      validate.py                # replaces finetuning/data_validator.py
    prompts/
      templates.py               # ONE system prompt per format, build_messages()
    models/
      hf_train.py                # QLoRA / LoRA via Trainer, completion-only
      unsloth_train.py           # thin wrapper selecting unsloth if installed
      codet5_train.py            # seq2seq variant (from the notebook), same data
      hf_generate.py             # local HF/PEFT generation
      openai_client.py           # LM Studio / any OpenAI-compatible server
    eval/
      metrics.py                 # section 5.1
      baselines.py
      run_eval.py                # model-agnostic: takes a "generate(messages)->str" callable
      report.py                  # tables + CI + plots
      repair.py                  # optional MST repair, reported separately
    serve/
      server.py                  # FastAPI (from finetuning/model_server.py)
  scripts/
    mc.py                        # CLI driver: build-data | audit | train | eval | lmstudio-smoke | lmstudio-eval | report
  data/
    brep/                        # the 4 hand-authored gold shapes (unchanged)
    generated/<version>/         # git-ignored except a small sample + manifest.json (hash of configs/data.yaml)
    legacy/                      # csvs/, shapes2brep.csv, sequences.json (kept, flagged stale)
  results/                       # git-ignored; per-run folders with config snapshot
  tests/                         # moved from testing/ (keep test file names, update imports)
  archive/                       # old finetuning/, nemotron3/, codeT5/, ludwig/, prompt/, utils/ (moved, not deleted)
```

Naming rules: folders `snake_case`, one verb per script, model names only in `configs/`, never in
file names; run folders `results/<date>_<model>_<format>_<split>/`.

## 7. Risks and assumptions

- Shapely 1.8.5 is visible to the system Python; confirm it exists in the conda env that will run
  generation (`conda run -n genai python -c "import shapely; print(shapely.__version__)"`).
  Add `shapely` to `environment.yml` if missing. The `buffer(cap_style=...)` integer arguments
  (1 round, 2 flat, 3 square) work in 1.8 and 2.x.
- The recipe format assumes equal-width arms at junctions; generator phase 2 will contain
  unrecipeable vertices; the codec must support explicit-coordinate fallback.
- I could not measure token counts (no tokenizer download allowed); length numbers are estimates.
  Action item A-03 measures them.
- TRL / transformers versions drift; the plan avoids `SFTTrainer` on purpose.
- The reported 98% PSR and MAE 0.78 could not be reproduced from the checked-in files; treat them as
  historical until re-measured with the new harness on a clean split.

## 8. Numbered action list for Sonnet

General rules for the executor (Sonnet): do not run any git command (the user manages git); present
the plan for each Phase and wait for the user's go-ahead before starting it; before moving or
archiving files, list the destination and show a dry-run table; never delete, only move to
`archive/`; use Edit / Write tools for file changes (no heredocs, no `sed`); write scripts to
files then run them with `conda run -n genai python ...`; keep console output ASCII; after every
phase run `cd src && python -m pytest text_based -q` and report pass / fail counts; ignore
the privacy-sensitive context items; do not invoke any model download unless an item says so.
Effort: S under 1 h, M 1-3 h, L half day.

### Phase A - make results trustworthy (no restructuring, no GPU)

A-01 (S) Back up and repair the double-encoded CSVs.
- Create `utils/fix_double_encoded_csv.py` (new file). Logic: for each of
  `data/csvs/midcurve_llm.csv`, `_train`, `_val`, `_test`: read with pandas (`dtype=str`); for
  columns `Profile`, `Midcurve`, `Profile_brep`, `Midcurve_brep`: if the value `json.loads(v)` returns a
  `str`, replace by that string (loop at most twice); write the CSV back with `index=False`.
- Before writing, copy the four originals to `data/csvs/_backup_double_encoded/` (new dir). Print
  row counts before / after.
- Acceptance: `python -c "import pandas as pd,json; d=pd.read_csv('data/csvs/midcurve_llm_train.csv'); assert isinstance(json.loads(d.Profile_brep[0]),dict)"`
  succeeds for all four files; row counts unchanged (793 / 100 / 99 / 992); backup dir exists.

A-02 (S) Make parsers robust to wrapped strings.
- Edit `finetuning/metrics.py` `parse_brep` (`:9-24`) and the copy `nemotron3/metrics.py` to
  unwrap: after `json.loads`, `while isinstance(data, str): data = json.loads(data)` (max 2
  times, inside the existing try), and return `(None, np.array([]))` unless `isinstance(data, dict)`.
  Also set `json_validity` to 1.0 only if `"Points"` is a non-empty list.
- Add a test to `testing/test_text_based.py` (new class `TestCsvEncoding`): load the first 20
  rows of each CSV in `data/csvs/`, assert `json.loads(cell)` is a `dict` (not `str`) for
  `Profile_brep` and `Midcurve_brep`, and that `GeometricMetrics.compute_all_metrics(gt, gt, profile)`
  gives `json_validity == 1.0` and `hausdorff == 0.0`. Do not remove test 24's import guard.
- Acceptance: new tests pass; the 44/45 baseline does not get worse.

A-03 (M) Token-length audit script.
- Create `scripts/audit_lengths.py` (new dir `scripts/`). Args: `--model_id` (default
  `Qwen/Qwen2.5-Coder-1.5B-Instruct`), `--csv`, `--max_len 1024`, `--format json`. For each row
  build the exact training messages (system + user + assistant) with the repo's dataset_loader
  logic, tokenise with the model tokenizer (allowed to download the small tokenizer only, ask the
  user first if offline), print min / median / p95 / max of total tokens, answer tokens, and the
  count of rows with total > max_len, and the count where the last 5 tokens of the sequence
  after truncation are not the EOS.
- Run for Qwen and for `nvidia/Nemotron-Mini-4B-Instruct`. Write results to
  `results/length_audit.txt`.
- Acceptance: file exists; report states the truncated-row count (expected 0 for 1024 on the
  current data; if not 0 raise `MAX_SEQ_LENGTH` in both config files to 2048 and note it).

A-04 (S) Fix the few-shot prompter.
- Edit `nemotron3/fewshot_prompter.py`: line 77 defaults `max_new_tokens=768`, `max_input_len=4096`;
  line 160-162 remove `truncation=True, max_length=...` (keep a `assert inputs.input_ids.shape[1] < self.max_input_len`
  that prints a warning instead of truncating); lines 169-172 delete `temperature=1.0` and
  `repetition_penalty=1.1`; replace `_FEW_SHOT` (`:42-55`) with 4 examples, one each of I, L, T,
  Plus, built at runtime from `data/brep/*.json` canonical originals (not from CSV rows).
- Edit `n_samples` default to 40, selected stratified by family from the test CSV.
- Acceptance: unit test `TestFewShotPrompterLogic` still passes; a new test builds the prompt for a
  Plus row with `_FEW_SHOT` of 4 examples and asserts the character length is below
  `max_input_len*3` and the prompt ends with `Midcurve:`.

A-05 (M) New metric module (stays in place for now).
- Create `finetuning/metrics_v2.py` implementing section 5.1 metrics: `sample_polyline(points, edges, step_frac=0.01)`,
  `chamfer_n`, `hausdorff_n`, `edge_f1(tol_frac=0.02)`, `graph_exact`, `branch_acc`, `exact_match`,
  `wrong_but_valid`, `bootstrap_ci(values, n=1000, seed=0)`. Input: dicts with `Points` and
  `Lines`; normaliser = bbox diagonal of the PROFILE points.
- Add `baselines`: `nearest_train_copy(profile, train_rows)` (choose the training row of same
  family with the smallest mean absolute coordinate difference after bbox normalisation, map its
  midcurve through the bbox transform) and `empty_prediction()`.
- Do NOT change the old `compute_all_metrics`; add `combined_score_v2 = 0.5*(1-min(chamfer_n/0.1,1)) + 0.5*edge_f1`.
- Tests in `finetuning/test_metrics.py`: perfect prediction -> chamfer_n 0, edge_f1 1; T with a path
  instead of a star -> edge_f1 < 1 while the old `topology_accuracy` stays 1.0 (document with an
  assertion on both); disjoint prediction -> large chamfer_n.
- Acceptance: tests pass; a quick script run of `nearest_train_copy` on the clean `_test.csv`
  prints the baseline table (this quantifies the leakage - include the numbers in `TODO.md`).

A-06 (S) Update `analysis_report.md` and `TODO.md`: add the new findings (double encoding,
metric floor 0.6, few-shot truncation, EOS masking risk) as A4, B11-B14; mark them FIXED as items
A-01..A-05 complete. Do not edit `CLAUDE.md` unless the user asks.

### Phase B - new data pipeline and format (needs user go-ahead; no GPU)

B-01 (L) Package skeleton.
- Create dirs and empty `__init__.py` files per section 6 for `midcurve_text/` (sub-packages
  geometry, formats, data, prompts, models, eval, serve), plus `configs/`, `scripts/`, `tests/`.
- `midcurve_text/settings.py`: dataclass with paths (`ROOT = Path(__file__).resolve().parents[1]`),
  `load_yaml(name)` using `yaml.safe_load` (add `pyyaml` to `environment.yml` if missing).
- `configs/data.yaml`: `grid: 1000`, `seed: 42`, `n_train: 6000`, `n_val: 400`, `n_test_inst: 400`,
  `n_test_family: 200`, `families_train: [I, L, T, Plus, Z, U]`, `families_heldout: [H, E, Star5]`,
  `widths: [2,3,4,5,6,8]`, `arm_len_range_in_widths: [3,12]`.
- Acceptance: `python -c "import midcurve_text.settings"` works from `src/text_based`.

B-02 (M) Codecs.
- `midcurve_text/formats/brep_json.py`: `to_brep(points, edges)` and `from_brep(dict)` returning
  `(points, edges)`; `Segments` regenerated as `[[i] for i in range(len(edges))]` for midcurves and
  one loop for profiles.
- `mcv1.py`: `encode_profile(points)->str`, `encode_midcurve(points, edges)->str`,
  `decode_midcurve(text)->(points, edges)|None` with a strict regex
  (`^midcurve n=(\d+) e=(\d+)\n((?:-?\d+,-?\d+ ?)+)\n((?:\d+-\d+ ?)*)$`) and a lenient fallback
  regex that extracts all `-?\d+,-?\d+` pairs and all `\d+-\d+` pairs; return None if indices out
  of range.
- `mcv2.py`: `encode_midcurve(recipes, edges)` / `decode_midcurve(text, profile_points)` returning
  explicit coordinates; supports `v3 = (x,y)` fallback lines.
- `registry.py`: `get_codec(name)` with names `json`, `mcv1`, `mcv2`.
- Tests `tests/test_formats.py`: round trip on the 4 gold shapes (JSON -> text -> decode ==
  original within 1e-6 for json, within quantisation 0.1% of size for mcv1/mcv2); decode of garbage
  returns None; decode of truncated text returns None or partial flagged.
- Acceptance: tests pass.

B-03 (M) Canonicalisation.
- `midcurve_text/geometry/canonical.py` implementing section 4.1: `canonicalise(profile_pts, midcurve_pts, edges)`
  returning canonical integer points, the midcurve with canonical vertex order, and a `transform`
  dict (`flip`, `rot_deg`, `offset`, `scale`, `start_index`); `decanonicalise(points, transform)`.
- Test: for each gold shape and 50 random rotations / translations / scales / mirrors, canonicalise
  then decanonicalise the midcurve and assert max error < 0.01 * size; and that the canonical
  profile string is identical (up to quantisation, tolerance 2 grid units) for rotated copies
  of the same shape.
- Acceptance: tests pass; I/L/T/Plus canonical strings printed in the test log (for README).

B-04 (L) Procedural generator.
- `midcurve_text/geometry/generator.py` implementing section 4.4 phase 1: `sample_skeleton(family, rng)`,
  `skeleton_to_polygon(skel)`, `make_example(family, rng)` returning `{group_id, family, profile_pts, midcurve_pts, edges}`.
  Families v1: I (1 arm), L (2 arms with a bend), T, Plus, Z (two bends, opposite turns),
  U (two bends, same turn) - all single width per shape, axis-aligned. Held-out families for
  `test_family`: H, E (3 parallel teeth), Star5 is NOT axis-aligned, so skip it in v1 and use
  H, E only.
- Reject: invalid polygon, holes, area symmetric-difference > 1% vs `skeleton.buffer`, exact
  dimension match with `data/brep/*.json`.
- Tests `tests/test_generator.py`: 200 samples per family are valid; generator reproduces the gold
  I, L, T, Plus when called with their parameters (profile vertex sets equal as sets); fixed seed
  gives identical output twice.
- Acceptance: tests pass; a PNG preview (matplotlib, 4x6 grid of random samples with midcurve overlaid)
  saved to `results/generator_preview.png` for the user to look at, with the line
  `*Image file: results/generator_preview.png*` if embedded in any .md file (per the global markdown
  image rule).

B-05 (M) Recipes.
- `midcurve_text/geometry/recipes.py`: `find_recipe(profile_pts, v, tol=1e-6)` searching
  subsets of sizes 1, 2, 3, 4 (combinations of profile indices, max 12 vertices) whose mean equals
  `v`; returns tuple of indices or None. Cache by shape.
- Test: on the four gold shapes recipes exist for every midcurve vertex (T hub = (0,2) is one
  valid answer; any valid recipe is accepted). Report recipe coverage % on 1,000 generated
  samples per family (expected ~100% for equal-width shapes).
- Acceptance: tests pass; coverage printed.

B-06 (M) Dataset builder and splits.
- `midcurve_text/data/build_dataset.py` and `splits.py`: read `configs/data.yaml`, generate rows,
  assign `group_id` and `split`, apply `canonicalise`, write
  `data/generated/v1/{train,val,test_inst,test_family,gold}.jsonl` + `manifest.json` (config hash, counts, seed, git-free timestamp).
  Each row holds: `family`, `group_id`, canonical `profile` and `midcurve` points/edges,
  `transform`, and the pre-rendered text for each codec (`json`, `mcv1`, `mcv2` if recipe exists).
- `gold.jsonl` = the 4 hand-authored shapes plus 12 fixed rotations each (0, 30, 45, 60, 90, 120, 135,
  150, 180, 210, 270, 315) canonicalised (they should all collapse to near-identical strings:
  this is a built-in test of canonicalisation).
- `data/validate.py`: assert no `group_id` shared across splits, no duplicate profile strings across
  train and any test split, family held-out rule respected; run automatically at the end of build.
- Acceptance: `python scripts/mc.py build-data` (after B-09) or `python -m midcurve_text.data.build_dataset`
  produces the files; validator prints OK; row counts match config.

B-07 (M) Prompts.
- `midcurve_text/prompts/templates.py`: `SYSTEM[fmt]` (max 60 words each; for `mcv1` something like
  "Convert the polygon to its midcurve. Output the midcurve in the same format.") and
  `build_messages(example, fmt, shots=())`; shots appended as alternating user / assistant
  messages (not as a single user blob). Return `(messages, answer_text)`.
- Test: the training and inference paths call the same function (import test: both modules reference
  `templates.build_messages`); length of system prompt < 100 tokens with a whitespace estimate.
- Acceptance: tests pass.

B-08 (M) Metrics v2 into the package.
- Move the content of `finetuning/metrics_v2.py` (A-05) to `midcurve_text/eval/metrics.py`,
  re-export from the old location, add `run_eval.py` with `evaluate(generate_fn, split_rows, fmt, shots)`
  returning a DataFrame (raw vs repaired columns) and `report.py` producing `summary.md` with the
  section 5.1 table, per family and per split slices, bootstrap CI, baselines.
- Acceptance: `tests/test_eval.py` runs `evaluate` with a fake `generate_fn` that returns the GT
  (expect perfect) and one that returns garbage (expect parse_ok 0, no exceptions).

B-09 (S) Driver.
- `scripts/mc.py` using `argparse` subcommands `build-data`, `audit`, `train`, `eval`,
  `lmstudio-smoke`, `lmstudio-eval`, `report`, each delegating to package functions; global
  `--config configs/<name>.yaml`, `--run-name`. Writes the resolved config to the run folder.
- Acceptance: `python scripts/mc.py --help` lists all subcommands; `build-data` works end to end.

### Phase C - LM Studio harness (can start right after B-02, B-07, B-08; no GPU training)

C-01 (M) `midcurve_text/models/openai_client.py`: class `OpenAICompatClient(base_url, model=None, api_key="lm-studio", timeout=120)`
with `list_models()`, `chat(messages, temperature=0.0, max_tokens=1024, seed=0, response_format=None, stop=None)`
returning `{text, finish_reason, prompt_tokens, completion_tokens, latency_s}`; use the `openai`
package, fall back to `requests`. Handle connection refused with a clear message
("start LM Studio, load a model, enable the local server on port 1234").
- Test with a stub HTTP server (`http.server` in a thread) that implements `/v1/models` and
  `/v1/chat/completions` returning a fixed JSON: assert parsing, error handling, and that
  `response_format` is passed.

C-02 (M) `scripts/mc.py lmstudio-smoke` as specified in section 5.3 (5 steps, PASS/FAIL per step,
exit code). Uses gold rows only.
- Acceptance: with the stub server the smoke test passes steps 1-2 and handles step 3 decoding;
  with no server it exits 1 with the friendly message. (Real LM Studio check is done by the user.)

C-03 (M) `scripts/mc.py lmstudio-eval --format mcv1 --shots 2 --split test_inst --n 40 --model <id>` writing
`results/lmstudio/<run>/{raw.jsonl, metrics.csv, summary.md}`; shots from `train` only,
family-balanced, excluding the evaluated group; flags `--schema` (JSON format only). Include
resume support (skip prompt hashes already in raw.jsonl).
- Acceptance: runs against the stub server; produces the three files; summary shows baselines.

C-04 (S) Document usage in `README.md` section "LM Studio quick start" (5 lines, ASCII only).

### Phase D - training v2 (GPU; start only when the user asks)

D-01 (M) `midcurve_text/models/hf_train.py`: load `data/generated/v1/train.jsonl`/`val.jsonl`, build
messages via `templates.build_messages`, tokenise prompt and completion separately, labels masked,
EOS appended and verified, `DataCollatorForSeq2Seq(label_pad_token_id=-100)`, `transformers.Trainer`,
LoRA r=32 all-linear, config from `configs/train_*.yaml` (`model_id`, `lr`, `epochs`, `batch`,
`grad_acc`, `max_len`, `bnb_4bit: true|false`). On start, print the decoded first training example
twice: the full input and only the label positions; assert the labels end with EOS.
- Smoke: `python scripts/mc.py train --config configs/train_qwen15b.yaml --smoke` trains 5 steps on 32
  rows and writes an adapter; no assertion about quality.
- Acceptance: label-dump assertions pass; adapter saved with a `run_config.json` snapshot.

D-02 (M) `models/hf_generate.py`: load base + adapter in the SAME precision as training (unmerged if
4-bit), `generate(messages)->str` with explicit `eos_token_id`, greedy, `max_new_tokens=256` for mcv1.
Plug into `eval/run_eval.py` (`mc.py eval`).
- Acceptance: on the smoke adapter `mc.py eval --split gold --n 8` runs to completion and writes a report.

D-03 (S) Curriculum: in `hf_train.py` build the epoch order from `configs` key `curriculum: [[I,L],[I,L,T,Plus],[all]]`
(list per epoch of allowed families; default off). Test: with curriculum on, epoch-1 batches contain
only the listed families.

D-04 (S) `mc.py train --export-gguf` helper that merges the adapter in bf16, saves the merged HF
folder, and prints (does not run) the llama.cpp conversion commands.

### Phase E - consolidate and archive (needs explicit confirmation; dry run first)

E-01 (S) Produce a dry-run move table (source -> destination -> reason) for: `finetuning/` (all),
`nemotron3/` (all), `codeT5/`, `ludwig/`, `prompt/`, `utils/` (keep `utils/backup/` inside archive),
`testing/` -> `tests/`, `data/csvs/` + `data/shapes2brep.csv` + `data/sequences.json` ->
`data/legacy/`. Do NOT execute. Show the table to the user and wait.

E-02 (M) After confirmation, move (not delete) to `archive/` as per the table; leave one-line
shim modules only where the root `CLAUDE.md` demands (`config_enhanced.py`, `metrics_enhanced.py`
aliases - ask the user whether to keep them, since the old `finetuning/` is archived). Update
imports in `testing/test_text_based.py` (now `tests/`) and `src/benchmark.py`
(check with `grep -n "text_based" src/benchmark.py src/conftest.py src/pytest.ini`) and fix paths.
- Acceptance: `cd src && python -m pytest text_based -q` result equals or beats the Phase A baseline;
  `python src/benchmark.py --approaches text` still imports (or is documented as pointing at the
  new driver).

E-03 (S) Rewrite `README.md` (target layout, three-command quick start: `build-data`,
`lmstudio-smoke`, `train`) and update `TODO.md`. In every .md follow the repo image rule
(`![alt](images/name.png)` + a plain `*Image file: images/name.png*` line).

E-04 (S) Add `.gitignore` entries inside `src/text_based/` for `results/` and `data/generated/`
(keep a small `data/generated/sample/` and the manifest). Do not run git.

### Phase F - experiments to answer "is the LLM approach viable" (after D)

F-01 (M) Run the matrix and fill a table in `results/matrix.md`: models {Qwen2.5-Coder-1.5B, 7B,
Nemotron-Mini-4B} x formats {json, mcv1, mcv2} x {zero-shot, 4-shot, fine-tuned} on
`test_inst`, `test_family`, `gold`. Add baselines B0-B3. Decide from the table, not from
anecdotes.

F-02 (S) Write a short result note in `src/text_based/analysis_report.md` (new section 7:
"2026-11 re-evaluation") with the matrix and the leakage evidence from A-05.

## 9. Open decisions for the user (answer one at a time when asked)

1. Format default: mcv1 (explicit integer coordinates) or mcv2 (recipes)? Recommendation: build both,
   train mcv2 first.
2. Base model size to start with: 1.5B (recommended, fast), 3B, or 7B.
3. Should Phase E archive `finetuning/` and `nemotron3/` entirely (recommended) or keep thin shims?
4. Procedural generator scope for v1: axis-aligned only (recommended) or include arbitrary angles now?
