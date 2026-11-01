"""ONE driver for the geometry (graph) track.

  python run.py prepare
  python run.py baseline --model classical [--split iid|ood_deg4|ood_size] [--tag t] [--quick]
  python run.py train    --model set_transformer --split iid --tag t [--epochs 100] [--quick]
  python run.py eval     --model set_transformer --split iid --tag t

Run from this directory (src/geometry_based). Outputs go to runs/<model>__<split>__<tag>/
{metrics.json, grid.png, log.csv, best.pt, args.json}. Real shapes (I, L, T, Plus) are evaluation
only and are never trained on.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np

import dataset as D
import evaluate as ev
import prepare_data as pdata
from models import REGISTRY


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["prepare", "train", "eval", "baseline"])
    p.add_argument("--model", default="set_transformer")
    p.add_argument("--split", default="iid", choices=["iid", "ood_deg4", "ood_size"])
    p.add_argument("--tag", default="t")
    p.add_argument("--quick", action="store_true")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--n-train", type=int, default=20000, dest="n_train")
    p.add_argument("--n-val", type=int, default=2000, dest="n_val")
    p.add_argument("--n-test", type=int, default=1000, dest="n_test")
    p.add_argument("--batch-size", type=int, default=128, dest="batch_size")
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--d", type=int, default=64)
    p.add_argument("--enc-layers", type=int, default=3, dest="enc_layers")
    p.add_argument("--dec-layers", type=int, default=2, dest="dec_layers")
    p.add_argument("--device", default="cpu")
    p.add_argument("--threads", type=int, default=4, help="torch CPU threads (shared machine)")
    a = p.parse_args(argv)
    if a.quick:
        a.epochs, a.n_train, a.n_val, a.n_test = 3, 512, 128, 100
    return a


def run_dir_for(cfg):
    d = os.path.join(HERE, "runs", "%s__%s__%s" % (cfg.model, cfg.split, cfg.tag))
    os.makedirs(d, exist_ok=True)
    return d


def evaluate_run(cfg, predictor, splits, run_dir, extra=None):
    """Evaluate a predictor on the synthetic test sets of the split and on the real 4 shapes."""
    many = getattr(predictor, "many", None)

    def run_on(samples):
        if not samples:
            return [], []
        if many is not None:
            preds = many(samples)
            cache = {id(s): p for s, p in zip(samples, preds)}
            return ev.evaluate_samples(lambda s: cache[id(s)], samples)
        return ev.evaluate_samples(predictor, samples)

    out = dict(args=vars(cfg), synth={}, real4={})
    t0 = time.time()
    grid_s, grid_p, titles = [], [], []
    gold = D.load_gold()
    rrows, rpreds = run_on(gold)
    for s, r, (pn, pe) in zip(gold, rrows, rpreds):
        out["real4"][s["shape"]] = dict(metrics=r, pred_nodes=np.asarray(pn).tolist(), pred_edges=[list(e) for e in pe],
                                        n_nodes_pred=int(len(pn)), n_edges_pred=int(len(pe)))
        grid_s.append(s)
        grid_p.append((pn, pe))
        titles.append("%s H/w=%.2f %s" % (s["shape"], r["hausdorff_over_w"], "OK" if r["ok_025w"] else "FAIL"))
    out["real4_summary"] = ev.summarize(rrows)
    for name, samples in splits.items():
        if name in ("train", "val"):
            continue
        rows, preds = run_on(samples)
        out["synth"][name] = ev.summarize(rows)
        if name == "test":
            d4 = [r for r in rows if r["deg_max"] == 4]
            if d4:
                out["synth"]["test_deg4_subset"] = ev.summarize(d4)
            for s, r, p in list(zip(samples, rows, preds))[:4]:
                grid_s.append(s)
                grid_p.append(p)
                titles.append("synth H/w=%.2f %s" % (r["hausdorff_over_w"], "OK" if r["ok_025w"] else "FAIL"))
    plus = out["real4"]["Plus"]
    out["P5_real_plus_5nodes_4edges"] = bool(plus["n_nodes_pred"] == 5 and plus["n_edges_pred"] == 4
                                             and plus["metrics"]["ok_025w"])
    out["P4_real4_all_ok"] = bool(all(v["metrics"]["ok_025w"] for v in out["real4"].values()))
    if "test" in out["synth"]:
        s = out["synth"]["test"]
        out["P3_synthetic_test"] = bool(s["k_exact_rate"] >= 0.95 and s["deg_seq_match_rate"] >= 0.90
                                        and s["hausdorff_le_025w_rate"] >= 0.90)
    out["eval_seconds"] = round(time.time() - t0, 1)
    if extra:
        out.update(extra)
    ev.save_json(os.path.join(run_dir, "metrics.json"), out)
    ev.save_grid(os.path.join(run_dir, "grid.png"), grid_s, grid_p, titles)
    ev.save_json(os.path.join(run_dir, "args.json"), vars(cfg))
    return out


def print_summary(out):
    print("--- real4 ---")
    for k, v in out["real4"].items():
        m = v["metrics"]
        print("%-5s nodes %d edges %d  H/w %.3f  chamfer_raw %.3f  hausdorff_raw %.3f  ok_025w %s"
              % (k, v["n_nodes_pred"], v["n_edges_pred"], m["hausdorff_over_w"], m["chamfer_raw"],
                 m["hausdorff_raw"], m["ok_025w"]))
    for name, s in out["synth"].items():
        print("--- synth %s (n=%d) ---" % (name, s["n"]))
        print("k_exact %.3f deg_seq %.3f H<=0.25w %.3f ok_025w %.3f edge_f1 %.3f  H/w median %.3f"
              % (s["k_exact_rate"], s["deg_seq_match_rate"], s["hausdorff_le_025w_rate"], s["ok_025w_rate"],
                 s["edge_f1_mean"], s["hausdorff_over_w_median"]))
    for k in ("P3_synthetic_test", "P4_real4_all_ok", "P5_real_plus_5nodes_4edges"):
        if k in out:
            print(k, out[k])


def main(argv=None):
    cfg = parse(argv)
    if cfg.command == "prepare":
        pdata.prepare()
        return 0
    rd = run_dir_for(cfg)
    if cfg.command == "baseline":
        splits = D.build_splits(cfg.split, 0, 0, cfg.n_test)
        mod = REGISTRY[cfg.model]
        model = mod.build_model(cfg)
        out = evaluate_run(cfg, mod.make_predictor(model, cfg), splits, rd)
        print_summary(out)
        return 0
    mod = REGISTRY[cfg.model]
    splits = D.build_splits(cfg.split, cfg.n_train, cfg.n_val, cfg.n_test)
    if cfg.command == "train":
        ev.save_json(os.path.join(rd, "args.json"), vars(cfg))
        t0 = time.time()
        model = mod.fit(cfg, rd, splits)
        extra = dict(train_seconds=round(time.time() - t0, 1))
    else:
        model = mod.load_best(rd, cfg)
        extra = {}
    extra["nparams"] = int(sum(p.numel() for p in model.parameters()))
    out = evaluate_run(cfg, mod.make_predictor(model, cfg), splits, rd, extra)
    print_summary(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
