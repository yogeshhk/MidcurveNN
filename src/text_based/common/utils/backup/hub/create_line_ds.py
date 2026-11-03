"""
create_line_ds.py — Line-segment dataset generator.

For every raw shape (and each of its geometric variants), this module:

1. Converts the list of polygon/polyline points into explicit ``[[x1,y1],[x2,y2]]``
   line segments.
2. Applies the full set of geometric transformations defined in ``config.py``
   (scale, rotate, translate, mirror).
3. Writes one JSON file per variant to ``JSON_FOLDER``.

Output JSON schema
------------------
::

    {
        "ShapeName":      str,
        "Profile":        [[x, y], ...],
        "Midcurve":       [[x, y], ...],
        "Profile_lines":  [[[x1,y1],[x2,y2]], ...],
        "Midcurve_lines": [[[x1,y1],[x2,y2]], ...]
    }

Topology detection
------------------
Profile shapes are always closed polygons, so profile lines are simply
consecutive pairs that wrap around to the first point.

Midcurve topology (chain vs star) is detected automatically by
``prepare_data.detect_midcurve_hub`` — no per-shape ``if/elif`` branches.
"""

import json
import os

import numpy as np

from config import (
    RAW_DATA_FOLDER,
    JSON_FOLDER,
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


# ---------------------------------------------------------------------------
# Line conversion
# ---------------------------------------------------------------------------

def profile_points_to_lines(points: list) -> list:
    """
    Convert a closed-polygon point list into explicit line segments.

    Each consecutive pair of points forms a segment, and the last point
    connects back to the first to close the polygon.

    Parameters
    ----------
    points:
        List of ``(x, y)`` tuples representing the polygon vertices.

    Returns
    -------
    list of [[x1,y1],[x2,y2]]
    """
    n = len(points)
    return [
        [list(points[i]), list(points[(i + 1) % n])]
        for i in range(n)
    ]


def midcurve_points_to_lines(points: list) -> list:
    """
    Convert a midcurve point list into explicit line segments.

    Topology is detected automatically:

    * **Chain** — consecutive pairs ``[pt_i, pt_{i+1}]``.
    * **Star**  — all segments radiate from a single hub point.

    Parameters
    ----------
    points:
        List of ``(x, y)`` tuples representing the midcurve skeleton.

    Returns
    -------
    list of [[x1,y1],[x2,y2]]
    """
    hub = detect_midcurve_hub(points)
    if hub == -1:
        # Chain topology
        return [
            [list(points[i]), list(points[i + 1])]
            for i in range(len(points) - 1)
        ]
    else:
        # Star topology: all segments connect hub to each spoke endpoint
        return [
            [list(points[hub]), list(points[i])]
            for i in range(len(points))
            if i != hub
        ]


def _add_line_fields(shape_dict: dict) -> dict:
    """
    Add ``Profile_lines`` and ``Midcurve_lines`` fields to *shape_dict*
    in-place and return it.
    """
    shape_dict["Profile_lines"] = profile_points_to_lines(shape_dict["Profile"])
    shape_dict["Midcurve_lines"] = midcurve_points_to_lines(shape_dict["Midcurve"])
    return shape_dict


# ---------------------------------------------------------------------------
# JSON persistence
# ---------------------------------------------------------------------------

def write_shape_to_json(shape_dict: dict, output_folder: str = JSON_FOLDER) -> None:
    """
    Serialise *shape_dict* to ``<output_folder>/<ShapeName>.json``.

    Parameters
    ----------
    shape_dict:
        A fully populated shape dict (with ``Profile_lines`` / ``Midcurve_lines``).
    output_folder:
        Directory in which to write the JSON file.  Created if absent.
    """
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, shape_dict["ShapeName"] + ".json")
    with open(filepath, "w") as fh:
        json.dump(shape_dict, fh, indent=4)


def convert_and_save(shape_dicts: list, output_folder: str = JSON_FOLDER) -> None:
    """
    Add line fields to each shape dict in *shape_dicts* and write a JSON file
    for every entry.

    Parameters
    ----------
    shape_dicts:
        List of shape dicts (``ShapeName``, ``Profile``, ``Midcurve``).
    output_folder:
        Destination directory for JSON files.
    """
    for dct in shape_dicts:
        _add_line_fields(dct)
        write_shape_to_json(dct, output_folder)


# ---------------------------------------------------------------------------
# Transformation helpers
# ---------------------------------------------------------------------------

def _build_scaled_variants(shape_dicts: list) -> list:
    """
    Return a list of scaled shape dicts for every factor in the configured
    scale range.
    """
    variants = []
    factors = np.arange(SCALE_START, SCALE_STOP, SCALE_STEP)
    for factor in factors:
        for dct in shape_dicts:
            variants.append({
                "ShapeName": f"{dct['ShapeName']}_scaled_{round(factor, 4)}",
                "Profile":   scale_sequence(dct["Profile"], factor),
                "Midcurve":  scale_sequence(dct["Midcurve"], factor),
            })
    return variants


def _build_rotated_variants(shape_dicts: list) -> list:
    """
    Return a list of rotated shape dicts for every angle in the configured
    rotation range.
    """
    variants = []
    for theta in range(ROTATE_START, ROTATE_STOP, ROTATE_STEP):
        for dct in shape_dicts:
            variants.append({
                "ShapeName": f"{dct['ShapeName']}_rotated_{theta}",
                "Profile":   rotate_sequence(dct["Profile"], theta),
                "Midcurve":  rotate_sequence(dct["Midcurve"], theta),
            })
    return variants


def _build_translated_variants(shape_dicts: list) -> list:
    """
    Return a list of translated shape dicts for every ``(dx, dy)`` combination
    in the configured translation ranges.

    Both axes are varied independently, generating axial, diagonal, and
    arbitrary translations — not just ``dx == dy`` variants.
    """
    variants = []
    x_values = range(TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP)
    y_values = range(TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP)
    for dx in x_values:
        for dy in y_values:
            for dct in shape_dicts:
                variants.append({
                    "ShapeName": f"{dct['ShapeName']}_translated_{dx}_{dy}",
                    "Profile":   translate_sequence(dct["Profile"], dx, dy),
                    "Midcurve":  translate_sequence(dct["Midcurve"], dx, dy),
                })
    return variants


def _build_mirrored_variants(shape_dicts: list) -> list:
    """Return mirror-x and mirror-y variants for every shape in *shape_dicts*."""
    variants = []
    for axis_is_x, suffix in [(True, "mirrored_x"), (False, "mirrored_y")]:
        for dct in shape_dicts:
            variants.append({
                "ShapeName": f"{dct['ShapeName']}_{suffix}",
                "Profile":   mirror_sequence(dct["Profile"], axis_is_x),
                "Midcurve":  mirror_sequence(dct["Midcurve"], axis_is_x),
            })
    return variants


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Read raw .dat / .mid pairs
    original_shapes = read_dat_files(RAW_DATA_FOLDER)
    print(f"Loaded {len(original_shapes)} shape(s): "
          f"{[d['ShapeName'] for d in original_shapes]}")

    # Original shapes
    convert_and_save(original_shapes)

    # Scaled variants
    convert_and_save(_build_scaled_variants(original_shapes))

    # Rotated variants
    convert_and_save(_build_rotated_variants(original_shapes))

    # Translated variants (independent dx and dy)
    convert_and_save(_build_translated_variants(original_shapes))

    # Mirrored variants
    convert_and_save(_build_mirrored_variants(original_shapes))

    print("Done. JSON files written to:", JSON_FOLDER)
