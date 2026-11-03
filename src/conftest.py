"""
conftest.py -- pytest root configuration for MidcurveNN (src/).

Since the 2026-11-03 reorganisation each approach has its own conftest.py and pytest.ini and its own `common` /
`methods` packages, so the suites run in separate processes (see run_all_tests.py). This file only puts src/ on
sys.path for ad-hoc imports such as `from utils.prepare_data import ...`.
"""
import os
import sys

_SRC = os.path.dirname(os.path.abspath(__file__))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
