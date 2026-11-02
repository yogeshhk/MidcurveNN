"""unet: 4-level U-Net-lite, GroupNorm, CoordConv, concat skips, bilinear upsampling (~1.5M params)."""
from ._blocks import UNetLite


def build_model(cfg):
    return UNetLite(cfg.get("in_ch", 3), base=cfg.get("base", 24), depth=cfg.get("depth", 4),
                    skips=True, coord=True, drop=cfg.get("drop", 0.1))
