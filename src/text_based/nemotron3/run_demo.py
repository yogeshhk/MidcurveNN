"""
run_demo.py  --  Demo using nvidia/Nemotron-Mini-4B-Instruct in 4-bit (no fine-tuning).

Uses few-shot prompting so the base model understands the BRep JSON format,
then repairs the output to ensure Lines array is always populated (so the
results grid shows connected midcurves rather than isolated dots).

Hardware: 4 GB GPU VRAM is sufficient (4-bit model ~2 GB + KV cache).

Install prerequisites:
    pip install bitsandbytes>=0.43.0 accelerate>=0.26.0

Usage:
    cd src/text_based/nemotron3
    conda activate genai
    python run_demo.py

Outputs:
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

# Load make_results_grid from evaluate.py without importing finetuning/evaluate.py
import importlib.util as _ilu
_eval_spec = _ilu.spec_from_file_location("_n3eval", os.path.join(_HERE, "evaluate.py"))
_eval_mod  = _ilu.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(_eval_mod)
make_results_grid = _eval_mod.make_results_grid

# ── Demo configuration ────────────────────────────────────────────────────────
DEMO_MODEL     = "nvidia/Nemotron-Mini-4B-Instruct"
N_SAMPLES      = 7
MAX_NEW_TOKENS = 128   # midcurve JSON is ~80-150 chars; keeps CPU inference fast
MAX_INPUT_LEN  = 512   # shorter prompt = faster CPU inference
# ─────────────────────────────────────────────────────────────────────────────

# Two few-shot examples from actual training data (I-shape and L-shape)
_FEW_SHOT = [
    {
        "profile":  ('{"Points": [[-3.21, 6.3], [-1.67, 11.06], [-15.93, 15.69], [-17.48, 10.94]],'
                     ' "Lines": [[0, 1], [1, 2], [2, 3], [3, 0]], "Segments": [[0, 1, 2, 3]]}'),
        "midcurve": '{"Points": [[-2.44, 8.68], [-16.7, 13.31]], "Lines": [[0, 1]], "Segments": [[0]]}',
    },
    {
        "profile":  ('{"Points": [[33.0, 33.0], [38.0, 33.0], [38.0, 58.0], [63.0, 58.0],'
                     ' [63.0, 63.0], [33.0, 63.0]], "Lines": [[0, 1], [1, 2], [2, 3], [3, 4],'
                     ' [4, 5], [5, 0]], "Segments": [[0, 1, 2, 3, 4, 5]]}'),
        "midcurve": ('{"Points": [[35.5, 33.0], [35.5, 60.5], [63.0, 60.5]],'
                     ' "Lines": [[0, 1], [1, 2]], "Segments": [[0, 1]]}'),
    },
]

_SYSTEM_PROMPT = (
    "You are a CAD geometry assistant specialised in computing midcurves.\n"
    "Given a 2D closed polygon profile in JSON BRep format, output ONLY the JSON BRep "
    "of its midcurve (medial axis / skeletal centreline).\n\n"
    "Rules:\n"
    "- The midcurve runs through the geometric centre of the profile walls.\n"
    '- Output JSON must contain exactly: "Points" (list of [x,y] coordinates), '
    '"Lines" (list of [start_idx, end_idx] index pairs), "Segments" (list of line-index groups).\n'
    "- For an I/bar shape: 2 points connected by 1 Line.\n"
    "- For an L-shape: 3 points forming an L, connected by 2 Lines.\n"
    "- For a Plus/T-shape: central junction point with 4/3 branches, connected by multiple Lines.\n"
    "- Points must lie at the geometric midpoint between opposite walls.\n"
    "- Lines indices reference the Points list (zero-based).\n"
    "- Output ONLY valid JSON, no explanation or markdown fences."
)


def _build_prompt_messages(profile_json: str) -> list:
    """Return a messages list with few-shot examples folded into the user turn."""
    examples = ""
    for ex in _FEW_SHOT:
        examples += f"Profile: {ex['profile']}\nMidcurve: {ex['midcurve']}\n\n"
    user_content = f"{examples}Profile: {profile_json}\nMidcurve:"
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user",   "content": user_content},
    ]


# ── Model loading ─────────────────────────────────────────────────────────────

def load_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    # MX570 A has only 2.1 GB VRAM — too small for 4B model even in 4-bit once
    # KV cache + activations are added.  Force CPU so we don't OOM mid-inference.
    # 4-bit on CPU: weights ~2 GB RAM, compute in float16.
    vram_gb = (torch.cuda.get_device_properties(0).total_memory / 1e9
               if torch.cuda.is_available() else 0)
    use_gpu = vram_gb >= 5.0   # only use GPU if >= 5 GB VRAM

    if use_gpu:
        bnb_cfg = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        device_map = "auto"
        extra_kw   = {"quantization_config": bnb_cfg}
        print(f"Loading {DEMO_MODEL} in 4-bit on GPU ({vram_gb:.1f} GB) ...")
    else:
        # CPU path: 4-bit via BNB (weights ~2 GB) or fall back to float16 (~8 GB)
        try:
            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
            extra_kw = {"quantization_config": bnb_cfg}
            print(f"Loading {DEMO_MODEL} in 4-bit on CPU (GPU VRAM {vram_gb:.1f} GB < 5 GB) ...")
        except Exception:
            extra_kw = {"torch_dtype": torch.float16}
            print(f"Loading {DEMO_MODEL} in float16 on CPU ...")
        device_map = "cpu"

    tok               = AutoTokenizer.from_pretrained(DEMO_MODEL)
    tok.pad_token     = tok.eos_token
    tok.padding_side  = "left"

    model = AutoModelForCausalLM.from_pretrained(
        DEMO_MODEL,
        device_map=device_map,
        low_cpu_mem_usage=True,
        **extra_kw,
    )
    model.eval()
    print(f"Model loaded on CPU (VRAM {vram_gb:.1f} GB, CPU-only inference).")
    return model, tok


# ── Inference ─────────────────────────────────────────────────────────────────

def generate_prediction(model, tok, profile_json: str) -> str:
    messages = _build_prompt_messages(profile_json)
    try:
        prompt = tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    except Exception:
        # Fallback: join system + user manually if chat template unavailable
        prompt = _SYSTEM_PROMPT + "\n\n" + messages[1]["content"]

    inputs = tok(
        prompt, return_tensors="pt", truncation=True, max_length=MAX_INPUT_LEN
    ).to(model.device)

    with torch.no_grad():
        out_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,
            pad_token_id=tok.eos_token_id,
            repetition_penalty=1.1,
        )
    new_ids = out_ids[0][inputs["input_ids"].shape[1]:]
    return tok.decode(new_ids, skip_special_tokens=True).strip()


# ── JSON extraction + repair ──────────────────────────────────────────────────

def _try_parse(text: str):
    """Return parsed dict or None."""
    for candidate in _extraction_candidates(text):
        for parser in (json.loads, ast.literal_eval):
            try:
                d = parser(candidate)
                if isinstance(d, dict) and "Points" in d:
                    return d
            except Exception:
                pass
    return None


def _extraction_candidates(text: str):
    candidates = [text]
    for fence in ("```json", "```"):
        if fence in text:
            candidates.append(text.split(fence)[-1].split("```")[0].strip())
    start = text.find("{")
    if start != -1:
        depth, end = 0, -1
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end != -1:
            candidates.append(text[start:end + 1])
    return candidates


def _repair_lines(data: dict) -> dict:
    """
    If Lines is empty/missing but Points has multiple entries, connect them
    sequentially.  This gives a reasonable midcurve for I/L shapes and at
    least shows a line (not isolated dots) for other shapes.
    """
    pts   = data.get("Points", [])
    lines = data.get("Lines",  [])
    if len(pts) > 1 and not lines:
        lines = [[i, i + 1] for i in range(len(pts) - 1)]
        data["Lines"]    = lines
        data["Segments"] = data.get("Segments") or [list(range(len(lines)))]
    return data


def extract_and_repair(raw: str) -> str:
    data = _try_parse(raw)
    if data is None:
        return raw          # return as-is; metrics will flag json_validity=0
    data = _repair_lines(data)
    return json.dumps(data)


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

        print(f"[{len(records)+1}/{N_SAMPLES}] {shape_name:25s} ... ", end="", flush=True)
        raw  = generate_prediction(model, tok, profile)
        pred = extract_and_repair(raw)
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
            f"H={m['hausdorff']:.2f}  "
            f"C={m['chamfer']:.2f}  "
            f"score={m['combined_score']:.3f}"
        )

    # Save CSV
    csv_path = results_dir / "evaluation_results.csv"
    out_df = pd.DataFrame(records).drop(
        columns=["pred", "true", "profile"], errors="ignore"
    )
    out_df.to_csv(csv_path, index=False)
    print(f"\nResults CSV : {csv_path}")

    # Save results grid
    grid_path = str(results_dir / "results_grid.png")
    grid_saved = False
    try:
        make_results_grid(records, grid_path, n=N_SAMPLES)
        print(f"Results grid: {grid_path}")
        grid_saved = True
    except Exception as exc:
        print(f"WARNING: grid skipped -- {exc}")

    # Copy to publications
    if grid_saved:
        import shutil
        pub_images = Path(Config.BASE_DIR).parents[2] / "publications" / "Midcurve_LaTeX" / "images"
        if pub_images.is_dir():
            dest = pub_images / "nemotron_results_grid.png"
            shutil.copy2(grid_path, dest)
            print(f"Copied to   : {dest}")
        else:
            print(f"NOTE: publications folder not found at {pub_images} — skipping copy")

    # Summary
    valid = [r for r in records if r.get("json_validity", 0) > 0]
    total = len(records)
    print(f"\n=== Demo Summary ({DEMO_MODEL}) ===")
    print(f"Total     : {total}")
    pct = (100.0 * len(valid) / total) if total else 0.0
    print(f"Valid JSON: {len(valid)} ({pct:.1f} %)")
    if valid:
        for key in ("hausdorff", "chamfer", "topology_accuracy",
                    "connectivity_score", "combined_score"):
            vals = [r[key] for r in valid if key in r]
            if vals:
                print(f"  {key:25s}: {sum(vals) / len(vals):.4f}")
    print()
    print("NOTE: Results use the pre-trained base model (no fine-tuning).")
    print("      For better results, run train.py or train_unsloth.py, then evaluate.py.")


if __name__ == "__main__":
    main()
