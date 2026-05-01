"""
run_demo.py  --  Hardware-aware demo for the nemotron3 pipeline.

Why this exists
---------------
nvidia/Nemotron-Mini-4B-Instruct requires ~2-3 GB GPU VRAM (4-bit) plus an
~8 GB download.  The development machine has a 1 GB MX570 A GPU, so the full
model cannot be loaded.

This script uses google/flan-t5-large (770 M params, already cached locally,
fits in 1 GB VRAM with 4-bit quantization) to exercise the complete pipeline:
  data loading  ->  model inference  ->  metric computation
  ->  evaluation_results.csv  ->  results_grid.png

When running on a machine with >= 8 GB VRAM, replace DEMO_MODEL with
"nvidia/Nemotron-Mini-4B-Instruct" and set USE_CAUSAL_LM = True.

Outputs
-------
  results/evaluation_results.csv
  results/results_grid.png
"""
import os
import sys
import json
import ast
import torch
import pandas as pd
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from config import Config
from metrics import GeometricMetrics

# Load make_results_grid by explicit path to avoid finetuning/evaluate.py hijack
import importlib.util as _ilu
_eval_spec = _ilu.spec_from_file_location("_n3eval", os.path.join(_HERE, "evaluate.py"))
_eval_mod  = _ilu.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(_eval_mod)
make_results_grid = _eval_mod.make_results_grid

# ── Demo configuration ────────────────────────────────────────────────────────
# google/gemma-2b-it: cached locally, causal LM, instruction-tuned,
# fits in 1 GB VRAM with 4-bit quantisation (~1 GB model size).
DEMO_MODEL     = "google/gemma-2b-it"
USE_CAUSAL_LM  = True
N_SAMPLES      = 7
MAX_NEW_TOKENS = 256
# ─────────────────────────────────────────────────────────────────────────────

# Gemma does not support a system role; merge task description into user turn.
_TASK_DESC = (
    "You are a CAD geometry assistant. "
    "Given a 2D polygon profile in JSON BRep format (with keys \"Points\", \"Lines\", \"Segments\"), "
    "output ONLY the JSON BRep of its midcurve (medial axis / skeletal centreline). "
    "The midcurve runs through the geometric centre of the shape. "
    "Do not add any explanation — output valid JSON only.\n\n"
)


# ── Model loading ─────────────────────────────────────────────────────────────

def load_model():
    from transformers import (
        AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM,
    )

    # Load on CPU with float16 — avoids the 1 GB VRAM limit of the MX570 A.
    # gemma-2b-it in float16 is ~5 GB RAM; 15 GB system RAM handles it fine.
    print(f"Loading {DEMO_MODEL} on CPU (float16) …")
    tok = AutoTokenizer.from_pretrained(DEMO_MODEL)
    tok.pad_token = tok.eos_token

    model_cls = AutoModelForCausalLM if USE_CAUSAL_LM else AutoModelForSeq2SeqLM
    model = model_cls.from_pretrained(
        DEMO_MODEL,
        device_map="cpu",
        dtype=torch.float16,
        low_cpu_mem_usage=True,
    )
    model.eval()
    print("Model loaded on CPU.")
    return model, tok


# ── Inference ─────────────────────────────────────────────────────────────────

def generate_prediction(model, tok, profile_json):
    user_content = _TASK_DESC + "Profile BRep:\n" + str(profile_json) + "\n\nMidcurve BRep:"

    if USE_CAUSAL_LM:
        # Use chat template if available (gemma-2b-it supports it)
        try:
            messages = [{"role": "user", "content": user_content}]
            prompt   = tok.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            prompt = user_content

        inputs = tok(prompt, return_tensors="pt",
                     truncation=True, max_length=768).to(model.device)
        with torch.no_grad():
            out_ids = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                temperature=1.0,
                pad_token_id=tok.eos_token_id,
            )
        new_ids = out_ids[0][inputs["input_ids"].shape[1]:]
        return tok.decode(new_ids, skip_special_tokens=True).strip()
    else:
        # seq2seq (flan-t5 style)
        inputs = tok(user_content, return_tensors="pt",
                     truncation=True, max_length=512).to(model.device)
        with torch.no_grad():
            out_ids = model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                num_beams=4,
                early_stopping=True,
            )
        return tok.decode(out_ids[0], skip_special_tokens=True).strip()


def extract_json(text):
    """Try multiple strategies to extract a valid BRep JSON from raw model output."""
    candidates = [text]

    # Try content between code fences
    for fence in ["```json", "```"]:
        if fence in text:
            candidates.append(text.split(fence)[-1].split("```")[0].strip())

    # Try finding the first { … } span
    start = text.find("{")
    if start != -1:
        depth, end = 0, start
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        candidates.append(text[start:end + 1])

    for c in candidates:
        try:
            d = json.loads(c)
            if "Points" in d:
                return json.dumps(d)
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            d = ast.literal_eval(c)
            if isinstance(d, dict) and "Points" in d:
                return json.dumps(d)
        except Exception:
            pass

    return text  # return raw; metrics will flag json_validity = 0


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    results_dir = Path(Config.BASE_DIR) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(Config.TEST_FILE).head(N_SAMPLES)
    print(f"Loaded {len(df)} test samples from {Config.TEST_FILE}\n")

    model, tok = load_model()
    print()

    records = []
    for _, row in df.iterrows():
        profile    = str(row["Profile_brep"])
        truth      = str(row["Midcurve_brep"])
        shape_name = str(row.get("ShapeName", f"sample_{len(records)}"))

        print(f"[{len(records)+1}/{N_SAMPLES}] {shape_name:25s} … ", end="", flush=True)
        raw  = generate_prediction(model, tok, profile)
        pred = extract_json(raw)
        m    = GeometricMetrics.compute_all_metrics(pred, truth, profile)

        records.append({
            "index":       len(records),
            "shape_name":  shape_name,
            "pred":        pred,
            "true":        truth,
            "profile":     profile,
            **m,
            "success":     bool(m["json_validity"] > 0),
            "attempts":    1,
            "demo_model":  DEMO_MODEL,
        })
        print(
            f"valid={m['json_validity']:.0f}  "
            f"H={m['hausdorff']:.3f}  "
            f"C={m['chamfer']:.3f}  "
            f"score={m['combined_score']:.3f}"
        )

    # ── Save CSV ──────────────────────────────────────────────────────────────
    csv_path = results_dir / "evaluation_results.csv"
    out_df = pd.DataFrame(records).drop(
        columns=["pred", "true", "profile"], errors="ignore"
    )
    out_df.to_csv(csv_path, index=False)
    print(f"\nResults CSV  : {csv_path}")

    # ── Save grid ─────────────────────────────────────────────────────────────
    grid_path = str(results_dir / "results_grid.png")
    try:
        make_results_grid(records, grid_path, n=N_SAMPLES)
    except Exception as exc:
        print(f"WARNING: grid skipped — {exc}")

    # ── Summary ───────────────────────────────────────────────────────────────
    valid = [r for r in records if r.get("json_validity", 0) > 0]
    total = len(records)
    print(f"\n=== Demo Summary ({DEMO_MODEL}) ===")
    print(f"Total   : {total}")
    print(f"Valid JSON: {len(valid)} ({100*len(valid)//total if total else 0} %)")
    if valid:
        for key in ("hausdorff", "chamfer", "topology_accuracy",
                    "connectivity_score", "combined_score"):
            vals = [r[key] for r in valid if key in r]
            if vals:
                print(f"  {key:25s}: {sum(vals)/len(vals):.4f}")
    print()
    print("NOTE: Results use an untrained base model as demo.")
    print("      Fine-tune with train.py on hardware with >= 8 GB VRAM for")
    print("      real Nemotron-Mini-4B-Instruct results.")


if __name__ == "__main__":
    main()
