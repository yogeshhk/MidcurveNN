# nemotron3 — Midcurve Prediction with Nemotron-Mini-4B-Instruct

Three class-based approaches for predicting 2D polygon midcurves using
`nvidia/Nemotron-Mini-4B-Instruct` on the BRep JSON dataset.

---

## Approaches

| File | Class | Description |
|---|---|---|
| `hf_sft_trainer.py` | `HFSFTTrainer` | QLoRA fine-tuning via PEFT + HuggingFace SFTTrainer |
| `unsloth_trainer.py` | `UnslothTrainer` | Unsloth-accelerated QLoRA (2-4x faster, 70% less VRAM); falls back to PEFT |
| `fewshot_prompter.py` | `FewShotPrompter` | Few-shot prompting with the base model — no fine-tuning required |

All three share `config.py` (hyperparameters) and `dataset_loader.py` (CSV → HF Dataset).
Evaluation utilities live in `evaluate.py` / `metrics.py` / `inference.py`.

---

## Quick Start

```bash
cd src/text_based/nemotron3
conda activate genai
```

### Approach 1 — HuggingFace SFTTrainer QLoRA

```bash
python hf_sft_trainer.py
# Saves adapter to: results/Midcurve-Nemotron-Mini-v1/
```

### Approach 2 — Unsloth-accelerated QLoRA

```bash
# Install Unsloth first (Windows CUDA 12.1):
pip install "unsloth[cu121-windows]"

python unsloth_trainer.py
# Saves adapter to: results/Midcurve-Nemotron-Unsloth-v1/  (or -PEFT-v1 on fallback)
```

### Approach 3 — Few-shot prompting (base model, no adapter)

```bash
python fewshot_prompter.py
# Outputs: results/evaluation_results.csv  results/results_grid.png
```

### Evaluate a fine-tuned adapter

```bash
python evaluate.py --model_path results/Midcurve-Nemotron-Mini-v1
python inference.py --single
```

---

## Library Usage

```python
from hf_sft_trainer import HFSFTTrainer
from unsloth_trainer import UnslothTrainer
from fewshot_prompter import FewShotPrompter

# Fine-tune (one call orchestrator)
HFSFTTrainer().run()
UnslothTrainer().run()

# Few-shot prediction
p = FewShotPrompter(n_samples=7)
p.load_model()
result_json = p.predict('{"Points": [...], "Lines": [...], "Segments": [...]}')
p.evaluate()   # saves CSV + results grid
```

---

## Memory Requirements (4 GB VRAM)

| Setting | Value |
|---|---|
| Quantization | 4-bit NF4 (BitsAndBytes) |
| LoRA rank | 16 |
| Effective batch size | 16 (batch=1, grad_acc=16) |
| Max sequence length | 1024 |
| Optimizer | 8-bit AdamW |

The `FewShotPrompter` forces CPU if GPU VRAM < 5 GB; trainers use `device_map="auto"`.

---

## File Reference

| File | Role |
|---|---|
| `config.py` | `Config` class: MODEL_ID, LoRA hyperparameters, data paths |
| `dataset_loader.py` | `MidcurveDataset`: CSV → chat-format HuggingFace Dataset |
| `hf_sft_trainer.py` | `HFSFTTrainer`: load → apply LoRA → SFTTrainer → save |
| `unsloth_trainer.py` | `UnslothTrainer`: Unsloth/PEFT load → SFTTrainer → save |
| `fewshot_prompter.py` | `FewShotPrompter`: base model + 2-shot examples → predict/evaluate |
| `inference.py` | `NemotronInference`: load adapter, generate, validate, repair |
| `evaluate.py` | `NemotronEvaluator`: test-set loop, metrics, results grid |
| `metrics.py` | `GeometricMetrics`: Chamfer, Hausdorff, topology, connectivity |
| `results/` | Runtime outputs: CSV, results grid PNG |
