# -*- coding: utf-8 -*-
# All UNet hyperparameters are defined in src/config.py.
# This file re-exports them so that unet modules can do `from config import *`
# when run from the src/unet/ directory.
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *  # noqa: F401, F403
