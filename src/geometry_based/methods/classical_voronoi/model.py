"""Classical (no learning) midcurve baseline: Voronoi of the densified boundary.

Pipeline (see 03_graph_based_proposal.md, rung 0):
  1. densify the profile boundary (step = w/8; w = shortest profile edge unless a hint is given)
  2. scipy.spatial.Voronoi, keep finite ridges whose both endpoints are inside the polygon
  3. prune leaf branches shorter than 1.5 * local half-width (removes corner spurs)
  4. merge close junction vertices, split into chains between leaves/junctions
  5. per chain: Douglas-Peucker (tol 0.15 w) for bends, then re-fit every straight piece by least
     squares (ignoring the noisy 0.8 w near bends/junctions) and snap bends/junctions to the
     intersection of the fitted lines; extend leaves along the last piece to the profile boundary
     (leaf = end-cap midpoint, the repo convention).
Caveat: the snapping stage assumes piecewise-straight arms (true for the rectilinear thin shapes this
track covers); for curved profiles it degrades to the DP polyline. The residual against the hand-made
.mid files is reported as the "classical floor"; the algorithm was not tuned to hit a number.
"""
import numpy as np
from scipy.spatial import Voronoi

from common import geom


class ClassicalModel:
    name = "classical"

    def __init__(self, cfg=None):
        self.cfg = cfg

    def predict(self, sample):
        return classical_midcurve(sample["profile"], w_hint=None)


def build_model(cfg):
    return ClassicalModel(cfg)


def make_predictor(model, cfg=None):
    return model.predict


# ----------------------------------------------------------------------------- helpers
def _boundary_samples(poly, step):
    pts = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        L = np.linalg.norm(b - a)
        m = max(int(np.ceil(L / step)), 1)
        for k in range(m):
            pts.append(a + (b - a) * (k / m))
    return np.asarray(pts)


def _dp(pts, tol):
    """Indices kept by Douglas-Peucker on an open polyline."""
    keep = {0, len(pts) - 1}
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        d = b - a
        L = np.linalg.norm(d)
        seg = pts[i + 1:j]
        if L < 1e-12:
            dist = np.linalg.norm(seg - a, axis=1)
        else:
            dist = np.abs((seg[:, 0] - a[0]) * d[1] - (seg[:, 1] - a[1]) * d[0]) / L
        k = int(np.argmax(dist))
        if dist[k] > tol:
            m = i + 1 + k
            keep.add(m)
            stack.append((i, m))
            stack.append((m, j))
    return sorted(keep)


def _fit_line(pts):
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c)
    return c, vt[0]


def _line_intersection(p1, d1, p2, d2):
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) < 0.3:  # unit directions: |sin(angle)| < 0.3 -> nearly parallel
        return None
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return p1 + t * d1


def classical_midcurve(profile, w_hint=None):
    poly = geom.ensure_ccw(np.asarray(profile, dtype=float))
    w = float(w_hint) if w_hint else float(geom.edge_lengths(poly).min())
    step = w / 8.0
    sites = _boundary_samples(poly, step)
    vor = Voronoi(sites)
    V = vor.vertices
    inside = geom.point_in_polygon(V, poly, eps=0.0) & (geom.dist_to_boundary(V, poly) > 0.05 * step)
    adj = {}
    for a, b in vor.ridge_vertices:
        if a < 0 or b < 0 or a == b or not (inside[a] and inside[b]):
            continue
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    if not adj:
        c = poly.mean(0)
        return c[None], []
    # largest connected component by vertex count
    seen, comps = set(), []
    for s in adj:
        if s in seen:
            continue
        comp, st = [], [s]
        seen.add(s)
        while st:
            u = st.pop()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    st.append(v)
        comps.append(comp)
    main = set(max(comps, key=len))
    adj = {u: {v for v in nb if v in main} for u, nb in adj.items() if u in main}
    clear = {u: float(geom.dist_to_boundary(V[u][None], poly)[0]) for u in adj}

    def plen(path):
        return sum(float(np.linalg.norm(V[path[i]] - V[path[i + 1]])) for i in range(len(path) - 1))

    # 3. prune spurs
    for _ in range(60):
        removed = False
        to_remove = []
        for leaf in [u for u in adj if len(adj[u]) == 1]:
            path, prev, cur = [leaf], None, leaf
            while True:
                nxt = [v for v in adj[cur] if v != prev]
                if len(adj[cur]) >= 3 and cur != leaf:
                    break
                if not nxt:
                    cur = None
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            if cur is None:
                continue  # plain path without junction: keep
            if plen(path) < 1.5 * clear[cur]:
                to_remove.extend(path[:-1])  # decided on the pre-pass degrees, removed together
        for u in set(to_remove):
            for v in list(adj.get(u, ())):
                adj[v].discard(u)
            adj.pop(u, None)
            removed = True
        if not removed:
            break
    adj = {u: nb for u, nb in adj.items() if nb}
    if not adj:
        c = poly.mean(0)
        return c[None], []

    # 4. merge close junction vertices (deg >= 3) into clusters
    junc = [u for u in adj if len(adj[u]) >= 3]
    parent = {u: u for u in junc}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    for i, u in enumerate(junc):
        for v in junc[i + 1:]:
            if np.linalg.norm(V[u] - V[v]) < 1.0 * max(clear[u], clear[v]):
                parent[find(u)] = find(v)
    clusters = {}
    for u in junc:
        clusters.setdefault(find(u), []).append(u)
    rep_of = {}
    pos = {}
    for r, members in clusters.items():
        for m in members:
            rep_of[m] = r
        pos[r] = V[members].mean(0)
    # new graph over representative ids
    g = {}

    def rid(u):
        return rep_of.get(u, u)

    for u, nb in adj.items():
        for v in nb:
            a, b = rid(u), rid(v)
            if a != b:
                g.setdefault(a, set()).add(b)
                g.setdefault(b, set()).add(a)
    for u in g:
        pos.setdefault(u, V[u])
    keys = [u for u in g if len(g[u]) != 2]
    if not keys:  # closed loop (not expected for hole-free shapes)
        keys = [next(iter(g))]
    keyset = set(keys)

    # 5. chains
    chains, used = [], set()
    for a in keys:
        for nb in g[a]:
            if (a, nb) in used:
                continue
            path = [a, nb]
            prev, cur = a, nb
            while cur not in keyset:
                nxt = [v for v in g[cur] if v != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            used.add((a, path[1]))
            used.add((path[-1], path[-2]))
            chains.append(path)

    key_idx = {u: i for i, u in enumerate(keys)}
    key_pos = {u: pos[u].copy() for u in keys}
    chain_data = []  # (ka, kb, polyline points, kept indices, fitted lines per piece)
    end_lines = {u: [] for u in keys}  # lines incident to each key node
    for path in chains:
        P = np.array([pos[u] for u in path])
        s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
        kept = _dp(P, 0.15 * w)
        lines = []
        for t in range(len(kept) - 1):
            i0, i1 = kept[t], kept[t + 1]
            lo = s[i0] + (0.8 * w)
            hi = s[i1] - (0.8 * w)
            sel = P[i0:i1 + 1][(s[i0:i1 + 1] >= lo) & (s[i0:i1 + 1] <= hi)]
            if len(sel) < 2:
                sel = P[i0:i1 + 1]
            if len(sel) < 2:
                sel = np.vstack([P[i0], P[i1]])
            c, d = _fit_line(sel)
            # orient d from i0 towards i1
            if (P[i1] - P[i0]) @ d < 0:
                d = -d
            lines.append((c, d))
        chain_data.append((path[0], path[-1], P, kept, lines))
        if len(lines) >= 1:
            end_lines[path[0]].append(lines[0])
            end_lines[path[-1]].append(lines[-1])

    # junction refinement: least-squares intersection of incident fitted lines
    for u in keys:
        if len(g[u]) >= 3:
            A = np.zeros((2, 2))
            b = np.zeros(2)
            for c, d in end_lines[u]:
                M = np.eye(2) - np.outer(d, d)
                A += M
                b += M @ c
            if np.linalg.det(A) > 1e-6:
                x = np.linalg.solve(A, b)
                if np.linalg.norm(x - key_pos[u]) < 1.0 * w:
                    key_pos[u] = x

    nodes = [key_pos[u] for u in keys]
    edges = []
    for ka, kb, P, kept, lines in chain_data:
        seq = [key_idx[ka]]
        for t in range(1, len(kept) - 1):
            # bend between piece t-1 and t
            bend = None
            if len(lines) >= 2:
                bend = _line_intersection(lines[t - 1][0], lines[t - 1][1], lines[t][0], lines[t][1])
            if bend is None or np.linalg.norm(bend - P[kept[t]]) > 1.5 * w:
                bend = P[kept[t]]
            nodes.append(np.asarray(bend))
            seq.append(len(nodes) - 1)
        seq.append(key_idx[kb])
        for a, b in zip(seq[:-1], seq[1:]):
            if a != b:
                edges.append((min(a, b), max(a, b)))
    edges = sorted(set(edges))

    # leaves: extend along the last piece to the profile boundary
    deg = geom.degrees(len(nodes), edges)
    for ka, kb, P, kept, lines in chain_data:
        for end, ku in ((0, ka), (1, kb)):
            if len(g[ku]) != 1:
                continue
            c, d = lines[0] if end == 0 else lines[-1]
            out_dir = -d if end == 0 else d
            leaf = key_pos[ku]
            o = c + ((leaf - c) @ d) * d
            t = geom.ray_hit(o, out_dir, poly)
            if t is not None and t < 3.0 * w:
                nodes[key_idx[ku]] = o + t * out_dir / np.linalg.norm(out_dir)
    nodes = np.asarray(nodes, dtype=float).reshape(-1, 2)
    # drop duplicate/very close nodes (can arise from snapped bends)
    return nodes, edges
