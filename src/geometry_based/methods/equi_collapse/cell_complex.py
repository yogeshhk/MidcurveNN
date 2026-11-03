"""Interior Delaunay cell complex of a polygon and its dual graph. Pure numpy/scipy.

Construction (see src/proposal/07_GDL_RESEARCH_REPORT.md, section 5):
  1. Remove collinear vertices and estimate the wall width as w_hat = 2 * area / perimeter.
  2. Sample every wall uniformly at step h = h_ratio * w_hat.
  3. Delaunay-triangulate the samples and keep the triangles inside the polygon.
  4. Merge neighbouring triangles with the same circumcentre into one cell, so cocircular points give a
     canonical cell rather than an arbitrary diagonal.

For a simple polygon whose boundary samples all appear as Delaunay edges ("conforming"), every sample lies on the
boundary, so the dual graph is a tree. Conformity is checked per sample, not guaranteed. Polygons with holes are not
supported here: common/geom.py handles one ring only.
"""
import collections

import numpy as np
from scipy.spatial import Delaunay

from common import geom

MAX_SAMPLES = 2000  # guards against a tiny w_hat on very rough boundaries


def width_estimate(poly):
    """w_hat = 2 A / P. Invariant under E(2), scales with the shape, unchanged by collinear vertices."""
    return 2.0 * abs(geom.signed_area(poly)) / max(float(geom.edge_lengths(poly).sum()), 1e-30)


def boundary_samples(poly, h):
    pts = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        m = max(int(np.ceil(np.linalg.norm(b - a) / h - 1e-9)), 1)
        for k in range(m):
            pts.append(a + (b - a) * (k / m))
    return np.asarray(pts)


def _circumcentres(A, B, C):
    ax, ay, bx, by, cx, cy = A[:, 0], A[:, 1], B[:, 0], B[:, 1], C[:, 0], C[:, 1]
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return np.stack([ux, uy], 1)


def build_complex(profile, h_ratio=0.5, merge_tol=1e-6):
    """Returns a dict describing the complex. Keys: S, tris, tcell, ncell, wh, adj, x, radii, area, n_tris, n_boundary,
    max_chord, chords, emap, conforming, poly."""
    poly = geom.ensure_ccw(geom.remove_collinear(np.asarray(profile, dtype=float)))
    wh = width_estimate(poly)
    per = float(geom.edge_lengths(poly).sum())
    h = max(h_ratio * wh, per / MAX_SAMPLES)
    S = boundary_samples(poly, h)
    T = Delaunay(S).simplices
    A, B, C = S[T[:, 0]], S[T[:, 1]], S[T[:, 2]]
    ar = 0.5 * np.abs((B - A)[:, 0] * (C - A)[:, 1] - (B - A)[:, 1] * (C - A)[:, 0])
    keep = geom.point_in_polygon((A + B + C) / 3, poly, 0.0) & (ar > 1e-9 * wh * wh)
    if not keep.any():
        keep = ar == ar.max()
    tris, ar = T[keep], ar[keep]
    A, B, C = S[tris[:, 0]], S[tris[:, 1]], S[tris[:, 2]]
    cc = _circumcentres(A, B, C)

    emap = collections.defaultdict(list)
    for i, t in enumerate(tris):
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            emap[(int(min(u, v)), int(max(u, v)))].append(i)
    n = len(S)
    conforming = all((min(i, (i + 1) % n), max(i, (i + 1) % n)) in emap
                     and len(emap[(min(i, (i + 1) % n), max(i, (i + 1) % n))]) == 1 for i in range(n))

    par = list(range(len(tris)))

    def find(u):
        while par[u] != u:
            par[u] = par[par[u]]
            u = par[u]
        return u

    for ts in emap.values():
        if len(ts) == 2 and np.linalg.norm(cc[ts[0]] - cc[ts[1]]) < merge_tol * wh:
            par[find(ts[0])] = find(ts[1])
    roots = sorted({find(i) for i in range(len(tris))})
    cid = {r: k for k, r in enumerate(roots)}
    tcell = np.array([cid[find(i)] for i in range(len(tris))])
    ncell = len(roots)

    area, n_tris = np.zeros(ncell), np.zeros(ncell)
    x = np.zeros((ncell, 2))
    radii = np.zeros(ncell)
    np.add.at(area, tcell, ar)
    np.add.at(n_tris, tcell, 1)
    np.add.at(x, tcell, ((A + B + C) / 3) * ar[:, None])
    x /= area[:, None]
    radii[tcell] = np.linalg.norm(cc - A, axis=1)

    adj = [set() for _ in range(ncell)]
    n_boundary, max_chord = np.zeros(ncell), np.zeros(ncell)
    chords = []
    for e, ts in emap.items():
        if len(ts) == 1:
            n_boundary[tcell[ts[0]]] += 1
        elif len(ts) == 2 and tcell[ts[0]] != tcell[ts[1]]:
            a, b = int(tcell[ts[0]]), int(tcell[ts[1]])
            L = float(np.linalg.norm(S[e[0]] - S[e[1]]))
            adj[a].add(b)
            adj[b].add(a)
            max_chord[a] = max(max_chord[a], L)
            max_chord[b] = max(max_chord[b], L)
            chords.append((a, b, L))
    return dict(poly=poly, S=S, tris=tris, tcell=tcell, ncell=ncell, wh=wh, h=h, adj=adj, x=x, radii=radii, area=area,
                n_tris=n_tris, n_boundary=n_boundary, max_chord=max_chord, chords=chords, emap=emap,
                conforming=conforming)


def is_tree(cx):
    n = cx["ncell"]
    edges = sum(len(v) for v in cx["adj"]) // 2
    seen, st = {0}, [0]
    while st:
        for v in cx["adj"][st.pop()]:
            if v not in seen:
                seen.add(v)
                st.append(v)
    return len(seen) == n and edges == n - 1


FEAT_DIM = 8


def features(cx):
    """Per-cell invariant features and per-chord edge lists. All lengths are divided by w_hat."""
    wh = cx["wh"]
    r = cx["radii"] / wh
    deg = np.array([len(v) for v in cx["adj"]], dtype=float)
    mc = cx["max_chord"] / wh
    f = np.stack([np.minimum(r, 5.0), np.log(r + 1e-3), np.log1p(cx["n_tris"]), deg / 4.0, cx["n_boundary"] / 4.0,
                  np.minimum(cx["area"] / wh ** 2, 20.0), np.minimum(mc, 5.0), mc / (2 * np.minimum(r, 50.0) + 1e-6)], 1)
    ei, ej, ef = [], [], []
    for a, b, L in cx["chords"]:
        ei += [a, b]
        ej += [b, a]
        ef += [L / wh, L / wh]
    return (f.astype(np.float32), np.array(ei, dtype=np.int64), np.array(ej, dtype=np.int64),
            np.array(ef, dtype=np.float32).reshape(-1, 1))


def labels(cx, nodes):
    """key[c] = 1 if cell c contains a ground-truth node (all cells touching it, so ties stay symmetric).
    target[c] = (node - cell centroid) / w_hat."""
    S, tris, tc, wh, x = cx["S"], cx["tris"], cx["tcell"], cx["wh"], cx["x"]
    A, B, C = S[tris[:, 0]], S[tris[:, 1]], S[tris[:, 2]]

    def cr(u, v):
        return u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]

    key = np.zeros(cx["ncell"], dtype=np.float32)
    tgt = np.zeros((cx["ncell"], 2), dtype=np.float32)
    best = np.full(cx["ncell"], np.inf)
    tol = 1e-7 * wh * wh
    for p in np.asarray(nodes, dtype=float).reshape(-1, 2):
        d1, d2, d3 = cr(B - A, p - A), cr(C - B, p - B), cr(A - C, p - C)
        hit = np.nonzero(((d1 >= -tol) & (d2 >= -tol) & (d3 >= -tol)) | ((d1 <= tol) & (d2 <= tol) & (d3 <= tol)))[0]
        if len(hit) == 0:
            hit = [int(np.argmin(np.linalg.norm((A + B + C) / 3 - p, axis=1)))]
        for c in {int(tc[h]) for h in hit}:
            dist = float(np.linalg.norm(x[c] - p))
            if dist < best[c]:
                best[c] = dist
                key[c] = 1.0
                tgt[c] = (p - x[c]) / wh
    return key, tgt


def decode(cx, prob, pos, thr=0.5):
    """Key cells -> contract connected groups -> prune non-key leaves -> smooth non-key degree-2 cells.

    Any scores give a graph obtained from the dual graph by contraction and pendant removal, so a dual tree gives a tree
    (for any network weights). A non-key cell that remains a junction is kept, at its centroid. Returns (nodes, edges).
    """
    n, adj = cx["ncell"], cx["adj"]
    key = np.asarray(prob) > thr
    if not key.any():
        key[int(np.argmax(prob))] = True
    par = list(range(n))

    def find(u):
        while par[u] != u:
            par[u] = par[par[u]]
            u = par[u]
        return u

    for u in range(n):
        if key[u]:
            for v in adj[u]:
                if key[v]:
                    par[find(u)] = find(v)
    g = collections.defaultdict(set)
    for u in range(n):
        g[find(u)]
        for v in adj[u]:
            a, b = find(u), find(v)
            if a != b:
                g[a].add(b)
                g[b].add(a)
    iskey = {find(u): False for u in range(n)}
    for u in range(n):
        if key[u]:
            iskey[find(u)] = True
    changed = True
    while changed:
        changed = False
        for u in list(g):
            if not iskey[u] and len(g[u]) <= 1:
                for v in g[u]:
                    g[v].discard(u)
                del g[u]
                changed = True
    for u in list(g):
        if not iskey[u] and len(g[u]) == 2:
            a, b = tuple(g[u])
            if b not in g[a]:
                g[a].discard(u)
                g[b].discard(u)
                g[a].add(b)
                g[b].add(a)
                del g[u]
    ids = sorted(g)
    idx = {u: i for i, u in enumerate(ids)}
    pts, wt = np.zeros((len(ids), 2)), np.zeros(len(ids))
    for u in range(n):
        r = find(u)
        if key[u] and r in idx:
            w = max(float(prob[u]), 1e-3)
            pts[idx[r]] += w * pos[u]
            wt[idx[r]] += w
    for u in ids:
        if wt[idx[u]] == 0:
            pts[idx[u]] = cx["x"][u]
            wt[idx[u]] = 1.0
    pts /= wt[:, None]
    edges = sorted({(min(idx[u], idx[v]), max(idx[u], idx[v])) for u in g for v in g[u]})
    return pts, edges
