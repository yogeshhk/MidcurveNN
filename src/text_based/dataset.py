"""
dataset.py -- loads data/dataset_v1.jsonl and gives views of each row.

Row fields (see prepare_data.py): id, shape, kind ('pose' | 'gold'), pose_idx, pose_split, splits
(fold name -> role), aug, raw{profile, midcurve, edges}, canon{profile, midcurve, edges, transform},
text{fmt: {profile, midcurve}} (canonical pose).
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATH = os.path.join(HERE, "data", "dataset_v1.jsonl")


def load_rows(path=None):
    path = path or DEFAULT_PATH
    if not os.path.isfile(path):
        raise FileNotFoundError("%s not found; run: python run.py prepare" % path)
    rows = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def select(rows, fold="pose", role="test"):
    """Rows whose role in `fold` equals `role`. role='gold' returns the 4 gold rows."""
    if role == "gold":
        return [r for r in rows if r["kind"] == "gold"]
    return [r for r in rows if r["kind"] == "pose" and r["splits"].get(fold) == role]


def stratified(rows, n):
    """Up to n rows, round-robin across shapes (deterministic)."""
    if n is None or n >= len(rows):
        return list(rows)
    by = {}
    for r in rows:
        by.setdefault(r["shape"], []).append(r)
    out, i = [], 0
    names = sorted(by)
    while len(out) < n and any(i < len(v) for v in by.values()):
        for s in names:
            if i < len(by[s]) and len(out) < n:
                out.append(by[s][i])
        i += 1
    return out


def view(row, pose="canonical"):
    """(profile ndarray, midcurve ndarray, edges list) in the requested pose."""
    d = row["canon"] if pose == "canonical" else row["raw"]
    return (np.asarray(d["profile"], dtype=float), np.asarray(d["midcurve"], dtype=float),
            [tuple(e) for e in d["edges"]])


def raw_view(row):
    return view(row, "raw")
