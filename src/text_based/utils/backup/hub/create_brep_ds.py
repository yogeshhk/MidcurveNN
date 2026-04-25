"""
create_brep_ds.py — Boundary Representation (BRep) dataset generator.

For every raw shape (and each of its geometric variants), this module:

1. Builds a BRep structure for the profile (closed polygon) and midcurve
   (chain or star skeleton).
2. Applies the full set of geometric transformations defined in ``config.py``.
3. Splits the full dataset 80 / 10 / 10 into train / test / val CSV files.

BRep data schema
----------------
::

    {
        "Points":   [(x, y), ...],
        "Lines":    [[pt_idx_a, pt_idx_b], ...],   # edges by point index
        "Segments": [[line_idx, ...], ...]          # groups of lines forming
    }                                               # a loop or chain

Generic topology
----------------
* **Profile** is always a closed polygon → consecutive index pairs, one
  segment containing all lines.
* **Midcurve** topology (chain vs star) is detected automatically by
  ``prepare_data.detect_midcurve_hub`` — no shape-name ``if/elif`` branches.
"""

import json
import os
import random

import numpy as np
import pandas as pd

from config import (
    RAW_DATA_FOLDER,
    BREP_FOLDER,
    SCALE_START, SCALE_STOP, SCALE_STEP,
    ROTATE_START, ROTATE_STOP, ROTATE_STEP,
    TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP,
    TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP,
)
from prepare_data import (
    read_dat_files,
    scale_sequence,
    rotate_sequence,
    translate_sequence,
    mirror_sequence,
    detect_midcurve_hub,
)
from prepare_plots import plot_breps


# ---------------------------------------------------------------------------
# BRep construction
# ---------------------------------------------------------------------------

def build_profile_brep(points: list) -> dict:
    """
    Build a BRep structure for a closed polygon profile.

    The profile is always a simple closed loop regardless of shape,
    so this function is fully generic.

    Parameters
    ----------
    points:
        List of ``(x, y)`` tuples (polygon vertices in order).

    Returns
    -------
    dict with keys ``Points``, ``Lines``, ``Segments``.
    """
    n = len(points)
    lines    = [[i, (i + 1) % n] for i in range(n)]  # closed polygon
    segments = [list(range(n))]                        # one segment = the whole loop
    return {"Points": points, "Lines": lines, "Segments": segments}


def build_midcurve_brep(points: list) -> dict:
    """
    Build a BRep structure for a midcurve skeleton.

    Topology is detected automatically:

    * **Chain** — consecutive index pairs; all lines belong to a single
      segment (the full chain).
    * **Star**  — each line connects the hub to one spoke endpoint; every
      line is its own segment (independent spokes).

    Parameters
    ----------
    points:
        List of ``(x, y)`` tuples representing the midcurve.

    Returns
    -------
    dict with keys ``Points``, ``Lines``, ``Segments``.
    """
    hub = detect_midcurve_hub(points)
    if hub == -1:
        # Chain topology
        lines    = [[i, i + 1] for i in range(len(points) - 1)]
        segments = [list(range(len(lines)))]   # all lines form one chain
    else:
        # Star topology: independent spokes, each its own segment
        lines    = [[hub, i] for i in range(len(points)) if i != hub]
        segments = [[idx] for idx in range(len(lines))]

    return {"Points": points, "Lines": lines, "Segments": segments}


def build_brep_dict(shape_dict: dict) -> dict:
    """
    Wrap a raw shape dict with BRep structures for both profile and midcurve.

    Parameters
    ----------
    shape_dict:
        A shape dict with keys ``ShapeName``, ``Profile``, ``Midcurve``.

    Returns
    -------
    dict
        The original fields plus ``Profile_brep`` and ``Midcurve_brep``.
    """
    return {
        "ShapeName":    shape_dict["ShapeName"],
        "Profile":      shape_dict["Profile"],
        "Midcurve":     shape_dict["Midcurve"],
        "Profile_brep": build_profile_brep(shape_dict["Profile"]),
        "Midcurve_brep": build_midcurve_brep(shape_dict["Midcurve"]),
    }


def build_brep_list(shape_dicts: list) -> list:
    """
    Apply :func:`build_brep_dict` to every item in *shape_dicts*.

    Parameters
    ----------
    shape_dicts:
        List of raw shape dicts.

    Returns
    -------
    list of BRep dicts.
    """
    return [build_brep_dict(d) for d in shape_dicts]


# ---------------------------------------------------------------------------
# Transformation helpers
# ---------------------------------------------------------------------------

def _transform_shapes(shape_dicts: list, transform_fn, **kwargs) -> list:
    """
    Generic helper: apply *transform_fn* to the Profile and Midcurve of every
    dict in *shape_dicts*, return new BRep dicts.

    Parameters
    ----------
    shape_dicts:
        Source shape dicts (``ShapeName``, ``Profile``, ``Midcurve``).
    transform_fn:
        One of ``scale_sequence``, ``rotate_sequence``, etc.
    **kwargs:
        Extra keyword arguments forwarded to *transform_fn* and used to
        build the ``ShapeName`` suffix.

    Returns
    -------
    list of BRep dicts.
    """
    suffix = "_".join(str(v) for v in kwargs.values())
    transformed = [
        {
            "ShapeName": f"{d['ShapeName']}_{suffix}",
            "Profile":   transform_fn(d["Profile"],  **kwargs),
            "Midcurve":  transform_fn(d["Midcurve"], **kwargs),
        }
        for d in shape_dicts
    ]
    return build_brep_list(transformed)


def populate_by_transformation(original_shapes: list) -> list:
    """
    Generate all scaled, rotated, translated, and mirrored BRep variants of
    the original shapes.

    Transformation ranges come from ``config.py``.  Translations vary x and y
    **independently**, producing axial, diagonal, and arbitrary offset variants.

    Parameters
    ----------
    original_shapes:
        List of raw shape dicts (before BRep construction).

    Returns
    -------
    list of BRep dicts.
    """
    all_variants: list = []

    # Scale
    for factor in np.arange(SCALE_START, SCALE_STOP, SCALE_STEP):
        all_variants += _scaled_breps(original_shapes, float(factor))

    # Rotate
    for theta in range(ROTATE_START, ROTATE_STOP, ROTATE_STEP):
        all_variants += _rotated_breps(original_shapes, theta)

    # Translate (independent dx and dy)
    for dx in range(TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP):
        for dy in range(TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP):
            all_variants += _translated_breps(original_shapes, dx, dy)

    # Mirror
    all_variants += _mirrored_breps(original_shapes, axis_is_x=True)
    all_variants += _mirrored_breps(original_shapes, axis_is_x=False)

    return all_variants


# -- Individual transformation wrappers (keep populate_by_transformation clean) --

def _scaled_breps(shape_dicts: list, factor: float) -> list:
    transformed = [
        {
            "ShapeName": f"{d['ShapeName']}_scaled_{round(factor, 4)}",
            "Profile":   scale_sequence(d["Profile"],  factor),
            "Midcurve":  scale_sequence(d["Midcurve"], factor),
        }
        for d in shape_dicts
    ]
    return build_brep_list(transformed)


def _rotated_breps(shape_dicts: list, theta: float) -> list:
    transformed = [
        {
            "ShapeName": f"{d['ShapeName']}_rotated_{theta}",
            "Profile":   rotate_sequence(d["Profile"],  theta),
            "Midcurve":  rotate_sequence(d["Midcurve"], theta),
        }
        for d in shape_dicts
    ]
    return build_brep_list(transformed)


def _translated_breps(shape_dicts: list, dx: float, dy: float) -> list:
    transformed = [
        {
            "ShapeName": f"{d['ShapeName']}_translated_{dx}_{dy}",
            "Profile":   translate_sequence(d["Profile"],  dx, dy),
            "Midcurve":  translate_sequence(d["Midcurve"], dx, dy),
        }
        for d in shape_dicts
    ]
    return build_brep_list(transformed)


def _mirrored_breps(shape_dicts: list, axis_is_x: bool) -> list:
    suffix = "mirrored_x" if axis_is_x else "mirrored_y"
    transformed = [
        {
            "ShapeName": f"{d['ShapeName']}_{suffix}",
            "Profile":   mirror_sequence(d["Profile"],  axis_is_x),
            "Midcurve":  mirror_sequence(d["Midcurve"], axis_is_x),
        }
        for d in shape_dicts
    ]
    return build_brep_list(transformed)


# ---------------------------------------------------------------------------
# CSV persistence
# ---------------------------------------------------------------------------

def _brep_dict_to_csv_row(brep_dict: dict) -> dict:
    """
    Convert a BRep dict to a flat CSV row by JSON-serialising the complex
    fields.

    Parameters
    ----------
    brep_dict:
        A BRep dict (with ``Profile_brep`` and ``Midcurve_brep``).

    Returns
    -------
    dict suitable for a pandas DataFrame row.
    """
    return {
        "ShapeName":    brep_dict["ShapeName"],
        "Profile":      json.dumps(brep_dict["Profile"]),
        "Midcurve":     json.dumps(brep_dict["Midcurve"]),
        "Profile_brep": json.dumps(brep_dict["Profile_brep"]),
        "Midcurve_brep": json.dumps(brep_dict["Midcurve_brep"]),
    }


def write_to_csv(brep_dicts: list, filepath: str) -> None:
    """
    Serialise *brep_dicts* to a CSV file at *filepath*.

    Parameters
    ----------
    brep_dicts:
        List of BRep dicts.
    filepath:
        Full output path (including filename and extension).
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    rows = [_brep_dict_to_csv_row(d) for d in brep_dicts]
    pd.DataFrame(rows).to_csv(filepath, index=False)


def save_train_test_val_split(
    brep_dicts: list,
    base_filename: str,
    train_ratio: float = 0.8,
    test_ratio:  float = 0.1,
) -> None:
    """
    Split *brep_dicts* into train / test / validation sets and write them to
    separate CSV files.

    Parameters
    ----------
    brep_dicts:
        Full list of BRep dicts to split.
    base_filename:
        Base name (without extension) for the output files.
        Suffixes ``_train``, ``_test``, ``_val`` and ``.csv`` are appended.
    train_ratio:
        Fraction of data for the training set.
    test_ratio:
        Fraction of data for the test set (the remainder becomes validation).
    """
    total = len(brep_dicts)
    n_train = int(train_ratio * total)
    n_test  = int(test_ratio  * total)

    train = random.sample(brep_dicts, n_train)
    remaining = [d for d in brep_dicts if d not in train]
    test  = random.sample(remaining, n_test)
    val   = [d for d in remaining if d not in test]

    print(f"  Train: {len(train)}, Test: {len(test)}, Val: {len(val)}")

    base_path = os.path.join(BREP_FOLDER, base_filename)
    write_to_csv(brep_dicts, base_path + ".csv")
    write_to_csv(train,      base_path + "_train.csv")
    write_to_csv(test,       base_path + "_test.csv")
    write_to_csv(val,        base_path + "_val.csv")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Load raw .dat / .mid pairs and build original BRep dicts
    raw_shapes = read_dat_files(RAW_DATA_FOLDER)
    print(f"Loaded {len(raw_shapes)} shape(s): "
          f"{[d['ShapeName'] for d in raw_shapes]}")

    original_breps = build_brep_list(raw_shapes)

    # Optionally inspect a few originals
    # plot_breps(original_breps)

    # Generate all transformation variants
    print("Generating transformation variants…")
    all_variants = populate_by_transformation(raw_shapes)
    print(f"Total variants: {len(all_variants)}")

    # Save full dataset + train/test/val splits
    print("Saving CSV files…")
    save_train_test_val_split(
        original_breps + all_variants,
        base_filename="midcurve_brep",
    )
    print("Done. CSV files written to:", BREP_FOLDER)
