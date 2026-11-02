"""cnn_ae: plain convolutional encoder-decoder, NO skip connections (8x8 bottleneck), GroupNorm."""
from ._blocks import UNetLite


def build_model(cfg):
    return UNetLite(cfg.get("in_ch", 3), base=cfg.get("base", 24), depth=cfg.get("depth", 4),
                    skips=False, coord=True, drop=0.0)
