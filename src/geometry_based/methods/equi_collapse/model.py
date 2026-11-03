"""EquiCollapse: an E(2)-equivariant network on the dual graph of the polygon's interior Delaunay complex.

For each cell the network predicts a key probability (invariant) and a position offset (equivariant). The midcurve is
obtained by contracting the dual graph on the key cells (cell_complex.decode), so node count is not fixed by any slot
limit and the output is a tree on hole-free shapes for any weights. Pure PyTorch, no PyG. See README.md.
"""
import csv
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from common import evaluate as ev
from methods.equi_collapse import cell_complex as cc


class EquiLayer(nn.Module):
    """Message passing with scalar channels h[N,d] and vector channels V[N,m,2]. Geometry enters only through relative
    positions and dot products, so h is invariant and V equivariant under rotation, reflection and translation."""

    def __init__(self, d, m):
        super().__init__()
        self.msg = nn.Sequential(nn.Linear(2 * d + 2 + 3 * m, d), nn.GELU(), nn.Linear(d, d))
        self.a = nn.Linear(d, m)
        self.b = nn.Linear(d, m)
        self.upd = nn.Sequential(nn.Linear(2 * d + m, d), nn.GELU(), nn.Linear(d, d))
        self.norm = nn.LayerNorm(d)

    def forward(self, h, V, x, ei, ej, ef):
        r = x[ej] - x[ei]
        dist = r.norm(dim=-1, keepdim=True)
        vi_r = (V[ei] * r[:, None]).sum(-1)
        vj_r = (V[ej] * r[:, None]).sum(-1)
        vv = (V[ei] * V[ej]).sum(-1)
        m = self.msg(torch.cat([h[ei], h[ej], ef, dist, vi_r, vj_r, vv], -1))
        agg = torch.zeros_like(h).index_add_(0, ei, m)
        dV = torch.zeros_like(V).index_add_(0, ei, self.a(m)[..., None] * r[:, None] + self.b(m)[..., None] * V[ej])
        V = V + 0.25 * dV
        h = self.norm(h + self.upd(torch.cat([h, agg, (V ** 2).sum(-1)], -1)))
        return h, V


class EquiCollapseNet(nn.Module):
    def __init__(self, d=64, m=4, layers=6):
        super().__init__()
        self.m = m
        self.inp = nn.Linear(cc.FEAT_DIM, d)
        self.layers = nn.ModuleList([EquiLayer(d, m) for _ in range(layers)])
        self.key = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))
        self.off = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, m))

    def forward(self, f, x, ei, ej, ef):
        """Disjoint-union batch. Returns key logit[N] and offset[N,2], in units of w_hat."""
        h = self.inp(f)
        V = torch.zeros(len(f), self.m, 2, device=f.device)
        for layer in self.layers:
            h, V = layer(h, V, x, ei, ej, ef)
        return self.key(h).squeeze(-1), (self.off(h)[..., None] * V).sum(1)


def build_model(cfg):
    return EquiCollapseNet(d=getattr(cfg, "d", 64), layers=getattr(cfg, "layers", 6))


# ----------------------------------------------------------------------------- data
def pack(profile, nodes=None, h_ratio=0.5):
    cx = cc.build_complex(profile, h_ratio)
    f, ei, ej, ef = cc.features(cx)
    xn = ((cx["x"] - cx["x"].mean(0)) / cx["wh"]).astype(np.float32)
    item = dict(f=f, xn=xn, ei=ei, ej=ej, ef=ef, ncell=cx["ncell"], adj=cx["adj"], x=cx["x"], wh=cx["wh"])
    if nodes is not None:
        item["k"], item["t"] = cc.labels(cx, nodes)
    return item


def collate(items, device="cpu"):
    off = 0
    fs, xs, eis, ejs, efs, ks, ts, sizes = [], [], [], [], [], [], [], []
    for it in items:
        fs.append(it["f"])
        xs.append(it["xn"])
        eis.append(it["ei"] + off)
        ejs.append(it["ej"] + off)
        efs.append(it["ef"])
        sizes.append(len(it["f"]))
        if "k" in it:
            ks.append(it["k"])
            ts.append(it["t"])
        off += len(it["f"])
    b = [torch.from_numpy(np.concatenate(a)).to(device) for a in (fs, xs, eis, ejs, efs)]
    if ks:
        b += [torch.from_numpy(np.concatenate(ks)).to(device), torch.from_numpy(np.concatenate(ts)).to(device)]
    return b, sizes


def compute_loss(logit, off, k, t, pos_weight=3.0, w_off=2.0):
    bce = F.binary_cross_entropy_with_logits(logit, k, pos_weight=torch.tensor(pos_weight, device=logit.device))
    mask = k > 0.5
    reg = F.smooth_l1_loss(off[mask], t[mask], beta=0.1) if mask.any() else off.sum() * 0.0
    return bce + w_off * reg, float(bce.detach()), float(reg.detach())


# ----------------------------------------------------------------------------- inference
@torch.no_grad()
def predict_items(model, items, thr=0.5, device="cpu"):
    model.eval()
    (f, x, ei, ej, ef, *_), sizes = collate(items, device)
    logit, off = model(f, x, ei, ej, ef)
    prob, off = torch.sigmoid(logit).cpu().numpy(), off.cpu().numpy()
    out, s = [], 0
    for it, n in zip(items, sizes):
        pos = it["x"] + off[s:s + n] * it["wh"]
        out.append(cc.decode(it, prob[s:s + n], pos, thr))
        s += n
    return out


def make_predictor(model, cfg=None):
    device = getattr(cfg, "device", "cpu")
    thr = getattr(model, "thr", 0.5)

    def many(samples):
        res = []
        for i in range(0, len(samples), 128):
            items = [pack(s["profile"]) for s in samples[i:i + 128]]
            res.extend(predict_items(model, items, thr, device))
        return res

    def predict(sample):
        return many([sample])[0]

    predict.many = many
    return predict


def _val_scores(model, items, samples, thr, device):
    preds = []
    for i in range(0, len(items), 128):
        preds.extend(predict_items(model, items[i:i + 128], thr, device))
    rows = [ev.graph_metrics(p[0], p[1], s["nodes"], s["edges"], s["w"],
                             extent=float((s["profile"].max(0) - s["profile"].min(0)).max() / 2))
            for s, p in zip(samples, preds)]
    return float(np.mean([r["ok_025w"] for r in rows])), float(np.mean([r["k_exact"] for r in rows]))


# ----------------------------------------------------------------------------- training
def fit(cfg, run_dir, splits):
    """AdamW + one-cycle. No augmentation: the network is equivariant and the complex is built from the polygon itself.
    Saves best.pt (lowest val loss), last.pt, log.csv. The key threshold is chosen on validation data after training."""
    torch.set_num_threads(getattr(cfg, "threads", 4))
    torch.manual_seed(cfg.seed)
    device = cfg.device
    t0 = time.time()
    tr = [pack(s["profile"], s["nodes"]) for s in splits["train"]]
    va_s = splits["val"]
    va = [pack(s["profile"], s["nodes"]) for s in va_s]
    print("packed %d+%d samples in %.0fs, mean cells %.0f" % (len(tr), len(va), time.time() - t0,
                                                               np.mean([it["ncell"] for it in tr])), flush=True)
    model = build_model(cfg).to(device)
    nparams = sum(p.numel() for p in model.parameters())
    print("params:", nparams, flush=True)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=1e-4)
    bs = cfg.batch_size
    steps = cfg.epochs * max(len(tr) // bs, 1)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=cfg.lr, total_steps=steps, pct_start=0.05, anneal_strategy="cos")
    log_path, last_path = os.path.join(run_dir, "log.csv"), os.path.join(run_dir, "last.pt")
    best, start_ep, offset = float("inf"), 1, 0.0
    resume = bool(getattr(cfg, "resume", False)) and os.path.exists(last_path) and os.path.exists(log_path)
    if resume:
        ck = torch.load(last_path, map_location=device, weights_only=False)
        model.load_state_dict(ck["state"])
        opt.load_state_dict(ck["opt"])
        sched.load_state_dict(ck["sched"])
        best, start_ep, offset = ck["best"], ck["epoch"] + 1, ck.get("sec", 0.0)
        with open(log_path, newline="") as f:
            rows = list(csv.reader(f))
        with open(log_path, "w", newline="") as f:
            csv.writer(f).writerows([rows[0]] + [r for r in rows[1:] if r and int(r[0]) <= ck["epoch"]])
        print("resumed from epoch", ck["epoch"], flush=True)
    t0 = time.time() - offset
    rng = np.random.default_rng(cfg.seed + 7 * start_ep)
    args = {k: v for k, v in vars(cfg).items()}
    with open(log_path, "a" if resume else "w", newline="") as f:
        wr = csv.writer(f)
        if not resume:
            wr.writerow(["epoch", "train_loss", "train_bce", "train_off", "val_loss", "val_key_acc", "val_ok_025w", "val_k_exact", "sec"])
        for ep in range(start_ep, cfg.epochs + 1):
            model.train()
            perm = rng.permutation(len(tr))
            tl, tb, tr_off, n = 0.0, 0.0, 0.0, 0
            for i in range(max(len(tr) // bs, 1)):
                (fb, xb, ei, ej, ef, k, t), _ = collate([tr[j] for j in perm[i * bs:(i + 1) * bs]], device)
                logit, off = model(fb, xb, ei, ej, ef)
                loss, b, r = compute_loss(logit, off, k, t)
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
                sched.step()
                tl, tb, tr_off, n = tl + float(loss), tb + b, tr_off + r, n + 1
            model.eval()
            vl, acc, vn = 0.0, 0.0, 0
            with torch.no_grad():
                for i in range(0, len(va), 256):
                    (fb, xb, ei, ej, ef, k, t), _ = collate(va[i:i + 256], device)
                    logit, off = model(fb, xb, ei, ej, ef)
                    vl += compute_loss(logit, off, k, t)[0].item()
                    acc += float(((logit > 0) == (k > 0.5)).float().mean())
                    vn += 1
            vl, acc = vl / vn, acc / vn
            ok = kx = ""
            if ep % 10 == 0 or ep == cfg.epochs:
                ok, kx = _val_scores(model, va[:300], va_s[:300], 0.5, device)
                print("ep %3d train %.4f val %.4f key_acc %.4f val_ok_025w %.3f k_exact %.3f (%.0fs)"
                      % (ep, tl / n, vl, acc, ok, kx, time.time() - t0), flush=True)
            wr.writerow([ep, tl / n, tb / n, tr_off / n, vl, acc, ok, kx, round(time.time() - t0, 1)])
            f.flush()
            if vl < best:
                best = vl
                torch.save(dict(state=model.state_dict(), args=args, epoch=ep, val_loss=vl, nparams=nparams, thr=0.5),
                           os.path.join(run_dir, "best.pt"))
            torch.save(dict(state=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(), epoch=ep,
                            best=best, sec=time.time() - t0), last_path + ".tmp")
            os.replace(last_path + ".tmp", last_path)
    # choose the key threshold on validation data only
    best_ck = torch.load(os.path.join(run_dir, "best.pt"), map_location=device, weights_only=False)
    model.load_state_dict(best_ck["state"])
    scores = {t: _val_scores(model, va[:500], va_s[:500], t, device)[0] for t in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)}
    best_ck["thr"] = max(scores, key=lambda t: (scores[t], -abs(t - 0.5)))
    print("val ok_025w by threshold:", {k: round(v, 3) for k, v in scores.items()}, "chosen", best_ck["thr"], flush=True)
    torch.save(best_ck, os.path.join(run_dir, "best.pt"))
    return load_best(run_dir, cfg)


def load_best(run_dir, cfg):
    ck = torch.load(os.path.join(run_dir, "best.pt"), map_location=cfg.device, weights_only=False)
    a = ck["args"]
    model = EquiCollapseNet(d=a.get("d", 64), layers=a.get("layers", 6))
    model.load_state_dict(ck["state"])
    model.thr = ck.get("thr", 0.5)
    return model.to(cfg.device).eval()
