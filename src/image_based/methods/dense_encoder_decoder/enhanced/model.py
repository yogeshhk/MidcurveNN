"""dense_ae: deep fully connected autoencoder (legacy 'dense' baseline, modernised, ~34M params)."""
from common.blocks import FlatAE


def build_model(cfg):
    return FlatAE(cfg.get("size", 128), cfg.get("in_ch", 3), hidden=(512, 256), code=cfg.get("code", 128))
