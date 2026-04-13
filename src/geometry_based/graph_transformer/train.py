"""
train.py  –  MidcurveNN Phase II
==================================
Training loop for the Graph Transformer midcurve model.

Usage
-----
    python train.py                         # default settings
    python train.py --epochs 300 --lr 3e-4
    python train.py --data data/raw --no-augment

The script trains on ALL available data (leave-one-out cross-validation
is optional via --loo).  After training it saves:
    checkpoints/best_model.pt   – best validation checkpoint
    checkpoints/last_model.pt   – final epoch checkpoint
    training_log.csv            – epoch-level metrics
"""

import argparse
import os
import csv
import time
import random

import torch
import torch.optim as optim
from torch_geometric.loader import DataLoader

from graph_dataset import MidcurveGraphDataset
from graph_transformer import MidcurveGraphTransformer, midcurve_loss


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def set_seed(seed=42):
    random.seed(seed)
    torch.manual_seed(seed)


def split_dataset(dataset, val_ratio=0.15, test_ratio=0.10, seed=42):
    """Random split into train / val / test."""
    n = len(dataset)
    indices = list(range(n))
    random.seed(seed)
    random.shuffle(indices)
    n_test = max(1, int(n * test_ratio))
    n_val  = max(1, int(n * val_ratio))
    test_idx  = indices[:n_test]
    val_idx   = indices[n_test:n_test + n_val]
    train_idx = indices[n_test + n_val:]
    return (
        [dataset.get(i) for i in train_idx],
        [dataset.get(i) for i in val_idx],
        [dataset.get(i) for i in test_idx],
    )


def run_epoch(model, loader, optimizer, device, train=True,
              lambda_chamfer=1.0, lambda_adj=0.5):
    if train:
        model.train()
    else:
        model.eval()

    total_loss = total_ch = total_adj = 0.0
    n_samples = 0

    ctx = torch.enable_grad() if train else torch.no_grad()
    with ctx:
        for data in loader:
            data = data.to(device)
            coords_pred, adj_logits, _, _ = model(
                data.x, data.edge_index, data.edge_attr, data.batch)

            loss, lc, la = midcurve_loss(
                coords_pred, adj_logits,
                data.y, data.mid_edge_index,
                lambda_chamfer=lambda_chamfer,
                lambda_adj=lambda_adj)

            if train:
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            bs = data.num_graphs
            total_loss += loss.item() * bs
            total_ch   += lc * bs
            total_adj  += la * bs
            n_samples  += bs

    return (total_loss / n_samples,
            total_ch / n_samples,
            total_adj / n_samples)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def train(args):
    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] device={device}")

    # Data
    dataset = MidcurveGraphDataset(args.data, augment=not args.no_augment)
    train_data, val_data, test_data = split_dataset(
        dataset, val_ratio=args.val_ratio, test_ratio=args.test_ratio)
    print(f"[Train] split: {len(train_data)} train / "
          f"{len(val_data)} val / {len(test_data)} test")

    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_data,   batch_size=args.batch_size)
    test_loader  = DataLoader(test_data,  batch_size=args.batch_size)

    # Model
    model = MidcurveGraphTransformer(
        node_in=2, edge_in=1,
        hidden=args.hidden,
        ratio=args.ratio,
        num_layers=args.num_layers,
        heads=args.heads,
        lpe_k=args.lpe_k,
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"[Train] model parameters: {n_params:,}")

    optimizer = optim.AdamW(model.parameters(), lr=args.lr,
                            weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.lr * 0.01)

    # Checkpoint dir
    os.makedirs(args.ckpt_dir, exist_ok=True)
    log_path = os.path.join(args.ckpt_dir, "training_log.csv")

    best_val_loss = float("inf")
    history = []

    print(f"\n{'Epoch':>6} {'Train':>10} {'Ch':>9} {'Adj':>9} "
          f"{'Val':>10} {'Ch':>9} {'Adj':>9} {'LR':>9}  {'Time':>6}")
    print("-" * 85)

    with open(log_path, "w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["epoch","train_loss","train_chamfer","train_adj",
                         "val_loss","val_chamfer","val_adj","lr"])

        for epoch in range(1, args.epochs + 1):
            t0 = time.time()
            tr_l, tr_c, tr_a = run_epoch(model, train_loader, optimizer, device,
                                          train=True,
                                          lambda_chamfer=args.lambda_chamfer,
                                          lambda_adj=args.lambda_adj)
            vl_l, vl_c, vl_a = run_epoch(model, val_loader, optimizer, device,
                                          train=False,
                                          lambda_chamfer=args.lambda_chamfer,
                                          lambda_adj=args.lambda_adj)
            scheduler.step()
            lr = scheduler.get_last_lr()[0]
            elapsed = time.time() - t0

            row = [epoch, tr_l, tr_c, tr_a, vl_l, vl_c, vl_a, lr]
            writer.writerow(row)
            csvf.flush()
            history.append(row)

            if epoch % args.print_every == 0 or epoch == 1:
                print(f"{epoch:>6} {tr_l:>10.4f} {tr_c:>9.4f} {tr_a:>9.4f} "
                      f"{vl_l:>10.4f} {vl_c:>9.4f} {vl_a:>9.4f} "
                      f"{lr:>9.2e}  {elapsed:>5.1f}s")

            # Checkpoint
            if vl_l < best_val_loss:
                best_val_loss = vl_l
                torch.save({"epoch": epoch,
                            "model_state": model.state_dict(),
                            "val_loss": vl_l,
                            "args": vars(args)},
                           os.path.join(args.ckpt_dir, "best_model.pt"))

    # Final checkpoint
    torch.save({"epoch": args.epochs,
                "model_state": model.state_dict(),
                "args": vars(args)},
               os.path.join(args.ckpt_dir, "last_model.pt"))

    # Test evaluation
    print("\n--- Test set ---")
    ts_l, ts_c, ts_a = run_epoch(model, test_loader, optimizer, device,
                                  train=False,
                                  lambda_chamfer=args.lambda_chamfer,
                                  lambda_adj=args.lambda_adj)
    print(f"Test loss={ts_l:.4f}  chamfer={ts_c:.4f}  adj_bce={ts_a:.4f}")

    return model, history


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def get_args():
    p = argparse.ArgumentParser("MidcurveNN Phase II – Training")
    p.add_argument("--data",           default="data/raw")
    p.add_argument("--no-augment",     action="store_true")
    p.add_argument("--epochs",         type=int,   default=200)
    p.add_argument("--batch-size",     type=int,   default=16)
    p.add_argument("--lr",             type=float, default=3e-4)
    p.add_argument("--weight-decay",   type=float, default=1e-4)
    p.add_argument("--hidden",         type=int,   default=64)
    p.add_argument("--ratio",          type=float, default=0.6)
    p.add_argument("--num-layers",     type=int,   default=3)
    p.add_argument("--heads",          type=int,   default=4)
    p.add_argument("--lpe-k",          type=int,   default=4)
    p.add_argument("--lambda-chamfer", type=float, default=1.0)
    p.add_argument("--lambda-adj",     type=float, default=0.5)
    p.add_argument("--val-ratio",      type=float, default=0.15)
    p.add_argument("--test-ratio",     type=float, default=0.10)
    p.add_argument("--ckpt-dir",       default="checkpoints")
    p.add_argument("--print-every",    type=int,   default=10)
    p.add_argument("--seed",           type=int,   default=42)
    return p.parse_args()


if __name__ == "__main__":
    args = get_args()
    train(args)
