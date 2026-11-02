"""denoiser_ae: second-stage refiner. Input channels = [noisy midcurve, outline, filled mask].

Trained on CORRUPTED ground truth (blur, fade, noise, small shift), not on stage-1 output of its own
training data. At evaluation it is chained after a stage-1 predictor (a trained model's probabilities,
or the non-learned skeleton baseline). The hooks `train_input` and `eval_input` are used by trainer.py
and run.py.
"""
import torch

from ._blocks import UNetLite
from losses import blur


def build_model(cfg):
    return UNetLite(3, base=cfg.get("base", 24), depth=cfg.get("depth", 3), skips=True, coord=True, drop=0.0)


def corrupt(y, gen=None):
    """y: (B,1,H,W) thin GT in {0,1}. Returns a plausible 'bad stage-1 output' in [0,1]."""
    s = blur(y, 1.0 + 2.0 * float(torch.rand(()).item()))
    s = s / s.amax(dim=(2, 3), keepdim=True).clamp_min(1e-6)
    s = s * (0.3 + 0.7 * torch.rand(y.shape[0], 1, 1, 1, device=y.device))
    s = s + 0.08 * torch.randn_like(s)
    dx, dy = [int(v) for v in torch.randint(-2, 3, (2,))]
    s = torch.roll(s, (dy, dx), (2, 3))
    return s.clamp(0, 1)


def train_input(x, y):
    return torch.cat([corrupt(y), x[:, :2]], 1)


def eval_input(x, stage1_prob):
    return torch.cat([stage1_prob, x[:, :2]], 1)
