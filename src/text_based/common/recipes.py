"""
recipes.py -- express a midcurve vertex as the mean of a few profile vertices.

Every midcurve vertex of the gold shapes is the mean of 1, 2 or 4 profile vertices. Writing the
vertex as `mean(a,b)` means the LLM outputs a few small integers and never does float arithmetic.
"""
import itertools

import numpy as np


def recipe_tol(pose):
    """Matching tolerance: canonical grid is quantised to integers, raw poses are rounded to 6 dp."""
    return 1.01 if pose == "canonical" else 1e-4


def find_recipe(profile, v, tol=1e-6, max_size=4):
    """Smallest tuple of profile indices whose mean is within tol of v (min error, then
    lexicographic); None if no subset of size <= max_size matches."""
    P = np.asarray(profile, dtype=float)
    v = np.asarray(v, dtype=float)
    n = len(P)
    for k in range(1, min(max_size, n) + 1):
        best = None
        for idx in itertools.combinations(range(n), k):
            err = float(np.linalg.norm(P[list(idx)].mean(axis=0) - v))
            if err <= tol and (best is None or err < best[0] - 1e-9):
                best = (err, idx)
        if best is not None:
            return tuple(int(i) for i in best[1])
    return None


def recipes_for(profile, midcurve, tol=1e-6):
    return [find_recipe(profile, v, tol) for v in np.asarray(midcurve, dtype=float)]


def coverage(profile, midcurve, tol=1e-6):
    rec = recipes_for(profile, midcurve, tol)
    return sum(r is not None for r in rec) / max(1, len(rec))
