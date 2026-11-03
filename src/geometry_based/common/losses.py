"""Hungarian set loss (DETR style) for the node-set model. No mixing between samples in a batch."""
import numpy as np
import torch
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment


def hungarian_match(xy, logit, gt_xy, gt_mask):
    """Per-sample matching. Returns a list of (query_idx, gt_idx) numpy arrays.

    cost[q, j] = L1(xy_q, gt_j) - 0.5 * sigmoid(logit_q)
    """
    B = xy.shape[0]
    out = []
    with torch.no_grad():
        prob = torch.sigmoid(logit)
        for b in range(B):
            gi = torch.nonzero(gt_mask[b]).flatten()
            if len(gi) == 0:
                out.append((np.zeros(0, int), np.zeros(0, int)))
                continue
            cost = torch.cdist(xy[b], gt_xy[b][gi], p=1) - 0.5 * prob[b][:, None]
            r, c = linear_sum_assignment(cost.cpu().numpy())
            out.append((r, gi[c].cpu().numpy()))
    return out


def set_loss(xy, logit, gt_xy, gt_mask, w_xy=5.0, w_empty=0.5):
    """xy[B,K,2], logit[B,K], gt_xy[B,K,2], gt_mask[B,K] (bool).

    total = w_xy * mean matched L1 + BCE over all K slots (target 1 matched, 0 else; empties weighted).
    Returns (total, dict(l1=..., bce=...)).
    """
    match = hungarian_match(xy, logit, gt_xy, gt_mask)
    B, Kq = logit.shape
    target = torch.zeros_like(logit)
    l1_terms = []
    for b, (q, g) in enumerate(match):
        if len(q) == 0:
            continue
        qi = torch.as_tensor(q, device=xy.device)
        gi = torch.as_tensor(g, device=xy.device)
        target[b, qi] = 1.0
        l1_terms.append((xy[b, qi] - gt_xy[b, gi]).abs().sum(-1).mean())
    l1 = torch.stack(l1_terms).mean() if l1_terms else xy.sum() * 0.0
    weight = torch.where(target > 0.5, torch.ones_like(logit), torch.full_like(logit, w_empty))
    bce = (F.binary_cross_entropy_with_logits(logit, target, reduction="none") * weight).sum(1).mean() / Kq
    total = w_xy * l1 + bce
    return total, dict(l1=float(l1.detach()), bce=float(bce.detach()))
