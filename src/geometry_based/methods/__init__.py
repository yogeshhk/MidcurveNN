"""Method registry for the geometry track. Each module exposes build_model(cfg) and make_predictor(model, cfg).

CLI name (--model) -> method folder. set_transformer and classical_voronoi have no older implementation,
so their model.py and runs/ sit at the method's top level. graph_transformer, finetuned_graph_transformer and
gnn_encoder_decoder are the older implementations kept as they were (frozen negative result / retired); they are
scripts, not registry entries.

Modules are imported lazily so that `classical` works without torch.
"""
import importlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))

FOLDERS = {"classical": "classical_voronoi", "set_transformer": "set_transformer", "equi_collapse": "equi_collapse"}
NAMES = list(FOLDERS)


def _module(name):
    if name not in NAMES:
        raise KeyError("unknown model %r; known: %s" % (name, NAMES))
    return importlib.import_module("methods.%s.model" % FOLDERS[name])


def runs_dir(name):
    """Run root for a model: methods/<method>/runs (run folders are <split>__<tag>)."""
    if name not in NAMES:
        raise KeyError("unknown model %r; known: %s" % (name, NAMES))
    return os.path.join(HERE, FOLDERS[name], "runs")


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
