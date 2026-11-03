"""Raw data -> graph dataset, plus the procedural generator for synthetic (profile, midcurve) pairs.

Gold data (the 4 hand-made shapes) is converted to data/dataset_v1.json:
  profile nodes + ring edges (including the closing edge last->first), midcurve nodes + edges
  (from <Shape>.edges), shape name, split roles (from src/data/raw/splits.json), wall width w.
Synthetic data is NEVER written in bulk: make_dataset(n, seed, ...) regenerates it from a seed.
Only a 20-sample preview is written to data/synthetic_sample_v1.json.

Generator convention (matches the hand-made files exactly, see tests P2):
  random lattice tree -> merge collinear degree-2 nodes -> optional jitter of column/row gaps
  -> union of flat-capped boxes of width w around every skeleton edge; each box is extended by
  w/2 at endpoints of degree >= 2 (fills bends/junctions) and not at leaves (leaf = end-cap midpoint).
"""
import json
import os

import numpy as np

from common import geom
from common.geom import Rejected

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # geometry_based/ (this file is in common/)
RAW = os.path.normpath(os.path.join(HERE, "..", "data", "raw"))
DATA_DIR = os.path.join(HERE, "data")
DATASET_PATH = os.path.join(DATA_DIR, "dataset_v1.json")
SAMPLE_PATH = os.path.join(DATA_DIR, "synthetic_sample_v1.json")
NMAX = 40  # max profile vertices the models accept

REAL_SPECS = {
    "I": dict(nodes=[(7.5, 5.0), (7.5, 20.0)], edges=[(0, 1)], w=5.0),
    "L": dict(nodes=[(7.5, 5.0), (7.5, 32.5), (35.0, 32.5)], edges=[(0, 1), (1, 2)], w=5.0),
    "T": dict(nodes=[(12.5, 0.0), (12.5, 22.5), (25.0, 22.5), (0.0, 22.5)],
              edges=[(0, 1), (1, 2), (1, 3)], w=5.0),
    "Plus": dict(nodes=[(12.5, 0.0), (12.5, 22.5), (12.5, 45.0), (0.0, 22.5), (25.0, 22.5)],
                 edges=[(0, 1), (1, 2), (1, 3), (1, 4)], w=5.0),
}
SHAPES = ["I", "L", "T", "Plus"]
GEN_STATS = {"attempted": 0, "accepted": 0}


# ----------------------------------------------------------------------------- generator
def from_skeleton(nodes, edges, w, min_sep=1.5):
    """Axis-aligned skeleton -> profile polygon (CCW, collinear vertices removed)."""
    nodes = np.asarray(nodes, dtype=float)
    deg = geom.degrees(len(nodes), edges)
    boxes = []
    for i, j in edges:
        a, b = nodes[i], nodes[j]
        d = b - a
        L = np.linalg.norm(d)
        if L < 1e-9 or (abs(d[0]) > 1e-9 and abs(d[1]) > 1e-9):
            raise Rejected("edge not axis aligned")
        u = d / L
        a2 = a - u * (w / 2.0 if deg[i] >= 2 else 0.0)
        b2 = b + u * (w / 2.0 if deg[j] >= 2 else 0.0)
        p = np.array([-u[1], u[0]]) * (w / 2.0)
        xs = [a2[0] + p[0], a2[0] - p[0], b2[0] + p[0], b2[0] - p[0]]
        ys = [a2[1] + p[1], a2[1] - p[1], b2[1] + p[1], b2[1] - p[1]]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    # reject strips that nearly touch (non-adjacent edges closer than min_sep * w)
    for e in range(len(edges)):
        for f in range(e + 1, len(edges)):
            if set(edges[e]) & set(edges[f]):
                continue
            d = geom.seg_seg_distance(nodes[edges[e][0]], nodes[edges[e][1]],
                                      nodes[edges[f][0]], nodes[edges[f][1]])
            if d < min_sep * w:
                raise Rejected("strips too close")
    profile = geom.union_of_boxes(boxes)
    return dict(profile=profile, nodes=nodes.copy(), edges=sorted((min(e), max(e)) for e in edges), w=float(w))


_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def sample_skeleton(rng, n_edges, allow_deg4=True, jitter=True, gap_range=(0.7, 2.0)):
    """Random lattice tree -> (nodes[K,2], edges) with collinear degree-2 nodes merged."""
    maxdeg = 4 if allow_deg4 else 3
    adj = {(0, 0): set()}
    for _ in range(n_edges):
        cands = []
        for u in adj:
            if len(adj[u]) >= maxdeg:
                continue
            for dx, dy in _DIRS:
                v = (u[0] + dx, u[1] + dy)
                if v in adj:
                    continue
                nb = sum(1 for ex, ey in _DIRS if (v[0] + ex, v[1] + ey) in adj)
                if nb == 1:
                    cands.append((u, v))
        if not cands:
            break
        u, v = cands[int(rng.integers(len(cands)))]
        adj[v] = {u}
        adj[u].add(v)
    # merge collinear degree-2 nodes
    changed = True
    while changed:
        changed = False
        for u in list(adj):
            if len(adj[u]) == 2:
                a, b = sorted(adj[u])
                va, vb = (a[0] - u[0], a[1] - u[1]), (b[0] - u[0], b[1] - u[1])
                # collinear: parallel (zero cross product) and pointing opposite ways; integer lattice, so exact
                if va[0] * vb[1] - va[1] * vb[0] == 0 and va[0] * vb[0] + va[1] * vb[1] < 0:
                    adj[a].discard(u)
                    adj[b].discard(u)
                    adj[a].add(b)
                    adj[b].add(a)
                    del adj[u]
                    changed = True
                    break
    cols = sorted({u[0] for u in adj})
    rows = sorted({u[1] for u in adj})

    def coords(vals):
        lo, hi = min(vals), max(vals)
        pos = {lo: 0.0}
        for c in range(lo + 1, hi + 1):
            g = float(rng.uniform(*gap_range)) if jitter else 1.0
            pos[c] = pos[c - 1] + g
        return pos

    px, py = coords(cols), coords(rows)
    keys = sorted(adj)
    idx = {k: n for n, k in enumerate(keys)}
    nodes = np.array([[px[k[0]], py[k[1]]] for k in keys], dtype=float)
    edges = sorted({(min(idx[u], idx[v]), max(idx[u], idx[v])) for u in adj for v in adj[u]})
    return nodes, edges


def make_sample(rng, min_edges=1, max_edges=7, allow_deg4=True, jitter=True):
    """Loop until a valid sample is produced. Returns the sample dict (see from_skeleton) + meta."""
    while True:
        GEN_STATS["attempted"] += 1
        n_lat = int(rng.integers(min_edges, max_edges + 1))
        nodes, edges = sample_skeleton(rng, n_lat, allow_deg4, jitter)
        if len(edges) < 1:
            continue
        w = float(rng.uniform(0.25, 0.6))
        try:
            s = from_skeleton(nodes, edges, w)
        except Rejected:
            continue
        if len(s["profile"]) > NMAX or len(nodes) > 12:
            continue
        deg = geom.degrees(len(nodes), s["edges"])
        s["deg_max"] = int(deg.max())
        s["n_lat_edges"] = n_lat
        s["shape"] = "synthetic"
        GEN_STATS["accepted"] += 1
        return s


def make_dataset(n, seed, **kw):
    rng = np.random.default_rng(seed)
    return [make_sample(rng, **kw) for _ in range(n)]


# ----------------------------------------------------------------------------- gold shapes
def load_splits():
    with open(os.path.join(RAW, "splits.json"), "r") as f:
        return json.load(f)


def load_gold():
    """The 4 real shapes as sample dicts (profile as listed in .dat, midcurve nodes/edges)."""
    out = []
    for name in SHAPES:
        prof = geom.read_pts(os.path.join(RAW, name + ".dat"))
        nodes = geom.read_pts(os.path.join(RAW, name + ".mid"))
        edges = geom.read_edges(os.path.join(RAW, name + ".edges"))
        w = float(geom.edge_lengths(prof).min())
        deg = geom.degrees(len(nodes), edges)
        out.append(dict(profile=prof, nodes=nodes, edges=edges, w=w, shape=name, deg_max=int(deg.max()),
                        n_lat_edges=len(edges)))
    return out


def _to_json(s, extra=None):
    n = len(s["profile"])
    d = dict(
        shape=s.get("shape", "synthetic"),
        profile_nodes=np.asarray(s["profile"]).tolist(),
        profile_edges=[[i, (i + 1) % n] for i in range(n)],  # ring incl. closing edge
        midcurve_nodes=np.asarray(s["nodes"]).tolist(),
        midcurve_edges=[list(e) for e in s["edges"]],
        w=s["w"],
    )
    if extra:
        d.update(extra)
    return d


def prepare(verbose=True):
    os.makedirs(DATA_DIR, exist_ok=True)
    splits = load_splits()
    gold = load_gold()
    entries = []
    for s in gold:
        roles = dict(
            default=next((r for r in ("train", "val", "test") if s["shape"] in splits["default"][r]), None),
            pose="train/val/test",
            role_in_graph_track="real4 (evaluation only, never trained on)",
        )
        entries.append(_to_json(s, dict(split=roles)))
    meta = dict(version=1, source="src/data/raw/{I,L,T,Plus}.dat/.mid/.edges + splits.json",
                note="Gold shapes only. Synthetic data is generated on the fly from a seed "
                     "(prepare_data.make_dataset); a 20-sample preview is in synthetic_sample_v1.json.",
                shapes=entries)
    with open(DATASET_PATH, "w") as f:
        json.dump(meta, f, indent=1)
    GEN_STATS.update(attempted=0, accepted=0)
    preview = make_dataset(20, seed=splits.get("seeds", {}).get("train", 0))
    with open(SAMPLE_PATH, "w") as f:
        json.dump(dict(version=1, seed=0, samples=[_to_json(s, dict(deg_max=s["deg_max"])) for s in preview]),
                  f, indent=1)
    if verbose:
        print("wrote", DATASET_PATH, os.path.getsize(DATASET_PATH), "bytes")
        print("wrote", SAMPLE_PATH, os.path.getsize(SAMPLE_PATH), "bytes")
    return DATASET_PATH


if __name__ == "__main__":
    prepare()
