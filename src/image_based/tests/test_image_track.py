"""Tests for the new image track (CPU only, no TF). Run from src/image_based:
    conda run -n genai python -m pytest -q
"""
import os
import sys

import numpy as np
import pytest
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.dirname(HERE)
if IMG not in sys.path:
    sys.path.insert(0, IMG)

from common import dataset as ds            # noqa: E402
from common import evaluate as ev           # noqa: E402
from common import losses as L              # noqa: E402
from common import prepare_data as prep     # noqa: E402
from methods import REGISTRY, build_model   # noqa: E402

CPU = torch.device("cpu")


@pytest.fixture(scope="module")
def dataset_path(tmp_path_factory):
    """A small private dataset file (does not touch data/dataset_v1.npz)."""
    p = str(tmp_path_factory.mktemp("d") / "tiny.npz")
    prep.build(p, n_per_shape={"train": 4, "val": 3, "test": 3})
    return p


# ---------------------------------------------------------------- dataset
def test_dataset_shapes_and_channels(dataset_path):
    parts = ds.make_datasets("pose", 8, aug=True, path=dataset_path)
    for part in ("train", "val", "test"):
        x, y, name, scale = parts[part][0]
        assert x.shape == (3, 128, 128) and y.shape == (1, 128, 128)
        assert x.dtype == torch.float32
        assert float(y.sum()) > 10
        assert float(x[1].sum()) > float(y.sum())          # filled mask is larger than the midcurve
        assert 0.0 <= float(x[2].max()) <= 1.0 and abs(float(x[2].max()) - 1.0) < 0.01
        assert scale > 0
    # val is one fixed pose set, deterministic across calls
    a, b = parts["val"][1], parts["val"][1]
    assert torch.equal(a[0], b[0]) and torch.equal(a[1], b[1])


def test_aug_deterministic_with_seed_and_same_transform(dataset_path):
    d = ds.MidcurveDataset(["I", "L", "T", "Plus"], "train", aug=True, length=8, seed=7, path=dataset_path)
    x1, y1, n1, _ = d[3]
    x2, y2, n2, _ = d[3]
    assert n1 == n2 and torch.equal(x1, x2) and torch.equal(y1, y2)
    # same transform for input and target: midcurve pixels lie inside the filled mask dilated by 2 px
    import cv2
    for i in range(8):
        x, y, _, _ = d[i]
        fm = cv2.dilate((x[1].numpy() > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8))
        assert (y[0].numpy() > 0.5)[fm == 0].sum() == 0


def test_split_is_by_shape_name(dataset_path):
    for ho in ("I", "L", "T", "Plus"):
        parts = ds.make_datasets("loso:" + ho, 4, path=dataset_path)
        tr, va, te = parts["shapes"]
        assert te == [ho] and ho not in tr and ho not in va
        names = {parts["test"][i][2] for i in range(len(parts["test"]))}
        assert names == {ho}
        names_tr = {parts["train"][i][2] for i in range(4)}
        assert ho not in names_tr
    tr, va, te = ds.make_datasets("default", 2, path=dataset_path)["shapes"]
    assert (tr, va, te) == (["I", "L"], ["T"], ["Plus"])


def test_edges_match_raw():
    splits, geom = prep.load_raw()
    assert geom["T"]["edges"].tolist() == [[0, 1], [1, 2], [1, 3]]
    assert geom["Plus"]["edges"].tolist() == [[0, 1], [1, 2], [1, 3], [1, 4]]


# ---------------------------------------------------------------- loss
def _line_target(h=64):
    y = torch.zeros(1, 1, h, h)
    y[:, :, h // 2, 8:h - 8] = 1.0
    return y


def test_loss_ordering_and_backward():
    y = _line_target()
    good = (y * 16 - 8).clone().requires_grad_(True)       # confident on the line
    blank = torch.full_like(y, -8.0, requires_grad=True)   # predicts nothing
    for kind in ("bcedice", "focaldice", "bce"):
        lg, lb = L.seg_loss(good, y, kind=kind), L.seg_loss(blank, y, kind=kind)
        assert torch.isfinite(lg) and torch.isfinite(lb)
        assert lg < lb
    L.seg_loss(torch.randn(2, 1, 64, 64, requires_grad=True), y.repeat(2, 1, 1, 1)).backward()


def test_soft_target_peak_is_one():
    t = L.soft_target(_line_target())
    assert abs(float(t.max()) - 1.0) < 1e-5 and float(t.min()) >= 0.0


# ---------------------------------------------------------------- metrics
def _gt():
    y = np.zeros((128, 128), np.float32)
    y[40, 20:100] = 1
    y[40:90, 60] = 1
    return y


def test_metric_identities():
    y = _gt()
    m = ev.sample_metrics(y, y, scale=2.0)
    assert m["f1"] == pytest.approx(1.0) and m["chamfer"] == pytest.approx(0.0)
    assert m["hausdorff"] == pytest.approx(0.0) and m["topo_ok"] == 1.0
    shifted = np.roll(y, 1, axis=0)
    ms = ev.sample_metrics(shifted, y, scale=2.0)
    assert ms["f1"] == pytest.approx(1.0)                   # 1 px shift is inside the 2 px tolerance
    assert ms["chamfer_raw"] == pytest.approx(ms["chamfer"] / 2.0)
    far = np.roll(np.roll(y, 12, axis=0), 12, axis=1)
    assert ev.sample_metrics(far, y)["f1"] < 0.5
    blank = ev.sample_metrics(np.zeros_like(y), y)
    assert blank["f1"] == 0.0 and blank["chamfer"] > 50


# ---------------------------------------------------------------- models
@pytest.mark.parametrize("name", sorted(REGISTRY))
@pytest.mark.parametrize("bs", [1, 2])
def test_forward_all_models(name, bs):
    m = build_model(name, {"size": 128, "in_ch": 3})
    x = torch.rand(bs, 3, 128, 128)
    x[:, 1] = (x[:, 1] > 0.5).float()
    m.eval()
    with torch.no_grad():
        out = m(x)
    assert out.shape == (bs, 1, 128, 128) and torch.isfinite(out).all()


def test_no_batchnorm_anywhere():
    for name in REGISTRY:
        m = build_model(name, {})
        assert not any(isinstance(mod, torch.nn.modules.batchnorm._BatchNorm) for mod in m.modules())


def test_registry_covers_template():
    assert set(REGISTRY) == {"skeleton", "simple_ae", "dense_ae", "cnn_ae", "denoiser_ae", "unet", "pix2pix"}


def test_skeleton_baseline_is_decent(dataset_path):
    parts = ds.make_datasets("pose", 2, path=dataset_path)
    from torch.utils.data import DataLoader
    col = ev.collect(build_model("skeleton"), DataLoader(parts["test"], batch_size=4), CPU)
    assert ev.score(col, 0.5)["all"]["f1"] > 0.6


# ---------------------------------------------------------------- tiny overfit
def test_tiny_overfit(dataset_path):
    """A small unet must fit 8 fixed samples (F1@2px > 0.8) in a couple of minutes on CPU."""
    torch.manual_seed(0)
    parts = ds.make_datasets("pose", 8, path=dataset_path)
    items = [parts["test"][i] for i in range(8)]
    x = torch.stack([it[0] for it in items])
    y = torch.stack([it[1] for it in items])
    model = build_model("unet", {"base": 8, "depth": 3, "drop": 0.0})
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    for _ in range(120):
        loss = L.seg_loss(model(x), y)
        opt.zero_grad()
        loss.backward()
        opt.step()
    model.eval()
    prob = ev.predict_batch(model, x).numpy()[:, 0]
    f1 = np.mean([ev.sample_metrics(p, yy, 1.0, 0.5)["f1"] for p, yy in zip(prob, y.numpy()[:, 0])])
    assert f1 > 0.8, f1
