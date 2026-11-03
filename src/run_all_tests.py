"""Run every test suite of MidcurveNN, one pytest process per suite, and print a table.

    cd src
    conda run -n genai python run_all_tests.py            # approach suites + method-local legacy suites
    conda run -n genai python run_all_tests.py --approach image_based
    conda run -n genai python run_all_tests.py --no-legacy-methods

Why separate processes: each approach has its own `common` and `methods` packages, and several old scripts define
generic module names (config, utils), so suites cannot share one interpreter. Known failures that predate the
2026-11-03 reorganisation are listed in proposal/08_REORG_PLAN.md (baseline table).
"""
import argparse
import os
import re
import subprocess
import sys

SRC = os.path.dirname(os.path.abspath(__file__))

# (approach, target relative to the approach folder, kind)
SUITES = [
    ("image_based", "tests", "approach"),
    ("geometry_based", "tests", "approach"),
    ("text_based", "tests", "approach"),
    ("image_based", "methods/unet/test_unet.py", "method"),
    ("image_based", "methods/pix2pix/test_pix2pix.py", "method"),
    ("image_based", "methods/pix2pix/img2img/test_img2img.py", "method"),
    ("image_based", "methods/simple_encoder_decoder/test_simple_encoderdecoder.py", "method"),
    ("image_based", "methods/cnn_encoder_decoder/test_cnn_encoderdecoder.py", "method"),
    ("image_based", "methods/dense_encoder_decoder/test_dense_encoderdecoder.py", "method"),
    ("image_based", "methods/denoiser_encoder_decoder/test_denoiser_encoderdecoder.py", "method"),
    ("geometry_based", "methods/graph_transformer/test_graph_transformer.py", "method"),
    ("geometry_based", "methods/finetuned_graph_transformer/test_finetuned_graph_transformer.py", "method"),
    ("text_based", "methods/qwen_qlora/test_metrics.py", "method"),
]


def run(approach, target):
    cmd = [sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider"]
    p = subprocess.run(cmd, cwd=os.path.join(SRC, approach), capture_output=True, text=True)
    out = (p.stdout or "") + (p.stderr or "")
    tail = [ln for ln in out.splitlines() if re.search(r"\b(passed|failed|error|errors|skipped)\b", ln)]
    return (tail[-1].strip("= ").strip() if tail else "no result line (exit %d)" % p.returncode), p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--approach", default=None)
    ap.add_argument("--no-legacy-methods", action="store_true")
    a = ap.parse_args()
    rows = []
    for approach, target, kind in SUITES:
        if a.approach and approach != a.approach:
            continue
        if a.no_legacy_methods and kind == "method":
            continue
        res, code = run(approach, target)
        rows.append((approach, target, res))
        print("%-15s %-75s %s" % (approach, target, res), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
