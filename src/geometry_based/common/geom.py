"""Polygon helpers for the geometry track. Pure numpy/scipy (no shapely).

Conventions: a polygon is an (N,2) float array of vertices in order (no repeated closing vertex).
Edges of a graph are lists of (i, j) index pairs with i < j.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree


class Rejected(Exception):
    """Raised by the generator when a candidate skeleton gives an unusable profile."""


# ----------------------------------------------------------------------------- IO
def read_pts(path):
    rows = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                rows.append([float(parts[0]), float(parts[1])])
    return np.asarray(rows, dtype=float)


def read_edges(path):
    out = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2:
                i, j = int(parts[0]), int(parts[1])
                out.append((min(i, j), max(i, j)))
    return sorted(out)


# ----------------------------------------------------------------------------- polygon basics
def signed_area(poly):
    x, y = poly[:, 0], poly[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def ensure_ccw(poly):
    poly = np.asarray(poly, dtype=float)
    return poly if signed_area(poly) >= 0 else poly[::-1].copy()


def remove_collinear(poly, tol=1e-9):
    """Drop vertices whose cross product with their neighbours is ~0 (cyclic), repeat until stable."""
    pts = [tuple(p) for p in np.asarray(poly, dtype=float)]
    changed = True
    while changed and len(pts) > 3:
        changed = False
        n = len(pts)
        for i in range(n):
            a, b, c = np.array(pts[i - 1]), np.array(pts[i]), np.array(pts[(i + 1) % n])
            u, v = b - a, c - b
            cr = u[0] * v[1] - u[1] * v[0]
            scale = max(np.linalg.norm(u) * np.linalg.norm(v), 1e-30)
            if abs(cr) / scale < tol:
                del pts[i]
                changed = True
                break
    return np.asarray(pts, dtype=float)


def edge_lengths(poly):
    return np.linalg.norm(np.roll(poly, -1, axis=0) - poly, axis=1)


def dist_to_boundary(points, poly):
    """Min distance from each point (M,2) to the closed polygon boundary."""
    P = np.asarray(points, dtype=float).reshape(-1, 2)
    A = poly
    B = np.roll(poly, -1, axis=0)
    AB = B - A
    L2 = np.maximum((AB ** 2).sum(1), 1e-30)
    AP = P[:, None, :] - A[None, :, :]
    t = np.clip((AP * AB[None]).sum(2) / L2[None], 0.0, 1.0)
    proj = A[None] + t[..., None] * AB[None]
    d = np.linalg.norm(P[:, None, :] - proj, axis=2)
    return d.min(1)


def point_in_polygon(points, poly, eps=0.0):
    """True for points inside the polygon or within eps of its boundary."""
    P = np.asarray(points, dtype=float).reshape(-1, 2)
    x, y = P[:, 0][:, None], P[:, 1][:, None]
    px, py = poly[:, 0][None], poly[:, 1][None]
    qx, qy = np.roll(poly[:, 0], -1)[None], np.roll(poly[:, 1], -1)[None]
    cond = (py > y) != (qy > y)
    with np.errstate(divide="ignore", invalid="ignore"):
        xint = px + (y - py) * (qx - px) / (qy - py)
    cross = cond & (x < xint)
    inside = (cross.sum(1) % 2) == 1
    if eps > 0:
        inside = inside | (dist_to_boundary(P, poly) <= eps)
    return inside


def segment_inside(a, b, poly, eps=1e-9):
    """True if the closed segment a-b lies inside the closed polygon (tolerance eps)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    d = b - a
    dl = float(np.linalg.norm(d))
    if dl < 1e-12:
        return bool(point_in_polygon(a[None], poly, eps)[0])
    P = poly
    Q = np.roll(poly, -1, axis=0)
    E = Q - P
    denom = d[0] * E[:, 1] - d[1] * E[:, 0]
    ts = [0.0, 1.0]
    PA = P - a
    nonpar = np.abs(denom) > 1e-12 * dl * np.maximum(np.linalg.norm(E, axis=1), 1e-30)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (PA[:, 0] * E[:, 1] - PA[:, 1] * E[:, 0]) / denom
        s = (PA[:, 0] * d[1] - PA[:, 1] * d[0]) / denom
    ok = nonpar & (s >= -1e-9) & (s <= 1 + 1e-9) & (t > 0) & (t < 1)
    ts.extend(t[ok].tolist())
    # collinear / parallel overlap: add projections of polygon vertices lying on the line
    par = ~nonpar
    if par.any():
        for V in (P[par], Q[par]):
            cr = np.abs((V[:, 0] - a[0]) * d[1] - (V[:, 1] - a[1]) * d[0]) / dl
            on = cr <= max(eps, 1e-9)
            if on.any():
                tt = ((V[on] - a) @ d) / (dl * dl)
                tt = tt[(tt > 0) & (tt < 1)]
                ts.extend(tt.tolist())
    ts = np.unique(np.asarray(ts))
    gaps = ts[1:] - ts[:-1]
    mids = (ts[:-1] + ts[1:]) / 2.0
    mids = mids[gaps > 1e-9]
    pts = np.vstack([a[None], b[None], a[None] + mids[:, None] * d[None]])
    return bool(point_in_polygon(pts, poly, eps).all())


def seg_seg_distance(p1, p2, q1, q2):
    """Distance between two 2D segments."""
    p1, p2, q1, q2 = [np.asarray(v, dtype=float) for v in (p1, p2, q1, q2)]

    def pt_seg(p, a, b):
        ab = b - a
        l2 = float(ab @ ab)
        t = 0.0 if l2 < 1e-30 else float(np.clip((p - a) @ ab / l2, 0, 1))
        return float(np.linalg.norm(p - (a + t * ab)))

    d1 = p2 - p1
    d2 = q2 - q1
    den = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(den) > 1e-12:
        w = q1 - p1
        t = (w[0] * d2[1] - w[1] * d2[0]) / den
        s = (w[0] * d1[1] - w[1] * d1[0]) / den
        if 0 <= t <= 1 and 0 <= s <= 1:
            return 0.0
    return min(pt_seg(p1, q1, q2), pt_seg(p2, q1, q2), pt_seg(q1, p1, p2), pt_seg(q2, p1, p2))


def ray_hit(origin, direction, poly):
    """Smallest t>1e-9 where origin + t*direction meets the polygon boundary; None if no hit."""
    o = np.asarray(origin, dtype=float)
    d = np.asarray(direction, dtype=float)
    d = d / max(np.linalg.norm(d), 1e-30)
    P = poly
    E = np.roll(poly, -1, axis=0) - P
    denom = d[0] * E[:, 1] - d[1] * E[:, 0]
    PA = P - o
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (PA[:, 0] * E[:, 1] - PA[:, 1] * E[:, 0]) / denom
        s = (PA[:, 0] * d[1] - PA[:, 1] * d[0]) / denom
    ok = (np.abs(denom) > 1e-12) & (s >= -1e-9) & (s <= 1 + 1e-9) & (t > 1e-9)
    if not ok.any():
        return None
    return float(t[ok].min())


# ----------------------------------------------------------------------------- normalisation
def normalize(profile, nodes=None):
    """Centre on the bbox centre, scale by the max bbox half-side (isotropic).

    Returns (profile_n, nodes_n, centre, half_extent). nodes may be None.
    """
    profile = np.asarray(profile, dtype=float)
    lo, hi = profile.min(0), profile.max(0)
    centre = (lo + hi) / 2.0
    he = float(max((hi - lo).max() / 2.0, 1e-12))
    prof_n = (profile - centre) / he
    nodes_n = None if nodes is None else (np.asarray(nodes, dtype=float) - centre) / he
    return prof_n, nodes_n, centre, he


def denormalize(pts, centre, he):
    return np.asarray(pts, dtype=float) * he + np.asarray(centre, dtype=float)


# ----------------------------------------------------------------------------- graphs
def degrees(n, edges):
    deg = np.zeros(n, dtype=int)
    for i, j in edges:
        deg[i] += 1
        deg[j] += 1
    return deg


def remove_collinear_nodes(nodes, edges, tol=1e-9):
    """Drop degree-2 nodes lying on a straight line between their neighbours; returns (nodes, edges).

    Used by run.py --clean-labels. The generator's own merge misses these nodes (see 07_GDL_RESEARCH_REPORT.md,
    section 3.3); that generator bug is deliberately left unfixed for now.
    """
    nodes = np.asarray(nodes, dtype=float).reshape(-1, 2)
    adj = {i: set() for i in range(len(nodes))}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    changed = True
    while changed:
        changed = False
        for u in sorted(adj):
            if len(adj[u]) == 2:
                a, b = tuple(adj[u])
                v1, v2 = nodes[a] - nodes[u], nodes[b] - nodes[u]
                cr = v1[0] * v2[1] - v1[1] * v2[0]
                if abs(cr) < tol * np.linalg.norm(v1) * np.linalg.norm(v2) and v1 @ v2 < 0:
                    adj[a].discard(u)
                    adj[b].discard(u)
                    adj[a].add(b)
                    adj[b].add(a)
                    del adj[u]
                    changed = True
                    break
    ids = sorted(adj)
    m = {u: i for i, u in enumerate(ids)}
    return nodes[ids], sorted({(min(m[a], m[b]), max(m[a], m[b])) for a in ids for b in adj[a]})


def densify(nodes, edges, step):
    """Points along every edge at spacing <= step, plus the nodes. No edges -> the nodes."""
    nodes = np.asarray(nodes, dtype=float).reshape(-1, 2)
    out = [nodes]
    for i, j in edges:
        L = float(np.linalg.norm(nodes[j] - nodes[i]))
        n = max(int(np.ceil(L / step)), 1) + 1
        s = np.linspace(0.0, 1.0, n)[:, None]
        out.append(nodes[i][None] * (1 - s) + nodes[j][None] * s)
    return np.vstack(out)


def merge_close(nodes, tol):
    """Greedy merge of nodes closer than tol (centroid of the cluster)."""
    nodes = np.asarray(nodes, dtype=float).reshape(-1, 2)
    used = np.zeros(len(nodes), dtype=bool)
    out = []
    for i in range(len(nodes)):
        if used[i]:
            continue
        grp = [i]
        used[i] = True
        for j in range(i + 1, len(nodes)):
            if not used[j] and np.linalg.norm(nodes[j] - nodes[i]) < tol:
                grp.append(j)
                used[j] = True
        out.append(nodes[grp].mean(0))
    return np.asarray(out, dtype=float).reshape(-1, 2)


def snap_inside(points, poly):
    """Move points lying outside the polygon to their nearest boundary point."""
    P = np.asarray(points, dtype=float).reshape(-1, 2).copy()
    out = ~point_in_polygon(P, poly, 0.0)
    A, B = poly, np.roll(poly, -1, axis=0)
    AB = B - A
    L2 = np.maximum((AB ** 2).sum(1), 1e-30)
    for k in np.nonzero(out)[0]:
        t = np.clip(((P[k] - A) * AB).sum(1) / L2, 0.0, 1.0)
        proj = A + t[:, None] * AB
        P[k] = proj[np.argmin(np.linalg.norm(proj - P[k], axis=1))]
    return P


def edges_from_nodes(nodes, poly, eps_rel=1e-6, force_connected=False):
    """Minimum spanning forest over node pairs whose segment lies inside the polygon.

    Returns a sorted list of (i, j), i < j. If the allowed-pair graph is disconnected the result is
    a spanning forest, unless force_connected=True: then pairs whose segment leaves the polygon are
    still available at 1000x their length, so the result is always a spanning tree that uses
    inside-polygon pairs whenever they suffice. (Used for predicted nodes, never for the oracle P1.)
    """
    nodes = np.asarray(nodes, dtype=float).reshape(-1, 2)
    n = len(nodes)
    if n < 2:
        return []
    extent = float((poly.max(0) - poly.min(0)).max())
    eps = eps_rel * max(extent, 1e-12)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            dist = max(float(np.linalg.norm(nodes[i] - nodes[j])), 1e-12)
            if segment_inside(nodes[i], nodes[j], poly, eps):
                W[i, j] = dist
            elif force_connected:
                W[i, j] = 1000.0 * dist
    T = minimum_spanning_tree(csr_matrix(W)).tocoo()
    return sorted((int(min(a, b)), int(max(a, b))) for a, b in zip(T.row, T.col))


# ----------------------------------------------------------------------------- union of boxes
def union_of_boxes(boxes):
    """Outline of the union of axis-aligned boxes (x0,y0,x1,y1) as a CCW polygon, collinear
    vertices removed. Raises Rejected unless the union is one simple region without holes or
    pinch points.
    """
    xs = sorted({round(v, 12) for b in boxes for v in (b[0], b[2])})
    ys = sorted({round(v, 12) for b in boxes for v in (b[1], b[3])})
    xi = {v: k for k, v in enumerate(xs)}
    yi = {v: k for k, v in enumerate(ys)}
    nx, ny = len(xs) - 1, len(ys) - 1
    filled = np.zeros((nx, ny), dtype=bool)
    for x0, y0, x1, y1 in boxes:
        filled[xi[round(x0, 12)]:xi[round(x1, 12)], yi[round(y0, 12)]:yi[round(y1, 12)]] = True

    def f(i, j):
        return 0 <= i < nx and 0 <= j < ny and filled[i, j]

    out = {}
    for i in range(nx):
        for j in range(ny):
            if not filled[i, j]:
                continue
            if not f(i, j - 1):
                out.setdefault((i, j), []).append((i + 1, j))
            if not f(i + 1, j):
                out.setdefault((i + 1, j), []).append((i + 1, j + 1))
            if not f(i, j + 1):
                out.setdefault((i + 1, j + 1), []).append((i, j + 1))
            if not f(i - 1, j):
                out.setdefault((i, j + 1), []).append((i, j))
    for v, nxt in out.items():
        if len(nxt) != 1:
            raise Rejected("pinch point")
    total = sum(len(v) for v in out.values())
    start = next(iter(out))
    loop = [start]
    cur = out[start][0]
    while cur != start:
        loop.append(cur)
        cur = out[cur][0]
        if len(loop) > total + 1:
            raise Rejected("untraceable")
    if len(loop) != total:
        raise Rejected("more than one boundary loop (hole or several parts)")
    poly = np.array([[xs[a], ys[b]] for a, b in loop], dtype=float)
    poly = remove_collinear(poly)
    return ensure_ccw(poly)


def canonical_cycle(poly, nd=9):
    """Canonical form of a polygon (CCW, rotated to the lexicographically smallest vertex)."""
    p = ensure_ccw(np.round(np.asarray(poly, dtype=float), nd))
    k = min(range(len(p)), key=lambda i: (p[i, 0], p[i, 1]))
    return np.roll(p, -k, axis=0)
