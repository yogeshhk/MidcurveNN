"""Loss options for the image track. Ink = 1, background = 0. Models output LOGITS.

kinds:
  bce        plain unweighted BCE on the hard 1-px target (what the legacy code effectively did)
  bcedice    soft (Gaussian) target + pos-weighted BCE + soft Dice   (default)
  focaldice  soft target + focal BCE + soft Dice
"""
import torch
import torch.nn.functional as F


def _gauss1d(sigma, device, dtype):
    r = max(1, int(3 * sigma))
    x = torch.arange(-r, r + 1, device=device, dtype=dtype)
    k = torch.exp(-(x ** 2) / (2 * sigma ** 2))
    return k / k.sum()


def blur(t, sigma=1.2):
    """Separable Gaussian blur of a (B,1,H,W) tensor."""
    k = _gauss1d(sigma, t.device, t.dtype)
    r = k.numel() // 2
    t = F.conv2d(F.pad(t, (r, r, 0, 0), mode="replicate"), k.view(1, 1, 1, -1))
    t = F.conv2d(F.pad(t, (0, 0, r, r), mode="replicate"), k.view(1, 1, -1, 1))
    return t


def soft_target(y_thin, sigma=1.2):
    if sigma <= 0:
        return y_thin
    s = blur(y_thin, sigma)
    return s / s.amax(dim=(2, 3), keepdim=True).clamp_min(1e-6)


def dice_loss(logits, target, eps=1.0):
    p = torch.sigmoid(logits)
    inter = (p * target).sum(dim=(1, 2, 3))
    den = p.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3))
    return (1.0 - (2 * inter + eps) / (den + eps)).mean()


def focal_bce(logits, target, gamma=2.0, alpha=0.75):
    bce = F.binary_cross_entropy_with_logits(logits, target, reduction="none")
    p = torch.sigmoid(logits)
    pt = target * p + (1 - target) * (1 - p)
    a = target * alpha + (1 - target) * (1 - alpha)
    return (a * (1 - pt) ** gamma * bce).mean()


def seg_loss(logits, y_thin, pos_weight=10.0, sigma=1.2, dice_w=1.0, kind="bcedice"):
    if kind == "bce":
        return F.binary_cross_entropy_with_logits(logits, y_thin)
    t = soft_target(y_thin, sigma)
    if kind == "focaldice":
        return focal_bce(logits, t) * 10.0 + dice_w * dice_loss(logits, t)
    if kind != "bcedice":
        raise ValueError("unknown loss kind %r" % kind)
    pw = torch.tensor(float(pos_weight), device=logits.device)
    bce = F.binary_cross_entropy_with_logits(logits, t, pos_weight=pw)
    return bce + dice_w * dice_loss(logits, t)
