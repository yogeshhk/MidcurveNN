"""ONE driver for the image track.

  python run.py prepare
  python run.py train --model unet --split pose --tag base
  python run.py eval  --model unet --split pose --tag base --tta
  python run.py train --model cnn_ae --split loso:Plus --tag base

Models: skeleton simple_ae dense_ae cnn_ae denoiser_ae unet pix2pix
Splits: pose | default | loso:<Shape>     (by shape NAME, from data/dataset_v1.npz / splits.json)
Run folder: runs/<model>__<split>__<tag>/{metrics.json, grid.png, log.csv, best.pt, args.json}
"""
import argparse
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import torch
from torch.utils.data import DataLoader

import dataset as ds
import evaluate as ev
import prepare_data as prep
from losses import seg_loss
from models import REGISTRY, get_module

DEFAULT_RUNS = os.path.join(HERE, "runs")


def parse(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["prepare", "train", "eval"])
    p.add_argument("--model", default="unet", choices=sorted(REGISTRY))
    p.add_argument("--split", default="pose")
    p.add_argument("--tag", default="base")
    p.add_argument("--quick", action="store_true", help="2 epochs x 5 steps, batch 4 (smoke test)")
    p.add_argument("--epochs", type=int, default=40)
    p.add_argument("--steps", type=int, default=125, help="batches per epoch")
    p.add_argument("--bs", type=int, default=16)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--loss", default="bcedice", choices=["bce", "bcedice", "focaldice"])
    p.add_argument("--pos-weight", type=float, default=10.0)
    p.add_argument("--sigma", type=float, default=1.2)
    p.add_argument("--dice-w", type=float, default=1.0)
    p.add_argument("--tol", type=float, default=2.0)
    p.add_argument("--tta", action="store_true")
    p.add_argument("--in-ch", type=int, default=3, choices=[1, 3])
    p.add_argument("--no-aug", action="store_true", help="train on the stored fixed poses only")
    p.add_argument("--base", type=int, default=None)
    p.add_argument("--depth", type=int, default=None)
    p.add_argument("--adv-warmup", type=int, default=5)
    p.add_argument("--adv-ramp", type=int, default=10)
    p.add_argument("--stage1", default=None, help="denoiser_ae: run dir of a trained stage-1 model "
                                                  "(default: the non-learned skeleton baseline)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default="auto")
    p.add_argument("--workers", type=int, default=0)
    p.add_argument("--out", default=DEFAULT_RUNS)
    a = p.parse_args(argv)
    if a.quick:
        a.epochs, a.steps, a.bs, a.adv_warmup, a.adv_ramp = 2, 5, 4, 0, 1
    if a.lr is None:
        a.lr = 5e-4 if a.model == "pix2pix" else 2e-3
    return a


def run_name(a):
    return "%s__%s__%s" % (a.model, a.split.replace(":", "-"), a.tag)


def get_device(a):
    if a.device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(a.device)


def model_cfg(a):
    cfg = {"size": prep.SIZE, "in_ch": a.in_ch}
    if a.base:
        cfg["base"] = a.base
    if a.depth:
        cfg["depth"] = a.depth
    return cfg


def n_params(m):
    return int(sum(p.numel() for p in m.parameters()))


class DefaultTrainer:
    """AdamW + OneCycle + grad clip; optional input hook (denoiser corruption)."""

    def __init__(self, model, a, dev, spe, mod):
        self.model, self.a, self.mod = model, a, mod
        self.opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
        self.sched = torch.optim.lr_scheduler.OneCycleLR(self.opt, max_lr=a.lr,
                                                         total_steps=max(2, a.epochs * spe))
        self.hook = getattr(mod, "train_input", None)

    def step(self, x, y, epoch):
        xin = self.hook(x, y) if self.hook else x
        loss = seg_loss(self.model(xin), y, self.a.pos_weight, self.a.sigma, self.a.dice_w, self.a.loss)
        self.opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
        self.opt.step()
        self.sched.step()
        return float(loss.item())


def load_model_from_run(run_dir, dev):
    with open(os.path.join(run_dir, "args.json")) as f:
        ra = argparse.Namespace(**json.load(f))
    m = get_module(ra.model).build_model(model_cfg(ra)).to(dev)
    ck = os.path.join(run_dir, "best.pt")
    if os.path.exists(ck):
        m.load_state_dict(torch.load(ck, map_location=dev))
    m.eval()
    return m


def make_pre(a, dev):
    """Input hook for the denoiser (chained after a stage-1 predictor); None for other models."""
    mod = get_module(a.model)
    if not hasattr(mod, "eval_input"):
        return None
    if a.stage1:
        s1 = load_model_from_run(a.stage1, dev)
    else:
        s1 = get_module("skeleton").build_model({})
    s1.eval()

    def pre(x):
        with torch.no_grad():
            return mod.eval_input(x, torch.sigmoid(s1(x)))
    return pre


def loaders(parts, a):
    mk = lambda d, sh: DataLoader(d, batch_size=a.bs, shuffle=sh, num_workers=a.workers, drop_last=False)
    return mk(parts["train"], False), mk(parts["val"], False), mk(parts["test"], False)


def do_train(a):
    dev = get_device(a)
    torch.manual_seed(a.seed)
    np.random.seed(a.seed)
    if not os.path.exists(prep.DATASET):
        print("dataset missing, building ...")
        prep.build()
    out = os.path.join(a.out, run_name(a))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "args.json"), "w") as f:
        json.dump(vars(a), f, indent=1)
    parts = ds.make_datasets(a.split, a.steps * a.bs, a.in_ch, aug=not a.no_aug)
    trl, val, tel = loaders(parts, a)
    mod = get_module(a.model)
    model = mod.build_model(model_cfg(a)).to(dev)
    pre = make_pre(a, dev)
    trainable = n_params(model) > 0
    print("run %s | device %s | params %d | train shapes %s | val %s | test %s" % (
        run_name(a), dev, n_params(model), parts["shapes"][0], parts["shapes"][1], parts["shapes"][2]))
    secs, best_ep, best = [], -1, -1.0
    t_start = time.time()
    if trainable:
        spe = len(trl)
        trainer = mod.make_trainer(model, a, dev, spe) if hasattr(mod, "make_trainer") \
            else DefaultTrainer(model, a, dev, spe, mod)
        logf = open(os.path.join(out, "log.csv"), "w", newline="")
        w = csv.writer(logf)
        w.writerow(["epoch", "loss", "val_f1", "val_chamfer_raw", "sec"])
        for ep in range(a.epochs):
            t0 = time.time()
            model.train()
            tot = 0.0
            for x, y, _, _ in trl:
                tot += trainer.step(x.to(dev), y.to(dev), ep)
            sec = time.time() - t0
            col = ev.collect(model, val, dev, False, pre)
            r = ev.score(col, 0.5, a.tol)["all"]
            secs.append(sec)
            w.writerow([ep, tot / len(trl), r["f1"], r["chamfer_raw"], sec])
            logf.flush()
            print("ep %d loss %.4f val_f1 %.3f val_chamfer_raw %.3f (%.1fs)" % (
                ep, tot / len(trl), r["f1"], r["chamfer_raw"], sec), flush=True)
            if r["f1"] > best:
                best, best_ep = r["f1"], ep
                torch.save(model.state_dict(), os.path.join(out, "best.pt"))
        logf.close()
        model.load_state_dict(torch.load(os.path.join(out, "best.pt"), map_location=dev))
    train_time = time.time() - t_start
    write_final(a, model, val, tel, dev, pre, out, "metrics.json", "grid.png",
                extra=dict(params=n_params(model), epochs=a.epochs, steps_per_epoch=len(trl),
                           best_epoch=best_ep, sec_per_epoch=float(np.mean(secs)) if secs else 0.0,
                           train_time_s=train_time, device=str(dev)))


def write_final(a, model, val, tel, dev, pre, out, mname, gname, extra=None):
    cv = ev.collect(model, val, dev, a.tta, pre)
    thr = 0.5 if a.model == "skeleton" else ev.tune_threshold(cv, a.tol)
    ct = ev.collect(model, tel, dev, a.tta, pre)
    res = dict(model=a.model, split=a.split, tag=a.tag, tta=bool(a.tta), thr=thr, tol=a.tol,
               val_seen_shapes_new_poses=ev.score(cv, thr, a.tol), test=ev.score(ct, thr, a.tol))
    res.update(extra or {})
    with open(os.path.join(out, mname), "w") as f:
        json.dump(res, f, indent=1)
    ev.save_grid(ct, os.path.join(out, gname), thr)
    t = res["test"]["all"]
    print("TEST %s %s: f1 %.3f prec %.3f rec %.3f chamfer_raw %.3f hausdorff_raw %.3f topo_ok %.2f thr %.1f" % (
        a.model, a.split, t["f1"], t["prec"], t["rec"], t["chamfer_raw"], t["hausdorff_raw"], t["topo_ok"], thr))
    return res


def do_eval(a):
    dev = get_device(a)
    out = os.path.join(a.out, run_name(a))
    if not os.path.isdir(out):
        raise SystemExit("run folder %s not found; train first" % out)
    with open(os.path.join(out, "args.json")) as f:
        ra = argparse.Namespace(**json.load(f))
    ra.tta, ra.stage1, ra.out = a.tta, a.stage1 or getattr(ra, "stage1", None), a.out
    model = load_model_from_run(out, dev)
    parts = ds.make_datasets(ra.split, 1, ra.in_ch, aug=False)
    _, val, tel = loaders(parts, ra)
    pre = make_pre(ra, dev)
    suffix = "_tta" if a.tta else ""
    write_final(ra, model, val, tel, dev, pre, out, "metrics_eval%s.json" % suffix, "grid_eval%s.png" % suffix)


def main(argv=None):
    a = parse(argv)
    if a.cmd == "prepare":
        path, n = prep.build()
        print("wrote %s (%d samples, %.1f MB)" % (path, n, os.path.getsize(path) / 1e6))
    elif a.cmd == "train":
        do_train(a)
    else:
        do_eval(a)


if __name__ == "__main__":
    main()
