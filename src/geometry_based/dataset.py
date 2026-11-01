"""Dataset access for the geometry track: gold shapes, seeded synthetic splits, torch featurisation.

Per-vertex features (7): x, y, prev-edge vector (dx,dy), next-edge vector (dx,dy), convex/reflex flag.
Everything is padded to NMAX vertices (boolean mask) and K=12 ground-truth node slots (boolean mask).
"""
import numpy as np

import geom
import prepare_data as pdata

NMAX = pdata.NMAX
K = 12
FEAT_DIM = 7


def load_gold():
    return pdata.load_gold()


def build_splits(split, n_train=20000, n_val=2000, n_test=1000, seeds=(0, 1, 2)):
    """Return dict name -> list of samples. Synthetic data only; real4 is added by the caller."""
    s_tr, s_va, s_te = seeds
    if split == "iid":
        return dict(train=pdata.make_dataset(n_train, s_tr),
                    val=pdata.make_dataset(n_val, s_va),
                    test=pdata.make_dataset(n_test, s_te))
    if split == "ood_deg4":
        out = dict(train=pdata.make_dataset(n_train, s_tr, allow_deg4=False),
                   val=pdata.make_dataset(n_val, s_va, allow_deg4=False),
                   test_in=pdata.make_dataset(n_test, s_te, allow_deg4=False))
        rng = np.random.default_rng(s_te + 1000)
        test = []
        while len(test) < n_test:
            s = pdata.make_sample(rng, allow_deg4=True)
            if s["deg_max"] == 4:
                test.append(s)
        out["test"] = test
        return out
    if split == "ood_size":
        return dict(train=pdata.make_dataset(n_train, s_tr, max_edges=5),
                    val=pdata.make_dataset(n_val, s_va, max_edges=5),
                    test=pdata.make_dataset(n_test, s_te, min_edges=6, max_edges=7))
    raise ValueError("unknown split %r (iid | ood_deg4 | ood_size)" % split)


def _insert_collinear(prof, nd_unused, rng, p=0.3, max_new=3):
    pts = []
    n = len(prof)
    budget = NMAX - n
    for i in range(n):
        a, b = prof[i], prof[(i + 1) % n]
        pts.append(a)
        if budget > 0 and rng.random() < p:
            k = min(int(rng.integers(1, max_new + 1)), budget)
            ts = np.sort(rng.uniform(0.1, 0.9, size=k))
            for t in ts:
                pts.append(a * (1 - t) + b * t)
            budget -= k
    return np.asarray(pts)


def featurize(profile, nodes, rng=None, augment=False):
    """Return a dict of numpy arrays. Augmentation acts on profile and GT nodes together."""
    prof = np.asarray(profile, dtype=float).copy()
    nd = np.asarray(nodes, dtype=float).copy()
    if augment:
        k = int(rng.integers(4))
        for _ in range(k):
            prof = np.stack([-prof[:, 1], prof[:, 0]], 1)
            nd = np.stack([-nd[:, 1], nd[:, 0]], 1)
        if rng.random() < 0.5:
            prof[:, 0] *= -1
            nd[:, 0] *= -1
        if rng.random() < 0.5:
            prof = prof[::-1].copy()
        prof = _insert_collinear(prof, nd, rng) if rng.random() < 0.5 else prof
        prof = np.roll(prof, int(rng.integers(len(prof))), axis=0)
    prof_n, nd_n, centre, he = geom.normalize(prof, nd)
    n = len(prof_n)
    nxt = np.roll(prof_n, -1, axis=0) - prof_n
    prv = prof_n - np.roll(prof_n, 1, axis=0)
    orient = 1.0 if geom.signed_area(prof_n) >= 0 else -1.0
    cr = prv[:, 0] * nxt[:, 1] - prv[:, 1] * nxt[:, 0]
    scale = np.maximum(np.linalg.norm(prv, axis=1) * np.linalg.norm(nxt, axis=1), 1e-12)
    flag = np.where(np.abs(cr) / scale < 1e-6, 0.0, np.sign(cr) * orient)
    feats = np.zeros((NMAX, FEAT_DIM), dtype=np.float32)
    feats[:n] = np.concatenate([prof_n, prv, nxt, flag[:, None]], 1)
    mask = np.zeros(NMAX, dtype=bool)
    mask[:n] = True
    gt = np.zeros((K, 2), dtype=np.float32)
    gm = np.zeros(K, dtype=bool)
    m = len(nd_n)
    gt[:m] = nd_n
    gm[:m] = True
    return dict(feats=feats, mask=mask, gt=gt, gt_mask=gm, centre=centre, he=he)


try:
    import torch
    from torch.utils.data import Dataset, DataLoader

    class MidcurveDataset(Dataset):
        def __init__(self, samples, augment=False, seed=0):
            self.samples = samples
            self.augment = augment
            self.rng = np.random.default_rng(seed)

        def __len__(self):
            return len(self.samples)

        def __getitem__(self, i):
            s = self.samples[i]
            return featurize(s["profile"], s["nodes"], self.rng, self.augment)

    def collate(items):
        n = int(max(it["mask"].sum() for it in items))  # trim padding to the longest ring in the batch
        return dict(
            feats=torch.from_numpy(np.stack([it["feats"][:n] for it in items])),
            mask=torch.from_numpy(np.stack([it["mask"][:n] for it in items])),
            gt=torch.from_numpy(np.stack([it["gt"] for it in items])),
            gt_mask=torch.from_numpy(np.stack([it["gt_mask"] for it in items])),
            centre=np.stack([it["centre"] for it in items]),
            he=np.array([it["he"] for it in items]),
        )

    def make_loader(samples, batch_size=128, shuffle=False, augment=False, seed=0):
        return DataLoader(MidcurveDataset(samples, augment, seed), batch_size=batch_size,
                          shuffle=shuffle, collate_fn=collate, num_workers=0)
except ImportError:  # pragma: no cover
    torch = None
