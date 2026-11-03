"""Compare trained models on the same tests beyond run.py's metrics.json. Trains nothing; loads existing best.pt files.

Run from src/geometry_based:  conda run -n genai python methods/equi_collapse/evaluate_extended.py
Writes methods/equi_collapse/runs/extended_metrics.json.

Tests (all on seed-2 synthetic data, or real shapes):
  iid_published     labels exactly as generated, including the known collinear artefact nodes
  iid_corrected     collinear degree-2 nodes removed from the ground truth
  rot_<deg>         corrected labels, profile and labels rotated by <deg> degrees (300 samples)
  noise_<s>         corrected labels; walls subdivided up to 40 vertices, then every vertex jittered by s * w (300 samples)
  deg4_corrected    degree-4-only shapes, corrected labels
  real4, real4_rot37
Noise is applied at test time only; no model here was trained on noisy shapes.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import numpy as np
import torch

from common import evaluate as ev
from common import geom
from common import prepare_data as pd
from methods import REGISTRY, runs_dir

CFG = argparse.Namespace(device="cpu")


def clean(s):
    nodes, edges = geom.remove_collinear_nodes(s["nodes"], s["edges"])
    return dict(s, nodes=nodes, edges=edges)


def rotate(s, deg):
    th = np.radians(deg)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return dict(s, profile=s["profile"] @ R.T, nodes=s["nodes"] @ R.T)


def rough(s, sigma, rng, nmax=40):
    """Add midpoints to the longest walls up to nmax vertices, then jitter every vertex. Label stays the clean midcurve."""
    p = [v for v in s["profile"]]
    while len(p) < nmax:
        L = [np.linalg.norm(p[(i + 1) % len(p)] - p[i]) for i in range(len(p))]
        i = int(np.argmax(L))
        p.insert(i + 1, (p[i] + p[(i + 1) % len(p)]) / 2)
    p = np.asarray(p) + rng.normal(0.0, sigma * s["w"], size=(len(p), 2))
    return dict(s, profile=p)


def score(predictor, samples):
    many = getattr(predictor, "many", None)
    preds = many(samples) if many else [predictor(s) for s in samples]
    rows = []
    for s, (pn, pe) in zip(samples, preds):
        ext = float((s["profile"].max(0) - s["profile"].min(0)).max() / 2)
        rows.append(ev.graph_metrics(pn, pe, s["nodes"], s["edges"], s["w"], extent=ext))
    return dict(n=len(rows), k_exact=float(np.mean([r["k_exact"] for r in rows])),
                deg_seq=float(np.mean([r["deg_seq_match"] for r in rows])),
                h_le_025w=float(np.mean([r["hausdorff_over_w"] <= 0.25 for r in rows])),
                ok_025w=float(np.mean([r["ok_025w"] for r in rows])),
                edge_f1=float(np.mean([r["edge_f1"] for r in rows])),
                h_over_w_median=float(np.median([r["hausdorff_over_w"] for r in rows])),
                is_tree=float(np.mean([r["is_tree"] for r in rows])))


def load(model, run):
    mod = REGISTRY[model]
    if model == "classical":
        return mod.make_predictor(mod.build_model(CFG), CFG)
    path = os.path.join(runs_dir(model), run)
    if not os.path.exists(os.path.join(path, "best.pt")):
        return None
    return mod.make_predictor(mod.load_best(path, CFG), CFG)


# name -> (model, run folder, trained without degree 4?)
MODELS = {
    "classical": ("classical", None, False),
    "set_transformer_e100_published_labels": ("set_transformer", "iid__e100", False),
    "set_transformer_control_n8000": ("set_transformer", "iid__clrot_n8000_e80", False),
    "equi_collapse_n8000": ("equi_collapse", "iid__n8000_e80", False),
    "set_transformer_control_n8000_nodeg4": ("set_transformer", "ood_deg4__clrot_n8000_e80", True),
    "equi_collapse_n8000_nodeg4": ("equi_collapse", "ood_deg4__n8000_e80", True),
}


def main():
    torch.set_num_threads(2)
    test = pd.make_dataset(1000, 2)
    test_c = [clean(s) for s in test]
    sub = test_c[:300]
    gold = pd.load_gold()
    rng = np.random.default_rng(1002)
    d4 = []
    while len(d4) < 1000:
        s = pd.make_sample(rng, allow_deg4=True)
        if s["deg_max"] == 4:
            d4.append(clean(s))
    out = {}
    for name, (model, run, nodeg4) in MODELS.items():
        pred = load(model, run)
        if pred is None:
            print("SKIP (no checkpoint):", name, flush=True)
            continue
        res = {}
        if not nodeg4:
            res["iid_published"] = score(pred, test)
            res["iid_corrected"] = score(pred, test_c)
            for deg in (5, 15, 30, 45):
                res["rot_%d" % deg] = score(pred, [rotate(s, deg) for s in sub])
            for sigma in (0.01, 0.02, 0.05, 0.1):
                r = np.random.default_rng(int(sigma * 1000))
                res["noise_%g" % sigma] = score(pred, [rough(s, sigma, r) for s in sub])
            res["real4"] = score(pred, gold)
            res["real4_rot37"] = score(pred, [rotate(g, 37) for g in gold])
        res["deg4_corrected"] = score(pred, d4)
        out[name] = res
        print(name, flush=True)
        for k, v in res.items():
            print("  %-16s n=%4d k_exact %.3f deg %.3f H<=.25w %.3f ok %.3f F1 %.3f" % (
                k, v["n"], v["k_exact"], v["deg_seq"], v["h_le_025w"], v["ok_025w"], v["edge_f1"]), flush=True)
    path = os.path.join(runs_dir("equi_collapse"), "extended_metrics.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
