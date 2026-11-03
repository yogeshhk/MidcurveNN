"""Method registry for the image track.

Each CLI model name (``--model``) maps to the module that holds the current driver and to its method folder.
Every module exposes build_model(cfg) -> nn.Module mapping [B,3,H,W] -> logits [B,1,H,W].
cfg is a plain dict (keys used: size, in_ch, base, depth, drop, code). Modules are imported lazily so that
importing the registry does not pull in every dependency.

Layout: methods/<method>/ holds the old implementation (top level), enhanced/ holds the standard version
(model.py, runs/, tests/). Methods with no old implementation (skeleton) keep model.py and runs/ at the top.
"""
import importlib
import os

REGISTRY = {
    "skeleton": "methods.skeleton.model",
    "simple_ae": "methods.simple_encoder_decoder.enhanced.model",
    "dense_ae": "methods.dense_encoder_decoder.enhanced.model",
    "cnn_ae": "methods.cnn_encoder_decoder.enhanced.model",
    "denoiser_ae": "methods.denoiser_encoder_decoder.enhanced.model",
    "unet": "methods.unet.enhanced.model",
    "pix2pix": "methods.pix2pix.enhanced.model",
}

HERE = os.path.dirname(os.path.abspath(__file__))


def method_dir(name):
    """Folder that holds the model module of CLI name `name` (the dir with model.py)."""
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    parts = REGISTRY[name].split(".")[1:-1]          # drop 'methods' and 'model'
    return os.path.join(HERE, *parts)


def runs_dir(name):
    """Default run folder for a model: <method dir>/runs (runs/<split>__<tag>/ inside)."""
    return os.path.join(method_dir(name), "runs")


def get_module(name):
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    return importlib.import_module(REGISTRY[name])


def build_model(name, cfg=None):
    return get_module(name).build_model(dict(cfg or {}))
