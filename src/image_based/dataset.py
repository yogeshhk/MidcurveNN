"""Loads data/dataset_v1.npz. One sample = (x float32 [3,H,W], y float32 [1,H,W], shape_name, scale).

Ink = 1, background = 0. Channels: 0 outline, 1 filled mask, 2 distance transform (0..1).
Train parts can render fresh random poses on the fly (aug=True): the SAME transform is applied to the
profile and midcurve vertices before rasterising. Val/test parts are the stored fixed poses.
"""
import itertools
import json

import numpy as np
import torch
from torch.utils.data import Dataset

import prepare_data as pd_

_CACHE = {}


def load_npz(path=pd_.DATASET):
    if path not in _CACHE:
        z = np.load(path, allow_pickle=False)
        d = {k: z[k] for k in z.files}
        d["geom_obj"] = pd_.geom_from_json(str(d["geom"]))
        d["splits_obj"] = json.loads(str(d["splits"]))
        d["names"] = [str(s) for s in d["shape_names"]]
        _CACHE[path] = d
    return _CACHE[path]


def resolve_split(spec, splits):
    """spec: 'pose' | 'default' | 'loso:<Shape>' -> (train_shapes, val_shapes, test_shapes)."""
    if spec == "pose":
        s = splits["pose"]
        return list(s["train"]), list(s["val"]), list(s["test"])
    if spec == "default":
        s = splits["default"]
        return list(s["train"]), list(s["val"]), list(s["test"])
    if spec.startswith("loso:"):
        ho = spec.split(":", 1)[1]
        for f in splits["loso"]:
            if f["holdout"] == ho:
                return list(f["train"]), list(f["train"]), list(f["test"])
        raise ValueError("unknown loso holdout %r" % ho)
    raise ValueError("unknown split %r (use pose, default or loso:<Shape>)" % spec)


class MidcurveDataset(Dataset):
    def __init__(self, shapes, part, aug=False, length=None, seed=None, in_ch=3, path=pd_.DATASET):
        """part: 'train' | 'val' | 'test'. aug=True renders poses on the fly (length samples);
        seed=int makes the on-the-fly samples deterministic per index; seed=None draws a fresh seed
        from torch's RNG on every call (reproducible after torch.manual_seed)."""
        self.d = load_npz(path)
        self.shapes = list(shapes)
        self.part, self.aug, self.seed, self.in_ch = part, aug, seed, in_ch
        self.size = int(self.d["size"])
        names = self.d["names"]
        want = pd_.ROLES[part]
        per = []
        for n in self.shapes:
            k = names.index(n)
            per.append(list(np.where((self.d["shape_id"] == k) & (self.d["role"] == want))[0]))
        # interleave shapes so that any prefix cycles through the shapes
        self.idx = [i for grp in itertools.zip_longest(*per) for i in grp if i is not None]
        self.length = int(length) if (aug and length) else len(self.idx)

    def __len__(self):
        return self.length

    def _chan(self, x):
        if self.in_ch == 1:
            x[1:] = 0.0
        return x

    def __getitem__(self, i):
        d = self.d
        if self.aug:
            if self.seed is None:
                rng = np.random.default_rng(int(torch.randint(0, 2 ** 31 - 1, (1,)).item()))
            else:
                rng = np.random.default_rng([self.seed, int(i)])
            name = self.shapes[int(rng.integers(len(self.shapes)))]
            g = d["geom_obj"][name]
            ext, _ = pd_.shape_frame(g)
            pose = pd_.sample_pose(rng, self.size, ext, True)
            x, y, s = pd_.render(g, pose, self.size)
        else:
            j = self.idx[i]
            x, y, s = d["inputs"][j], d["targets"][j], float(d["scale"][j])
            name = d["names"][int(d["shape_id"][j])]
        xf = x.astype(np.float32)
        xf[2] /= 255.0
        xf = self._chan(xf)
        return torch.from_numpy(xf), torch.from_numpy(y.astype(np.float32))[None], name, np.float32(s)


def make_datasets(split_spec, n_train, in_ch=3, aug=True, path=pd_.DATASET):
    """-> dict(train, val, test, shapes=(tr, va, te)). Splits are by shape NAME."""
    d = load_npz(path)
    tr, va, te = resolve_split(split_spec, d["splits_obj"])
    return dict(
        train=MidcurveDataset(tr, "train", aug=aug, length=n_train, seed=None, in_ch=in_ch, path=path),
        val=MidcurveDataset(va, "val", aug=False, in_ch=in_ch, path=path),
        test=MidcurveDataset(te, "test", aug=False, in_ch=in_ch, path=path),
        shapes=(tr, va, te))
