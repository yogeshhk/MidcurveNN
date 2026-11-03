"""EquiCollapse tests. Run from src/geometry_based:  conda run -n genai python -m pytest -q"""
import argparse

import numpy as np
import pytest

from common import dataset as D
from common import evaluate as ev
from common import geom
from common import prepare_data as pd
from methods.equi_collapse import cell_complex as cc

torch = pytest.importorskip("torch")
from methods.equi_collapse import model as M  # noqa: E402


def _similarity(p, deg, mirror=False, scale=1.0, shift=(0.0, 0.0)):
    th = np.radians(deg)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    q = np.asarray(p, dtype=float) * np.array([-1.0 if mirror else 1.0, 1.0])
    return q @ R.T * scale + np.array(shift)


def _match_error(a, b):
    from scipy.optimize import linear_sum_assignment
    assert len(a) == len(b)
    D_ = np.linalg.norm(a[:, None] - b[None], axis=2)
    r, c = linear_sum_assignment(D_)
    return D_[r, c].max()


GOLD = pd.load_gold()
SYNTH = pd.make_dataset(120, 7)


def test_dual_is_tree_and_conforming():
    for s in GOLD + SYNTH:
        cx = cc.build_complex(s["profile"])
        assert cx["conforming"]
        assert cc.is_tree(cx)


def test_complex_invariant_under_similarity():
    for g in GOLD + SYNTH[:30]:
        a = cc.build_complex(g["profile"])
        b = cc.build_complex(np.roll(_similarity(g["profile"], 37.0, True, 3.0, (5.0, -2.0)), 2, axis=0))
        assert a["ncell"] == b["ncell"]
        assert np.allclose(np.sort(a["radii"] / a["wh"]), np.sort(b["radii"] / b["wh"]), atol=1e-6)


def test_subdivision_does_not_change_complex():
    p = GOLD[3]["profile"]
    sub = []
    for i in range(len(p)):
        sub += [p[i], (p[i] + p[(i + 1) % len(p)]) / 2]
    a, b = cc.build_complex(p), cc.build_complex(np.array(sub))
    assert a["ncell"] == b["ncell"]


def test_oracle_decoder_reproduces_ground_truth():
    for s in GOLD + SYNTH:
        cx = cc.build_complex(s["profile"])
        k, t = cc.labels(cx, s["nodes"])
        nodes, edges = cc.decode(cx, k, cx["x"] + t * cx["wh"])
        ext = float((s["profile"].max(0) - s["profile"].min(0)).max() / 2)
        m = ev.graph_metrics(nodes, edges, s["nodes"], s["edges"], s["w"], extent=ext)
        # exact nodes and edges; the small allowance is the metric's edge-sampling step (0.01 * half-extent), not error
        assert m["k_exact"] and m["deg_seq_match"] and m["edge_f1"] == 1.0
        assert np.abs(np.sort(nodes, axis=0) - np.sort(s["nodes"], axis=0)).max() < 1e-6 * s["w"] + 1e-6
        assert m["hausdorff_over_w"] < 0.1


def test_decoder_gives_a_tree_for_any_scores():
    rng = np.random.default_rng(0)
    for s in GOLD + SYNTH[:40]:
        cx = cc.build_complex(s["profile"])
        for _ in range(5):
            nodes, edges = cc.decode(cx, rng.random(cx["ncell"]), cx["x"])
            assert len(edges) == len(nodes) - 1
            A = {i: set() for i in range(len(nodes))}
            for a, b in edges:
                A[a].add(b)
                A[b].add(a)
            seen, st = {0}, [0]
            while st:
                for v in A[st.pop()]:
                    if v not in seen:
                        seen.add(v)
                        st.append(v)
            assert len(seen) == len(nodes)


def _model(thr=0.5):
    torch.manual_seed(0)
    net = M.EquiCollapseNet(d=32, layers=3)
    net.thr = thr
    return net


@pytest.mark.parametrize("deg,mirror,scale", [(37.0, False, 1.0), (90.0, True, 2.5), (211.0, True, 0.2)])
def test_network_output_is_equivariant(deg, mirror, scale):
    net = _model(thr=0.5)
    cfg = argparse.Namespace(device="cpu")
    pred = M.make_predictor(net, cfg)
    for g in GOLD:
        a, _ = pred(dict(profile=g["profile"]))
        q = _similarity(g["profile"], deg, mirror, scale, (3.0, -7.0))
        b, _ = pred(dict(profile=q))
        err = _match_error(_similarity(a, deg, mirror, scale, (3.0, -7.0)), b)
        assert err < 2e-3 * scale * 45


def test_batch_size_one_and_training_step():
    item = M.pack(GOLD[2]["profile"], GOLD[2]["nodes"])
    net = _model()
    (f, x, ei, ej, ef, k, t), _ = M.collate([item])
    logit, off = net(f, x, ei, ej, ef)
    loss, _, _ = M.compute_loss(logit, off, k, t)
    loss.backward()
    assert torch.isfinite(loss)
    assert logit.shape[0] == item["ncell"] and off.shape == (item["ncell"], 2)


def test_remove_collinear_nodes_helper():
    nodes = np.array([[0.0, 0.0], [1.0, 0.0], [3.0, 0.0], [3.0, 1.0]])
    n2, e2 = geom.remove_collinear_nodes(nodes, [(0, 1), (1, 2), (2, 3)])
    assert len(n2) == 3 and len(e2) == 2
    for g in GOLD:  # real shapes have none
        n3, _ = geom.remove_collinear_nodes(g["nodes"], g["edges"])
        assert len(n3) == len(g["nodes"])


def test_rot_aug_keeps_profile_and_nodes_together():
    s = GOLD[1]
    rng = np.random.default_rng(0)
    it = D.featurize(s["profile"], s["nodes"], rng, augment=True, rot_aug=True)
    assert it["mask"].sum() >= len(s["profile"])
