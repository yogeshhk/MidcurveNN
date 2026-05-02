"""
evaluate.py  --  Evaluate fine-tuned Nemotron-Mini on the held-out test set.

Outputs
-------
  results/evaluation_results.csv   -- per-sample metrics
  results/results_grid.png         -- 7-row x 3-col visualisation grid

Usage:
    cd src/text_based/nemotron3
    conda activate genai
    python evaluate.py
    python evaluate.py --n 20          # quick run on first 20 test samples
    python evaluate.py --model_path /path/to/adapter
"""
import os
import sys
import json
import argparse
from pathlib import Path

import pandas as pd

_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.normpath(os.path.join(_DIR, '..', '..'))
sys.path.insert(0, _DIR)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from config import Config
from inference import NemotronInference
from metrics import GeometricMetrics


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def make_results_grid(records, save_path, n=7):
    """Create and save a n-row x 3-col results grid PNG using shared utility."""
    from utils.prepare_plots import save_results_grid_brep

    # Prefer samples with valid JSON; fall back to any
    samples = [r for r in records if r.get("json_validity", 0) > 0][:n]
    if not samples:
        samples = records[:n]
    if not samples:
        print("No samples to visualise.")
        return

    save_results_grid_brep(
        [r["profile"] for r in samples],
        [r["true"]    for r in samples],
        [r["pred"]    for r in samples],
        save_path=save_path,
        n=len(samples),
        shape_names=[r.get("shape_name", "") for r in samples],
        scores=[r.get("combined_score", 0.0) for r in samples],
        title="Nemotron-Mini Midcurve Predictions",
    )


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

class NemotronEvaluator:
    def __init__(self, model_path=None):
        self.model_path  = str(
            model_path or Path(Config.BASE_DIR) / Config.NEW_MODEL_NAME
        )
        self.inferencer  = NemotronInference()
        self.records     = []
        self.results_dir = Path(Config.BASE_DIR) / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run(self, test_file=None, n_samples=None):
        test_file = test_file or Config.TEST_FILE
        df = pd.read_csv(test_file)
        if n_samples:
            df = df.head(n_samples)

        self.inferencer.load_model(self.model_path)

        for idx, row in df.iterrows():
            profile    = str(row["Profile_brep"])
            truth      = str(row["Midcurve_brep"])
            shape_name = str(row.get("ShapeName", ""))

            pred, meta = self.inferencer.predict(profile)
            m = GeometricMetrics.compute_all_metrics(pred, truth, profile)

            self.records.append({
                "index":       idx,
                "shape_name":  shape_name,
                "pred":        pred,
                "true":        truth,
                "profile":     profile,
                **m,
                **meta,
            })

            print(
                f"[{len(self.records):3d}/{len(df)}] {shape_name:22s} | "
                f"valid={m.get('json_validity', 0):.0f}  "
                f"H={m.get('hausdorff', 0):.3f}  "
                f"C={m.get('chamfer', 0):.3f}  "
                f"score={m.get('combined_score', 0):.3f}"
            )

        self._save_csv()
        self._print_summary()
        self._save_grid()

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def _save_csv(self):
        out = self.results_dir / "evaluation_results.csv"
        df  = pd.DataFrame(self.records)
        # Omit raw text columns to keep CSV manageable
        df.drop(columns=["pred", "true", "profile"],
                errors="ignore", inplace=True)
        df.to_csv(out, index=False)
        print(f"Results CSV: {out}")

    def _print_summary(self):
        total = len(self.records)
        if total == 0:
            return
        valid = [r for r in self.records if r.get("json_validity", 0) > 0]
        print(f"\n=== Evaluation Summary ===")
        print(f"Total  : {total}")
        print(f"Valid JSON : {len(valid)} ({100 * len(valid) / total:.1f} %)")
        if valid:
            for key in ("hausdorff", "chamfer", "topology_accuracy",
                        "connectivity_score", "combined_score"):
                vals = [r[key] for r in valid if key in r]
                if vals:
                    print(f"  {key:25s}: {sum(vals)/len(vals):.4f}")

    def _save_grid(self):
        grid_path = str(self.results_dir / "results_grid.png")
        try:
            make_results_grid(self.records, grid_path)
        except Exception as exc:
            print(f"WARNING: grid generation skipped — {exc}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Evaluate Nemotron-Mini on the MidcurveNN test set."
    )
    ap.add_argument("--model_path", default=None,
                    help="Path to fine-tuned LoRA adapter dir "
                         "(default: results/Midcurve-Nemotron-Mini-v1)")
    ap.add_argument("--n", type=int, default=None,
                    help="Limit to first N test samples (default: all)")
    args = ap.parse_args()

    ev = NemotronEvaluator(model_path=args.model_path)
    ev.run(n_samples=args.n)


if __name__ == "__main__":
    main()
