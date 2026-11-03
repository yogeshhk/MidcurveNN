"""Set-prediction model for the midcurve node set (DETR style, pure PyTorch, no PyG).

profile vertices (7 features) -> Linear -> TransformerEncoder (global attention, no positional
encoding: the ring order is already in the prev/next edge features) -> K=12 learned queries in a
TransformerDecoder -> heads: xy (2) and existence logit (1). Loss: Hungarian set loss (losses.py).
Edges are NOT learned: geom.edges_from_nodes (inside-polygon MST) on the thresholded nodes.
"""
import csv
import json
import os
import time

import numpy as np
import torch
import torch.nn as nn

from common import dataset as D
from common import evaluate as ev
from common import geom
from common import losses


class MidcurveSetNet(nn.Module):
    def __init__(self, d=64, heads=4, enc_layers=3, dec_layers=2, k=D.K, ff=None):
        super().__init__()
        ff = ff or 2 * d
        self.k = k
        self.inp = nn.Linear(D.FEAT_DIM, d)
        enc = nn.TransformerEncoderLayer(d, heads, ff, dropout=0.0, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(enc, enc_layers, enable_nested_tensor=False)
        self.queries = nn.Embedding(k, d)
        dec = nn.TransformerDecoderLayer(d, heads, ff, dropout=0.0, batch_first=True, norm_first=True)
        self.dec = nn.TransformerDecoder(dec, dec_layers)
        self.norm = nn.LayerNorm(d)
        self.xy = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, 2))
        self.exist = nn.Linear(d, 1)

    def forward(self, feats, mask):
        """feats[B,N,7] float, mask[B,N] bool (True = real vertex). Returns xy[B,K,2], logit[B,K]."""
        pad = ~mask
        h = self.enc(self.inp(feats), src_key_padding_mask=pad)
        q = self.queries.weight[None].expand(feats.shape[0], -1, -1)
        o = self.norm(self.dec(q, h, memory_key_padding_mask=pad))
        return self.xy(o), self.exist(o).squeeze(-1)


def build_model(cfg):
    return MidcurveSetNet(d=getattr(cfg, "d", 64), enc_layers=getattr(cfg, "enc_layers", 3),
                          dec_layers=getattr(cfg, "dec_layers", 2))


# ----------------------------------------------------------------------------- inference
@torch.no_grad()
def predict_batch(model, samples, device="cpu", thr=0.5, merge=0.02):
    """samples -> list of (nodes, edges) in each sample's own coordinates."""
    model.eval()
    items = [D.featurize(s["profile"], s["nodes"]) for s in samples]
    b = D.collate(items)
    xy, logit = model(b["feats"].to(device), b["mask"].to(device))
    xy, prob = xy.cpu().numpy(), torch.sigmoid(logit).cpu().numpy()
    out = []
    for i, s in enumerate(samples):
        keep = prob[i] > thr
        if not keep.any():
            keep = prob[i] == prob[i].max()
        nodes_n = geom.merge_close(xy[i][keep], merge)
        nodes = geom.denormalize(nodes_n, b["centre"][i], b["he"][i])
        poly = geom.ensure_ccw(s["profile"])
        nodes = geom.snap_inside(nodes, poly)
        out.append((nodes, geom.edges_from_nodes(nodes, poly, force_connected=True)))
    return out


def make_predictor(model, cfg=None):
    device = getattr(cfg, "device", "cpu")
    cache = {}

    def predict(sample):
        return predict_batch(model, [sample], device)[0]

    def predict_many(samples):
        res = []
        for i in range(0, len(samples), 256):
            res.extend(predict_batch(model, samples[i:i + 256], device))
        return res

    predict.many = predict_many
    return predict


# ----------------------------------------------------------------------------- training
def fit(cfg, run_dir, splits):
    """Train with AdamW + cosine schedule; save best.pt (lowest val set-loss) and log.csv."""
    torch.set_num_threads(getattr(cfg, "threads", 4))
    torch.manual_seed(cfg.seed)
    np.random.seed(cfg.seed)
    device = cfg.device
    model = build_model(cfg).to(device)
    nparams = sum(p.numel() for p in model.parameters())
    print("params:", nparams)
    tr = D.make_loader(splits["train"], cfg.batch_size, shuffle=True, augment=True, seed=cfg.seed,
                       rot_aug=getattr(cfg, "rot_aug", False))
    va = D.make_loader(splits["val"], 256, shuffle=False, augment=False)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=1e-4)
    steps = cfg.epochs * len(tr)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=cfg.lr, total_steps=steps, pct_start=0.05,
                                                anneal_strategy="cos")
    log_path = os.path.join(run_dir, "log.csv")
    last_path = os.path.join(run_dir, "last.pt")
    best, t0, start_ep, offset = float("inf"), time.time(), 1, 0.0
    resume = bool(getattr(cfg, "resume", False)) and os.path.exists(last_path) and os.path.exists(log_path)
    if resume:
        ck = torch.load(last_path, map_location=device, weights_only=False)
        model.load_state_dict(ck["state"])
        opt.load_state_dict(ck["opt"])
        sched.load_state_dict(ck["sched"])
        best, start_ep, offset = ck["best"], ck["epoch"] + 1, ck.get("sec", 0.0)
        # drop any log rows beyond the checkpointed epoch (crash between log write and checkpoint)
        with open(log_path, newline="") as f:
            rows = list(csv.reader(f))
        keep = [rows[0]] + [r for r in rows[1:] if r and int(r[0]) <= ck["epoch"]]
        with open(log_path, "w", newline="") as f:
            csv.writer(f).writerows(keep)
        print("resumed from epoch", ck["epoch"], flush=True)
    t0 = time.time() - offset
    with open(log_path, "a" if resume else "w", newline="") as f:
        wr = csv.writer(f)
        if not resume:
            wr.writerow(["epoch", "train_loss", "train_l1", "val_loss", "val_l1", "val_ok_025w", "val_k_exact", "sec"])
        for ep in range(start_ep, cfg.epochs + 1):
            model.train()
            tl, tl1, n = 0.0, 0.0, 0
            for b in tr:
                xy, logit = model(b["feats"].to(device), b["mask"].to(device))
                loss, parts = losses.set_loss(xy, logit, b["gt"].to(device), b["gt_mask"].to(device))
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                tl += float(loss) * len(b["mask"])
                tl1 += parts["l1"] * len(b["mask"])
                n += len(b["mask"])
            model.eval()
            vl, vl1, vn = 0.0, 0.0, 0
            with torch.no_grad():
                for b in va:
                    xy, logit = model(b["feats"].to(device), b["mask"].to(device))
                    loss, parts = losses.set_loss(xy, logit, b["gt"].to(device), b["gt_mask"].to(device))
                    vl += float(loss) * len(b["mask"])
                    vl1 += parts["l1"] * len(b["mask"])
                    vn += len(b["mask"])
            vl, vl1 = vl / vn, vl1 / vn
            ok = kx = ""
            if ep % 10 == 0 or ep == cfg.epochs:
                sub = splits["val"][:300]
                preds = predict_batch(model, sub, device)
                rr = [ev.graph_metrics(p[0], p[1], s["nodes"], s["edges"], s["w"],
                                       extent=float((s["profile"].max(0) - s["profile"].min(0)).max() / 2))
                      for s, p in zip(sub, preds)]
                ok = float(np.mean([r["ok_025w"] for r in rr]))
                kx = float(np.mean([r["k_exact"] for r in rr]))
                print("ep %3d train %.4f val %.4f val_ok_025w %.3f k_exact %.3f (%.0fs)"
                      % (ep, tl / n, vl, ok, kx, time.time() - t0), flush=True)
            wr.writerow([ep, tl / n, tl1 / n, vl, vl1, ok, kx, round(time.time() - t0, 1)])
            f.flush()
            if vl < best:
                best = vl
                torch.save(dict(state=model.state_dict(), args=vars(cfg), epoch=ep, val_loss=vl,
                                nparams=nparams), os.path.join(run_dir, "best.pt"))
            torch.save(dict(state=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(),
                            epoch=ep, best=best, sec=time.time() - t0), last_path + ".tmp")
            os.replace(last_path + ".tmp", last_path)
    return load_best(run_dir, cfg)


def load_best(run_dir, cfg):
    ck = torch.load(os.path.join(run_dir, "best.pt"), map_location=cfg.device, weights_only=False)
    a = ck["args"]
    model = MidcurveSetNet(d=a.get("d", 64), enc_layers=a.get("enc_layers", 3), dec_layers=a.get("dec_layers", 2))
    model.load_state_dict(ck["state"])
    return model.to(cfg.device).eval()
