"""
create_brep_csvs.py — BRep dataset generator (the only dataset pipeline script).

Reads hand/auto-authored shape JSON files, applies geometric transformations, and
writes train / test / val CSV files.  ``create_line_ds.py`` is no longer part
of the pipeline — the JSON format is the single source of truth for both
geometry and topology.

Pipeline summary
----------------
1. ``read_all_shapes()``        — load all ``.json`` files from ``RAW_DATA_FOLDER``.
2. ``populate_by_transformation()`` — generate scaled / rotated / translated /
   mirrored variants.  Only ``Points`` change; ``Lines`` and ``Segments`` are
   carried through unchanged.
3. ``save_dataset()``           — write the full dataset plus 80/10/10
   train / test / val CSV splits to ``BREP_FOLDER``.

CSV column layout
-----------------
``ShapeName | Profile | Midcurve | Profile_brep | Midcurve_brep``

The four geometry columns are JSON-serialised strings so a single CSV cell
holds the complete structured data.

Usage
-----
::

    python create_brep_ds.py
"""

import json
import os
import random

import numpy as np
import pandas as pd

from config import (
    RAW_DATA_FOLDER,
    BREP_FOLDER,
    SCALE_START,  SCALE_STOP,  SCALE_STEP,
    ROTATE_START, ROTATE_STOP, ROTATE_STEP,
    TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP,
    TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP,
)
from prepare_data import (
    read_all_shapes,
    apply_transform_to_shape,
    scale_points,
    rotate_points,
    translate_points,
    mirror_points,
)


# ---------------------------------------------------------------------------
# Transformation variant generators
# ---------------------------------------------------------------------------

def _scaled_variants(shapes: list) -> list:
    """
    Return scaled shape dicts for every factor in the configured range.

    Parameters
    ----------
    shapes:
        List of source shape dicts.

    Returns
    -------
    list of shape dicts.
    """
    variants = []
    for factor in np.arange(SCALE_START, SCALE_STOP, SCALE_STEP):
        f = round(float(factor), 4)
        for shape in shapes:
            variants.append(
                apply_transform_to_shape(
                    shape, scale_points, f"scaled_{f}", factor=f
                )
            )
    return variants


def _rotated_variants(shapes: list) -> list:
    """
    Return rotated shape dicts for every angle in the configured range.

    Parameters
    ----------
    shapes:
        List of source shape dicts.

    Returns
    -------
    list of shape dicts.
    """
    variants = []
    for theta in range(ROTATE_START, ROTATE_STOP, ROTATE_STEP):
        for shape in shapes:
            variants.append(
                apply_transform_to_shape(
                    shape, rotate_points, f"rotated_{theta}", theta_deg=theta
                )
            )
    return variants


def _translated_variants(shapes: list) -> list:
    """
    Return translated shape dicts for every ``(dx, dy)`` combination in
    the configured ranges.

    X and Y are varied independently, so axial, diagonal, and arbitrary
    offsets are all generated — not just ``dx == dy`` diagonal variants.

    Parameters
    ----------
    shapes:
        List of source shape dicts.

    Returns
    -------
    list of shape dicts.
    """
    variants = []
    for dx in range(TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP):
        for dy in range(TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP):
            for shape in shapes:
                variants.append(
                    apply_transform_to_shape(
                        shape, translate_points,
                        f"translated_{dx}_{dy}",
                        dx=dx, dy=dy,
                    )
                )
    return variants


def _mirrored_variants(shapes: list) -> list:
    """
    Return mirror-x and mirror-y variants for every shape.

    Parameters
    ----------
    shapes:
        List of source shape dicts.

    Returns
    -------
    list of shape dicts.
    """
    variants = []
    for axis_is_x, suffix in [(True, "mirrored_x"), (False, "mirrored_y")]:
        for shape in shapes:
            variants.append(
                apply_transform_to_shape(
                    shape, mirror_points, suffix, axis_is_x=axis_is_x
                )
            )
    return variants


def populate_by_transformation(original_shapes: list) -> list:
    """
    Generate all transformation variants of *original_shapes*.

    Transformation ranges are read from ``config.py``.

    Parameters
    ----------
    original_shapes:
        List of original (pre-transformation) shape dicts loaded from JSON.

    Returns
    -------
    list of shape dicts — does NOT include the originals themselves.
    """
    all_variants: list = []
    all_variants += _scaled_variants(original_shapes)
    all_variants += _rotated_variants(original_shapes)
    all_variants += _translated_variants(original_shapes)
    all_variants += _mirrored_variants(original_shapes)
    return all_variants


# ---------------------------------------------------------------------------
# CSV serialisation
# ---------------------------------------------------------------------------

def _shape_to_csv_row(shape: dict) -> dict:
    """
    Flatten a shape dict to a single CSV row by JSON-serialising the
    structured geometry fields.

    Parameters
    ----------
    shape:
        A fully populated shape dict.

    Returns
    -------
    dict
        Flat dict suitable for a pandas DataFrame row.
    """
    return {
        "ShapeName":    shape["ShapeName"],
        "Profile":      json.dumps(shape["Profile"]),
        "Midcurve":     json.dumps(shape["Midcurve"]),
        "Profile_brep": json.dumps(shape["Profile_brep"]),
        "Midcurve_brep": json.dumps(shape["Midcurve_brep"]),
    }


def write_csv(shapes: list, filepath: str) -> None:
    """
    Write *shapes* to a CSV file at *filepath*.

    The output directory is created automatically if it does not exist.

    Parameters
    ----------
    shapes:
        List of shape dicts to serialise.
    filepath:
        Full destination path including filename and ``.csv`` extension.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    rows = [_shape_to_csv_row(s) for s in shapes]
    pd.DataFrame(rows).to_csv(filepath, index=False)
    print(f"  Written: {filepath}  ({len(shapes)} rows)")


# ---------------------------------------------------------------------------
# Train / test / val split
# ---------------------------------------------------------------------------

def save_dataset(
    shapes: list,
    base_name: str = "midcurve_brep",
    train_ratio: float = 0.8,
    test_ratio:  float = 0.1,
    random_seed: int   = 42,
) -> None:
    """
    Write the full dataset and 80 / 10 / 10 train / test / val CSV splits
    to ``BREP_FOLDER``.

    Files written
    -------------
    - ``<base_name>.csv``       — complete dataset
    - ``<base_name>_train.csv``
    - ``<base_name>_test.csv``
    - ``<base_name>_val.csv``

    Parameters
    ----------
    shapes:
        Complete list of shape dicts (originals + all variants).
    base_name:
        Filename stem (no extension) for output files.
    train_ratio:
        Fraction allocated to training.
    test_ratio:
        Fraction allocated to testing (remainder becomes validation).
    random_seed:
        Seed for reproducible splits.
    """
    random.seed(random_seed)

    total   = len(shapes)
    n_train = int(train_ratio * total)
    n_test  = int(test_ratio  * total)

    shuffled   = shapes[:]
    random.shuffle(shuffled)
    train = shuffled[:n_train]
    test  = shuffled[n_train : n_train + n_test]
    val   = shuffled[n_train + n_test :]

    print(f"\nDataset split — total:{total}  "
          f"train:{len(train)}  test:{len(test)}  val:{len(val)}")

    base_path = os.path.join(BREP_FOLDER, base_name)
    write_csv(shuffled, base_path + ".csv")
    write_csv(train,    base_path + "_train.csv")
    write_csv(test,     base_path + "_test.csv")
    write_csv(val,      base_path + "_val.csv")


# ---------------------------------------------------------------------------
# CSV reading helpers  (for downstream model training scripts)
# ---------------------------------------------------------------------------

def load_csv(filepath: str) -> list:
    """
    Load a dataset CSV written by :func:`write_csv` and return a list of
    shape dicts with all JSON fields deserialised back to Python objects.

    Parameters
    ----------
    filepath:
        Path to the CSV file.

    Returns
    -------
    list of dict
        Each dict has the same schema as the original shape JSON.
    """
    df = pd.read_csv(filepath)
    shapes = []
    for _, row in df.iterrows():
        shapes.append({
            "ShapeName":    row["ShapeName"],
            "Profile":      json.loads(row["Profile"]),
            "Midcurve":     json.loads(row["Midcurve"]),
            "Profile_brep": json.loads(row["Profile_brep"]),
            "Midcurve_brep": json.loads(row["Midcurve_brep"]),
        })
    return shapes


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Reading shape JSONs from: {RAW_DATA_FOLDER}")
    original_shapes = read_all_shapes(RAW_DATA_FOLDER)
    print(f"Loaded {len(original_shapes)} shape(s): "
          f"{[s['ShapeName'] for s in original_shapes]}")

    print("\nGenerating transformation variants…")
    variants = populate_by_transformation(original_shapes)
    print(f"Variants generated: {len(variants)}")

    all_shapes = original_shapes + variants
    print(f"Total shapes (originals + variants): {len(all_shapes)}")

    print(f"\nSaving dataset to: {BREP_FOLDER}")
    save_dataset(all_shapes)

    print("\nDone.")
