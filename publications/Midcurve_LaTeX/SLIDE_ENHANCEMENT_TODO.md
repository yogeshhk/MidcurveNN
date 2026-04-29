# Slide Deck Enhancement — TODO Report
**File:** `publications/Midcurve_LaTeX/Main_Midcurve_short_Presentation.tex`  
**Target impl slides:** `midcurve_impl_ann_short.tex`, `midcurve_impl_llm_short.tex`  
**Date created:** 2026-04-29

---

## Summary

The short presentation pulls 5 module files via `seminar_midcurve_short_content.tex`:
- `midcurve_intro_short.tex` — midcurve problem intro (images only, no code)
- `midcurve_intro_ann_short.tex` — graph-2-graph problem framing, image-as-proxy twist
- `midcurve_impl_ann_short.tex` — image-based ANN implementation slides ← **primary target**
- `midcurve_impl_llm_short.tex` — LLM / text-based implementation slides ← **primary target**
- `midcurve_refs.tex` — references

All result images go to `publications/Midcurve_LaTeX/images/` and are referenced as
`\includegraphics[width=\linewidth,keepaspectratio]{<name>}` (no extension, no path prefix —
`graphicspath{{images/}}` is set in the main file).

---

## Phase A — Generate Result Images (MUST DO FIRST)

All scripts require `conda activate midcurvenn` (Python 3.10, TF 2.13, PyTorch).

### A1 — Simple Encoder-Decoder results
```
cd src/image_based/simpleencoderdecoder
python main_simple_encoderdecoder.py
```
- Output: `src/image_based/simpleencoderdecoder/results/results_grid.png`
- Copy to: `publications/Midcurve_LaTeX/images/simple_results_grid.png`

### A2 — CNN Encoder-Decoder results
```
cd src/image_based/cnnencoderdecoder
python main_cnn_encoderdecoder.py
```
- Output: `src/image_based/cnnencoderdecoder/results/results_grid.png`
- Copy to: `publications/Midcurve_LaTeX/images/cnn_results_grid.png`

### A3 — UNet results
```
cd src/image_based/unet
python test.py
```
- Requires weights at `src/image_based/unet/weights/stage1/weights.h5` and `stage2/weights.h5`
- Output: `src/image_based/unet/results/results_grid.png`
- Copy to: `publications/Midcurve_LaTeX/images/unet_results_grid.png`

### A4 — Graph Transformer results (Phase III)
```
cd src/geometry_based/graph_transformer
python evaluate.py
```
- Requires trained checkpoint at `checkpoints/best_model.pt`
  (run `python main_graph_transformer.py` first if checkpoint absent)
- Output: `src/geometry_based/graph_transformer/results/results_grid.png`
- Copy to: `publications/Midcurve_LaTeX/images/graph_transformer_results_grid.png`

### A5 — Text/LLM results (Phase II)
- Requires a trained QLoRA checkpoint. Run only after fine-tuning completes:
```
cd src/text_based/finetuning
python evaluate.py --model_path Midcurve-Qwen-Coder-v1 --visualize
```
- Output: `src/text_based/finetuning/evaluation_plots/metric_distributions.png`
- Copy to: `publications/Midcurve_LaTeX/images/llm_metric_distributions.png`
- (Optional) capture a sample row from `evaluation_results.csv` as a screenshot

---

## Phase B — Slide Changes in `midcurve_impl_ann_short.tex`

### B1 — Expand "Simple Encoder Decoder" slide
Current state: shows only `midcurve32` image.  
**TODO:** Add bullet points below the image:
- Input: 100×100 grayscale bitmap (flattened to 10,000 dims)
- Hidden: Dense(100, relu) + L1 activity regulariser
- Output: Dense(10,000, sigmoid)
- Loss: binary cross-entropy; Optimizer: Adadelta

### B2 — Update "Keras Implementation" code slide
Current state: shows an older single-autoencoder snippet.  
**TODO:** Replace lstlisting with current `_build()` method from
`src/image_based/simpleencoderdecoder/build_simple_encoderdecoder_model.py`.
Key lines to show: Input → Dense(encoding_dim) → Dense(input_dim), Model compile.

### B3 — NEW slide: "CNN Encoder Decoder Architecture" (insert after Simple AE results)
**TODO:** Add new frame with:
- Bullets: 4-level Conv2D encoder, Conv2DTranspose decoder, CoordConv (3-channel input = x_coord + y_coord + image), 128×128
- Code snippet from `build_cnn_encoderdecoder_model.py` showing Conv2D → MaxPool stack

### B4 — NEW slide: "UNet Architecture" (insert after CNN slide)
**TODO:** Add new frame with:
- Bullets: 8-level UNet, auxiliary reconstruction decoder, CoordConv, 2-stage WBCE loss, 256×256
- Code snippet from `unet/train.py`: the `init()` function signature and key loss definition

### B5 — Update "Results" slide (currently shows `midcurve33`)
**TODO:** Replace the single old image with three result slides:
1. Simple AE results: `\includegraphics[width=\linewidth,keepaspectratio]{simple_results_grid}`
2. CNN results: `\includegraphics[width=\linewidth,keepaspectratio]{cnn_results_grid}`
3. UNet results: `\includegraphics[width=\linewidth,keepaspectratio]{unet_results_grid}`

Each slide title: "Results — Simple AE", "Results — CNN Encoder-Decoder", "Results — UNet"

---

## Phase C — Slide Changes in `midcurve_impl_llm_short.tex`

### C1 — NEW slide: "QLoRA Fine-tuning Pipeline" (insert before "2D Brep Representation")
**TODO:** Add frame with code snippet from `src/text_based/finetuning/train.py`:
```python
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16)

lora_config = LoraConfig(
    r=16, lora_alpha=32,
    target_modules=["q_proj","v_proj","k_proj","o_proj"],
    lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")
```

### C2 — NEW slide: "SFT Trainer Setup"
**TODO:** Add frame with:
```python
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    peft_config=lora_config,
    formatting_func=format_prompt,
    max_seq_length=Config.MAX_SEQ_LENGTH,
    args=training_args)
trainer.train()
```

### C3 — Expand "Data" slide (currently shows only `shapes_csv` image)
**TODO:** Add bullet list below image:
- 993 rows total: 80% train / 10% val / 10% test
- 4 base shapes: I, L, T, Plus — augmented by rotation, translation, mirroring
- BRep JSON columns: `Profile_brep` → `Midcurve_brep` (Points / Lines / Segments)

### C4 — NEW slide: "Evaluation Metrics"
**TODO:** Add frame with bullet list:
- JSON validity (parse success rate)
- Chamfer distance (point-cloud proximity)
- Hausdorff distance (worst-case deviation)
- Topology accuracy (correct node/edge count)
- Combined score (weighted average)

Short snippet from `metrics_enhanced.py` showing `compute_all_metrics()` signature.

### C5 — NEW slide: "Fine-tuning Results" (add AFTER A5 image is generated)
**TODO:** Add frame referencing:
- `\includegraphics[width=\linewidth,keepaspectratio]{llm_metric_distributions}`
- Caption: "Metric distributions across test set after QLoRA fine-tuning"

---

## Phase D — New slide in `midcurve_intro_ann_short.tex`

### D1 — NEW slide: "Phase III — Graph Transformer" (append at end of file)
**TODO:** Add frame:
- Input: polygon graph (nodes = corner points with (x,y) features, edges = polygon sides)
- Output: midcurve node coordinates + predicted adjacency matrix
- Architecture: LaplacianPE → TransformerConv layers (residual + LayerNorm) → TopKPooling bottleneck → Non-auto-regressive decoder
- Loss: Chamfer distance + adjacency BCE
- Slide with `\includegraphics[width=\linewidth,keepaspectratio]{graph_transformer_results_grid}` (from A4)

---

## Phase E — Update `midcurve_refs.tex`

### E1 — Add new references
**TODO:** Add to the itemize list:
- Kulkarni, Y.H. "Midcurve Computation using LLM Fine-tuning" ICACCS 2024 / Gen4SE 2024
- Kulkarni, Y.H. "MidcurveNN Phase III: Graph Transformer for Midcurve Computation" (this work, 2025)

---

## Execution Order

```
1. conda activate midcurvenn
2. Run A1 → copy simple_results_grid.png
3. Run A2 → copy cnn_results_grid.png
4. Run A3 → copy unet_results_grid.png   (only if weights exist)
5. Run A4 → copy graph_transformer_results_grid.png  (train first if no checkpoint)
6. Run A5 → copy llm_metric_distributions.png  (only after fine-tuning)
7. Edit midcurve_impl_ann_short.tex   (B1–B5)
8. Edit midcurve_impl_llm_short.tex   (C1–C5; C5 only after A5)
9. Edit midcurve_intro_ann_short.tex  (D1; image ref only after A4)
10. Edit midcurve_refs.tex             (E1)
11. Compile: pdflatex Main_Midcurve_short_Presentation.tex (x2)
12. Check PDF — confirm images render, no overfull hbox warnings on code slides
```

---

## Notes

- All `lstlisting` code slides must have `[fragile]` on the frame (already the case in existing slides).
- Keep code snippets to ~10-15 lines max; use `\ldots` or `% ...` to elide less important lines.
- `basicstyle=\tiny` may be needed for longer snippets to fit the slide.
- Images from `results_grid.png` are 5-row × 3-col grids: Input Profile | Ground Truth | Predicted.
- The `midcurve_impl_cnn.tex` and `midcurve_impl_geometry.tex` files exist as longer variants
  but are NOT included in the short presentation — do not edit those unless switching to the full deck.
