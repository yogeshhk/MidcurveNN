"""
run.py -- ONE driver for the text / LLM track.

  python run.py prepare                                   build data/dataset_v1.jsonl from src/data/raw
  python run.py check-model --base-url http://localhost:1234/v1 --model gemma-2-2b-it
                                                          the "is this new LLM any good?" check
  python run.py eval --model lmstudio_prompt --model-id gemma-2-2b-it --format mcv2 --shots 4
  python run.py train --model qwen_qlora --format mcv2 --confirm-gpu   (GPU + model download; not run here)

check-model: --model is the model id served by the OpenAI-compatible server. eval/train: --model is
a registry name (see models/__init__.py); use --model-id for the served / hub model id.
Exit codes: 0 ok, 2 server not reachable or bad usage.
"""
import argparse
import datetime
import importlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from text_based import dataset, evaluate, prompts  # noqa: E402
from text_based.models import REGISTRY, ServerUnavailable, build_model  # noqa: E402

RUNS = os.path.join(_HERE, "runs")


def _safe(name):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def _load_or_build(path=None):
    path = path or dataset.DEFAULT_PATH
    if os.path.isfile(path):
        return dataset.load_rows(path)
    from text_based import prepare_data
    print("NOTE: %s not found; building rows in memory (run 'python run.py prepare' to save them)" % path)
    return prepare_data.build_rows()


def _model_cfg(a):
    return dict(name=a.model, base_url=a.base_url, model_id=a.model_id, max_tokens=a.max_tokens,
                temperature=0.0, adapter_dir=a.adapter_dir, timeout=a.timeout)


def cmd_prepare(a):
    from text_based import prepare_data
    return prepare_data.main(["--seed", str(a.seed), "--n-train", str(a.n_train), "--n-val", str(a.n_val),
                              "--n-test", str(a.n_test)])


CHECK_STYLES = [  # (label, style, format, pose)
    ("brep", "brep", "json", "raw"),
    ("pointlist", "pointlist", "lines", "raw"),
    ("description", "description", "json", "raw"),
    ("fewshot-mcv1", "fewshot", "mcv1", "canonical"),
    ("fewshot-mcv2", "fewshot", "mcv2", "canonical"),
]


def cmd_check_model(a):
    from text_based.models.lmstudio_prompt import LMStudioPrompt, probe_server, DEFAULT_URL
    base_url = a.base_url or DEFAULT_URL
    try:
        ids = probe_server(base_url, timeout=3.0)
    except ServerUnavailable as exc:
        print("check-model: " + str(exc))
        return 2
    chat_ids = [i for i in ids if "embed" not in i.lower()]
    model_id = a.model_id or a.model
    if model_id is None or model_id in REGISTRY:
        model_id = chat_ids[0] if chat_ids else None
    if model_id is None:
        print("check-model: the server lists no chat model; load one in LM Studio.")
        return 2
    if model_id not in ids:
        print("check-model: model %r is not served. Available: %s" % (model_id, ", ".join(ids)))
        return 2
    wanted = set(a.styles.split(",")) if a.styles else None
    model = LMStudioPrompt(base_url=base_url, model_id=model_id, temperature=0.0, max_tokens=a.max_tokens,
                           timeout=a.timeout)
    rows = _load_or_build(a.dataset)
    gold = dataset.select(rows, "pose", "gold")
    pool = gold  # shots are the OTHER gold shapes (no self leak)
    named = {}
    print("check-model: %s at %s, %d gold shapes, shots=%d (leave-self-out)" % (model_id, base_url, len(gold), a.shots))
    try:
        for label, style, fmt, pose in CHECK_STYLES:
            if wanted and label not in wanted:
                continue
            for shots in sorted({0, a.shots}):
                name = "%s/%dshot" % (label, shots)
                print(name)
                named[name] = evaluate.evaluate_rows(model, gold, fmt, pose, shots, style, pool)
    except ServerUnavailable as exc:
        print("check-model: " + str(exc))
        return 2
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    run_dir = os.path.join(RUNS, "check_%s__%s" % (_safe(model_id), stamp))
    cfg = dict(command="check-model", model=model_id, base_url=base_url, temperature=0.0,
               max_tokens=a.max_tokens, shots=a.shots, shot_policy="other gold shapes (leave-self-out)",
               dataset_rows=len(rows))
    notes = ["Model: `%s` at %s, temperature 0, max_tokens %d." % (model_id, base_url, a.max_tokens),
             "Queries are the 4 unaugmented gold shapes (I, L, T, Plus), n=4 per configuration. Shots are the "
             "other gold shapes (the evaluated shape is never a shot), so at most 3 shots are available.",
             "Styles: brep, pointlist, description (raw pose, from prompts/*.txt) and fewshot-mcv1 / "
             "fewshot-mcv2 (canonical pose, compact formats). Raw completions are in raw.jsonl."]
    evaluate.write_run(run_dir, cfg, named, "Model check: %s" % model_id, notes)
    print("\nwrote %s" % run_dir)
    for f in ("raw.jsonl", "metrics.json", "summary.md"):
        p = os.path.join(run_dir, f)
        print("  %-13s %8d bytes" % (f, os.path.getsize(p)))
    print()
    print(open(os.path.join(run_dir, "summary.md"), "r", encoding="utf-8").read())
    return 0


def cmd_eval(a):
    rows = _load_or_build(a.dataset)
    test = dataset.stratified(dataset.select(rows, a.fold, a.split), a.n)
    pool = dataset.select(rows, a.fold, "train")
    if not test:
        print("eval: no rows for fold=%s split=%s" % (a.fold, a.split))
        return 2
    if a.model == "lmstudio_prompt":
        from text_based.models.lmstudio_prompt import probe_server, DEFAULT_URL
        try:
            probe_server(a.base_url or DEFAULT_URL, timeout=3.0)
        except ServerUnavailable as exc:
            print("eval: " + str(exc))
            return 2
    model = build_model(_model_cfg(a))
    print("eval: model=%s id=%s fmt=%s pose=%s style=%s shots=%d fold=%s split=%s n=%d"
          % (a.model, a.model_id, a.format, a.pose, a.style, a.shots, a.fold, a.split, len(test)))
    try:
        res = evaluate.evaluate_rows(model, test, a.format, a.pose, a.shots, a.style, pool)
    except ServerUnavailable as exc:
        print("eval: " + str(exc))
        return 2
    named = {"%s (%dshot)" % (a.model_id or a.model, a.shots): res,
             "baseline: nearest_train_copy": evaluate.baseline_results("nearest_train_copy", test, pool),
             "baseline: empty": evaluate.baseline_results("empty", test, pool)}
    tag = a.tag or "%s_%s_%dshot_%s_%s" % (a.format, a.style, a.shots, a.fold, a.split)
    run_dir = os.path.join(RUNS, "%s__%s" % (_safe(a.model_id or a.model), _safe(tag)))
    cfg = dict(command="eval", model=a.model, model_id=a.model_id, format=a.format, pose=a.pose, style=a.style,
               shots=a.shots, fold=a.fold, split=a.split, n=len(test), base_url=a.base_url)
    notes = ["Fold `%s`, split `%s`, n=%d. Fold `pose` means every shape is also in training (pose-level only, "
             "not shape generalisation)." % (a.fold, a.split, len(test))]
    evaluate.write_run(run_dir, cfg, named, "Eval: %s" % tag, notes)
    print("wrote %s" % run_dir)
    print(open(os.path.join(run_dir, "summary.md"), "r", encoding="utf-8").read())
    return 0


def cmd_train(a):
    if a.model not in REGISTRY:
        print("train: unknown model %r; choose from %s" % (a.model, sorted(REGISTRY)))
        return 2
    mod = importlib.import_module(REGISTRY[a.model])
    if not hasattr(mod, "train"):
        print("train: %s has no train(); only qwen_qlora and nemotron_qlora do." % a.model)
        return 2
    if not a.confirm_gpu:
        print("train: this needs a GPU and a model download. Re-run with --confirm-gpu when you are ready.")
        return 2
    out = os.path.join(RUNS, "%s__%s" % (a.model, a.tag or a.format))
    cfg = dict(model_id=a.model_id, fmt=a.format, pose=a.pose, style=a.style, fold=a.fold, out_dir=out,
               max_steps=a.max_steps if a.max_steps else -1, dataset=a.dataset)
    print("train: ->", mod.train(cfg))
    return 0


def build_parser():
    ap = argparse.ArgumentParser(description="Text / LLM track driver")
    ap.add_argument("command", choices=["prepare", "eval", "check-model", "train"])
    ap.add_argument("--model", default=None, help="registry name (eval/train) or served model id (check-model)")
    ap.add_argument("--model-id", default=None, help="served / hub model id")
    ap.add_argument("--format", default="mcv2", choices=["json", "mcv1", "mcv2", "lines"])
    ap.add_argument("--pose", default="canonical", choices=["canonical", "raw"])
    ap.add_argument("--style", default="fewshot", help="prompt style: %s" % ", ".join(prompts.list_styles()))
    ap.add_argument("--fold", default="pose", help="pose | default | loso_<Shape>")
    ap.add_argument("--split", default="test", help="train | val | test | gold")
    ap.add_argument("--shots", type=int, default=None)
    ap.add_argument("--n", type=int, default=40, help="max eval rows (stratified by shape)")
    ap.add_argument("--base-url", default=None, help="OpenAI-compatible server, default http://localhost:1234/v1")
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--timeout", type=float, default=240.0, help="per request seconds")
    ap.add_argument("--styles", default=None, help="check-model: comma list of brep,pointlist,description,fewshot-mcv1,fewshot-mcv2")
    ap.add_argument("--adapter-dir", default=None)
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--confirm-gpu", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=100)
    ap.add_argument("--n-val", type=int, default=10)
    ap.add_argument("--n-test", type=int, default=20)
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    if a.shots is None:
        a.shots = 3 if a.command == "check-model" else 0
    if a.command == "eval" and a.model is None:
        a.model = "lmstudio_prompt"
    return {"prepare": cmd_prepare, "check-model": cmd_check_model, "eval": cmd_eval,
            "train": cmd_train}[a.command](a)


if __name__ == "__main__":
    sys.exit(main())
