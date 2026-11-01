"""
prepare_data.py -- raw (.dat / .mid / .edges + splits.json) -> data/dataset_v1.jsonl

Reads src/data/raw/{I,L,T,Plus}.{dat,mid,edges} and splits.json (read-only), generates seeded pose
augmentations (mirror, rotation, scale, translation), canonicalises every sample, pre-renders the
canonical text for each codec, and assigns a role per fold:

  fold 'pose'      : every shape in every role (roles differ by pose seed). NOT shape generalisation.
  fold 'default'   : splits.json 'default' (train I,L / val T / test Plus), by shape name.
  fold 'loso_<S>'  : leave-one-shape-out, shape S is the test shape.

Gold rows (kind 'gold') are the 4 unaugmented originals; they are excluded from all train/val/test.

Usage:  python prepare_data.py [--seed 0] [--n-train 100] [--n-val 10] [--n-test 20]
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from text_based import canonical, formats, recipes  # noqa: E402

RAW_DIR = os.path.join(_SRC, "data", "raw")
OUT_PATH = os.path.join(_HERE, "data", "dataset_v1.jsonl")
FORMATS = ("json", "mcv1", "mcv2", "lines")


def _read_xy(path):
    pts = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            t = line.split()
            if len(t) >= 2:
                pts.append((float(t[0]), float(t[1])))
    return np.array(pts, dtype=float)


def _read_edges(path):
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            t = line.split()
            if len(t) >= 2:
                out.append((int(t[0]), int(t[1])))
    return out


def load_raw(raw_dir=RAW_DIR):
    with open(os.path.join(raw_dir, "splits.json"), "r", encoding="utf-8") as fh:
        splits = json.load(fh)
    shapes = {}
    for s in splits["shapes"]:
        shapes[s] = dict(profile=_read_xy(os.path.join(raw_dir, s + ".dat")),
                         midcurve=_read_xy(os.path.join(raw_dir, s + ".mid")),
                         edges=_read_edges(os.path.join(raw_dir, s + ".edges")))
    return shapes, splits


def augment(profile, midcurve, rng):
    """Random mirror, rotation, scale, translation (same transform on both). Returns arrays, aug dict."""
    mirror = bool(rng.random() < 0.5)
    rot = float(rng.uniform(0.0, 360.0))
    scale = float(rng.uniform(0.5, 5.0))
    tx, ty = (float(v) for v in rng.uniform(-50.0, 50.0, size=2))
    a = np.deg2rad(rot)
    R = canonical.rot_matrix(a)

    def f(P):
        P = np.array(P, dtype=float)
        if mirror:
            P[:, 0] *= -1.0
        P = (P @ R.T) * scale + np.array([tx, ty])
        return np.round(P, 6)

    return f(profile), f(midcurve), dict(mirror=mirror, rot_deg=round(rot, 3), scale=round(scale, 4),
                                         tx=round(tx, 3), ty=round(ty, 3))


def fold_roles(shape, pose_split, splits):
    """Role of a pose-row in each fold."""
    roles = {"pose": pose_split}
    d = splits["default"]
    for role in ("train", "val", "test"):
        if shape in d[role]:
            roles["default"] = role
    for f in splits["loso"]:
        if shape == f["holdout"]:
            roles["loso_" + f["holdout"]] = "test"
        else:
            roles["loso_" + f["holdout"]] = {"train": "train", "val": "val"}.get(pose_split, "unused")
    return roles


def make_row(rid, shape, kind, pose_idx, pose_split, aug, profile, midcurve, edges, splits):
    c = canonical.canonicalise(profile, midcurve, edges)
    text = {}
    for fmt in FORMATS:
        codec = formats.get_codec(fmt)
        text[fmt] = dict(
            profile=codec.encode_profile(c["profile"]),
            midcurve=codec.encode_midcurve(c["midcurve"], c["edges"], c["profile"], recipes.recipe_tol("canonical")))
    cov = recipes.coverage(c["profile"], c["midcurve"], recipes.recipe_tol("canonical"))
    if kind == "gold":
        roles = {f: "gold" for f in ["pose", "default"] + ["loso_" + x["holdout"] for x in splits["loso"]]}
    else:
        roles = fold_roles(shape, pose_split, splits)
    return dict(
        id=rid, shape=shape, kind=kind, pose_idx=pose_idx, pose_split=pose_split, splits=roles, aug=aug,
        raw=dict(profile=np.asarray(profile).tolist(), midcurve=np.asarray(midcurve).tolist(),
                 edges=[list(e) for e in edges]),
        canon=dict(profile=c["profile"].tolist(), midcurve=c["midcurve"].tolist(),
                   edges=[list(e) for e in c["edges"]], transform=c["transform"]),
        text=text, recipe_coverage=cov)


def build_rows(seed=0, n_train=100, n_val=10, n_test=20, raw_dir=RAW_DIR):
    shapes, splits = load_raw(raw_dir)
    counts = {"train": n_train, "val": n_val, "test": n_test}
    rows = []
    for si, name in enumerate(splits["shapes"]):
        sh = shapes[name]
        rows.append(make_row("%s_gold" % name, name, "gold", 0, None,
                             dict(mirror=False, rot_deg=0.0, scale=1.0, tx=0.0, ty=0.0),
                             sh["profile"], sh["midcurve"], sh["edges"], splits))
        for role in ("train", "val", "test"):
            rng = np.random.default_rng([seed, splits["seeds"][role], si])
            for k in range(counts[role]):
                P, M, aug = augment(sh["profile"], sh["midcurve"], rng)
                rows.append(make_row("%s_%s_%03d" % (name, role, k), name, "pose", k, role, aug,
                                     P, M, sh["edges"], splits))
    return rows


def write_rows(rows, path=OUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    manifest = dict(path=os.path.basename(path), n_rows=len(rows), sha256_16=digest,
                    counts={k: sum(1 for r in rows if r["pose_split"] == k) for k in ("train", "val", "test")},
                    gold=sum(1 for r in rows if r["kind"] == "gold"))
    with open(path.replace(".jsonl", ".manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=100)
    ap.add_argument("--n-val", type=int, default=10)
    ap.add_argument("--n-test", type=int, default=20)
    ap.add_argument("--out", default=OUT_PATH)
    a = ap.parse_args(argv)
    rows = build_rows(a.seed, a.n_train, a.n_val, a.n_test)
    m = write_rows(rows, a.out)
    print("wrote %s: %s" % (a.out, m))
    low = [r["id"] for r in rows if r["recipe_coverage"] < 1.0]
    print("rows without full recipe coverage: %d" % len(low))
    return 0


if __name__ == "__main__":
    sys.exit(main())
