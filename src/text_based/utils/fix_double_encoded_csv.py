"""
fix_double_encoded_csv.py -- repair double-encoded JSON cells in data/csvs/*.csv.

The checked-in train/val/test CSVs store each Profile / Midcurve / *_brep cell as a JSON string
literal wrapping the JSON. This script unwraps those cells (max 2 passes) and rewrites the CSV.
Originals are copied first to data/csvs/_backup_double_encoded/ (never overwritten).

Usage (from src/text_based):
    conda run -n genai python utils/fix_double_encoded_csv.py
"""
import json
import os
import shutil

import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.normpath(os.path.join(_HERE, "..", "data", "csvs"))
BACKUP_DIR = os.path.join(CSV_DIR, "_backup_double_encoded")
FILES = ["midcurve_llm.csv", "midcurve_llm_train.csv", "midcurve_llm_val.csv", "midcurve_llm_test.csv"]
COLS = ["Profile", "Midcurve", "Profile_brep", "Midcurve_brep"]


def unwrap(value):
    """If the cell is a JSON string literal, return the inner string (max 2 passes)."""
    for _ in range(2):
        if not isinstance(value, str):
            break
        try:
            inner = json.loads(value)
        except (ValueError, TypeError):
            break
        if isinstance(inner, str):
            value = inner
        else:
            break
    return value


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for fname in FILES:
        src = os.path.join(CSV_DIR, fname)
        if not os.path.isfile(src):
            print("skip (missing):", fname)
            continue
        bak = os.path.join(BACKUP_DIR, fname)
        if not os.path.isfile(bak):
            shutil.copy2(src, bak)
        df = pd.read_csv(src, dtype=str, keep_default_na=False)
        n_before = len(df)
        changed = 0
        for col in COLS:
            if col not in df.columns:
                continue
            new = df[col].map(unwrap)
            changed += int((new != df[col]).sum())
            df[col] = new
        df.to_csv(src, index=False)
        n_after = len(pd.read_csv(src, dtype=str, keep_default_na=False))
        print("%-26s rows %d -> %d, cells unwrapped: %d" % (fname, n_before, n_after, changed))


if __name__ == "__main__":
    main()
