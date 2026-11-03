"""
evaluate.py -- the ONE evaluation for every text-track model.

Predictions are decoded, mapped back to the ORIGINAL (raw) pose and scored there, so Chamfer and
Hausdorff are in raw units (comparable with the other tracks). Distances are computed on points
sampled along the EDGES (not just the vertices). There is no combined score and no floor.

Per-example metrics
  parse_strict / parse_ok   strict decoder passed / lenient decoder produced a valid graph
  chamfer, hausdorff        raw units, edge-sampled (step = 1% of the profile bbox diagonal)
  chamfer_n, hausdorff_n    same, divided by the profile bbox diagonal
  edge_f1                   edge matches when both endpoints are within 2% of the diagonal
  graph_exact               same node count, edge count, sorted degree sequence, component count
  branch_acc                same number of degree>=3 vertices, all within tolerance
  exact_match               decoded graph re-encodes to the gold text
  wrong_but_valid           parse_ok and not graph_exact
Baselines: 'empty' (no prediction) and 'nearest_train_copy' (copy the midcurve of the closest
training profile). Unparsed outputs count as 0 for rates and are excluded from distance means; a
separate chamfer_pen column charges them the profile diagonal.
"""
import json
import math
import os
import time

import numpy as np

from text_based.common import canonical, dataset, formats, prompts, recipes
from text_based.common.formats import Graph
from text_based.methods import ServerUnavailable

STEP_FRAC = 0.01
TOL_FRAC = 0.02


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------

def diag_of(profile):
    P = np.asarray(profile, dtype=float)
    return float(np.linalg.norm(P.max(axis=0) - P.min(axis=0)))


def sample_polyline(points, edges, step):
    P = np.asarray(points, dtype=float)
    out, used = [], set()
    for a, b in edges:
        p, q = P[a], P[b]
        k = max(1, int(math.ceil(float(np.linalg.norm(q - p)) / step)))
        t = np.linspace(0.0, 1.0, k + 1)[:, None]
        out.append(p + (q - p) * t)
        used.update((a, b))
    for i in range(len(P)):
        if i not in used:
            out.append(P[i:i + 1])
    return np.vstack(out)


def _nn(A, B):
    D = np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2)
    return D.min(axis=1), D.min(axis=0)


def chamfer_hausdorff(pred, gt, step):
    A = sample_polyline(pred.points, pred.edges, step)
    B = sample_polyline(gt.points, gt.edges, step)
    ab, ba = _nn(A, B)
    return 0.5 * (float(ab.mean()) + float(ba.mean())), float(max(ab.max(), ba.max()))


def edge_f1(pred, gt, tol):
    if not pred.edges and not gt.edges:
        return 1.0
    if not pred.edges or not gt.edges:
        return 0.0
    used, tp = set(), 0
    for a, b in pred.edges:
        pa, pb = pred.points[a], pred.points[b]
        for k, (c, d) in enumerate(gt.edges):
            if k in used:
                continue
            ga, gb = gt.points[c], gt.points[d]
            d1 = max(np.linalg.norm(pa - ga), np.linalg.norm(pb - gb))
            d2 = max(np.linalg.norm(pa - gb), np.linalg.norm(pb - ga))
            if min(d1, d2) <= tol:
                used.add(k)
                tp += 1
                break
    prec, rec = tp / len(pred.edges), tp / len(gt.edges)
    return 0.0 if tp == 0 else 2 * prec * rec / (prec + rec)


def _degrees(g):
    deg = [0] * len(g.points)
    for a, b in g.edges:
        deg[a] += 1
        deg[b] += 1
    return deg


def _components(g):
    parent = list(range(len(g.points)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in g.edges:
        parent[find(a)] = find(b)
    return len({find(i) for i in range(len(g.points))})


def graph_exact(pred, gt):
    return (len(pred.points) == len(gt.points) and len(pred.edges) == len(gt.edges)
            and sorted(_degrees(pred)) == sorted(_degrees(gt)) and _components(pred) == _components(gt))


def branch_acc(pred, gt, tol):
    pj = [pred.points[i] for i, d in enumerate(_degrees(pred)) if d >= 3]
    gj = [gt.points[i] for i, d in enumerate(_degrees(gt)) if d >= 3]
    if len(pj) != len(gj):
        return False
    free = list(range(len(gj)))
    for p in pj:
        hit = [k for k in free if np.linalg.norm(p - gj[k]) <= tol]
        if not hit:
            return False
        free.remove(hit[0])
    return True


def bootstrap_ci(values, n=1000, seed=0):
    v = np.asarray([x for x in values if x is not None and np.isfinite(x)], dtype=float)
    if len(v) == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = [rng.choice(v, size=len(v), replace=True).mean() for _ in range(n)]
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------

def gt_raw_graph(row):
    P, M, E = dataset.view(row, "raw")
    return Graph(M, E), P


def score_graph(pred, row):
    """Metrics of a predicted Graph (raw pose) or None against the gold of `row`."""
    gt, profile = gt_raw_graph(row)
    diag = diag_of(profile)
    rec = dict(parse_ok=pred is not None)
    if pred is None:
        rec.update(chamfer=None, hausdorff=None, chamfer_n=None, hausdorff_n=None, chamfer_pen=diag,
                   chamfer_pen_n=1.0, edge_f1=0.0, graph_exact=False, branch_acc=False,
                   wrong_but_valid=False)
        return rec
    c, h = chamfer_hausdorff(pred, gt, STEP_FRAC * diag)
    ge = graph_exact(pred, gt)
    rec.update(chamfer=c, hausdorff=h, chamfer_n=c / diag, hausdorff_n=h / diag, chamfer_pen=c,
               chamfer_pen_n=c / diag, edge_f1=edge_f1(pred, gt, TOL_FRAC * diag), graph_exact=ge,
               branch_acc=branch_acc(pred, gt, TOL_FRAC * diag), wrong_but_valid=not ge)
    return rec


def decode_to_raw(text, row, fmt, pose):
    """Decode model text to a Graph in raw pose. Returns (Graph|None, strict_ok, view_graph|None)."""
    codec = formats.get_codec(fmt)
    profile = dataset.view(row, pose)[0]
    try:
        g, strict = codec.decode_midcurve(text, profile)
    except Exception:
        return None, False, None
    if g is None:
        return None, False, None
    pts = canonical.decanonicalise(g.points, row["canon"]["transform"]) if pose == "canonical" else g.points
    return Graph(np.asarray(pts, dtype=float), g.edges), strict, g


def score_text(row, text, fmt, pose, gold_text=None):
    pred, strict, vg = decode_to_raw(text, row, fmt, pose)
    rec = score_graph(pred, row)
    rec["parse_strict"] = bool(strict)
    exact = False
    if vg is not None and gold_text is not None:
        try:
            profile = dataset.view(row, pose)[0]
            exact = formats.get_codec(fmt).encode_midcurve(vg.points, vg.edges, profile,
                                                           recipes.recipe_tol(pose)) == gold_text
        except Exception:
            exact = False
    rec["exact_match"] = bool(exact)
    return rec


# ---------------------------------------------------------------------------
# baselines
# ---------------------------------------------------------------------------

def nearest_train_copy(row, train_rows):
    """Copy the canonical midcurve of the closest training profile into this row's pose."""
    Q = np.asarray(row["canon"]["profile"], dtype=float)
    best, best_d = None, float("inf")
    for t in train_rows:
        T = np.asarray(t["canon"]["profile"], dtype=float)
        if len(T) == len(Q):
            d = float(np.abs(T - Q).mean())
        else:
            D = np.linalg.norm(Q[:, None, :] - T[None, :, :], axis=2)
            d = 1e6 + float(D.min(axis=1).mean() + D.min(axis=0).mean())
        if d < best_d:
            best, best_d = t, d
    if best is None:
        return None
    pts = canonical.decanonicalise(np.asarray(best["canon"]["midcurve"], dtype=float), row["canon"]["transform"])
    return Graph(pts, [tuple(e) for e in best["canon"]["edges"]])


def baseline_results(name, rows, train_rows):
    out = []
    for r in rows:
        pred = None if name == "empty" else nearest_train_copy(r, train_rows)
        rec = score_graph(pred, r)
        rec.update(parse_strict=pred is not None, exact_match=False, id=r["id"], shape=r["shape"])
        out.append(rec)
    return out


# ---------------------------------------------------------------------------
# running a model
# ---------------------------------------------------------------------------

def evaluate_rows(model, rows, fmt, pose, shots, style, pool, progress=True):
    st, fmt_r, pose_r = prompts.resolve(fmt, pose, style)
    results = []
    for k, row in enumerate(rows):
        shot_rows = prompts.select_shots(row, pool, shots)
        msgs, gold = prompts.build_messages(row, fmt, pose, shot_rows, style)
        err, text = None, ""
        t0 = time.time()
        try:
            text = model.generate(msgs)
        except ServerUnavailable:
            raise
        except Exception as exc:  # one bad item must not kill the run
            err = "%s: %s" % (type(exc).__name__, exc)
        rec = score_text(row, text, fmt_r, pose_r, gold)
        info = dict(getattr(model, "last_info", {}) or {})
        rec.update(id=row["id"], shape=row["shape"], style=style, format=fmt_r, pose=pose_r,
                   shots_requested=shots, shots_used=len(shot_rows), prompt_hash=prompts.prompt_hash(msgs),
                   messages=msgs, gold=gold, completion=text, error=err,
                   latency_s=info.get("latency_s", round(time.time() - t0, 3)),
                   finish_reason=info.get("finish_reason"), prompt_tokens=info.get("prompt_tokens"),
                   completion_tokens=info.get("completion_tokens"))
        results.append(rec)
        if progress:
            print("  [%d/%d] %-14s parse=%s strict=%s edge_f1=%.2f exact_graph=%s"
                  % (k + 1, len(rows), row["id"], rec["parse_ok"], rec["parse_strict"], rec["edge_f1"],
                     rec["graph_exact"]))
    return results


# ---------------------------------------------------------------------------
# summaries
# ---------------------------------------------------------------------------

def _mean(v):
    v = [x for x in v if x is not None]
    return float(np.mean(v)) if v else float("nan")


def _median(v):
    v = [x for x in v if x is not None]
    return float(np.median(v)) if v else float("nan")


def summarize(results):
    n = len(results)
    if n == 0:
        return dict(n=0)
    ci_f1 = bootstrap_ci([r["edge_f1"] for r in results])
    ci_c = bootstrap_ci([r["chamfer_n"] for r in results if r["chamfer_n"] is not None])
    return dict(
        n=n,
        parse_strict=_mean([float(r["parse_strict"]) for r in results]),
        parse_ok=_mean([float(r["parse_ok"]) for r in results]),
        chamfer_mean=_mean([r["chamfer"] for r in results]), chamfer_median=_median([r["chamfer"] for r in results]),
        hausdorff_mean=_mean([r["hausdorff"] for r in results]),
        hausdorff_median=_median([r["hausdorff"] for r in results]),
        chamfer_n_mean=_mean([r["chamfer_n"] for r in results]),
        chamfer_n_ci95=list(ci_c),
        chamfer_pen_n_mean=_mean([r["chamfer_pen_n"] for r in results]),
        edge_f1_mean=_mean([r["edge_f1"] for r in results]), edge_f1_ci95=list(ci_f1),
        graph_exact=_mean([float(r["graph_exact"]) for r in results]),
        branch_acc=_mean([float(r["branch_acc"]) for r in results]),
        exact_match=_mean([float(r["exact_match"]) for r in results]),
        wrong_but_valid=_mean([float(r["wrong_but_valid"]) for r in results]))


def summarize_by_shape(results):
    shapes = sorted({r["shape"] for r in results})
    return {s: summarize([r for r in results if r["shape"] == s]) for s in shapes}


def _f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else ("%.*f" % (d, x))


def summary_markdown(title, named, notes=()):
    """named: ordered dict name -> results list. Returns markdown text."""
    lines = ["# " + title, ""]
    for n in notes:
        lines.append(n)
    if notes:
        lines.append("")
    lines += ["## Overall", "",
              "| config | n | parse strict | parse ok | chamfer (raw) | hausdorff (raw) | chamfer_n | chamfer_pen_n | edge F1 | graph exact | branch acc | exact text | wrong but valid |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, res in named.items():
        s = summarize(res)
        if s["n"] == 0:
            continue
        lines.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            name, s["n"], _f(s["parse_strict"], 2), _f(s["parse_ok"], 2), _f(s["chamfer_mean"]),
            _f(s["hausdorff_mean"]), _f(s["chamfer_n_mean"]), _f(s["chamfer_pen_n_mean"]),
            _f(s["edge_f1_mean"], 2), _f(s["graph_exact"], 2), _f(s["branch_acc"], 2), _f(s["exact_match"], 2),
            _f(s["wrong_but_valid"], 2)))
    lines += ["", "chamfer / hausdorff: mean over parsed outputs only, raw units. chamfer_pen_n charges unparsed "
              "outputs the full profile diagonal. n is small (see caveats); read rates as counts.", "",
              "## Per shape (edge F1 / graph exact)", ""]
    shapes = sorted({r["shape"] for res in named.values() for r in res})
    lines.append("| config | " + " | ".join(shapes) + " |")
    lines.append("|---|" + "---|" * len(shapes))
    for name, res in named.items():
        cells = []
        for s in shapes:
            sub = [r for r in res if r["shape"] == s]
            if not sub:
                cells.append("-")
                continue
            cells.append("%s / %s" % (_f(_mean([r["edge_f1"] for r in sub]), 2),
                                      _f(_mean([float(r["graph_exact"]) for r in sub]), 2)))
        lines.append("| %s | %s |" % (name, " | ".join(cells)))
    return "\n".join(lines) + "\n"


def write_run(run_dir, config, named, title, notes=()):
    """Write raw.jsonl, metrics.json, summary.md into run_dir."""
    os.makedirs(run_dir, exist_ok=True)
    with open(os.path.join(run_dir, "raw.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
        for name, res in named.items():
            for r in res:
                fh.write(json.dumps(dict(config_name=name, **r)) + "\n")
    metrics = dict(config=config, overall={n: summarize(r) for n, r in named.items()},
                   by_shape={n: summarize_by_shape(r) for n, r in named.items()})
    with open(os.path.join(run_dir, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    with open(os.path.join(run_dir, "summary.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(summary_markdown(title, named, notes))
    return metrics
