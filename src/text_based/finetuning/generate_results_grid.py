"""
generate_results_grid.py
Generate results/results_grid.png for the QLoRA fine-tuning approach.

Data source priority:
  1. results/evaluation_results.csv  — if it has profile_input / ground_truth / prediction columns
  2. Fine-tuned model directory      — run live inference on N test samples
  3. Test CSV fallback               — show profile + GT; prediction panel says "model not available"

Usage:
    cd src/text_based/finetuning
    conda activate midcurvenn
    python generate_results_grid.py
    python generate_results_grid.py --n 7
"""
import os
import sys
import argparse
from pathlib import Path

_HERE = Path(__file__).resolve().parent        # src/text_based/finetuning/
_SRC  = _HERE.parent.parent                    # src/
sys.path.insert(0, str(_SRC))   # src/ at [1] after next insert
sys.path.insert(0, str(_HERE))  # finetuning/ wins over src/ for local config

from config import Config  # noqa: E402  (after sys.path setup)

RESULTS_DIR = _HERE / "results"
GRID_PATH   = str(RESULTS_DIR / "results_grid.png")
_N_DEFAULT  = 7


# ---------------------------------------------------------------------------
# Source helpers
# ---------------------------------------------------------------------------

def _load_from_results_csv(n):
    """Try loading (profile, gt, pred, name, score) from a saved evaluation CSV."""
    candidates = [
        RESULTS_DIR / "evaluation_results.csv",
        RESULTS_DIR / "evaluation_results_sample.csv",
    ]
    for path in candidates:
        if not path.exists():
            continue
        try:
            import pandas as pd
            df = pd.read_csv(path)
            needed = {"profile_input", "ground_truth", "prediction"}
            if not needed.issubset(df.columns):
                print(f"[grid] {path.name} lacks prediction columns, skipping")
                continue
            df = df.head(n)
            names  = list(df.get("shape_name", [f"sample_{i}" for i in range(len(df))]))
            scores = list(df["combined_score"]) if "combined_score" in df.columns else None
            print(f"[grid] loaded {len(df)} samples from {path.name}")
            return (list(df["profile_input"]), list(df["ground_truth"]),
                    list(df["prediction"]),    names, scores)
        except Exception as exc:
            print(f"[grid] could not read {path}: {exc}")
    return None


def _load_from_model(n):
    """Load fine-tuned model and run inference on N test samples."""
    model_candidates = [
        _HERE / Config.NEW_MODEL_NAME,
        Path(Config.NEW_MODEL_NAME),
    ]
    model_path = None
    for candidate in model_candidates:
        if candidate.exists():
            model_path = str(candidate)
            break

    if model_path is None:
        print(f"[grid] no trained model found (looked for '{Config.NEW_MODEL_NAME}')")
        return None

    print(f"[grid] loading fine-tuned model from {model_path}")
    try:
        import torch
        import pandas as pd
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        from metrics import GeometricMetrics

        base = AutoModelForCausalLM.from_pretrained(
            Config.MODEL_ID, device_map="auto", torch_dtype=torch.float16)
        tok  = AutoTokenizer.from_pretrained(Config.MODEL_ID)
        model = PeftModel.from_pretrained(base, model_path).merge_and_unload()
        model.eval()

        df = pd.read_csv(Config.TEST_FILE).head(n)
        profiles, gts, preds, names, scores = [], [], [], [], []

        for _, row in df.iterrows():
            profile = str(row["Profile_brep"])
            gt      = str(row["Midcurve_brep"])
            name    = str(row.get("ShapeName", ""))

            messages = [
                {"role": "system", "content": Config.SYSTEM_PROMPT},
                {"role": "user",   "content": profile},
            ]
            text   = tok.apply_chat_template(messages, tokenize=False,
                                              add_generation_prompt=True)
            inputs = tok([text], return_tensors="pt").to(model.device)
            with torch.no_grad():
                out = model.generate(
                    inputs.input_ids,
                    max_new_tokens=Config.MAX_NEW_TOKENS,
                    do_sample=False,
                    temperature=Config.TEMPERATURE,
                )
            resp  = tok.batch_decode(
                [out[0][inputs.input_ids.shape[1]:]], skip_special_tokens=True
            )[0].strip()

            m     = GeometricMetrics.compute_all_metrics(resp, gt, profile)
            score = m.get("combined_score", 0.0)
            profiles.append(profile); gts.append(gt); preds.append(resp)
            names.append(name);        scores.append(score)
            print(f"  {name}: score={score:.3f}")

        return profiles, gts, preds, names, scores

    except Exception as exc:
        print(f"[grid] model inference failed: {exc}")
        return None


def _load_from_test_csv(n):
    """Fallback: load test CSV, use GT as placeholder for predicted."""
    import pandas as pd
    df    = pd.read_csv(Config.TEST_FILE).head(n)
    names = list(df.get("ShapeName", [f"sample_{i}" for i in range(len(df))]))
    print(f"[grid] using {len(df)} samples from test CSV (no model available)")
    return (list(df["Profile_brep"]), list(df["Midcurve_brep"]),
            [None] * len(df), names, None)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Generate results_grid.png for the QLoRA finetuning approach"
    )
    ap.add_argument("--n", type=int, default=_N_DEFAULT,
                    help="Number of sample rows in the grid (default: 7)")
    args = ap.parse_args()
    n    = args.n

    result = (_load_from_results_csv(n)
              or _load_from_model(n)
              or _load_from_test_csv(n))

    profiles, gts, preds, names, scores = result

    from utils.prepare_plots import save_results_grid_brep
    save_results_grid_brep(
        profiles, gts, preds,
        save_path=GRID_PATH,
        n=n,
        shape_names=names,
        scores=scores,
        title="QLoRA Midcurve Predictions (Finetuning)",
    )


if __name__ == "__main__":
    main()
