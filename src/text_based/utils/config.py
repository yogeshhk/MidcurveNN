"""
config.py — Central configuration for the Midcurve Dataset Pipeline.

All folder paths and transformation parameters live here so that the
pipeline scripts stay in sync automatically.

Directory layout (relative to text_based/)
------------------------------------------
text_based/
    utils/
        config.py          ← this file
        prepare_data.py
        prepare_plots.py
        create_brep_jsons.py
        create_brep_csvs.py
    data/
        brep/              ← hand-authored .json shape files live here
        csvs/              ← generated CSV dataset files written here
    results/               ← model checkpoints and outputs
"""

from os import path

BASE_DIR = path.dirname(path.abspath(__file__))  # text_based/utils/

# ---------------------------------------------------------------------------
# Folder paths
# ---------------------------------------------------------------------------

RAW_DATA_FOLDER = path.join(BASE_DIR, "..", "data", "brep")
BREP_FOLDER     = path.join(BASE_DIR, "..", "data", "csvs")
MODELS_FOLDER   = path.join(BASE_DIR, "..", "results")

# ---------------------------------------------------------------------------
# Transformation ranges
#
# Scale and rotation use numpy.arange / range respectively.
# Translation varies x and y independently (not just diagonal dx==dy).
# ---------------------------------------------------------------------------

# Uniform scale factor applied to both axes.
SCALE_START = 2.0
SCALE_STOP  = 6.0      # exclusive upper bound
SCALE_STEP  = 0.25

# Rotation angle in degrees (integer steps).
ROTATE_START = 1
ROTATE_STOP  = 181     # exclusive — covers 1° through 180°
ROTATE_STEP  = 1

# Translation in data units — x and y varied independently.
TRANSLATE_X_START = -50
TRANSLATE_X_STOP  =  51   # exclusive — covers -50 through 50
TRANSLATE_X_STEP  =   2

TRANSLATE_Y_START = -50
TRANSLATE_Y_STOP  =  51
TRANSLATE_Y_STEP  =   2
