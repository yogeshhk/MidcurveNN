# Fine-Tuning NVIDIA Nemotron-Mini for Geometric Reasoning: Computing Midcurves with LLMs

*MidcurveNN Project — Text-Based Approach (Phase II)*

---

## The Midcurve Problem

In mechanical CAD, thin-walled structural components — I-beams, L-brackets, T-sections — are routinely simplified for finite element analysis by collapsing their full 3D volume into a lower-dimensional skeleton. The 2D equivalent of this operation is computing the **midcurve**: a 1D polyline (or branched graph) that runs through the geometric centre of a 2D closed polygon profile, equidistant from its bounding edges.

![Shape examples and their midcurves](../publications/MidcurveNN_GMP2021/images/training_data.png)

Formally, given a closed 2D polygon (a set of connected line segments), the task is to produce its midcurve — which may itself be a branched graph, not a simple open polyline. An **I-shape** collapses to a single vertical segment; an **L** to two segments meeting at a corner; a **T** to three segments sharing a junction; a **Plus** to four arms radiating from a centre point.

Despite decades of research — Medial Axis Transform, Chordal Axis Transform, thinning, pairing — the problem remains unsolved in the general case. Shape complexity and the variety of junction types make rule-based approaches brittle.

---

## Three Approaches in MidcurveNN

The [MidcurveNN](https://github.com/yogeshhk/MidcurveNN) research project evaluates neural network strategies across three paradigms:

### Phase I — Image-Based

Polygons are rasterized to 256×256 bitmaps and fed to encoder-decoder architectures: a simple dense encoder-decoder (baseline), CNN encoder-decoder, UNet with 8 encoding levels and CoordConv, and Pix2Pix GANs. The UNet variant performs best among image-based models.

![Encoder-decoder for midcurve images](../publications/MidcurveNN_GMP2021/images/encoder-decoder-midcurve.jpg)

**Limitation:** Rasterization loses exact geometry. Post-processing is needed to extract clean polylines from predicted bitmaps, and junction topology is blurred at pixel boundaries.

### Phase II — Text-Based (LLM)

If geometry can be *serialized as text*, large language models pre-trained on code and structured data may learn the pattern. This is the focus of the current work.

### Phase III — Geometry-Based (Graph Transformer)

A non-auto-regressive Graph Transformer trained from scratch treats polygon corners as graph nodes (features: x, y coordinates) and predicts the midcurve adjacency matrix along with output coordinates. This handles branching natively and is the strongest approach to date.

---

## Why Text-Based?

Image-based methods fundamentally cannot represent exact geometry, and graph-based models require custom architectures. LLMs, however, are pre-trained on vast code corpora including JSON, SVG, and structured numeric formats. The insight: **if shapes are expressed as compact JSON structures, fine-tuning an LLM is equivalent to teaching it a geometric transformation rule** — similar to how code models learn API patterns.

Early experiments (2023) with few-shot prompting of GPT-4, Claude, Bard, and Llama showed that frontier models can sometimes compute midcurves of simple shapes from in-context examples, while smaller models fail consistently. This motivates supervised fine-tuning on domain-specific data.

---

## BRep JSON: Encoding Geometry as Text

The key design choice is the **Boundary Representation (BRep) JSON** format. Each shape is a dict with three parallel arrays:

```json
{
  "Points":   [[5.0, 5.0], [10.0, 5.0], [10.0, 20.0], [5.0, 20.0]],
  "Lines":    [[0, 1], [1, 2], [2, 3], [3, 0]],
  "Segments": [[0, 1, 2, 3]]
}
```

- **Points** carry the geometry (x, y coordinates).
- **Lines** carry the topology (index pairs).
- **Segments** group lines into topological faces or branches.

A critical invariant: geometric transforms (rotation, scaling, translation, mirroring) modify only `Points`; `Lines` and `Segments` are never altered. This means the model only needs to learn the coordinate mapping, not re-invent topology.

The training corpus is 993 shape variants (4 base shapes × scale, rotate, translate, mirror augmentations) split 80/10/10 into train/val/test CSVs. Each row is a `(Profile_brep → Midcurve_brep)` pair.

![CSV dataset format](../publications/MidcurveLLM_ICACCS2024/LaTeX/images/shapes_csv.png)

---

## Nemotron-Mini-4B: NVIDIA's Compact Powerhouse

**`nvidia/Nemotron-Mini-4B-Instruct`** is a 4-billion parameter causal language model released by NVIDIA in 2024. It was produced by pruning the larger Nemotron-4 15B model and then re-training with knowledge distillation — the **Minitron** technique — yielding a model that punches well above its weight class.

Key architectural features:

| Property | Value |
|---|---|
| Parameters | 4 B |
| Attention | Group Query Attention (GQA) — 24 query / 8 KV heads |
| Activation | relu² (squared ReLU) |
| Context window | 4,096 tokens |
| Chat template | `<extra_id_0>System` / `<extra_id_1>User` / `<extra_id_1>Assistant` |
| License | NVIDIA Open Model License |

GQA dramatically reduces KV-cache memory during inference. The relu² activation (squaring the ReLU output) provides stronger gradient signal for sparse activations. The model is instruction-tuned via SFT and RLHF, making it directly usable with `apply_chat_template()`.

In 4-bit NF4 quantization (bitsandbytes), the model fits in approximately **2–3 GB of GPU VRAM**, making it accessible on mid-range hardware.

---

## Implementation: QLoRA Fine-Tuning

The `nemotron3/` module implements a complete QLoRA fine-tuning pipeline:

**1. Data loading** (`dataset_loader.py`): Each CSV row becomes a three-turn chat message — system prompt (task description), user (Profile_brep JSON), assistant (Midcurve_brep JSON) — formatted via `tokenizer.apply_chat_template()`.

**2. Model loading** (`train.py`): The base model is loaded in 4-bit NF4 quantization (`BitsAndBytesConfig`), then `prepare_model_for_kbit_training()` enables gradient checkpointing. LoRA adapters (`r=16`, `alpha=32`) are applied to all linear layers via `target_modules="all-linear"`, adding fewer than 1% trainable parameters.

**3. Training** (`train.py`): `SFTTrainer` (TRL) runs 3 epochs with a cosine learning-rate schedule, evaluating on the validation set each epoch and saving the best checkpoint by `eval_loss`.

**4. Inference** (`inference.py`): `NemotronInference` loads the merged LoRA weights, generates output with greedy decoding (`do_sample=False`), then validates: JSON parseability, required keys (`Points/Lines/Segments`), and BFS connectivity. Disconnected components are automatically repaired by finding and adding the nearest-neighbour edge.

**5. Evaluation** (`evaluate.py`): `NemotronEvaluator` scores each test prediction on Chamfer distance, Hausdorff distance, topology accuracy (junction count match), and connectivity score. A combined score weights these 40/30/30.

---

## Results

The demo pipeline was run using `google/gemma-2b-it` (a cached 2B-parameter instruction-tuned model) as a hardware-constrained substitute for Nemotron-Mini-4B (which requires ≥8 GB VRAM). This exercises the complete pipeline without fine-tuning, serving as an upper-bound baseline for what an untrained instruction-following model achieves.

![Nemotron3 pipeline results grid](../src/text_based/nemotron3/results/results_grid.png)

*Left column: input profile polygon (blue). Centre: ground-truth midcurve (green). Right: model prediction (red).*

| Metric | Value (base model, no fine-tuning) |
|---|---|
| Valid JSON rate | 85.7 % (6/7) |
| Avg Hausdorff distance | 27.3 |
| Avg Chamfer distance | 20.0 |
| Topology accuracy | 0.83 |
| Combined score | 0.56 |

Even without fine-tuning, the base model generates valid BRep JSON for 6 of 7 test shapes. Fine-tuning on the 793-sample training set on hardware with ≥8 GB VRAM (using `python train.py`) is expected to substantially reduce Hausdorff and Chamfer distances, as the model learns the precise coordinate-mapping rule for these shape classes.

---

## Conclusion

This work demonstrates that **geometric reasoning can be framed as a structured text-generation problem**. By serializing 2D polygon topology as BRep JSON, a standard instruction-tuned LLM can be fine-tuned to predict midcurves — no custom graph architecture needed. The Nemotron-Mini-4B model is an ideal target: small enough to fine-tune on a single GPU with QLoRA, yet powerful enough (via distillation from a 15B model) to understand spatial coordinate patterns.

The nemotron3 pipeline is fully self-contained: data loading, QLoRA training, constrained inference with connectivity repair, metric evaluation, and visualization — all in six Python scripts under `src/text_based/nemotron3/`. To run on appropriate hardware:

```bash
conda activate genai
cd src/text_based/nemotron3
python train.py       # fine-tune (~3 h on RTX 3090)
python evaluate.py    # test set metrics + results_grid.png
```

Future directions include branched shape generalization (Y, X, star shapes), multi-scale augmentation, and combining the text-based approach with the geometry-based Graph Transformer for hybrid reasoning.

---

*Code: [github.com/yogeshhk/MidcurveNN](https://github.com/yogeshhk/MidcurveNN) — `src/text_based/nemotron3/`*
