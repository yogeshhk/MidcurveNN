"""
prepare_data.py — Core data layer for the Midcurve Dataset Pipeline.

Responsibilities
----------------
1. Read raw ``.dat`` (profile polygon) and ``.mid`` (midcurve polyline) file pairs
   from a folder and assemble them into Python dicts.
2. Provide coordinate-level geometric transformations (scale, rotate, translate,
   mirror) implemented as 3×3 homogeneous-matrix operations so they can be
   composed if needed.
3. Provide a generic midcurve topology detector that determines whether the
   midcurve points form a simple chain (polyline) or a star/tree (one hub
   connected to several terminal spokes).  This replaces all shape-name-based
   ``if``/``elif`` branches in the original code.
4. Provide plotting utilities for visual inspection.

Data format
-----------
Each ``.dat`` / ``.mid`` file contains one ``x y`` coordinate pair per line.

* ``.dat``  — closed polygon (last point implicitly connects back to first).
* ``.mid``  — open polyline or star skeleton; topology is auto-detected.

A *shape dict* has the following keys after loading::

    {
        "ShapeName": str,
        "Profile":   [(x, y), ...],   # closed polygon vertices
        "Midcurve":  [(x, y), ...],   # midcurve skeleton points
    }
"""

import json
import math
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

from config import RAW_DATA_FOLDER, SEQUENCES_FILEPATH

np.set_printoptions(threshold=sys.maxsize)


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _get_index(shapename: str, profile_dict_list: list) -> int:
    """Return the list index of the dict whose ShapeName matches *shapename*, or -1."""
    for i, dct in enumerate(profile_dict_list):
        if dct["ShapeName"] == shapename:
            return i
    return -1


def _get_or_create_profile_dict(shapename: str, profiles_dict_list: list) -> dict:
    """
    Return the existing dict for *shapename* from *profiles_dict_list*, or
    create and return a new one if it is not yet present.
    """
    i = _get_index(shapename, profiles_dict_list)
    if i == -1:
        return {"ShapeName": shapename}
    return profiles_dict_list[i]


def read_dat_files(datafolder: str = RAW_DATA_FOLDER) -> list:
    """
    Scan *datafolder* for ``.dat`` / ``.mid`` file pairs and parse them into
    a list of shape dicts.

    Files are paired by base-name: ``Foo.dat`` and ``Foo.mid`` together produce
    a dict with ``ShapeName == "Foo"``.  Shapes that are missing either file
    are silently skipped.

    Parameters
    ----------
    datafolder:
        Directory that contains the ``.dat`` and ``.mid`` files.

    Returns
    -------
    list of dict
        Each dict has keys ``ShapeName``, ``Profile``, and ``Midcurve``.
    """
    profiles_dict_list: list = []

    for filename in os.listdir(datafolder):
        filepath = os.path.join(datafolder, filename)
        if os.path.isdir(filepath):
            continue

        base = filename.split(".")[0]
        profile_dict = _get_or_create_profile_dict(base, profiles_dict_list)

        if filename.endswith(".dat"):
            with open(filepath) as fh:
                profile_dict["Profile"] = [
                    tuple(map(float, line.split())) for line in fh
                ]
        elif filename.endswith(".mid"):
            with open(filepath) as fh:
                profile_dict["Midcurve"] = [
                    tuple(map(float, line.split())) for line in fh
                ]

        if _get_index(profile_dict["ShapeName"], profiles_dict_list) == -1:
            profiles_dict_list.append(profile_dict)

    # Drop incomplete shapes (missing Profile or Midcurve)
    complete = [
        d for d in profiles_dict_list
        if "Profile" in d and "Midcurve" in d
    ]
    skipped = len(profiles_dict_list) - len(complete)
    if skipped:
        print(
            f"[read_dat_files] WARNING: {skipped} shape(s) skipped "
            "due to missing .dat or .mid file."
        )
    return complete


# ---------------------------------------------------------------------------
# Geometric transformations (homogeneous 3×3 matrices)
# ---------------------------------------------------------------------------

def scale_sequence(sequence: list, factor: float = 1.0) -> list:
    """
    Scale all points in *sequence* by *factor* around the origin.

    Parameters
    ----------
    sequence:
        List of ``(x, y)`` tuples.
    factor:
        Uniform scale factor applied to both axes.

    Returns
    -------
    list of (float, float)
    """
    T = np.array([[factor, 0, 0],
                  [0, factor, 0],
                  [0, 0,      1]])
    return _apply_transform(sequence, T)


def rotate_sequence(sequence: list, theta_deg: float = 30.0) -> list:
    """
    Rotate all points in *sequence* by *theta_deg* degrees counter-clockwise
    around the origin.

    Parameters
    ----------
    sequence:
        List of ``(x, y)`` tuples.
    theta_deg:
        Rotation angle in degrees.

    Returns
    -------
    list of (float, float)
    """
    theta = math.radians(theta_deg)
    c, s = math.cos(theta), math.sin(theta)
    T = np.array([[ c, -s, 0],
                  [ s,  c, 0],
                  [ 0,  0, 1]])
    return _apply_transform(sequence, T)


def translate_sequence(
    sequence: list,
    distance_x: float = 10.0,
    distance_y: float = 10.0,
) -> list:
    """
    Translate all points in *sequence* by ``(distance_x, distance_y)``.

    Parameters
    ----------
    sequence:
        List of ``(x, y)`` tuples.
    distance_x:
        Horizontal displacement.
    distance_y:
        Vertical displacement.

    Returns
    -------
    list of (float, float)
    """
    T = np.array([[1, 0, distance_x],
                  [0, 1, distance_y],
                  [0, 0, 1]])
    return _apply_transform(sequence, T)


def mirror_sequence(sequence: list, axis_is_x: bool = True) -> list:
    """
    Mirror all points in *sequence* across the X-axis (``axis_is_x=True``)
    or across the Y-axis (``axis_is_x=False``).

    Parameters
    ----------
    sequence:
        List of ``(x, y)`` tuples.
    axis_is_x:
        ``True``  → mirror across X-axis (negate y).
        ``False`` → mirror across Y-axis (negate x).

    Returns
    -------
    list of (float, float)
    """
    if axis_is_x:
        T = np.array([[ 1,  0, 0],
                      [ 0, -1, 0],
                      [ 0,  0, 1]])
    else:
        T = np.array([[-1,  0, 0],
                      [ 0,  1, 0],
                      [ 0,  0, 1]])
    return _apply_transform(sequence, T)


def _apply_transform(sequence: list, T: np.ndarray) -> list:
    """
    Apply homogeneous transformation matrix *T* (3×3) to every point in
    *sequence* and return the result as a list of ``(float, float)`` tuples.
    """
    pts_h = np.array([(x, y, 1.0) for x, y in sequence])
    transformed = (T @ pts_h.T).T          # shape (N, 3)
    return [(round(float(r[0]), 2), round(float(r[1]), 2)) for r in transformed]


# ---------------------------------------------------------------------------
# Generic midcurve topology detection
# ---------------------------------------------------------------------------

def detect_midcurve_hub(points: list) -> int:
    """
    Determine whether the midcurve points form a *star* topology (one hub
    connected to several terminal spokes) or a *chain* topology (simple
    polyline).

    Algorithm
    ---------
    1. Compute the geometric centroid of all points.
    2. Identify the point closest to the centroid as the *hub candidate*.
    3. Compute the angular spread of all other points around the candidate.
    4. If the angular spread exceeds 180° the candidate is a genuine hub
       (rays extend in more than two distinct directions, which a chain cannot
       produce) → return its index.
    5. Otherwise return ``-1`` (chain topology).

    Parameters
    ----------
    points:
        List of ``(x, y)`` tuples representing the midcurve.

    Returns
    -------
    int
        Index of the hub point, or ``-1`` if the midcurve is a simple chain.
    """
    n = len(points)
    if n <= 2:
        return -1   # single segment — unambiguously a chain

    pts = np.array(points, dtype=float)
    centroid = pts.mean(axis=0)

    distances_to_centroid = np.linalg.norm(pts - centroid, axis=1)
    hub_candidate = int(np.argmin(distances_to_centroid))

    hub_pos = pts[hub_candidate]
    other_pts = np.delete(pts, hub_candidate, axis=0)
    vectors = other_pts - hub_pos

    angles = np.arctan2(vectors[:, 1], vectors[:, 0])
    angular_span = float(np.max(angles) - np.min(angles))

    if angular_span > math.pi:      # spokes fan out in > 180° → star
        return hub_candidate
    return -1                       # all spokes point in the same half-plane → chain


# ---------------------------------------------------------------------------
# Plotting utilities
# ---------------------------------------------------------------------------

def _plot_point_sequence(sequence: list, close: bool = False, color: str = "black",
                          linestyle: str = "solid") -> None:
    """Internal helper: plot a sequence of (x, y) points."""
    xs = [p[0] for p in sequence]
    ys = [p[1] for p in sequence]
    if close:
        xs.append(xs[0])
        ys.append(ys[0])
    plt.scatter(xs, ys, color=color, s=20, zorder=3)
    plt.plot(xs, ys, color=color, linestyle=linestyle)


def plot_profile_dict(profile_dict: dict) -> None:
    """
    Display a single shape dict — profile as a closed black solid polygon,
    midcurve as an open red dashed polyline.

    Parameters
    ----------
    profile_dict:
        A shape dict with keys ``ShapeName``, ``Profile``, and ``Midcurve``.
    """
    plt.figure()
    ax = plt.gca()
    _plot_point_sequence(profile_dict["Profile"], close=True,
                          color="black", linestyle="solid")
    _plot_point_sequence(profile_dict["Midcurve"], close=False,
                          color="red", linestyle="dashed")
    ax.set_aspect("equal")
    ax.grid(True)
    plt.title(profile_dict["ShapeName"])
    plt.tight_layout()
    plt.show()


def generate_sequences(
    sequences_filepath: str = SEQUENCES_FILEPATH,
    recreate_data: bool = False,
) -> list:
    """
    Generate all transformed sequence variants for every shape found in
    :data:`RAW_DATA_FOLDER` and persist them to *sequences_filepath* as JSON.

    If the file already exists and *recreate_data* is ``False``, the function
    returns an empty list without regenerating anything.

    Parameters
    ----------
    sequences_filepath:
        Path to the output JSON file.
    recreate_data:
        Force regeneration even if the file already exists.

    Returns
    -------
    list of dict
        The list of shape dicts (populated with transformation variants).
    """
    import numpy as np

    profiles_dict_list: list = []
    if not os.path.exists(sequences_filepath) or recreate_data:
        with open(sequences_filepath, "w") as fout:
            print("Transformed sequence JSON not found — regenerating…")
            profiles_dict_list = read_dat_files()

            for profile_dict in profiles_dict_list:
                # Scale
                for i, factor in enumerate(np.linspace(1.2, 2.2, 10)):
                    key = str(i + 1)
                    profile_dict[f"Scaled_Profile_{key}"] = scale_sequence(
                        profile_dict["Profile"], factor
                    )
                    profile_dict[f"Scaled_Midcurve_{key}"] = scale_sequence(
                        profile_dict["Midcurve"], factor
                    )

                # Translate (independent x and y, not just diagonal)
                for ix, dx in enumerate(np.linspace(-100, 110, 20)):
                    for iy, dy in enumerate(np.linspace(-100, 110, 20)):
                        key = f"{ix + 1}_{iy + 1}"
                        profile_dict[f"Translated_Profile_{key}"] = translate_sequence(
                            profile_dict["Profile"], dx, dy
                        )
                        profile_dict[f"Translated_Midcurve_{key}"] = translate_sequence(
                            profile_dict["Midcurve"], dx, dy
                        )

                # Rotate
                for i, theta in enumerate(np.linspace(30, 370, 12)):
                    key = str(i + 1)
                    profile_dict[f"Rotated_Profile_{key}"] = rotate_sequence(
                        profile_dict["Profile"], theta
                    )
                    profile_dict[f"Rotated_Midcurve_{key}"] = rotate_sequence(
                        profile_dict["Midcurve"], theta
                    )

                plot_profile_dict(profile_dict)

            json.dump(profiles_dict_list, fout)

    return profiles_dict_list


if __name__ == "__main__":
    sequences = generate_sequences(recreate_data=True)
    print(sequences)
