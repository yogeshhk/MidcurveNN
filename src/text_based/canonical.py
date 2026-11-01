"""
canonical.py -- canonical pose for (profile, midcurve) pairs.

canonicalise() maps any rotated / mirrored / translated / scaled copy of a polygon to one
integer-grid pose, so an LLM sees a single pose. It is invertible: the transform is returned and
decanonicalise() maps canonical coordinates back to the original pose (error <= 0.5 grid unit).

Steps (see 02_llm_based_proposal.md section 4.1):
  1. candidates = {mirror or not} x {longest edge horizontal, both directions}
  2. force counter-clockwise vertex order (reverse if needed)
  3. translate bbox min to the origin, scale the longer bbox side to `grid` (default 1000)
  4. start vertex = lowest y (then lowest x); list counter-clockwise from there
  5. among all candidates keep the lexicographically smallest integer vertex string
  6. midcurve vertices: DFS order from the vertex nearest the profile start; edges sorted i<j
"""
import math

import numpy as np

GRID = 1000


def signed_area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def rot_matrix(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s], [s, c]])


def _candidate(P, M, mirror, angle_extra_idx, grid):
    """Yield (key, payload) for each candidate pose of one mirror setting."""
    P1 = P.copy()
    M1 = M.copy()
    if mirror:
        P1[:, 0] *= -1.0
        M1[:, 0] *= -1.0
    n = len(P1)
    reversed_ = signed_area(P1) < 0
    if reversed_:
        P1 = P1[::-1].copy()
    E = np.roll(P1, -1, axis=0) - P1
    L = np.linalg.norm(E, axis=1)
    cands = np.where(L >= L.max() * (1.0 - 1e-3))[0]
    for e in cands:
        theta = math.atan2(E[e, 1], E[e, 0])
        for extra in (0.0, math.pi):
            angle = -theta + extra
            R = rot_matrix(angle)
            Pr = P1 @ R.T
            Mr = M1 @ R.T
            mn = Pr.min(axis=0)
            size = float((Pr.max(axis=0) - mn).max())
            if size <= 0:
                continue
            scale = grid / size
            Ps = (Pr - mn) * scale
            ymin = Ps[:, 1].min()
            near = np.where(Ps[:, 1] <= ymin + 1e-6 * grid)[0]
            start = int(near[np.argmin(Ps[near, 0])])
            Ps = np.roll(Ps, -start, axis=0)
            Pq = np.rint(Ps).astype(int)
            key = tuple(int(v) for v in Pq.ravel())
            payload = dict(Pq=Pq, Ms=(Mr - mn) * scale, mirror=mirror, reversed=reversed_,
                           angle=angle, offset=mn.copy(), scale=scale, start=start, n=n)
            yield key, payload


def _order_midcurve(Mq, edges, anchor):
    """DFS ordering of midcurve vertices; returns (new_points, new_edges, perm)."""
    m = len(Mq)
    adj = {i: set() for i in range(m)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)

    def k(i):
        return (int(Mq[i][1]), int(Mq[i][0]))

    seen, order = set(), []
    remaining = list(range(m))
    while len(seen) < m:
        cand = [i for i in remaining if i not in seen]
        root = min(cand, key=lambda i: (float(np.hypot(*(Mq[i] - anchor))), k(i)))
        stack = [root]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            order.append(u)
            for v in sorted(adj[u], key=k, reverse=True):  # reversed so smallest pops first
                if v not in seen:
                    stack.append(v)
    new_index = {old: new for new, old in enumerate(order)}
    pts = Mq[order]
    new_edges = sorted({tuple(sorted((new_index[a], new_index[b]))) for a, b in edges})
    return pts, [tuple(int(v) for v in e) for e in new_edges], order


def canonicalise(profile, midcurve, edges, grid=GRID):
    """Return dict(profile=int array, midcurve=int array, edges=list, transform=dict)."""
    P = np.asarray(profile, dtype=float)
    M = np.asarray(midcurve, dtype=float).reshape(-1, 2)
    best = None
    for mirror in (False, True):
        for key, payload in _candidate(P, M, mirror, 0, grid):
            if best is None or key < best[0]:
                best = (key, payload)
    if best is None:
        raise ValueError("degenerate profile (zero size)")
    pl = best[1]
    Mq = np.rint(pl["Ms"]).astype(int)
    mpts, medges, order = _order_midcurve(Mq, [tuple(e) for e in edges], pl["Pq"][0].astype(float))
    transform = dict(mirror=bool(pl["mirror"]), reversed=bool(pl["reversed"]), angle=float(pl["angle"]),
                     offset=[float(pl["offset"][0]), float(pl["offset"][1])], scale=float(pl["scale"]),
                     start=int(pl["start"]), grid=int(grid))
    return dict(profile=pl["Pq"], midcurve=mpts, edges=medges, transform=transform)


def decanonicalise(points, transform):
    """Map canonical coordinates back to the original pose (float array)."""
    Q = np.asarray(points, dtype=float).reshape(-1, 2)
    t = transform
    P = Q / t["scale"] + np.asarray(t["offset"], dtype=float)
    P = P @ rot_matrix(-t["angle"]).T
    if t["mirror"]:
        P[:, 0] *= -1.0
    return P
