"""ONE metric set for every image model.

Prediction probabilities -> threshold -> remove tiny blobs -> skeletonise -> compare with the skeleton
of the GT 1-px midcurve:
  prec / rec / f1   within `tol` pixels (default 2 px at 128 px)
  chamfer, hausdorff  on skeleton pixels, in pixels AND in raw units (pixels / scale)
  topo_ok           components, endpoints and junction clusters equal to the GT's
Also writes a results grid PNG (rows: input / GT / prediction, fixed 0..1 scale).
"""
import numpy as np
import torch
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

_K8 = np.ones((3, 3), int)
THRESHOLDS = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


def skeleton(mask):
    return skeletonize(mask.astype(bool))


def to_polyline_mask(prob, thr=0.5, min_px=8):
    b = prob >= thr
    lab, n = ndi.label(b, structure=_K8)
    if n:
        sizes = ndi.sum(b, lab, index=np.arange(1, n + 1))
        b = np.isin(lab, 1 + np.where(sizes >= min_px)[0])
    return skeleton(b)


def topo_counts(skel):
    skel = skel.astype(bool)
    nb = ndi.convolve(skel.astype(int), _K8, mode="constant") * skel
    ends = int(((nb == 2) & skel).sum())
    junc = ndi.label((nb >= 4) & skel, structure=_K8)[1]
    comps = ndi.label(skel, structure=_K8)[1]
    return comps, ends, junc


def tolerance_scores(pred, gt, tol=2.0):
    """pred, gt: boolean skeleton masks. Distances in pixels."""
    pred, gt = pred.astype(bool), gt.astype(bool)
    diag = float(np.hypot(*gt.shape))
    if not pred.any():
        return dict(prec=0.0, rec=0.0, f1=0.0, chamfer=diag, hausdorff=diag)
    d_gt = ndi.distance_transform_edt(~gt)
    d_pr = ndi.distance_transform_edt(~pred)
    a, b = d_gt[pred], d_pr[gt]
    prec, rec = float((a <= tol).mean()), float((b <= tol).mean())
    f1 = 0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec)
    return dict(prec=prec, rec=rec, f1=f1, chamfer=float(0.5 * (a.mean() + b.mean())),
                hausdorff=float(max(a.max(), b.max())))


def sample_metrics(prob, y_thin, scale=1.0, thr=0.5, tol=2.0):
    sk = to_polyline_mask(prob, thr)
    gk = skeleton(y_thin > 0.5)
    m = tolerance_scores(sk, gk, tol)
    m["chamfer_raw"] = m["chamfer"] / scale
    m["hausdorff_raw"] = m["hausdorff"] / scale
    m["topo_ok"] = float(topo_counts(sk) == topo_counts(gk))
    return m


KEYS = ["prec", "rec", "f1", "chamfer", "hausdorff", "chamfer_raw", "hausdorff_raw", "topo_ok"]


def aggregate(rows):
    out = {"all": {k: float(np.mean([r[k] for r in rows])) for k in KEYS}}
    out["all"]["n"] = len(rows)
    for s in sorted({r["shape"] for r in rows}):
        sub = [r for r in rows if r["shape"] == s]
        out[s] = {k: float(np.mean([r[k] for r in sub])) for k in KEYS}
        out[s]["n"] = len(sub)
    return out


@torch.no_grad()
def predict_batch(model, x, tta=False):
    """sigmoid probabilities, optionally averaged over the 8 dihedral transforms."""
    ops = [(k, f) for k in range(4) for f in (False, True)] if tta else [(0, False)]
    acc = 0
    for k, f in ops:
        xi = torch.rot90(x, k, (2, 3))
        if f:
            xi = torch.flip(xi, (3,))
        p = torch.sigmoid(model(xi))
        if f:
            p = torch.flip(p, (3,))
        acc = acc + torch.rot90(p, -k, (2, 3))
    return acc / len(ops)


@torch.no_grad()
def collect(model, loader, dev, tta=False, pre=None):
    """Run the model over a loader once. pre(x) may transform the input (denoiser chaining).
    Returns dict(x, y, prob, names, scale) as numpy / lists."""
    was = model.training
    model.eval()
    xs, ys, ps, names, scales = [], [], [], [], []
    for x, y, n, s in loader:
        xd = x.to(dev)
        if pre is not None:
            xd = pre(xd)
        p = predict_batch(model, xd, tta).cpu().numpy()[:, 0]
        xs.append(x.numpy()); ys.append(y.numpy()[:, 0]); ps.append(p)
        names += list(n); scales += [float(v) for v in s]
    model.train(was)
    return dict(x=np.concatenate(xs), y=np.concatenate(ys), prob=np.concatenate(ps),
                names=names, scale=scales)


def score(col, thr=0.5, tol=2.0):
    rows = []
    for p, y, n, s in zip(col["prob"], col["y"], col["names"], col["scale"]):
        m = sample_metrics(p, y, s, thr, tol)
        m["shape"] = n
        rows.append(m)
    return aggregate(rows)


def tune_threshold(col, tol=2.0):
    best = max(THRESHOLDS, key=lambda t: score(col, t, tol)["all"]["f1"])
    return float(best)


def save_grid(col, path, thr=0.5, n=8):
    """Rows: input (filled mask + outline), GT midcurve, prediction probability (fixed 0..1 scale)
    with the thresholded skeleton overlaid in red."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = min(n, len(col["prob"]))
    fig, ax = plt.subplots(3, n, figsize=(1.7 * n, 5.3), squeeze=False)
    for j in range(n):
        x, y, p = col["x"][j], col["y"][j], col["prob"][j]
        inp = 1.0 - 0.35 * x[1] - 0.65 * x[0]
        ax[0, j].imshow(inp, cmap="gray", vmin=0, vmax=1)
        ax[0, j].set_title(col["names"][j], fontsize=8)
        ax[1, j].imshow(1.0 - y, cmap="gray", vmin=0, vmax=1)
        ax[2, j].imshow(1.0 - p, cmap="gray", vmin=0, vmax=1)
        sk = to_polyline_mask(p, thr)
        ov = np.zeros(sk.shape + (4,), np.float32)
        ov[sk] = [1, 0, 0, 0.8]
        ax[2, j].imshow(ov)
        for i in range(3):
            ax[i, j].axis("off")
    for i, t in enumerate(["input", "GT", "pred"]):
        ax[i, 0].text(-0.08, 0.5, t, transform=ax[i, 0].transAxes, rotation=90, va="center", ha="right",
                      fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
