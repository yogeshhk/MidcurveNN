"""
conftest.py — pytest root configuration for MidcurveNN.

Adds src/ and the image_based/ sub-tree to sys.path so that cross-approach
imports (e.g. `from utils.prepare_data import ...`) resolve correctly for
all three approach test suites when running `python -m pytest` from src/.
"""
import sys
import os

_SRC = os.path.dirname(os.path.abspath(__file__))

for _p in [
    _SRC,
    os.path.join(_SRC, "image_based"),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
