"""Raw shapes -> ONE dataset file for the image track: data/dataset_v1.npz.

Inputs (read-only): src/data/raw/{I,L,T,Plus}.dat (closed profile), .mid (midcurve points),
.edges (midcurve edges, 'i j' per line, 0-based into .mid), splits.json.

Rasterisation uses OpenCV + numpy only (no drawsvg, no shapely).

Sample layout in the npz (N samples, H = W = size):
  inputs    uint8 [N,3,H,W]  ch0 outline (0/1), ch1 filled mask (0/1), ch2 distance transform
                             of the filled mask divided by its max, quantised to 0..255
  targets   uint8 [N,H,W]    1-px midcurve (0/1)
  shape_id  int16 [N]        index into shape_names
  role      int8  [N]        0 train, 1 val, 2 test (pose seeds from splits.json)
  scale     float32 [N]      pixels per raw unit (to report Chamfer/Hausdorff in raw units)
  pose      float32 [N,5]    theta, mirror, frac, tx, ty
  geom      str (json)       raw geometry per shape (used by dataset.py for on-the-fly poses)
  splits    str (json)       copy of splits.json
"""
import json
import math
import os

import cv2
import numpy as np
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # image_based/ (this file is in common/)
RAW_DIR = os.path.normpath(os.path.join(HERE, "..", "data", "raw"))
DATA_DIR = os.path.join(HERE, "data")
DATASET = os.path.join(DATA_DIR, "dataset_v1.npz")
SIZE = 128
N_PER_SHAPE = {"train": 256, "val": 32, "test": 64}
ROLES = {"train": 0, "val": 1, "test": 2}


def _read_pts(path):
    rows = []
    with open(path) as f:
        for line in f:
            t = line.split()
            if len(t) >= 2:
                rows.append([float(t[0]), float(t[1])])
    return np.asarray(rows, np.float32)


def _read_edges(path):
    rows = []
    with open(path) as f:
        for line in f:
            t = line.split()
            if len(t) >= 2:
                rows.append([int(t[0]), int(t[1])])
    return np.asarray(rows, np.int64)


def load_raw(raw_dir=RAW_DIR):
    """-> (splits dict, geom dict name -> {profile, mid, edges} as numpy arrays)."""
    with open(os.path.join(raw_dir, "splits.json")) as f:
        splits = json.load(f)
    geom = {}
    for name in splits["shapes"]:
        geom[name] = dict(
            profile=_read_pts(os.path.join(raw_dir, name + ".dat")),
            mid=_read_pts(os.path.join(raw_dir, name + ".mid")),
            edges=_read_edges(os.path.join(raw_dir, name + ".edges")),
        )
    return splits, geom


def geom_to_json(geom):
    return json.dumps({k: {a: np.asarray(b).tolist() for a, b in v.items()} for k, v in geom.items()})


def geom_from_json(s):
    d = json.loads(s)
    out = {}
    for k, v in d.items():
        out[k] = dict(profile=np.asarray(v["profile"], np.float32), mid=np.asarray(v["mid"], np.float32),
                      edges=np.asarray(v["edges"], np.int64).reshape(-1, 2))
    return out


def shape_frame(g):
    """(extent, centre) of the profile bounding box."""
    p = g["profile"]
    ext = float(np.ptp(p, axis=0).max())
    ctr = (p.min(0) + p.max(0)) / 2.0
    return ext, ctr


def sample_pose(rng, size, ext, aug=True):
    """Random pose: rotation, mirror, scale (35-80 percent of the frame), translation."""
    if aug:
        theta = float(rng.uniform(0, 2 * math.pi))
        mirror = float(rng.random() < 0.5)
        frac = float(rng.uniform(0.35, 0.80))
    else:
        theta, mirror, frac = 0.0, 0.0, 0.6
    half = 0.5 * frac * size * (abs(math.cos(theta)) + abs(math.sin(theta)))
    room = max(0.0, size / 2.0 - 2.0 - half)
    if aug and room > 0:
        tx, ty = (float(v) for v in rng.uniform(-room, room, 2))
    else:
        tx = ty = 0.0
    return np.asarray([theta, mirror, frac, tx, ty], np.float32)


def xform(P, ctr, pose, ext, size):
    theta, mirror, frac, tx, ty = [float(v) for v in pose]
    s = frac * size / ext
    Q = (P - ctr) * np.array([-1.0 if mirror > 0.5 else 1.0, 1.0], np.float32)
    c, sn = math.cos(theta), math.sin(theta)
    R = np.array([[c, -sn], [sn, c]], np.float32)
    return (Q @ R.T) * s + np.array([size / 2.0 + tx, size / 2.0 + ty], np.float32), s


def render(g, pose, size=SIZE):
    """Render one shape in one pose. Same transform for profile and midcurve.
    Returns inputs uint8 [3,H,W], target uint8 [H,W], scale (px per raw unit)."""
    ext, ctr = shape_frame(g)
    prof, s = xform(g["profile"], ctr, pose, ext, size)
    mpts, _ = xform(g["mid"], ctr, pose, ext, size)
    pi = np.round(prof).astype(np.int32)
    outline = np.zeros((size, size), np.uint8)
    cv2.polylines(outline, [pi], True, 1, 1)
    filled = np.zeros((size, size), np.uint8)
    cv2.fillPoly(filled, [pi], 1)
    mid = np.zeros((size, size), np.uint8)
    mi = np.round(mpts).astype(int)
    for a, b in g["edges"]:
        cv2.line(mid, (int(mi[a, 0]), int(mi[a, 1])), (int(mi[b, 0]), int(mi[b, 1])), 1, 1)
    dt = ndi.distance_transform_edt(filled)
    dt = dt / max(float(dt.max()), 1e-6)
    x = np.stack([outline, filled, np.round(dt * 255).astype(np.uint8)]).astype(np.uint8)
    return x, mid, float(s)


def build(path=DATASET, size=SIZE, raw_dir=RAW_DIR, n_per_shape=None):
    n_per_shape = n_per_shape or N_PER_SHAPE
    splits, geom = load_raw(raw_dir)
    names = list(splits["shapes"])
    seeds = splits.get("seeds", {"train": 0, "val": 1, "test": 2})
    X, Y, sid, role, scale, pose = [], [], [], [], [], []
    for part, n in n_per_shape.items():
        for k, name in enumerate(names):
            rng = np.random.default_rng([int(seeds[part]), k])
            ext, _ = shape_frame(geom[name])
            for i in range(n):
                p = sample_pose(rng, size, ext, True)
                x, y, s = render(geom[name], p, size)
                X.append(x); Y.append(y); sid.append(k); role.append(ROLES[part])
                scale.append(s); pose.append(p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez_compressed(
        path, inputs=np.stack(X), targets=np.stack(Y), shape_id=np.asarray(sid, np.int16),
        shape_names=np.asarray(names), role=np.asarray(role, np.int8),
        scale=np.asarray(scale, np.float32), pose=np.stack(pose).astype(np.float32),
        geom=np.asarray(geom_to_json(geom)), splits=np.asarray(json.dumps(splits)),
        size=np.asarray(size), version=np.asarray(1))
    return path, len(X)


if __name__ == "__main__":
    p, n = build()
    print("wrote %s (%d samples, %.1f MB)" % (p, n, os.path.getsize(p) / 1e6))
