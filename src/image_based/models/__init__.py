"""Model registry. Every module exposes build_model(cfg) -> nn.Module mapping [B,3,H,W] -> logits [B,1,H,W].

cfg is a plain dict (keys used: size, in_ch, base, depth, drop, code). Modules are imported lazily so that
importing the registry does not pull in every dependency.
"""
import importlib

REGISTRY = {
    "skeleton": "models.skeleton",
    "simple_ae": "models.simple_ae",
    "dense_ae": "models.dense_ae",
    "cnn_ae": "models.cnn_ae",
    "denoiser_ae": "models.denoiser_ae",
    "unet": "models.unet",
    "pix2pix": "models.pix2pix",
}


def get_module(name):
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    return importlib.import_module(REGISTRY[name])


def build_model(name, cfg=None):
    return get_module(name).build_model(dict(cfg or {}))
