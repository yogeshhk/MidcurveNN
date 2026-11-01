"""
test_text_track.py -- tests for the new text / LLM track (no GPU, no model download, no real server).

    cd src
    conda run -n genai python -m pytest text_based/tests/test_text_track.py -q
"""
import inspect
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(os.path.dirname(_HERE))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from text_based import canonical, dataset, evaluate, formats, prepare_data, prompts, recipes  # noqa: E402
from text_based.formats import Graph  # noqa: E402

SHAPES = ["I", "L", "T", "Plus"]


@pytest.fixture(scope="module")
def raw():
    shapes, splits = prepare_data.load_raw()
    return shapes


@pytest.fixture(scope="module")
def rows():
    return prepare_data.build_rows(seed=0, n_train=6, n_val=2, n_test=3)


@pytest.fixture(scope="module")
def gold(rows):
    return dataset.select(rows, "pose", "gold")


# ---------------------------------------------------------------------------
# raw data and codecs
# ---------------------------------------------------------------------------

def test_edges_match_brep_json(raw):
    brep = os.path.join(_SRC, "text_based", "data", "brep")
    for s in SHAPES:
        d = json.load(open(os.path.join(brep, s + ".json"), encoding="utf-8"))
        pts = np.array(d["Midcurve_brep"]["Points"], float)
        assert pts.shape == raw[s]["midcurve"].shape and np.allclose(pts, raw[s]["midcurve"])
        a = {tuple(sorted(e)) for e in d["Midcurve_brep"]["Lines"]}
        b = {tuple(sorted(e)) for e in raw[s]["edges"]}
        assert a == b, s


@pytest.mark.parametrize("fmt", ["json", "mcv1", "mcv2", "lines"])
@pytest.mark.parametrize("pose", ["raw", "canonical"])
def test_codec_round_trip_on_gold(gold, fmt, pose):
    codec = formats.get_codec(fmt)
    assert len(gold) == 4
    for r in gold:
        profile, mid, edges = dataset.view(r, pose)
        text = codec.encode_midcurve(mid, edges, profile, recipes.recipe_tol(pose))
        g, strict = codec.decode_midcurve(text, profile)
        assert g is not None and strict, (fmt, pose, r["id"], text)
        assert len(g.points) == len(mid) and len(g.edges) == len(edges)
        # same geometry as a set of edges (lines codec reorders points)
        want = sorted(tuple(sorted(map(tuple, np.round(mid[list(e)], 2).tolist()))) for e in edges)
        have = sorted(tuple(sorted(map(tuple, np.round(g.points[list(e)], 2).tolist()))) for e in g.edges)
        np.testing.assert_allclose(np.array(want), np.array(have), atol=1.01 if pose == "canonical" else 1e-6)


def test_garbage_and_truncation_decode_to_none_or_flagged(gold):
    profile = dataset.view(gold[0], "canonical")[0]
    for fmt in ("json", "mcv1", "mcv2", "lines"):
        codec = formats.get_codec(fmt)
        for junk in ("", "I do not know", "{{{{", "[]"):
            g, strict = codec.decode_midcurve(junk, profile)
            assert g is None and not strict, (fmt, junk)
    full = formats.get_codec("json").encode_midcurve(*dataset.view(gold[2], "raw")[1:], None)
    g, strict = formats.get_codec("json").decode_midcurve(full[:len(full) // 2])
    assert g is None or not strict


def test_lenient_decoders_accept_chatty_output(gold):
    profile, mid, edges = dataset.view(gold[2], "raw")
    js = formats.get_codec("json").encode_midcurve(mid, edges)
    g, strict = formats.get_codec("json").decode_midcurve("Sure! Here you go:\n```json\n%s\n```\nHope it helps" % js)
    assert g is not None and not strict and len(g.edges) == 3
    g, strict = formats.get_codec("json").decode_midcurve("<think>{x}</think>" + js.replace('"', "'"))
    assert g is not None and not strict
    g, strict = formats.get_codec("mcv1").decode_midcurve("midcurve n=2 e=1\n(0,1) (5,6)\n0-1 trailing words")
    assert g is not None and not strict and g.edges == [(0, 1)]


def test_decoder_does_not_fabricate_edges():
    g, _ = formats.get_codec("json").decode_midcurve('{"Points": [[0,0],[1,1],[2,2]]}')
    assert g is not None and g.edges == []


# ---------------------------------------------------------------------------
# canonicalisation
# ---------------------------------------------------------------------------

def _transform(P, M, rng):
    mirror = rng.random() < 0.5
    a = rng.uniform(0, 2 * np.pi)
    s = rng.uniform(0.5, 6)
    t = rng.uniform(-50, 50, 2)
    R = canonical.rot_matrix(a)

    def f(Q):
        Q = np.array(Q, float)
        if mirror:
            Q[:, 0] *= -1
        return (Q @ R.T) * s + t

    return f(P), f(M)


@pytest.mark.parametrize("name", SHAPES)
def test_canonical_invariance_and_inverse(raw, name):
    sh = raw[name]
    base = canonical.canonicalise(sh["profile"], sh["midcurve"], sh["edges"])
    rng = np.random.default_rng(1)
    for _ in range(25):
        P, M = _transform(sh["profile"], sh["midcurve"], rng)
        c = canonical.canonicalise(P, M, sh["edges"])
        assert c["profile"].shape == base["profile"].shape
        assert np.abs(c["profile"] - base["profile"]).max() <= 2
        assert np.abs(c["midcurve"] - base["midcurve"]).max() <= 2
        assert c["edges"] == base["edges"]
        back = canonical.decanonicalise(c["midcurve"], c["transform"])
        size = np.ptp(P, axis=0).max()
        dm = np.linalg.norm(back[:, None, :] - M[None, :, :], axis=2)  # canonical vertex order differs
        assert dm.min(axis=1).max() < 0.01 * size and dm.min(axis=0).max() < 0.01 * size
        backp = canonical.decanonicalise(c["profile"], c["transform"])
        # profile came back in canonical vertex order: every point must match some original vertex
        d = np.linalg.norm(backp[:, None, :] - P[None, :, :], axis=2).min(axis=1)
        assert d.max() < 0.01 * size


def test_dataset_rows_and_splits(rows):
    assert {r["shape"] for r in rows} == set(SHAPES)
    assert sum(r["kind"] == "gold" for r in rows) == 4
    for r in rows:
        assert r["recipe_coverage"] == 1.0
        if r["kind"] == "pose":
            assert r["splits"]["default"] in ("train", "val", "test")
    assert all(r["shape"] == "Plus" for r in dataset.select(rows, "default", "test"))
    assert {r["shape"] for r in dataset.select(rows, "loso_T", "test")} == {"T"}
    assert "T" not in {r["shape"] for r in dataset.select(rows, "loso_T", "train")}
    again = prepare_data.build_rows(seed=0, n_train=6, n_val=2, n_test=3)
    assert json.dumps(again[5]) == json.dumps(rows[5])  # seeded, reproducible


# ---------------------------------------------------------------------------
# recipes
# ---------------------------------------------------------------------------

def test_recipes_exist_for_all_gold_midcurve_vertices(raw):
    for s in SHAPES:
        for v in raw[s]["midcurve"]:
            r = recipes.find_recipe(raw[s]["profile"], v, 1e-6)
            assert r is not None, (s, v)
            np.testing.assert_allclose(raw[s]["profile"][list(r)].mean(axis=0), v, atol=1e-6)


# ---------------------------------------------------------------------------
# metrics
# ---------------------------------------------------------------------------

def _row(gold, name):
    return [r for r in gold if r["shape"] == name][0]


def test_metric_identities(gold):
    for r in gold:
        gt, _ = evaluate.gt_raw_graph(r)
        rec = evaluate.score_graph(Graph(gt.points.copy(), list(gt.edges)), r)
        assert rec["chamfer"] == pytest.approx(0, abs=1e-9) and rec["hausdorff"] == pytest.approx(0, abs=1e-9)
        assert rec["edge_f1"] == 1.0 and rec["graph_exact"] and rec["branch_acc"] and not rec["wrong_but_valid"]


def test_metric_star_vs_path_and_disjoint_and_empty(gold):
    r = _row(gold, "T")
    gt, profile = evaluate.gt_raw_graph(r)
    path = Graph(gt.points.copy(), [(0, 1), (1, 2), (2, 3)])  # same vertices, wrong edges
    rec = evaluate.score_graph(path, r)
    assert rec["edge_f1"] < 1.0 and rec["wrong_but_valid"] and not rec["graph_exact"]
    far = Graph(gt.points + 1000.0, list(gt.edges))
    rec = evaluate.score_graph(far, r)
    assert rec["chamfer_n"] > 10 and rec["edge_f1"] == 0.0
    rec = evaluate.score_graph(None, r)
    assert rec["parse_ok"] is False and rec["edge_f1"] == 0.0 and rec["chamfer_pen_n"] == 1.0


def test_sample_polyline_covers_edges():
    pts = evaluate.sample_polyline(np.array([[0.0, 0.0], [10.0, 0.0]]), [(0, 1)], 1.0)
    assert len(pts) == 11 and pts[:, 0].max() == 10.0


def test_score_text_end_to_end_gold_text_is_perfect(rows, gold):
    for fmt, pose in (("json", "raw"), ("mcv1", "canonical"), ("mcv2", "canonical"), ("lines", "raw")):
        for r in gold + dataset.select(rows, "pose", "test")[:6]:
            msgs, ans = prompts.build_messages(r, fmt, pose)
            rec = evaluate.score_text(r, ans, fmt, pose, ans)
            assert rec["parse_strict"] and rec["graph_exact"] and rec["edge_f1"] == 1.0, (fmt, pose, r["id"])
            assert rec["chamfer_n"] < 0.01


def test_baselines(rows):
    test = dataset.select(rows, "pose", "test")
    train = dataset.select(rows, "pose", "train")
    empty = evaluate.baseline_results("empty", test, train)
    assert all(not x["parse_ok"] for x in empty)
    near = evaluate.baseline_results("nearest_train_copy", test, train)
    assert np.mean([x["edge_f1"] for x in near]) > 0.9  # pose-level fold: copying works (the leak, shown)
    loso = evaluate.baseline_results("nearest_train_copy", dataset.select(rows, "loso_T", "test"),
                                     dataset.select(rows, "loso_T", "train"))
    assert np.mean([x["edge_f1"] for x in loso]) < 0.6  # unseen shape: copying fails


# ---------------------------------------------------------------------------
# prompts: one builder for training and inference
# ---------------------------------------------------------------------------

class StubTok:
    eos_token_id = 99
    pad_token_id = 0

    def apply_chat_template(self, messages, add_generation_prompt=False, tokenize=True, **kw):
        text = "".join("<%s>%s" % (m["role"], m["content"]) for m in messages) + "<assistant>"
        return [ord(c) % 90 + 1 for c in text]

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [ord(c) % 90 + 1 for c in text]}


def test_prompt_builder_identical_for_train_and_inference(rows):
    from text_based.models import sft_common
    src = inspect.getsource(sft_common.build_examples)
    assert "prompts.build_messages" in src
    r = dataset.select(rows, "pose", "train")[0]
    m1, a1 = prompts.build_messages(r, "mcv2", "canonical", (), "fewshot")
    m2, a2 = prompts.build_messages(r, "mcv2", "canonical", (), "fewshot")
    assert m1 == m2 and a1 == a2 and m1[-1]["role"] == "user"
    tok = StubTok()
    ex = sft_common.build_examples(tok, [r], "mcv2", "canonical", "fewshot", 4096)[0]
    prompt_ids = tok.apply_chat_template(m1, add_generation_prompt=True)
    assert ex["input_ids"][:len(prompt_ids)] == prompt_ids  # inference prompt == training prefix
    assert all(l == -100 for l in ex["labels"][:len(prompt_ids)])
    assert ex["labels"][-1] == tok.eos_token_id and ex["labels"][len(prompt_ids)] != -100
    with pytest.raises(ValueError):
        sft_common.tokenize_example(tok, m1, a1, max_len=10)


def test_shots_never_use_query_shape_and_style_files(rows):
    pool = dataset.select(rows, "pose", "train")
    q = dataset.select(rows, "pose", "test")[0]
    shots = prompts.select_shots(q, pool, 4)
    assert len(shots) == 4 and all(s["shape"] != q["shape"] for s in shots)
    msgs, _ = prompts.build_messages(q, "json", "raw", shots, "brep")
    assert [m["role"] for m in msgs] == ["system"] + ["user", "assistant"] * 4 + ["user"]
    for st in ("brep", "pointlist", "description", "fewshot"):
        assert prompts.load_style(st)["system"]
    assert "Description:" in prompts.build_messages(q, "json", "raw", (), "description")[0][-1]["content"]
    merged = prompts.merge_system_into_user(msgs)
    assert merged[0]["role"] == "user" and "geometric transformation" in merged[0]["content"]


# ---------------------------------------------------------------------------
# lmstudio client + check-model against a stub server
# ---------------------------------------------------------------------------

class _Stub(BaseHTTPRequestHandler):
    reject_system = False
    seen = []
    reply = '{"Points": [[0, 0], [1, 0]], "Lines": [[0, 1]], "Segments": [[0]]}'

    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/models"):
            self._send(200, {"object": "list", "data": [{"id": "stub-model", "object": "model"},
                                                         {"id": "text-embedding-x", "object": "model"}]})
        else:
            self._send(404, {})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n).decode("utf-8"))
        _Stub.seen.append(req)
        if _Stub.reject_system and any(m["role"] == "system" for m in req["messages"]):
            self._send(400, {"error": {"message": "System role not supported", "type": "invalid_request_error"}})
            return
        self._send(200, {"id": "x", "object": "chat.completion", "created": 0, "model": req["model"],
                         "choices": [{"index": 0, "finish_reason": "stop",
                                      "message": {"role": "assistant", "content": _Stub.reply}}],
                         "usage": {"prompt_tokens": 7, "completion_tokens": 5, "total_tokens": 12}})


@pytest.fixture()
def stub():
    _Stub.seen = []
    _Stub.reject_system = False
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Stub)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:%d/v1" % srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def test_lmstudio_client_against_stub(stub):
    from text_based.models import build_model
    from text_based.models.lmstudio_prompt import probe_server
    assert probe_server(stub, timeout=3) == ["stub-model", "text-embedding-x"]
    m = build_model({"name": "lmstudio_prompt", "base_url": stub})  # no model id: first non-embedding
    msgs = [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}]
    out = m.generate(msgs)
    assert out.startswith("{") and m.model_id == "stub-model"
    assert m.last_info["finish_reason"] == "stop" and m.last_info["prompt_tokens"] == 7
    req = _Stub.seen[-1]
    assert req["temperature"] == 0.0 and req["max_tokens"] >= 1024 and req["messages"][0]["role"] == "system"


def test_lmstudio_client_merges_system_when_rejected(stub):
    from text_based.models import build_model
    _Stub.reject_system = True
    m = build_model({"name": "lmstudio_prompt", "base_url": stub, "model_id": "stub-model"})
    out = m.generate([{"role": "system", "content": "SYS"}, {"role": "user", "content": "U"}])
    assert out and m.last_info["system_merged"]
    assert _Stub.seen[-1]["messages"][0]["role"] == "user" and "SYS" in _Stub.seen[-1]["messages"][0]["content"]


def test_unreachable_server_is_friendly():
    from text_based.models import ServerUnavailable
    from text_based.models.lmstudio_prompt import probe_server
    with pytest.raises(ServerUnavailable):
        probe_server("http://127.0.0.1:9/v1", timeout=1)


def test_registry_lists_all_models():
    from text_based.models import REGISTRY
    assert set(REGISTRY) == {"lmstudio_prompt", "fewshot_prompt", "qwen_qlora", "nemotron_qlora"}


def test_check_model_end_to_end_against_stub(stub, tmp_path, capsys):
    import text_based.run as run
    run.RUNS = str(tmp_path)
    code = run.main(["check-model", "--base-url", stub, "--model", "stub-model", "--max-tokens", "256"])
    assert code == 0
    dirs = [d for d in os.listdir(str(tmp_path)) if d.startswith("check_stub-model__")]
    assert len(dirs) == 1
    d = os.path.join(str(tmp_path), dirs[0])
    for f in ("raw.jsonl", "metrics.json", "summary.md"):
        assert os.path.getsize(os.path.join(d, f)) > 0
    lines = [json.loads(l) for l in open(os.path.join(d, "raw.jsonl"), encoding="utf-8")]
    assert len(lines) == 4 * 2 * 5  # 4 shapes x {0,3 shots} x 5 prompt styles
    assert all("completion" in l and "messages" in l for l in lines)
    met = json.load(open(os.path.join(d, "metrics.json"), encoding="utf-8"))
    assert "brep/0shot" in met["overall"]
    assert "Model check" in open(os.path.join(d, "summary.md"), encoding="utf-8").read()


def test_check_model_without_server_exits_with_message(capsys):
    import text_based.run as run
    code = run.main(["check-model", "--base-url", "http://127.0.0.1:9/v1", "--model", "whatever"])
    assert code == 2
    assert "Start LM Studio" in capsys.readouterr().out


def test_eval_against_stub_has_baselines(stub, tmp_path):
    import text_based.run as run
    run.RUNS = str(tmp_path)
    code = run.main(["eval", "--model", "lmstudio_prompt", "--model-id", "stub-model", "--base-url", stub,
                     "--format", "json", "--pose", "raw", "--n", "4", "--shots", "2"])
    assert code == 0
    d = os.path.join(str(tmp_path), os.listdir(str(tmp_path))[0])
    text = open(os.path.join(d, "summary.md"), encoding="utf-8").read()
    assert "baseline: nearest_train_copy" in text and "baseline: empty" in text
