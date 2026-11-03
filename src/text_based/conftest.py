"""pytest configuration for src/text_based.

The text track is imported as the package `text_based` (text_based.common, text_based.methods), so only src/ is
needed on sys.path. Each approach has packages named `common` / `methods` in its own namespace, so run one approach per
pytest process (see ../run_all_tests.py).
"""
import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC in sys.path:
    sys.path.remove(_SRC)
sys.path.insert(0, _SRC)
