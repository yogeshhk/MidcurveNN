"""Model registry. Each module exposes build_model(cfg) and make_predictor(model, cfg).

Modules are imported lazily so that `classical` works without torch.
"""
import importlib

NAMES = ["classical", "set_transformer"]


def _module(name):
    if name not in NAMES:
        raise KeyError("unknown model %r; known: %s" % (name, NAMES))
    return importlib.import_module("models." + name)


class _Registry(dict):
    def __missing__(self, key):
        mod = _module(key)
        self[key] = mod
        return mod

    def keys(self):
        return list(NAMES)

    def __contains__(self, key):
        return key in NAMES


REGISTRY = _Registry()


def build_model(cfg):
    return REGISTRY[cfg.model].build_model(cfg)
