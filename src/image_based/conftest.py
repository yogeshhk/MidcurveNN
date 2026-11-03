"""pytest configuration for src/image_based.

Puts image_based/ first on sys.path so that the approach packages `common` and `methods` resolve, and src/ so
that the shared `utils` / `config` used by the old (Keras) scripts resolve. Each approach has its own `common`
and `methods` packages, so run one approach per pytest process (see ../run_all_tests.py).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)

for _p in (_SRC, _HERE):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
