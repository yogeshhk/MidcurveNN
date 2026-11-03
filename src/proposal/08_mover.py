"""Reorg mover. Usage: python mover.py plan | exec <approach> | verify <approach>
Spec is the single source of the dry-run manifest (08_moves.csv) and the executed moves (08_moves_done.csv).
ASCII only.
"""
import csv
import os
import shutil
import sys
import time

SRC = "D:/Yogesh/GitHub/MidcurveNN/src"
PROP = SRC + "/proposal"
MANIFEST = PROP + "/08_moves.csv"
DONE = PROP + "/08_moves_done.csv"


def ls(p):
    return sorted(os.listdir(os.path.join(SRC, p))) if os.path.isdir(os.path.join(SRC, p)) else []


def spec_image():
    A = "image_based"
    M = A + "/methods"
    out = []

    def mv(o, n):
        out.append((o, n))
    mv(A + "/simpleencoderdecoder", M + "/simple_encoder_decoder")
    mv(A + "/kaggle/simple-encode-decoder-for-midcurvenn.ipynb", M + "/simple_encoder_decoder/kaggle/simple-encode-decoder-for-midcurvenn.ipynb")
    mv(A + "/denseencoderdecoder", M + "/dense_encoder_decoder")
    mv(A + "/cnnencoderdecoder", M + "/cnn_encoder_decoder")
    mv(A + "/denoiserencoderdecoder", M + "/denoiser_encoder_decoder")
    mv(A + "/unet", M + "/unet")
    mv(A + "/pix2pix", M + "/pix2pix")
    mv(A + "/img2img", M + "/pix2pix/img2img")
    mv(A + "/models/__init__.py", M + "/__init__.py")
    mv(A + "/models/_blocks.py", A + "/common/blocks.py")
    mv(A + "/models/simple_ae.py", M + "/simple_encoder_decoder/enhanced/model.py")
    mv(A + "/models/dense_ae.py", M + "/dense_encoder_decoder/enhanced/model.py")
    mv(A + "/models/cnn_ae.py", M + "/cnn_encoder_decoder/enhanced/model.py")
    mv(A + "/models/denoiser_ae.py", M + "/denoiser_encoder_decoder/enhanced/model.py")
    mv(A + "/models/unet.py", M + "/unet/enhanced/model.py")
    mv(A + "/models/pix2pix.py", M + "/pix2pix/enhanced/model.py")
    mv(A + "/models/skeleton.py", M + "/skeleton/model.py")
    for f in ("dataset", "evaluate", "losses", "prepare_data", "collect_results"):
        mv(A + "/%s.py" % f, A + "/common/%s.py" % f)
    mv(A + "/analysis_report.md", A + "/docs/analysis_report.md")
    mv(A + "/testing/test_image_based.py", A + "/tests/test_legacy_image_based.py")
    mv(A + "/testing/__init__.py", A + "/tests/legacy_testing_init.py")
    d = {"skeleton": ("skeleton", False), "simple_ae": ("simple_encoder_decoder", True),
         "dense_ae": ("dense_encoder_decoder", True), "cnn_ae": ("cnn_encoder_decoder", True),
         "denoiser_ae": ("denoiser_encoder_decoder", True), "unet": ("unet", True), "pix2pix": ("pix2pix", True)}
    for r in ls(A + "/runs"):
        mdl, rest = r.split("__", 1)
        m, enh = d[mdl]
        mv(A + "/runs/" + r, M + "/%s/%sruns/%s" % (m, "enhanced/" if enh else "", rest))
    for r in ls(A + "/runs_smoke"):
        mdl, rest = r.split("__", 1)
        m, enh = d[mdl]
        rest = rest.rsplit("__", 1)[0]
        mv(A + "/runs_smoke/" + r, M + "/%s/%sruns/smoke__%s" % (m, "enhanced/" if enh else "", rest))
    return out


def spec_geometry():
    A = "geometry_based"
    M = A + "/methods"
    out = []

    def mv(o, n):
        out.append((o, n))
    mv(A + "/graph_transformer", M + "/graph_transformer")
    mv(A + "/finetuned_graph_transformer", M + "/finetuned_graph_transformer")
    mv(A + "/gnnencoderdecoder", M + "/gnn_encoder_decoder")
    mv(A + "/models/__init__.py", M + "/__init__.py")
    mv(A + "/models/classical.py", M + "/classical_voronoi/model.py")
    mv(A + "/models/set_transformer.py", M + "/set_transformer/model.py")
    for f in ("geom", "dataset", "evaluate", "losses", "prepare_data"):
        mv(A + "/%s.py" % f, A + "/common/%s.py" % f)
    mv(A + "/analysis_report.md", A + "/docs/analysis_report.md")
    mv(A + "/testing/test_geometry_based.py", A + "/tests/test_legacy_geometry_based.py")
    mv(A + "/testing/__init__.py", A + "/tests/legacy_testing_init.py")
    d = {"classical": "classical_voronoi", "set_transformer": "set_transformer"}
    for r in ls(A + "/runs"):
        p = A + "/runs/" + r
        if os.path.isdir(os.path.join(SRC, p)):
            mdl, rest = r.split("__", 1)
            mv(p, M + "/%s/runs/%s" % (d[mdl], rest))
        else:
            m = "classical_voronoi" if r.startswith("classical") else "set_transformer"
            mv(p, M + "/%s/runs/logs/%s" % (m, r))
    return out


def spec_text():
    A = "text_based"
    M = A + "/methods"
    out = []

    def mv(o, n):
        out.append((o, n))
    mv(A + "/finetuning", M + "/qwen_qlora")
    mv(A + "/nemotron3", M + "/nemotron_qlora")
    mv(A + "/codeT5", M + "/code_t5")
    mv(A + "/ludwig", M + "/ludwig")
    mv(A + "/prompt", M + "/manual_prompt")
    mv(A + "/models/__init__.py", M + "/__init__.py")
    mv(A + "/models/fewshot_prompt.py", M + "/fewshot_prompt/model.py")
    mv(A + "/models/lmstudio_prompt.py", M + "/lmstudio_prompt/model.py")
    mv(A + "/models/qwen_qlora.py", M + "/qwen_qlora/enhanced/model.py")
    mv(A + "/models/nemotron_qlora.py", M + "/nemotron_qlora/enhanced/model.py")
    mv(A + "/models/sft_common.py", A + "/common/sft_common.py")
    for f in ("canonical", "formats", "recipes", "prompts", "dataset", "evaluate", "prepare_data"):
        mv(A + "/%s.py" % f, A + "/common/%s.py" % f)
    mv(A + "/prompts", A + "/common/prompt_templates")
    mv(A + "/utils", A + "/common/utils")
    mv(A + "/analysis_report.md", A + "/docs/analysis_report.md")
    mv(A + "/testing/test_text_based.py", A + "/tests/test_legacy_text_based.py")
    mv(A + "/testing/__init__.py", A + "/tests/legacy_testing_init.py")
    return out


SPECS = {"image_based": spec_image, "geometry_based": spec_geometry, "text_based": spec_text}


def stats(path):
    full = os.path.join(SRC, path)
    if os.path.isfile(full):
        return 1, os.path.getsize(full)
    n = s = 0
    for r, ds, fs in os.walk(full):
        ds[:] = [d for d in ds if d not in ("__pycache__", ".pytest_cache")]
        for f in fs:
            n += 1
            s += os.path.getsize(os.path.join(r, f))
    return n, s


def typ(p):
    return "dir" if os.path.isdir(os.path.join(SRC, p)) else "file"


def plan():
    rows = []
    dests = {}
    problems = []
    for a, fn in SPECS.items():
        for o, n in fn():
            if not os.path.exists(os.path.join(SRC, o)):
                problems.append("MISSING source " + o)
            if n in dests:
                problems.append("DUP dest " + n)
            dests[n] = o
            if os.path.exists(os.path.join(SRC, n)):
                problems.append("EXISTS dest " + n)
            rows.append((o, n, typ(o)))
    with open(MANIFEST, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["old_path", "new_path", "type"])
        w.writerows(rows)
    print("manifest rows", len(rows), "problems", len(problems))
    for p in problems:
        print(p)


def exec_(approach):
    new = not os.path.exists(DONE)
    f = open(DONE, "a", newline="")
    w = csv.writer(f)
    if new:
        w.writerow(["old_path", "new_path", "type", "files", "bytes", "time"])
    done = set()
    if not new:
        with open(DONE) as g:
            done = {r["old_path"] for r in csv.DictReader(g)}
    bad = 0
    for o, n in SPECS[approach]():
        if o in done:
            continue
        so, dn = os.path.join(SRC, o), os.path.join(SRC, n)
        if not os.path.exists(so):
            print("SKIP missing", o)
            bad += 1
            continue
        if os.path.exists(dn):
            print("STOP dest exists", n)
            bad += 1
            continue
        c0 = stats(o)
        os.makedirs(os.path.dirname(dn), exist_ok=True)
        shutil.move(so, dn)
        c1 = stats(n)
        ok = c0 == c1
        w.writerow([o, n, typ(n), c1[0], c1[1], time.strftime("%Y-%m-%d %H:%M:%S")])
        f.flush()
        if not ok:
            print("COUNT MISMATCH", o, c0, c1)
            bad += 1
    f.close()
    print("exec done", approach, "problems", bad)


if __name__ == "__main__":
    if sys.argv[1] == "plan":
        plan()
    elif sys.argv[1] == "exec":
        exec_(sys.argv[2])
