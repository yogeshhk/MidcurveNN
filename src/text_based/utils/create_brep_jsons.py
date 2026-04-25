"""
convert_to_brep_json.py — Two-stage converter from raw shape files to BRep JSON.

Given a pair of files in ``RAW_DATA_FOLDER``:
  - ``<ShapeName>.dat``                        — profile polygon (one x y per line)
  - ``<ShapeName>_MidcurvesByYogeshMethod.txt`` — Yogesh method output

This script runs two stages for every matching pair it finds:

Stage 1 — Extract midcurve → write ``<ShapeName>.mid``
    Parse the Yogesh txt file, extract the ordered unique midcurve points,
    and write them as a plain ``x y`` point file (one point per line).

Stage 2 — Build BRep JSON → write ``<ShapeName>.json``
    Read the ``.dat`` and the freshly written ``.mid``, build full BRep
    structures for both profile and midcurve, and write the self-contained
    JSON used by the rest of the pipeline.

Yogesh txt file structure
--------------------------
::

    <pt1_x>  <pt1_y>          ← midcurve segment 0, point A
    <pt2_x>  <pt2_y>          ← midcurve segment 0, point B
                               ← 2 blank lines between consecutive segments
                               ←
    <pt3_x>  <pt3_y>          ← midcurve segment 1, point A
    <pt4_x>  <pt4_y>          ← midcurve segment 1, point B
                               ← 4 blank lines separate midcurve section
                               ← from profile section
                               ←
                               ←
    <x0>  <y0>                 ← profile point 0  (closed polygon —
    <x1>  <y1>                   first point is repeated at the end)
    ...
    <x0>  <y0>                 ← closing point (same as first)

The 4-blank-line separator (5 consecutive newlines) is the reliable
structural marker used to split the two sections.

BRep conventions used
---------------------
Profile BRep
    Closed polygon → N points, N lines (consecutive index pairs wrapping
    back to 0), one segment containing all line indices.

Midcurve BRep
    Topology is read directly from the Yogesh segments:
    - Each input segment becomes one ``Line`` (pair of point indices).
    - Each ``Line`` is its own ``Segment`` (independent arm or chain piece).
    - Points are de-duplicated in first-appearance order; shared junction
      points naturally appear once in the ``Points`` list and are referenced
      by multiple ``Lines``.

Usage
-----
::

    python convert_to_brep_json.py                  # process all pairs found
    python convert_to_brep_json.py --shape L        # process one shape only
    python convert_to_brep_json.py --dry-run        # parse and print, no files written
"""

import argparse
import json
import os
import re
import sys

from config import RAW_DATA_FOLDER


# ---------------------------------------------------------------------------
# Stage 1 helpers — parse Yogesh txt → .mid
# ---------------------------------------------------------------------------

def _parse_yogesh_txt(filepath: str) -> tuple[list, list]:
    """
    Parse a ``*_MidcurvesByYogeshMethod.txt`` file.

    Parameters
    ----------
    filepath:
        Path to the Yogesh method text file.

    Returns
    -------
    (midcurve_segments, profile_points)

    ``midcurve_segments`` is a list of segments; each segment is a list of
    ``[x, y]`` pairs (always exactly 2 for axis-aligned shapes).

    ``profile_points`` is the flat ``[[x, y], ...]`` polygon list with the
    closing repeated point removed.

    Raises
    ------
    ValueError
        If the 4-blank-line separator is not found (malformed file).
    """
    with open(filepath, "rb") as fh:
        raw = fh.read()

    # Normalise line endings
    text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

    # Split on 4+ blank lines (= 5+ consecutive newline characters)
    parts = re.split(r"\n{5,}", text)
    if len(parts) < 2:
        raise ValueError(
            f"{filepath}: expected 4-blank-line separator between midcurve "
            "section and profile section, but none found."
        )

    def _parse_block(block: str) -> list:
        """Split a text block on single blank lines into groups of float pairs."""
        groups: list = []
        current: list = []
        for line in block.strip().split("\n"):
            stripped = line.strip()
            if stripped == "":
                if current:
                    groups.append(current[:])
                    current = []
            else:
                current.append([float(v) for v in stripped.split()])
        if current:
            groups.append(current)
        return groups

    mid_groups     = _parse_block(parts[0])
    profile_groups = _parse_block(parts[1])

    if not profile_groups:
        raise ValueError(f"{filepath}: no profile points found after separator.")

    profile_pts = profile_groups[0]

    # Remove the closing repeated point if the polygon is closed
    if (len(profile_pts) > 1
            and abs(profile_pts[0][0] - profile_pts[-1][0]) < 1e-9
            and abs(profile_pts[0][1] - profile_pts[-1][1]) < 1e-9):
        profile_pts = profile_pts[:-1]

    return mid_groups, profile_pts


def _ordered_unique_points(segments: list) -> list:
    """
    Return a de-duplicated list of all points that appear in *segments*,
    in first-appearance order.

    Shared junction points appear exactly once, preserving the natural
    index assignment used when building the BRep.

    Parameters
    ----------
    segments:
        List of segments; each segment is a list of ``[x, y]`` pairs.

    Returns
    -------
    list of ``[float, float]``
    """
    seen: set = set()
    ordered: list = []
    for seg in segments:
        for pt in seg:
            key = (pt[0], pt[1])
            if key not in seen:
                ordered.append([pt[0], pt[1]])
                seen.add(key)
    return ordered


def write_mid_file(mid_points: list, filepath: str) -> None:
    """
    Write a ``.mid`` file: one ``x y`` coordinate pair per line.

    Parameters
    ----------
    mid_points:
        Ordered list of ``[x, y]`` pairs.
    filepath:
        Destination path.
    """
    lines = []
    for pt in mid_points:
        x = int(pt[0]) if pt[0] == int(pt[0]) else pt[0]
        y = int(pt[1]) if pt[1] == int(pt[1]) else pt[1]
        lines.append(f"{x} {y}")
    with open(filepath, "w") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Stage 2 helpers — build BRep JSON
# ---------------------------------------------------------------------------

def _build_profile_brep(profile_pts: list) -> dict:
    """
    Build a BRep sub-dict for a closed polygon profile.

    Every closed polygon has the same topology regardless of shape:
    N points → N lines (consecutive pairs wrapping back to 0) →
    one segment containing all line indices.

    Parameters
    ----------
    profile_pts:
        ``[[x, y], ...]`` polygon vertices (not closed — no repeated point).

    Returns
    -------
    dict with keys ``Points``, ``Lines``, ``Segments``.
    """
    n = len(profile_pts)
    lines    = [[i, (i + 1) % n] for i in range(n)]
    segments = [list(range(n))]
    return {
        "Points":   profile_pts,
        "Lines":    lines,
        "Segments": segments,
    }


def _build_midcurve_brep(mid_pts: list, mid_segments: list) -> dict:
    """
    Build a BRep sub-dict for the midcurve skeleton.

    Topology is taken directly from the Yogesh segments:
    each input segment becomes one ``Line`` (index pair), and each ``Line``
    is its own ``Segment``.  Shared junction points are referenced by
    multiple ``Lines`` via their single index in ``Points``.

    Parameters
    ----------
    mid_pts:
        De-duplicated ordered point list (from :func:`_ordered_unique_points`).
    mid_segments:
        Raw segment list from the Yogesh txt parser.

    Returns
    -------
    dict with keys ``Points``, ``Lines``, ``Segments``.
    """
    idx = {(pt[0], pt[1]): i for i, pt in enumerate(mid_pts)}
    lines    = [[idx[(seg[0][0], seg[0][1])],
                 idx[(seg[1][0], seg[1][1])]] for seg in mid_segments]
    segments = [[i] for i in range(len(lines))]
    return {
        "Points":   mid_pts,
        "Lines":    lines,
        "Segments": segments,
    }


def _read_dat_file(filepath: str) -> list:
    """
    Read a ``.dat`` profile file and return ``[[x, y], ...]``.

    Parameters
    ----------
    filepath:
        Path to the ``.dat`` file.

    Returns
    -------
    list of ``[float, float]``
    """
    pts = []
    with open(filepath) as fh:
        for line in fh:
            stripped = line.strip()
            if stripped:
                pts.append([float(v) for v in stripped.split()])
    return pts


def _build_shape_json(shape_name: str,
                      profile_pts: list,
                      mid_pts: list,
                      mid_segments: list) -> dict:
    """
    Assemble the complete shape dict in the pipeline's standard JSON schema.

    Parameters
    ----------
    shape_name:
        e.g. ``"L"``, ``"T"``, ``"Plus"``.
    profile_pts:
        Polygon vertices from the ``.dat`` file.
    mid_pts:
        De-duplicated ordered midcurve points.
    mid_segments:
        Raw Yogesh segments (used to build topology).

    Returns
    -------
    dict matching the pipeline JSON schema.
    """
    return {
        "ShapeName":     shape_name,
        "Profile":       profile_pts,
        "Midcurve":      mid_pts,
        "Profile_brep":  _build_profile_brep(profile_pts),
        "Midcurve_brep": _build_midcurve_brep(mid_pts, mid_segments),
    }


def write_json_file(shape_dict: dict, filepath: str) -> None:
    """
    Write the shape dict to a JSON file with 4-space indentation.

    Parameters
    ----------
    shape_dict:
        Complete shape dict.
    filepath:
        Destination path.
    """
    with open(filepath, "w") as fh:
        json.dump(shape_dict, fh, indent=4)


# ---------------------------------------------------------------------------
# Discovery — find all processable pairs in RAW_DATA_FOLDER
# ---------------------------------------------------------------------------

YOGESH_SUFFIX = "_MidcurvesByYogeshMethod.txt"


def find_shape_pairs(datafolder: str) -> list:
    """
    Scan *datafolder* for ``<ShapeName>.dat`` /
    ``<ShapeName>_MidcurvesByYogeshMethod.txt`` pairs.

    A shape is included only if both files are present.

    Parameters
    ----------
    datafolder:
        Directory to scan.

    Returns
    -------
    list of ``(shape_name, dat_path, txt_path)`` tuples, sorted by shape name.
    """
    files = set(os.listdir(datafolder))
    pairs = []

    for filename in sorted(files):
        if not filename.endswith(".dat"):
            continue
        shape_name = filename[:-4]   # strip ".dat"
        txt_name   = shape_name + YOGESH_SUFFIX
        if txt_name in files:
            pairs.append((
                shape_name,
                os.path.join(datafolder, filename),
                os.path.join(datafolder, txt_name),
            ))

    return pairs


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_shape(shape_name: str,
                  dat_path: str,
                  txt_path: str,
                  datafolder: str,
                  dry_run: bool = False) -> None:
    """
    Run both stages for a single shape and write output files.

    Stage 1: ``<ShapeName>_MidcurvesByYogeshMethod.txt`` → ``<ShapeName>.mid``
    Stage 2: ``<ShapeName>.dat`` + ``<ShapeName>.mid``   → ``<ShapeName>.json``

    Parameters
    ----------
    shape_name:
        Shape identifier, e.g. ``"L"``.
    dat_path:
        Path to the ``.dat`` file.
    txt_path:
        Path to the Yogesh txt file.
    datafolder:
        Output directory (same as input — keeps all raw files together).
    dry_run:
        If ``True``, parse and print results without writing any files.
    """
    mid_path  = os.path.join(datafolder, shape_name + ".mid")
    json_path = os.path.join(datafolder, shape_name + ".json")

    print(f"\n{'─'*60}")
    print(f"  Shape: {shape_name}")
    print(f"{'─'*60}")

    # ------------------------------------------------------------------
    # Stage 1 — Parse Yogesh txt → extract midcurve → write .mid
    # ------------------------------------------------------------------
    print(f"\n  Stage 1: {os.path.basename(txt_path)} → {os.path.basename(mid_path)}")

    mid_segments, profile_from_txt = _parse_yogesh_txt(txt_path)
    mid_pts = _ordered_unique_points(mid_segments)

    print(f"    Midcurve segments parsed : {len(mid_segments)}")
    for i, seg in enumerate(mid_segments):
        print(f"      seg[{i}]: {seg[0]} → {seg[1]}")
    print(f"    Unique midcurve points   : {len(mid_pts)}")
    for pt in mid_pts:
        print(f"      {pt}")

    if not dry_run:
        write_mid_file(mid_pts, mid_path)
        print(f"    Written → {mid_path}")
    else:
        print(f"    [dry-run] would write → {mid_path}")

    # ------------------------------------------------------------------
    # Stage 2 — Load .dat + .mid → build BRep JSON → write .json
    # ------------------------------------------------------------------
    print(f"\n  Stage 2: {os.path.basename(dat_path)} + "
          f"{os.path.basename(mid_path)} → {os.path.basename(json_path)}")

    profile_pts = _read_dat_file(dat_path)

    # Sanity check: profile in txt must match the .dat file
    if len(profile_pts) != len(profile_from_txt):
        raise ValueError(
            f"{shape_name}: profile from txt has {len(profile_from_txt)} points "
            f"but .dat has {len(profile_pts)} points."
        )
    for i, (a, b) in enumerate(zip(profile_pts, profile_from_txt)):
        if abs(a[0]-b[0]) > 1e-6 or abs(a[1]-b[1]) > 1e-6:
            raise ValueError(
                f"{shape_name}: profile point {i} mismatch — "
                f"dat={a}, txt={b}"
            )

    shape_dict = _build_shape_json(shape_name, profile_pts, mid_pts, mid_segments)

    print(f"    Profile  : {len(profile_pts)} pts, "
          f"{len(shape_dict['Profile_brep']['Lines'])} lines, "
          f"{len(shape_dict['Profile_brep']['Segments'])} segment(s)")
    print(f"    Midcurve : {len(mid_pts)} pts, "
          f"{len(shape_dict['Midcurve_brep']['Lines'])} lines, "
          f"{len(shape_dict['Midcurve_brep']['Segments'])} segment(s)")
    print(f"    Mid BRep Lines    : {shape_dict['Midcurve_brep']['Lines']}")
    print(f"    Mid BRep Segments : {shape_dict['Midcurve_brep']['Segments']}")

    if not dry_run:
        write_json_file(shape_dict, json_path)
        print(f"    Written → {json_path}")
    else:
        print(f"    [dry-run] would write → {json_path}")


def run(datafolder: str = RAW_DATA_FOLDER,
        shape_filter: str | None = None,
        dry_run: bool = False) -> None:
    """
    Discover all ``.dat`` / Yogesh txt pairs in *datafolder* and process them.

    Parameters
    ----------
    datafolder:
        Directory containing input files and receiving output files.
    shape_filter:
        If given, process only the shape with this name.
    dry_run:
        Parse and print without writing any files.
    """
    pairs = find_shape_pairs(datafolder)

    if not pairs:
        print(f"No .dat / {YOGESH_SUFFIX} pairs found in: {datafolder}")
        sys.exit(1)

    if shape_filter:
        pairs = [(n, d, t) for n, d, t in pairs if n == shape_filter]
        if not pairs:
            print(f"Shape '{shape_filter}' not found in: {datafolder}")
            sys.exit(1)

    print(f"Found {len(pairs)} shape pair(s) in: {datafolder}")
    if shape_filter:
        print(f"(filtered to: {shape_filter})")
    if dry_run:
        print("DRY RUN — no files will be written.")

    for shape_name, dat_path, txt_path in pairs:
        process_shape(shape_name, dat_path, txt_path, datafolder, dry_run=dry_run)

    print(f"\n{'─'*60}")
    print(f"  Done. Processed {len(pairs)} shape(s).")
    print(f"{'─'*60}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Convert <shape>.dat + <shape>_MidcurvesByYogeshMethod.txt "
            "→ <shape>.mid + <shape>.json (BRep format)."
        )
    )
    parser.add_argument(
        "--shape", "-s",
        metavar="NAME",
        default=None,
        help="Process only this shape name (e.g. --shape L). "
             "Default: process all pairs found in RAW_DATA_FOLDER.",
    )
    parser.add_argument(
        "--folder", "-f",
        metavar="DIR",
        default=RAW_DATA_FOLDER,
        help=f"Input/output directory. Default: RAW_DATA_FOLDER from config.py "
             f"({RAW_DATA_FOLDER}).",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        default=False,
        help="Parse and print results without writing any files.",
    )
    args = parser.parse_args()
    run(datafolder=args.folder, shape_filter=args.shape, dry_run=args.dry_run)