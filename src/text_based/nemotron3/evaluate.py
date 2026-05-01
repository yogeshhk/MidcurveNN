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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from inference import NemotronInference
from metrics import GeometricMetrics


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def _draw_brep(ax, brep_str, title, color):
    """Plot a BRep (Points + Lines) onto a matplotlib Axes."""
    import ast as _ast
    data = None
    try:
        if isinstance(brep_str, dict):
            data = brep_str
        else:
            # Try JSON first, then Python repr (single-quote dicts from CSV)
            try:
                candidate = json.loads(brep_str)
            except (json.JSONDecodeError, TypeError, ValueError):
                candidate = _ast.literal_eval(brep_str)
            if isinstance(candidate, str):
                candidate = json.loads(candidate)
            if isinstance(candidate, dict):
                data = candidate
    except Exception:
        pass

    if data is None:
        ax.set_title(title, fontsize=8)
        ax.text(0.5, 0.5, "parse\nerror", ha="center", va="center",
                transform=ax.transAxes, color="red", fontsize=7)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        return

    pts   = data.get("Points", [])
    lines = data.get("Lines",  [])

    if not pts:
        ax.set_title(title, fontsize=8)
        return

    # Normalise flat [x,y,x,y,...] to [[x,y],[x,y],...]
    if pts and isinstance(pts[0], (int, float)):
        if len(pts) % 2 == 0:
            pts = [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]
        else:
            ax.set_title(title, fontsize=8)
            ax.text(0.5, 0.5, "bad\nformat", ha="center", va="center",
                    transform=ax.transAxes, color="orange", fontsize=7)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            return

    # Draw edges
    try:
        for ln in lines:
            if (isinstance(ln, (list, tuple)) and len(ln) >= 2
                    and ln[0] < len(pts) and ln[1] < len(pts)):
                x0, y0 = pts[ln[0]]
                x1, y1 = pts[ln[1]]
                ax.plot([x0, x1], [y0, y1], color=color, linewidth=1.5, zorder=2)
    except Exception:
        pass

    # Draw vertices
    try:
        xs, ys = zip(*pts)
        ax.scatter(xs, ys, color=color, s=18, zorder=3)
    except Exception:
        pass

    ax.set_title(title, fontsize=8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.25)
    ax.tick_params(labelsize=6)


def make_results_grid(records, save_path, n=7):
    """Create and save a n-row x 3-col results grid PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Prefer samples with valid JSON; fall back to any
    samples  = [r for r in records if r.get("json_validity", 0) > 0][:n]
    if not samples:
        samples = records[:n]
    n_rows = len(samples)
    if n_rows == 0:
        print("No samples to visualise.")
        return

    fig, axes = plt.subplots(n_rows, 3, figsize=(13, 3.5 * n_rows),
                             squeeze=False)

    for row_i, rec in enumerate(samples):
        shape = rec.get("shape_name", "")
        score = rec.get("combined_score", 0.0)
        row_ax = axes[row_i]

        _draw_brep(row_ax[0], rec["profile"],
                   f"Profile\n{shape}", "steelblue")
        _draw_brep(row_ax[1], rec["true"],
                   f"GT Midcurve\n{shape}", "forestgreen")
        _draw_brep(row_ax[2], rec["pred"],
                   f"Predicted\n{shape}\n(score={score:.2f})", "firebrick")

    plt.suptitle("Nemotron-Mini Midcurve Predictions", fontsize=10, y=1.01)
    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"Results grid saved: {save_path}")


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
