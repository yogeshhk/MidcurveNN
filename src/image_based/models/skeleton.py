"""skeleton: NON-LEARNED classical baseline = skeletonize(filled mask). No parameters, no training.

Returned as an nn.Module so it goes through the same evaluation path: logits are +10 on skeleton
pixels and -10 elsewhere.
"""
import numpy as np
import torch
import torch.nn as nn
from skimage.morphology import skeletonize


class Skeleton(nn.Module):
    trainable = False

    def forward(self, x):
        m = (x[:, 1].detach().cpu().numpy() > 0.5)
        out = np.stack([skeletonize(a) for a in m]).astype(np.float32)
        return torch.from_numpy(out * 20.0 - 10.0)[:, None].to(x.device)


def build_model(cfg):
    return Skeleton()
