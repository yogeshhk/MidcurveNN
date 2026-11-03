"""
prepare_data.py — I/O and geometric transformations for the Midcurve Pipeline.

Responsibilities
----------------
1. Read hand-authored shape JSON files from ``RAW_DATA_FOLDER``.
2. Provide coordinate-level geometric transformations (scale, rotate,
   translate, mirror) implemented as 3×3 homogeneous-matrix operations.
3. Provide a single entry-point that applies a transformation to a full
   shape dict — updating both the flat point lists and the BRep ``Points``
   arrays while leaving ``Lines`` and ``Segments`` completely unchanged.

Input JSON schema (one file per shape in ``data/raw/``)
-------------------------------------------------------
::

    {
        "ShapeName": "I",
        "Profile":   [[x, y], ...],          ← flat point list (kept for
        "Midcurve":  [[x, y], ...],            backward compat with .dat/.mid)
        "Profile_brep": {
            "Points":   [[x, y], ...],
            "Lines":    [[i, j], ...],        ← point-index pairs, never changed
            "Segments": [[line_idx, ...], ...]← groups of lines, never changed
        },
        "Midcurve_brep": {
            "Points":   [[x, y], ...],
            "Lines":    [[i, j], ...],
            "Segments": [[line_idx, ...], ...]
        }
    }

Key design decision
-------------------
Topology (Lines, Segments) is authored once in the JSON and is never
inferred or modified by the pipeline.  Transformations are purely
arithmetic on ``Points`` — the index structure is invariant because all
four supported transforms are 1-to-1 maps (they move points but never
change count or order).
"""

import copy
import json
import math
import os

import numpy as np

from config import RAW_DATA_FOLDER


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def read_shape_json(filepath: str) -> dict:
    """
    Load and return a single shape dict from a JSON file.

    Parameters
    ----------
    filepath:
        Absolute or relative path to the ``.json`` shape file.

    Returns
    -------
    dict
        Validated shape dict with keys ``ShapeName``, ``Profile``,
        ``Midcurve``, ``Profile_brep``, ``Midcurve_brep``.

    Raises
    ------
    KeyError
        If any of the required top-level keys is missing.
    """
    with open(filepath) as fh:
        shape = json.load(fh)

    required = {"ShapeName", "Profile", "Midcurve", "Profile_brep", "Midcurve_brep"}
    missing = required - shape.keys()
    if missing:
        raise KeyError(
            f"{filepath}: missing required keys: {missing}"
        )
    for brep_key in ("Profile_brep", "Midcurve_brep"):
        brep_required = {"Points", "Lines", "Segments"}
        brep_missing = brep_required - shape[brep_key].keys()
        if brep_missing:
            raise KeyError(
                f"{filepath} → {brep_key}: missing keys: {brep_missing}"
            )
    return shape


def read_all_shapes(datafolder: str = RAW_DATA_FOLDER) -> list:
    """
    Load every ``.json`` file in *datafolder* and return a list of shape
    dicts.

    Non-JSON files and sub-directories are silently skipped.  Files that
    fail validation raise immediately so errors are never hidden.

    Parameters
    ----------
    datafolder:
        Directory containing hand-authored shape JSON files.

    Returns
    -------
    list of dict
    """
    shapes = []
    for filename in sorted(os.listdir(datafolder)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(datafolder, filename)
        if os.path.isdir(filepath):
            continue
        shapes.append(read_shape_json(filepath))

    if not shapes:
        raise FileNotFoundError(
            f"No .json shape files found in: {datafolder}"
        )
    return shapes


# ---------------------------------------------------------------------------
# Geometric transformations (3×3 homogeneous matrices)
# ---------------------------------------------------------------------------

def scale_points(points: list, factor: float) -> list:
    """
    Scale every point in *points* by *factor* around the origin.

    Parameters
    ----------
    points:
        List of ``[x, y]`` pairs.
    factor:
        Uniform scale factor applied to both axes.

    Returns
    -------
    list of [float, float]
    """
    T = np.array([[factor, 0,      0],
                  [0,      factor, 0],
                  [0,      0,      1]], dtype=float)
    return _apply_transform(points, T)


def rotate_points(points: list, theta_deg: float) -> list:
    """
    Rotate every point in *points* by *theta_deg* degrees counter-clockwise
    around the origin.

    Parameters
    ----------
    points:
        List of ``[x, y]`` pairs.
    theta_deg:
        Rotation angle in degrees.

    Returns
    -------
    list of [float, float]
    """
    theta = math.radians(theta_deg)
    c, s = math.cos(theta), math.sin(theta)
    T = np.array([[ c, -s, 0],
                  [ s,  c, 0],
                  [ 0,  0, 1]], dtype=float)
    return _apply_transform(points, T)


def translate_points(points: list, dx: float, dy: float) -> list:
    """
    Translate every point in *points* by ``(dx, dy)``.

    Parameters
    ----------
    points:
        List of ``[x, y]`` pairs.
    dx:
        Horizontal displacement.
    dy:
        Vertical displacement.

    Returns
    -------
    list of [float, float]
    """
    T = np.array([[1, 0, dx],
                  [0, 1, dy],
                  [0, 0,  1]], dtype=float)
    return _apply_transform(points, T)


def mirror_points(points: list, axis_is_x: bool) -> list:
    """
    Mirror every point in *points* across an axis through the origin.

    Parameters
    ----------
    points:
        List of ``[x, y]`` pairs.
    axis_is_x:
        ``True``  → mirror across the X-axis (negate y).
        ``False`` → mirror across the Y-axis (negate x).

    Returns
    -------
    list of [float, float]
    """
    if axis_is_x:
        T = np.array([[ 1,  0, 0],
                      [ 0, -1, 0],
                      [ 0,  0, 1]], dtype=float)
    else:
        T = np.array([[-1,  0, 0],
                      [ 0,  1, 0],
                      [ 0,  0, 1]], dtype=float)
    return _apply_transform(points, T)


def _apply_transform(points: list, T: np.ndarray) -> list:
    """
    Apply 3×3 homogeneous matrix *T* to every point and return rounded
    ``[float, float]`` pairs.

    The rounding to 2 decimal places keeps CSV files readable and avoids
    floating-point noise accumulating across many transformation steps.
    """
    if not points:
        return []
    pts_h = np.array([[x, y, 1.0] for x, y in points])  # (N, 3)
    result = (T @ pts_h.T).T                              # (N, 3)
    return [[round(float(r[0]), 2), round(float(r[1]), 2)] for r in result]


# ---------------------------------------------------------------------------
# Shape-dict transformation
# ---------------------------------------------------------------------------

def apply_transform_to_shape(shape: dict, transform_fn, suffix: str, **kwargs) -> dict:
    """
    Apply a point-level transform function to all geometry in *shape* and
    return a new shape dict with an updated ``ShapeName``.

    ``Lines`` and ``Segments`` inside both BRep sub-dicts are copied
    unchanged — they reference point indices which remain valid because
    all supported transforms are bijections (1-to-1 point mappings).

    The flat ``Profile`` and ``Midcurve`` lists are updated in sync with
    the corresponding ``BRep["Points"]`` arrays so the two representations
    stay consistent.

    Parameters
    ----------
    shape:
        Source shape dict (not modified — a deep copy is made first).
    transform_fn:
        One of :func:`scale_points`, :func:`rotate_points`,
        :func:`translate_points`, or :func:`mirror_points`.
    suffix:
        String appended to ``ShapeName`` to identify the variant,
        e.g. ``"scaled_2.0"`` or ``"rotated_45"``.
    **kwargs:
        Keyword arguments forwarded to *transform_fn*.

    Returns
    -------
    dict
        New shape dict with transformed geometry and updated ``ShapeName``.
    """
    new_shape = copy.deepcopy(shape)
    new_shape["ShapeName"] = f"{shape['ShapeName']}_{suffix}"

    new_profile   = transform_fn(shape["Profile"],  **kwargs)
    new_midcurve  = transform_fn(shape["Midcurve"], **kwargs)

    new_shape["Profile"]  = new_profile
    new_shape["Midcurve"] = new_midcurve

    # BRep Points must stay in sync with the flat lists
    new_shape["Profile_brep"]["Points"]  = new_profile
    new_shape["Midcurve_brep"]["Points"] = new_midcurve

    # Lines and Segments are index-based — they never change
    # (deep copy already preserved them above)

    return new_shape
