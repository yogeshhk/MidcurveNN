# All shared hyperparameters are defined in src/config.py.
# This file re-exports them so that pix2pix modules can do `from config import *`
# when run from the src/image_based/pix2pix/ directory.
import sys
import os
import importlib.util as _util

_src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _src_dir)

# Load src/config.py under a unique name to avoid the self-import bug this used to have:
# `from config import *` while pix2pix/ is on sys.path resolved `config` to this very
# file (already in sys.modules), importing nothing (see analysis_report.md Bug 17).
_spec = _util.spec_from_file_location('_midcurvenn_src_config',
                                       os.path.join(_src_dir, 'config.py'))
_m = _util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
globals().update({k: v for k, v in vars(_m).items() if not k.startswith('_')})
