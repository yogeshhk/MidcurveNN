"""
train.py  –  MidcurveNN Phase II-b
=====================================
Fine-tune a pretrained Graphormer on the midcurve dataset.

Run
---
    cd src/geometry_based/finetuned_graph_transformer
    python train.py
    python train.py --epochs 50 --freeze-epochs 5 --quick
"""

import argparse
import os
import sys
import csv
import random
import torch
import torch.optim as optim

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)

from torch_geometric.loader import DataLoader
from geometry_based.graph_transformer.graph_dataset import MidcurveGraphDataset
from model import MidcurveFinetuned, finetuned_loss


def get_args():
    _default_data = os.path.join(_SRC, "data", "raw")
    p = argparse.ArgumentParser("MidcurveNN Phase II-b  –  Fine-tuned Graph Transformer")
    p.add_argument("--data",          default=_default_data)
    p.add_argument("--epochs",        type=int,   default=100)
    p.add_argument("--freeze-epochs", type=int,   default=20,
                   help="Epochs to keep backbone frozen before joint fine-tuning")
    p.add_argument("--batch-size",    type=int,   default=8)
    p.add_argument("--lr",            type=float, default=1e-4,
                   help="Head learning rate (backbone uses lr/10 after unfreeze)")
    p.add_argument("--max-nodes",     type=int,   default=32,
                   help="Maximum midcurve output nodes")
    p.add_argument("--lam-ch",        type=float, default=1.0)
    p.add_argument("--lam-adj",       type=float, default=0.5)
    p.add_argument("--ckpt-dir",      default="checkpoints")
    p.add_argument("--seed",          type=int,   default=42)
    p.add_argument("--no-pretrained", action="store_true",
                   help="Initialize from scratch (for offline / CI use)")
    p.add_argument("--quick",         action="store_true",
                   help="Smoke test: 5 epochs, no augmentation")
    return p.parse_args()


def train():
    args = get_args()
    if args.quick:
        args.epochs = 5
        args.freeze_epochs = 2

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Device: {device}")
    print(f"[Train] Data:   {args.data}")

    # Dataset
    dataset_aug = MidcurveGraphDataset(args.data, augment=not args.quick)
    dataset_raw = MidcurveGraphDataset(args.data, augment=False)
    n = len(dataset_aug)
    idx = list(range(n))
    random.shuffle(idx)
    n_test = max(1, int(n * 0.10))
    n_val  = max(1, int(n * 0.15))
    val_data   = [dataset_aug.get(i) for i in idx[n_test:n_test + n_val]]
    train_data = [dataset_aug.get(i) for i in idx[n_test + n_val:]]
    print(f"[Train] {len(train_data)} train / {len(val_data)} val")

    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_data,   batch_size=args.batch_size)

    # Model
    model = MidcurveFinetuned(
        max_nodes=args.max_nodes,
        freeze_epochs=args.freeze_epochs,
        pretrained=not args.no_pretrained,
    ).to(device)

    head_params = list(model.coord_head.parameters()) + list(model.adj_head.parameters())
    optimizer = optim.AdamW(head_params, lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    os.makedirs(args.ckpt_dir, exist_ok=True)
    log_path = os.path.join(args.ckpt_dir, "training_log.csv")
    best_val = float("inf")

    print(f"\n{'Ep':>5} {'Phase':>9} {'Tr-Loss':>9} {'Val-Loss':>10}")
    print("-" * 40)

    with open(log_path, "w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["epoch", "phase", "train_loss", "train_chamfer",
                         "val_loss", "val_chamfer", "lr"])

        for epoch in range(1, args.epochs + 1):
            # Unfreeze backbone after freeze_epochs
            if epoch == args.freeze_epochs + 1:
                model.unfreeze()
                backbone_params = list(model.backbone.parameters())
                optimizer.add_param_group(
                    {"params": backbone_params, "lr": args.lr / 10})
                print(f"  [Epoch {epoch}] Backbone unfrozen — joint fine-tuning starts")

            phase = "frozen" if epoch <= args.freeze_epochs else "finetune"

            # Train
            model.train()
            tr_l = tr_c = 0.0
            for data in train_loader:
                data = data.to(device)
                coords_pred, adj_logits = model(data.x, data.edge_index, data.batch)
                loss, lc, _ = finetuned_loss(
                    coords_pred, adj_logits, data.y, data.mid_edge_index,
                    args.lam_ch, args.lam_adj)
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                bs = data.num_graphs
                tr_l += loss.item() * bs
                tr_c += lc * bs
            tr_l /= len(train_data)
            tr_c /= len(train_data)

            # Validate
            model.eval()
            vl_l = vl_c = 0.0
            with torch.no_grad():
                for data in val_loader:
                    data = data.to(device)
                    coords_pred, adj_logits = model(data.x, data.edge_index, data.batch)
                    loss, lc, _ = finetuned_loss(
                        coords_pred, adj_logits, data.y, data.mid_edge_index,
                        args.lam_ch, args.lam_adj)
                    bs = data.num_graphs
                    vl_l += loss.item() * bs
                    vl_c += lc * bs
            vl_l /= len(val_data)
            vl_c /= len(val_data)

            scheduler.step()
            lr = scheduler.get_last_lr()[0]
            writer.writerow([epoch, phase, tr_l, tr_c, vl_l, vl_c, lr])
            csvf.flush()

            if vl_l < best_val:
                best_val = vl_l
                torch.save({"epoch": epoch, "model_state": model.state_dict(),
                            "args": vars(args)},
                           os.path.join(args.ckpt_dir, "best_model.pt"))

            if epoch % max(1, args.epochs // 10) == 0 or epoch == 1:
                print(f"{epoch:>5} {phase:>9} {tr_l:>9.4f} {vl_l:>10.4f}")

    torch.save({"epoch": args.epochs, "model_state": model.state_dict(),
                "args": vars(args)},
               os.path.join(args.ckpt_dir, "last_model.pt"))
    print(f"\n[Train] Best val loss: {best_val:.4f}")
    print(f"[Train] Checkpoints saved to: {args.ckpt_dir}/")


if __name__ == "__main__":
    train()
