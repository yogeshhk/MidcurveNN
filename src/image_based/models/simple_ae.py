"""simple_ae: one dense hidden code layer (legacy 'simple' baseline, modernised)."""
from ._blocks import FlatAE


def build_model(cfg):
    return FlatAE(cfg.get("size", 128), cfg.get("in_ch", 3), hidden=(), code=cfg.get("code", 256))
