"""ONE metric set for the geometry track.

graph_metrics works in whatever units the inputs are in (raw units for real shapes, generator units
for synthetic ones). Reported keys:
  chamfer_raw, hausdorff_raw      edge-sampled (step = 0.01 * bbox half-extent), raw units; chamfer =
                                  mean of the two directed mean nearest-distances (cross-paper numbers)
  chamfer_over_w, hausdorff_over_w  the same divided by wall width w
  chamfer_node                    node-only symmetric chamfer (blind to missing edges), raw units
  k_err, k_exact                  predicted minus true node count; exact match
  deg_seq_match                   sorted degree sequences equal
  branch_recall                   true nodes of degree >= 3 with a predicted node within 0.25 w
  connected, is_tree              properties of the predicted graph
  edge_precision/recall/f1        after Hungarian node matching with tolerance 0.25 w
  ok_025w                         hausdorff_over_w <= 0.25 and k_exact and deg_seq_match
"""
import json
import os

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

from common import geom

TOL_W = 0.25


def _directed(a, b):
    d, _ = cKDTree(b).query(a)
    return d


def chamfer_hausdorff(a, b):
    """Symmetric chamfer (mean of the two directed mean distances) and Hausdorff between point sets."""
    if len(a) == 0 or len(b) == 0:
        return float("inf"), float("inf")
    d1, d2 = _directed(a, b), _directed(b, a)
    return 0.5 * (d1.mean() + d2.mean()), max(d1.max(), d2.max())


def graph_metrics(pred_nodes, pred_edges, gt_nodes, gt_edges, w, extent=None):
    pn = np.asarray(pred_nodes, dtype=float).reshape(-1, 2)
    gn = np.asarray(gt_nodes, dtype=float).reshape(-1, 2)
    pe = [tuple(e) for e in pred_edges]
    ge = [tuple(e) for e in gt_edges]
    if extent is None:
        allp = np.vstack([pn, gn]) if len(pn) else gn
        extent = float(max((allp.max(0) - allp.min(0)).max() / 2.0, 1e-12))
    step = 0.01 * extent
    ch, hd = chamfer_hausdorff(geom.densify(pn, pe, step) if len(pn) else pn,
                               geom.densify(gn, ge, step))
    chn, _ = chamfer_hausdorff(pn, gn)
    K, Kg = len(pn), len(gn)
    dp = np.sort(geom.degrees(K, pe)) if K else np.zeros(0, int)
    dg = np.sort(geom.degrees(Kg, ge))
    k_exact = K == Kg
    deg_ok = bool(len(dp) == len(dg) and np.array_equal(dp, dg))
    tol = TOL_W * w
    # node matching
    n_match = 0
    pm, gm = {}, {}
    if K and Kg:
        D = np.linalg.norm(pn[:, None] - gn[None], axis=2)
        r, c = linear_sum_assignment(D)
        for a, b in zip(r, c):
            if D[a, b] <= tol:
                pm[a] = b
                gm[b] = a
    branch = [j for j in range(Kg) if dg is not None and geom.degrees(Kg, ge)[j] >= 3]
    if branch:
        if K:
            Dm = np.linalg.norm(pn[:, None] - gn[None], axis=2)
            branch_recall = float(np.mean([Dm[:, j].min() <= tol for j in branch]))
        else:
            branch_recall = 0.0
    else:
        branch_recall = 1.0
    gset = set((min(a, b), max(a, b)) for a, b in ge)
    correct = sum(1 for a, b in pe if a in pm and b in pm and (min(pm[a], pm[b]), max(pm[a], pm[b])) in gset)
    prec = correct / len(pe) if pe else (1.0 if not ge else 0.0)
    rec = correct / len(ge) if ge else 1.0
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    if K:
        A = np.zeros((K, K))
        for a, b in pe:
            A[a, b] = A[b, a] = 1
        ncomp = connected_components(csr_matrix(A), directed=False)[0]
        connected = ncomp == 1
        is_tree = bool(connected and len(pe) == K - 1)
    else:
        connected, is_tree = False, False
    hw = hd / w
    return dict(
        chamfer_raw=float(ch), hausdorff_raw=float(hd), chamfer_over_w=float(ch / w), hausdorff_over_w=float(hw),
        chamfer_node=float(chn), k_err=int(K - Kg), k_exact=bool(k_exact), deg_seq_match=deg_ok,
        branch_recall=branch_recall, connected=bool(connected), is_tree=bool(is_tree),
        edge_precision=float(prec), edge_recall=float(rec), edge_f1=float(f1),
        ok_025w=bool(hw <= TOL_W and k_exact and deg_ok),
    )


def evaluate_samples(predict, samples):
    """predict(sample) -> (nodes, edges) in the sample's own coordinates. Returns (rows, preds)."""
    rows, preds = [], []
    for s in samples:
        pn, pe = predict(s)
        ext = float(max((s["profile"].max(0) - s["profile"].min(0)).max() / 2.0, 1e-12))
        m = graph_metrics(pn, pe, s["nodes"], s["edges"], s["w"], extent=ext)
        m["shape"] = s.get("shape", "synthetic")
        m["deg_max"] = s.get("deg_max", -1)
        rows.append(m)
        preds.append((np.asarray(pn), list(pe)))
    return rows, preds


def summarize(rows):
    if not rows:
        return {}
    out = {"n": len(rows)}
    for k in ("chamfer_raw", "hausdorff_raw", "chamfer_over_w", "hausdorff_over_w", "chamfer_node",
              "edge_precision", "edge_recall", "edge_f1", "branch_recall"):
        v = np.array([r[k] for r in rows], dtype=float)
        v = v[np.isfinite(v)]
        out[k + "_mean"] = float(v.mean()) if len(v) else None
        out[k + "_median"] = float(np.median(v)) if len(v) else None
    for k in ("k_exact", "deg_seq_match", "connected", "is_tree", "ok_025w"):
        out[k + "_rate"] = float(np.mean([r[k] for r in rows]))
    out["k_err_mean"] = float(np.mean([r["k_err"] for r in rows]))
    out["hausdorff_le_025w_rate"] = float(np.mean([r["hausdorff_over_w"] <= TOL_W for r in rows]))
    return out


def p_table(synth_summary, real_rows, real_names, ood_real_ok=None):
    """P3/P4/P5 pass flags from measured summaries (thresholds from the proposal, section 3)."""
    p3 = (synth_summary["k_exact_rate"] >= 0.95 and synth_summary["deg_seq_match_rate"] >= 0.90
          and synth_summary["hausdorff_le_025w_rate"] >= 0.90)
    p4 = all(r["ok_025w"] for r in real_rows)
    return dict(P3=bool(p3), P4=bool(p4))


def save_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


def save_grid(path, samples, preds, titles=None, ncols=4):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(samples)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 3.2 * nrows), squeeze=False)
    for ax in axes.ravel():
        ax.axis("off")
    for k, (s, (pn, pe)) in enumerate(zip(samples, preds)):
        ax = axes.ravel()[k]
        p = np.vstack([s["profile"], s["profile"][:1]])
        ax.plot(p[:, 0], p[:, 1], "-", color="0.6", lw=1.2)
        for i, j in s["edges"]:
            ax.plot(s["nodes"][[i, j], 0], s["nodes"][[i, j], 1], "-", color="tab:green", lw=3, alpha=0.6)
        ax.plot(s["nodes"][:, 0], s["nodes"][:, 1], "o", color="tab:green", ms=8, alpha=0.6)
        for i, j in pe:
            ax.plot(pn[[i, j], 0], pn[[i, j], 1], "-", color="tab:red", lw=1.5)
        if len(pn):
            ax.plot(pn[:, 0], pn[:, 1], "x", color="tab:red", ms=7)
        ax.set_aspect("equal")
        ax.set_title(titles[k] if titles else s.get("shape", ""), fontsize=8)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=80)
    plt.close(fig)
