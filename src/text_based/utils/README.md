# Midcurve Generation Pipeline — Program Flow Documentation

## Overview

This pipeline converts 2D polygonal profile shapes and their 1D polyline
midcurves into a large augmented dataset, using geometric transformations
(scale, rotate, translate, mirror) to generate thousands of variants from a
small set of originals.

The dataset is intended as training/evaluation data for models that learn to
predict a midcurve from a profile — a core step in thin-wall structural
analysis.

### What changed from the original design

The original pipeline had two generators (`create_line_ds.py` and
`create_brep_csvs.py`) and inferred midcurve topology at runtime using
shape-name `if/elif` branches.  The current design eliminates both problems:

- **One generator only** — `create_brep_csvs.py`. Line-based JSON output
  (`create_line_ds.py`) is no longer needed; the BRep JSON is the complete
  representation.
- **No topology inference** — connectivity is authored once per shape in a
  hand-written JSON file and carried through every transformation unchanged.
  Adding a new shape never requires touching pipeline code.
- **Automated onboarding** — `create_brep_jsons.py` converts the raw
  `.dat` + `_MidcurvesByYogeshMethod.txt` pair for a new shape into a `.mid`
  file and a ready-to-use `.json` in one command, removing the need to author
  JSON by hand.

---

## Repository Layout

```
<project_root>/
    config.py                   ← all paths and transformation parameters
    prepare_data.py             ← I/O and geometric transforms (no plotting)
    prepare_plots.py            ← all visualization functions
    create_brep_jsons.py        ← onboarding: dat + Yogesh txt → mid + json
    create_brep_csvs.py         ← dataset generator (run this to build CSVs)
    data/
        raw/                    ← shape source files live here
            I.dat  I.mid  I.json
            L.dat  L.mid  L.json  L_MidcurvesByYogeshMethod.txt
            T.dat  T.mid  T.json  T_MidcurvesByYogeshMethod.txt
            Plus.dat  Plus.mid  Plus.json  Plus_MidcurvesByYogeshMethod.txt
        brep/                   ← generated CSV files written here
    models/
```

---

## Adding a New Shape — Recommended Workflow

The typical workflow for onboarding a new shape is now automated:

```
<ShapeName>.dat  +  <ShapeName>_MidcurvesByYogeshMethod.txt
        │
        ▼  python create_brep_jsons.py --shape <ShapeName>
        │
        ├── <ShapeName>.mid    (Stage 1 — midcurve point file)
        └── <ShapeName>.json   (Stage 2 — self-contained BRep JSON)
```

After running the converter, `<ShapeName>.json` is immediately usable by
`create_brep_csvs.py` — no further manual editing required.

---

## File-by-File Reference

### `create_brep_jsons.py` — Shape onboarding converter

Scans `RAW_DATA_FOLDER` for `<ShapeName>.dat` /
`<ShapeName>_MidcurvesByYogeshMethod.txt` pairs and runs two stages per pair.

#### Stage 1 — Extract midcurve → write `<ShapeName>.mid`

Parses the Yogesh method txt file, extracts the ordered unique midcurve
points, and writes them as a plain `x y` point file (one point per line),
matching the original `.mid` format.

**Yogesh txt file structure:**

```
125   0          ← midcurve segment 0, point A
125   225        ← midcurve segment 0, point B
                 ← 2 blank lines separate consecutive segments
                 ←
250   225        ← midcurve segment 1, point A
0     225        ← midcurve segment 1, point B
                 ← 4 blank lines separate midcurve section from profile
                 ←
                 ←
                 ←
0     250        ← profile polygon (closed — first point repeated at end)
250   250
...
0     250        ← closing point
```

The 4-blank-line separator (5 consecutive newlines) is the reliable structural
marker.  Points are de-duplicated in first-appearance order; shared junction
points appear exactly once in the output.

#### Stage 2 — Build BRep JSON → write `<ShapeName>.json`

Reads the `.dat` and the freshly written `.mid`, builds full BRep structures
for both profile and midcurve, cross-checks that the profile in the txt matches
the `.dat`, and writes the self-contained JSON.

**BRep conventions applied:**

- **Profile** — closed polygon: N points → N lines (consecutive index pairs
  wrapping back to 0) → one segment containing all line indices.
- **Midcurve** — topology from Yogesh segments: each input segment becomes one
  `Line` (index pair), each `Line` is its own `Segment`.  Shared junction
  points appear once in `Points` and are referenced by multiple `Lines`.

#### CLI usage

```bash
python create_brep_jsons.py                   # process all pairs found
python create_brep_jsons.py --shape L         # one shape only
python create_brep_jsons.py --dry-run         # parse and print, no files written
python create_brep_jsons.py --folder path/to/ # override RAW_DATA_FOLDER
```

#### Example output for T

```
Stage 1: T_MidcurvesByYogeshMethod.txt → T.mid
  seg[0]: [125.0, 0.0] → [125.0, 225.0]
  seg[1]: [250.0, 225.0] → [0.0, 225.0]
  Unique midcurve points: 4

Stage 2: T.dat + T.mid → T.json
  Profile  : 8 pts, 8 lines, 1 segment(s)
  Midcurve : 4 pts, 2 lines, 2 segment(s)
  Mid BRep Lines    : [[0, 1], [2, 3]]
  Mid BRep Segments : [[0], [1]]
```

---

### `config.py` — Central configuration

Single source of truth for all paths and transformation ranges.  All pipeline
scripts import from here so ranges are never duplicated.

```python
# Paths
RAW_DATA_FOLDER = "data/raw"
BREP_FOLDER     = "data/brep"

# Scale: np.arange(2.0, 6.0, 0.25) → 16 factors
SCALE_START, SCALE_STOP, SCALE_STEP = 2.0, 6.0, 0.25

# Rotate: range(1, 181, 1) → 180 angles (1° through 180°)
ROTATE_START, ROTATE_STOP, ROTATE_STEP = 1, 181, 1

# Translate: x and y varied independently
# range(-50, 51, 2) → 51 values each → 2,601 (dx,dy) combinations
TRANSLATE_X_START, TRANSLATE_X_STOP, TRANSLATE_X_STEP = -50, 51, 2
TRANSLATE_Y_START, TRANSLATE_Y_STOP, TRANSLATE_Y_STEP = -50, 51, 2
```

---

### `prepare_data.py` — I/O and geometric transforms

Pure data layer — no matplotlib dependency.

#### I/O functions

| Function | Description |
|---|---|
| `read_shape_json(filepath)` | Load and validate one shape JSON; raises `KeyError` on missing fields |
| `read_all_shapes(datafolder)` | Load every `.json` in a folder; raises `FileNotFoundError` if empty |

#### Point-level transform functions

Each takes a `[[x,y],...]` list and returns a transformed list of the same
length.  All use 3×3 homogeneous matrices internally.

| Function | Matrix | Parameters |
|---|---|---|
| `scale_points(points, factor)` | Diagonal scale | `factor: float` |
| `rotate_points(points, theta_deg)` | 2D rotation | `theta_deg: float` (degrees, CCW) |
| `translate_points(points, dx, dy)` | Translation | `dx: float`, `dy: float` |
| `mirror_points(points, axis_is_x)` | Reflection | `axis_is_x: bool` |

#### Shape-level transform

```python
apply_transform_to_shape(shape, transform_fn, suffix, **kwargs) → dict
```

1. Deep-copies the input shape dict (source is never mutated).
2. Calls `transform_fn` on `Profile` and `Midcurve`.
3. Writes the results back to both the flat lists and the corresponding
   `BRep["Points"]` arrays, keeping the two representations in sync.
4. Leaves `Lines` and `Segments` completely untouched.
5. Returns a new dict with `ShapeName` updated to `"<original>_<suffix>"`.

---

### `prepare_plots.py` — All visualization

All plotting functions live here.  `prepare_data.py` has no matplotlib
dependency.

| Function | Purpose |
|---|---|
| `plot_shape(shape_dict, ax)` | Single shape — profile (black) and midcurve (red) overlaid using BRep topology |
| `show_shape(shape_dict)` | Convenience wrapper: `plot_shape` + `plt.show()` |
| `plot_shape_grid(shape_dicts, n_cols, cell_size, title)` | N×M grid of shapes for dataset-wide quality inspection |
| `plot_prediction_comparison(shape_dict, predicted_midcurve_brep)` | Four-panel: profile \| actual midcurve \| predicted midcurve \| overlay |
| `animate_rotation(rotated_shape_dicts, interval_ms)` | `FuncAnimation` cycling through a rotation sequence |
| `export_plotly_html(shape_dicts, output_path)` | Interactive HTML (zoom/pan/hover coords), requires `pip install plotly` |

All functions resolve `Lines` and `Segments` to actual coordinates via
`_draw_brep()`, so disconnected components, branches, and star topologies all
render correctly without special-casing.

#### Usage examples

```python
from prepare_data import read_all_shapes
from prepare_plots import show_shape, plot_shape_grid, animate_rotation
from create_brep_ds import load_csv, _rotated_variants

# Inspect originals
shapes = read_all_shapes()
for s in shapes:
    show_shape(s)

# Dataset grid
all_shapes = load_csv("data/brep/midcurve_brep.csv")
plot_shape_grid(all_shapes[:20], n_cols=5)

# Rotation animation for one shape
rotated = _rotated_variants([shapes[0]])   # 180 frames
anim = animate_rotation(rotated)
plt.show()

# Model evaluation
plot_prediction_comparison(shape_dict, predicted_midcurve_brep)
```

---

### `create_brep_csvs.py` — Dataset generator

The only script you run to build the dataset.

```bash
python create_brep_csvs.py
```

#### Pipeline flow

```
read_all_shapes()
    │  loads I.json, L.json, T.json, Plus.json
    │
    ▼
populate_by_transformation()
    │
    ├── _scaled_variants()       16 factors  × 4 shapes =    64 variants
    ├── _rotated_variants()     180 angles   × 4 shapes =   720 variants
    ├── _translated_variants()  2601 combos  × 4 shapes = 10404 variants
    └── _mirrored_variants()      2 axes     × 4 shapes =     8 variants
                                                     ───────────────────
                                                          11196 variants
    ▼
originals (4) + variants (11196) = 11200 total shapes
    │
    ▼
save_dataset()
    ├── midcurve_brep.csv          (11200 rows — full dataset)
    ├── midcurve_brep_train.csv    ( 8960 rows — 80%)
    ├── midcurve_brep_test.csv     ( 1120 rows — 10%)
    └── midcurve_brep_val.csv      ( 1120 rows — 10%)
```

Splits use `random.seed(42)` for reproducibility.  The full dataset is
shuffled before splitting so originals and variants are distributed across
all three sets.

#### CSV column layout

| Column | Type in CSV | Content |
|---|---|---|
| `ShapeName` | string | e.g. `"T_rotated_45"` |
| `Profile` | JSON string | flat `[[x,y],...]` list |
| `Midcurve` | JSON string | flat `[[x,y],...]` list |
| `Profile_brep` | JSON string | full BRep sub-dict |
| `Midcurve_brep` | JSON string | full BRep sub-dict |

Use `load_csv(filepath)` to read a CSV back — it deserialises all JSON
columns automatically and returns a list of shape dicts.

#### ShapeName convention

| Transform | Example ShapeName |
|---|---|
| Original | `I` |
| Scale | `I_scaled_2.5` |
| Rotate | `T_rotated_45` |
| Translate | `L_translated_10_-20` |
| Mirror | `Plus_mirrored_x` |

---

## The JSON Shape Format

Each shape lives in a single self-contained JSON file in `data/raw/`.
The file contains both geometry (coordinate lists) and topology (BRep
connectivity) so nothing needs to be inferred at runtime.

```json
{
    "ShapeName": "I",
    "Profile":  [[5.0, 5.0], [10.0, 5.0], [10.0, 20.0], [5.0, 20.0]],
    "Midcurve": [[7.5, 5.0], [7.5, 20.0]],
    "Profile_brep": {
        "Points":   [[5.0, 5.0], [10.0, 5.0], [10.0, 20.0], [5.0, 20.0]],
        "Lines":    [[0, 1], [1, 2], [2, 3], [3, 0]],
        "Segments": [[0, 1, 2, 3]]
    },
    "Midcurve_brep": {
        "Points":   [[7.5, 5.0], [7.5, 20.0]],
        "Lines":    [[0, 1]],
        "Segments": [[0]]
    }
}
```

### BRep sub-dict schema

| Key | Type | Meaning |
|---|---|---|
| `Points` | `[[x,y], ...]` | Coordinate list — updated by every transform |
| `Lines` | `[[i,j], ...]` | Edges as pairs of point indices — **never changed** |
| `Segments` | `[[line_idx,...], ...]` | Groups of lines forming a loop or chain — **never changed** |

`Profile` and `Midcurve` at the top level are flat point lists kept for
backward compatibility with the original `.dat`/`.mid` format.  They are
always identical to `Profile_brep["Points"]` and `Midcurve_brep["Points"]`
respectively, and are kept in sync by every transform.

### Why topology is never inferred

`Lines` and `Segments` reference points by index.  All four supported
transforms are bijections — they move points but never change their count or
order.  The index structure is therefore invariant under any transformation,
so topology authored once (or generated by the converter) remains correct
forever.

---

## The Four Shape Files

### `I.json` — rectangular bar

| | Points | Lines | Segments |
|---|---|---|---|
| Profile | 4 | 4 | 1 (closed loop) |
| Midcurve | 2 | 1 | 1 (single segment) |

Profile is a simple rectangle.  Midcurve is a single vertical line at the
horizontal centre of the bar.  `I.json` was hand-authored (no Yogesh txt
available for this shape).

```
Profile (closed polygon)       Midcurve (chain)
  5,20 ──── 10,20                  7.5,20
   |              |                    |
  5,5  ──── 10,5                   7.5,5
```

### `L.json` — L-shaped section

| | Points | Lines | Segments |
|---|---|---|---|
| Profile | 6 | 6 | 1 (closed loop) |
| Midcurve | 3 | 2 | 2 (two arms meeting at a junction) |

Midcurve has two arms: a vertical leg up the web and a horizontal leg along
the flange.  Point `[1]` at `(75, 325)` is the shared junction.

```
Midcurve connectivity:
  [0](75, 50) ── [1](75, 325) ── [2](350, 325)
  Lines: [0,1], [2,1]   Segments: [[0],[1]]
```

> Note: `I.json` uses the original small-scale coordinates from the `.dat`/`.mid`
> files.  `L.json`, `T.json`, and `Plus.json` use the larger-scale coordinates
> from the Yogesh method files — ten times larger.  Both scales are valid inputs
> to the pipeline.

### `T.json` — T-shaped section

| | Points | Lines | Segments |
|---|---|---|---|
| Profile | 8 | 8 | 1 (closed loop) |
| Midcurve | 4 | 2 | 2 (stem + crossbar as separate segments) |

Midcurve has two independent segments reflecting the Yogesh representation:
a vertical stem `[0]→[1]` and a full-width crossbar `[2]→[3]`.  The stem
endpoint `[1]` at `(125, 225)` lies geometrically on the crossbar but is not
explicitly shared as a junction point in this topology — the crossbar is one
unbroken segment from right tip to left tip.

```
Midcurve connectivity:
  [2](250, 225) ─────── [3](0, 225)    ← crossbar (one segment)
              [1](125, 225)             ← stem top (on crossbar line)
                   |
              [0](125, 0)               ← stem bottom
  Lines: [0,1], [2,3]   Segments: [[0],[1]]
```

### `Plus.json` — Plus / cross section

| | Points | Lines | Segments |
|---|---|---|---|
| Profile | 12 | 12 | 1 (closed loop) |
| Midcurve | 5 | 3 | 3 (bottom arm + top arm + horizontal bar) |

Midcurve has three segments: two vertical arms sharing junction `[1]` at
`(125, 225)`, and a separate full-width horizontal bar.

```
Midcurve connectivity:
  [2](125, 450)                          ← top arm
       |
  [1](125, 225) ← junction (shared)
       |
  [0](125, 0)                            ← bottom arm

  [3](0, 225) ────────── [4](250, 225)   ← horizontal bar (one segment)

  Lines: [0,1], [2,1], [3,4]   Segments: [[0],[1],[2]]
```

---

## Transformation Summary

| Transform | Range | Step | Variants per shape |
|---|---|---|---|
| Scale | 2.0 → 6.0 (excl.) | 0.25 | 16 |
| Rotate | 1° → 180° (incl.) | 1° | 180 |
| Translate X×Y | −50 → 50 (incl.) each axis | 2 | 51 × 51 = 2,601 |
| Mirror X | — | — | 1 |
| Mirror Y | — | — | 1 |
| **Total per shape** | | | **2,799** |
| **Total for 4 shapes** | | | **11,196 variants + 4 originals = 11,200** |

Translation varies X and Y independently — both axial (dx-only, dy-only) and
diagonal offsets are generated.

---

## Design Decisions and Rationale

### Why JSON instead of `.dat` + `.mid` + `.topo` sidecar files

The `.dat`/`.mid` pair carries only geometry — topology must come from
somewhere else.  Encoding topology in a separate sidecar keeps the same
fragmentation problem.  A single JSON per shape is self-contained: open one
file and you have everything.  The flat `Profile` and `Midcurve` lists are
kept alongside the BRep for backward compatibility and convenient access.

### Why the converter extracts topology from the Yogesh txt rather than inferring it

The Yogesh method txt explicitly lists each midcurve segment as a pair of
points separated by blank lines, so the topology is directly readable — no
geometric inference needed.  An earlier heuristic (angular-span detection of
star vs chain) was considered but abandoned because it fails for shapes with
multiple junctions, concentric rings (like "O"), or arbitrary tree structures.
Reading topology from the Yogesh segments is exact for any shape the method
can handle.

### Why `create_line_ds.py` was removed

It solved a sub-problem (converting points to line segment pairs) that the
BRep already solves more completely.  The BRep `Lines` field is exactly a list
of index-pair segments, and `Segments` groups them by connected component.
There is no information in the line-based JSON that is not already in the BRep
JSON.

### Why `prepare_data.py` has no matplotlib import

Transformation scripts should not depend on a plotting library.  Keeping I/O
and math in `prepare_data.py` and all plotting in `prepare_plots.py` means
the pipeline can run in headless environments (CI, servers) without matplotlib
installed.

---

## Quick-Reference: End-to-End Flow

```
<ShapeName>.dat  +  <ShapeName>_MidcurvesByYogeshMethod.txt
          │
          ▼  python create_brep_jsons.py     (one-time per shape)
          │
          ├── <ShapeName>.mid    ← flat midcurve point list
          └── <ShapeName>.json   ← geometry + topology, self-contained
                    │
                    ▼  python create_brep_csvs.py
                    │
          read_all_shapes()                      ← prepare_data.py
                    │
          apply_transform_to_shape()             ← prepare_data.py
            scale / rotate / translate / mirror
            → Points updated, Lines/Segments unchanged
                    │
          populate_by_transformation()           ← create_brep_csvs.py
            11,196 variants across 4 shapes
                    │
          save_dataset()                         ← create_brep_csvs.py
            midcurve_brep_train/test/val.csv
                    │
          load_csv()  →  model training          ← create_brep_csvs.py
```
