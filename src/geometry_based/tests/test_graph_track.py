"""Tests for the geometry (graph) track. Run from src/geometry_based:  conda run -n genai python -m pytest -q

P1: inside-polygon MST reproduces the .edges of the 4 gold shapes and >= 500 synthetic samples.
P2: the generator reproduces the 4 gold .dat profiles exactly.
"""
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # src/geometry_based
while ROOT in sys.path:
    sys.path.remove(ROOT)
sys.path.insert(0, ROOT)
# generic module names (evaluate, dataset, models, ...) may already be cached by legacy tests
for _n in ["common", "methods"]:
    _m = sys.modules.get(_n)
    if _m is not None and not os.path.abspath(getattr(_m, "__file__", "") or "").startswith(ROOT):
        for _k in [k for k in sys.modules if k == _n or k.startswith(_n + ".")]:
            sys.modules.pop(_k, None)

from common import geom  # noqa: E402
from common import prepare_data as pdata  # noqa: E402
from common import evaluate as ev  # noqa: E402

torch = pytest.importorskip("torch")
from common import dataset as D  # noqa: E402
from common import losses  # noqa: E402
from methods.set_transformer.model import MidcurveSetNet  # noqa: E402

GOLD = pdata.load_gold()


@pytest.mark.parametrize("s", GOLD, ids=[g["shape"] for g in GOLD])
def test_p2_generator_reproduces_gold_profile(s):
    spec = pdata.REAL_SPECS[s["shape"]]
    g = pdata.from_skeleton(spec["nodes"], spec["edges"], spec["w"])
    a, b = geom.canonical_cycle(g["profile"]), geom.canonical_cycle(s["profile"])
    assert a.shape == b.shape
    assert np.abs(a - b).max() < 1e-9
    assert len(g["profile"]) == {"I": 4, "L": 6, "T": 8, "Plus": 12}[s["shape"]]


@pytest.mark.parametrize("s", GOLD, ids=[g["shape"] for g in GOLD])
def test_p1_mst_reproduces_gold_edges(s):
    e = geom.edges_from_nodes(s["nodes"], geom.ensure_ccw(s["profile"]))
    assert e == sorted(s["edges"])


def test_gold_edges_expected_lists():
    exp = {"I": [(0, 1)], "L": [(0, 1), (1, 2)], "T": [(0, 1), (1, 2), (1, 3)],
           "Plus": [(0, 1), (1, 2), (1, 3), (1, 4)]}
    for s in GOLD:
        assert s["edges"] == exp[s["shape"]]


def test_p1_mst_reproduces_synthetic_edges():
    pdata.GEN_STATS.update(attempted=0, accepted=0)
    ds = pdata.make_dataset(600, seed=7)
    assert len(ds) == 600
    assert max(len(d["nodes"]) for d in ds) <= 8
    assert pdata.GEN_STATS["accepted"] / pdata.GEN_STATS["attempted"] > 0.2
    bad = [i for i, d in enumerate(ds) if geom.edges_from_nodes(d["nodes"], d["profile"]) != d["edges"]]
    assert bad == [], "MST failed on synthetic samples %s" % bad[:5]


def test_generator_is_seeded_and_polygons_valid():
    a = pdata.make_dataset(5, seed=3)
    b = pdata.make_dataset(5, seed=3)
    for x, y in zip(a, b):
        assert np.array_equal(x["profile"], y["profile"])
        assert geom.signed_area(x["profile"]) > 0
    d4 = pdata.make_dataset(50, seed=1, allow_deg4=False)
    assert max(d["deg_max"] for d in d4) <= 3


def test_point_in_polygon_and_segment_inside():
    sq = np.array([[0, 0], [4, 0], [4, 4], [0, 4]], float)
    assert geom.point_in_polygon(np.array([[2, 2], [5, 5], [4, 2]]), sq, 1e-9).tolist() == [True, False, True]
    assert geom.segment_inside([1, 1], [3, 3], sq)
    assert not geom.segment_inside([1, 1], [5, 1], sq)
    ell = np.array([[0, 0], [4, 0], [4, 1], [1, 1], [1, 4], [0, 4]], float)
    assert not geom.segment_inside([0.5, 3.5], [3.5, 0.5], ell)


def test_metric_identities():
    n = np.array([[0, 0], [0, 10], [10, 10]], float)
    e = [(0, 1), (1, 2)]
    m = ev.graph_metrics(n, e, n, e, w=2.0)
    assert m["chamfer_raw"] == 0 and m["hausdorff_raw"] == 0 and m["edge_f1"] == 1.0
    assert m["ok_025w"] and m["k_err"] == 0 and m["is_tree"]
    m2 = ev.graph_metrics(n[:2], [(0, 1)], n, e, w=2.0)
    assert m2["k_err"] == -1 and not m2["ok_025w"]
    # symmetric
    a = ev.chamfer_hausdorff(np.random.rand(20, 2), np.random.rand(30, 2))
    assert a[0] <= a[1]


def test_featurize_rotation_consistency():
    s = GOLD[3]
    f = D.featurize(s["profile"], s["nodes"])
    assert f["feats"].shape == (D.NMAX, D.FEAT_DIM) and f["gt"].shape == (D.K, 2)
    assert f["mask"].sum() == len(s["profile"]) and f["gt_mask"].sum() == len(s["nodes"])
    rot = lambda p: np.stack([-p[:, 1], p[:, 0]], 1)
    f2 = D.featurize(rot(s["profile"]), rot(s["nodes"]))
    assert np.allclose(rot(f["gt"][f["gt_mask"]]), f2["gt"][f2["gt_mask"]], atol=1e-6)


@pytest.mark.parametrize("B", [1, 8])
def test_forward_pass_batch(B):
    samples = pdata.make_dataset(B, seed=5)
    batch = D.collate([D.featurize(s["profile"], s["nodes"]) for s in samples])
    model = MidcurveSetNet()
    xy, logit = model(batch["feats"], batch["mask"])
    assert xy.shape == (B, D.K, 2) and logit.shape == (B, D.K)
    assert torch.isfinite(xy).all()
    loss, parts = losses.set_loss(xy, logit, batch["gt"], batch["gt_mask"])
    loss.backward()
    assert torch.isfinite(loss)


def test_hungarian_loss_zero_on_permuted_gt():
    torch.manual_seed(0)
    B = 4
    gt = torch.zeros(B, D.K, 2)
    gm = torch.zeros(B, D.K, dtype=torch.bool)
    xy = torch.rand(B, D.K, 2)
    logit = torch.full((B, D.K), -20.0)
    for b in range(B):
        m = 3 + b
        gt[b, :m] = torch.rand(m, 2)
        gm[b, :m] = True
        perm = torch.randperm(D.K)[:m]
        xy[b, perm] = gt[b, :m][torch.randperm(m)]
        logit[b, perm] = 20.0
    total, parts = losses.set_loss(xy, logit, gt, gm)
    assert parts["l1"] < 1e-6
    assert parts["bce"] < 1e-6
    assert float(total) < 1e-5


def test_classical_matches_gold():
    from methods.classical_voronoi.model import classical_midcurve
    for s in GOLD:
        n, e = classical_midcurve(s["profile"])
        m = ev.graph_metrics(n, e, s["nodes"], s["edges"], s["w"])
        assert m["ok_025w"], (s["shape"], m)


def test_loso_real_split_holds_out_one_shape():
    sp = D.build_splits("loso_real", n_train=9, n_val=6, n_test=1, holdout="Plus")
    assert [s["shape"] for s in sp["test"]] == ["Plus"]
    assert {s["shape"] for s in sp["train"]} == {"I", "L", "T"}
    assert len(sp["train"]) == 9 and len(sp["val"]) == 6
    with pytest.raises(ValueError):
        D.build_splits("loso_real", 3, 3, 1)


def test_resume_continues_training(tmp_path):
    import types
    from methods.set_transformer import model as st
    sp = D.build_splits("iid", 64, 32, 10)
    cfg = types.SimpleNamespace(seed=0, device="cpu", threads=1, d=16, enc_layers=1, dec_layers=1,
                                batch_size=32, lr=1e-3, epochs=2, resume=False)
    st.fit(cfg, str(tmp_path), sp)
    # simulate a crash after epoch 1: checkpoint says epoch 1, log still has rows 1-2
    ck = torch.load(str(tmp_path / "last.pt"), weights_only=False)
    ck["epoch"] = 1
    ck["sched"]["_step_count"] = ck["sched"]["_step_count"] // 2
    ck["sched"]["last_epoch"] = ck["sched"]["last_epoch"] // 2
    torch.save(ck, str(tmp_path / "last.pt"))
    cfg.resume = True
    st.fit(cfg, str(tmp_path), sp)
    rows = (tmp_path / "log.csv").read_text().strip().splitlines()
    assert [r.split(",")[0] for r in rows[1:]] == ["1", "2"]


def test_generator_has_no_collinear_degree2_nodes():
    """Regression: the generator's merge once missed collinear nodes whose two neighbours were at different distances."""
    rng = np.random.default_rng(123)
    for _ in range(400):
        s = pdata.make_sample(rng)
        nodes2, _ = geom.remove_collinear_nodes(s["nodes"], s["edges"])
        assert len(nodes2) == len(s["nodes"])
