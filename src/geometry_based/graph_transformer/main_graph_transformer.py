"""
main_graph_transformer.py  –  MidcurveNN Phase II  (entry point)
=================================================================
End-to-end pipeline:
  1. Load dataset from .dat / .mid files with geometric augmentation
  2. Visualise dataset overview and one augmentation gallery
  3. Train the Graph Transformer model
  4. Evaluate on original (non-augmented) shapes and save result figures

Run
---
    python main_graph_transformer.py
    python main_graph_transformer.py --epochs 300 --quick   # short smoke-test
"""

import argparse
import os
import sys
import torch
import matplotlib
matplotlib.use("Agg")          # non-interactive backend; remove for interactive
import matplotlib.pyplot as plt
import numpy as np

from torch_geometric.loader import DataLoader
from torch_geometric.utils import to_dense_adj, dense_to_sparse

# ── Project modules ──────────────────────────────────────────────────────────
from graph_dataset  import MidcurveGraphDataset
from graph_transformer import (MidcurveGraphTransformer, midcurve_loss,
                                chamfer_loss)
from prepare_plots  import (plot_graph_dataset_summary, plot_augmentation_gallery,
                             plot_graph_prediction, plot_training_curves,
                             plot_adjacency_matrix)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def denorm(coords, centre, scale):
    return coords * scale + centre


def run_training(args, dataset_aug, device):
    """Train the model and return (model, history)."""
    import random, csv, time
    from torch_geometric.loader import DataLoader
    import torch.optim as optim

    random.seed(args.seed)
    torch.manual_seed(args.seed)

    # Split
    n = len(dataset_aug)
    idx = list(range(n))
    random.shuffle(idx)
    n_test = max(1, int(n * 0.10))
    n_val  = max(1, int(n * 0.15))
    test_data  = [dataset_aug.get(i) for i in idx[:n_test]]
    val_data   = [dataset_aug.get(i) for i in idx[n_test:n_test + n_val]]
    train_data = [dataset_aug.get(i) for i in idx[n_test + n_val:]]
    print(f"[Train] {len(train_data)} train / {len(val_data)} val / {len(test_data)} test")

    train_loader = DataLoader(train_data, batch_size=args.batch_size, shuffle=True)
    val_loader   = DataLoader(val_data,   batch_size=args.batch_size)

    model = MidcurveGraphTransformer(
        node_in=2, edge_in=1,
        hidden=args.hidden, ratio=args.ratio,
        num_layers=args.num_layers, heads=args.heads, lpe_k=args.lpe_k
    ).to(device)
    print(f"[Train] params: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")

    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.lr * 0.01)

    os.makedirs(args.ckpt_dir, exist_ok=True)
    log_path = os.path.join(args.ckpt_dir, "training_log.csv")
    best_val, history = float("inf"), []

    print(f"\n{'Ep':>5} {'Tr-Loss':>9} {'Tr-Ch':>8} {'Val-Loss':>10} {'Val-Ch':>8}")
    print("-" * 48)

    with open(log_path, "w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["epoch","train_loss","train_chamfer","train_adj",
                         "val_loss","val_chamfer","val_adj","lr"])

        for epoch in range(1, args.epochs + 1):
            # ── train ─────────────────────────────────────────────────────
            model.train()
            tr_l = tr_c = tr_a = 0.0
            for data in train_loader:
                data = data.to(device)
                coords_pred, adj_logits, _, _ = model(
                    data.x, data.edge_index, data.edge_attr, data.batch)
                loss, lc, la = midcurve_loss(
                    coords_pred, adj_logits, data.y, data.mid_edge_index,
                    args.lam_ch, args.lam_adj)
                optimizer.zero_grad(); loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                bs = data.num_graphs
                tr_l += loss.item() * bs; tr_c += lc * bs; tr_a += la * bs
            tr_l /= len(train_data); tr_c /= len(train_data); tr_a /= len(train_data)

            # ── val ───────────────────────────────────────────────────────
            model.eval()
            vl_l = vl_c = vl_a = 0.0
            with torch.no_grad():
                for data in val_loader:
                    data = data.to(device)
                    coords_pred, adj_logits, _, _ = model(
                        data.x, data.edge_index, data.edge_attr, data.batch)
                    loss, lc, la = midcurve_loss(
                        coords_pred, adj_logits, data.y, data.mid_edge_index,
                        args.lam_ch, args.lam_adj)
                    bs = data.num_graphs
                    vl_l += loss.item() * bs; vl_c += lc * bs; vl_a += la * bs
            vl_l /= len(val_data); vl_c /= len(val_data); vl_a /= len(val_data)

            scheduler.step()
            lr = scheduler.get_last_lr()[0]
            row = [epoch, tr_l, tr_c, tr_a, vl_l, vl_c, vl_a, lr]
            writer.writerow(row); csvf.flush()
            history.append(row)

            if vl_l < best_val:
                best_val = vl_l
                torch.save({"epoch": epoch, "model_state": model.state_dict(),
                            "args": vars(args)},
                           os.path.join(args.ckpt_dir, "best_model.pt"))

            if epoch % max(1, args.epochs // 10) == 0 or epoch == 1:
                print(f"{epoch:>5} {tr_l:>9.4f} {tr_c:>8.4f} {vl_l:>10.4f} {vl_c:>8.4f}")

    torch.save({"epoch": args.epochs, "model_state": model.state_dict(),
                "args": vars(args)},
               os.path.join(args.ckpt_dir, "last_model.pt"))
    print(f"\n[Train] Best val loss: {best_val:.4f}")
    return model, history, log_path


def evaluate_and_plot(model, dataset_raw, device, args):
    """Evaluate on original shapes and produce per-shape prediction plots."""
    model.eval()
    os.makedirs(args.results_dir, exist_ok=True)
    metrics = []

    print(f"\n{'Shape':>12}  {'Chamfer':>10}  {'Nodes-pred':>10}")
    print("-" * 38)

    for i in range(len(dataset_raw)):
        data = dataset_raw.get(i)
        label = data.label

        with torch.no_grad():
            d = data
            coords_pred, adj_logits, _, _ = model(
                d.x.to(device), d.edge_index.to(device), d.edge_attr.to(device))

        adj_prob = torch.sigmoid(adj_logits)
        adj_prob.fill_diagonal_(0.0)
        ei_pred, _ = dense_to_sparse(adj_prob > args.threshold)

        # Denormalise
        c, s = data.centre, data.scale
        prof_dn   = denorm(data.x,    c, s).numpy()
        gt_mid_dn = denorm(data.y,    c, s).numpy()
        pred_dn   = denorm(coords_pred.cpu(), c, s).numpy()

        ch = chamfer_loss(coords_pred.cpu(), data.y).item()
        metrics.append(ch)
        print(f"{label:>12}  {ch:>10.4f}  {pred_dn.shape[0]:>10}")

        # Adjacency heatmap
        gt_adj = to_dense_adj(data.mid_edge_index,
                               max_num_nodes=data.y.size(0)).squeeze(0).numpy()
        k = adj_logits.size(0)
        gt_k = np.zeros((k, k))
        sz = min(k, gt_adj.shape[0])
        gt_k[:sz, :sz] = gt_adj[:sz, :sz]

        fig = plot_adjacency_matrix(
            adj_logits.cpu().numpy(), gt_k,
            title=f"{label} – Adjacency Logits vs GT",
            save_path=os.path.join(args.results_dir, f"{label}_adj.png"))
        plt.close(fig)

        # Prediction three-panel
        fig = plot_graph_prediction(
            label,
            prof_dn, data.edge_index.numpy(),
            gt_mid_dn, data.mid_edge_index.numpy(),
            pred_dn, ei_pred.cpu().numpy() if ei_pred.numel() > 0 else np.empty((2,0),dtype=int),
            save_path=os.path.join(args.results_dir, f"{label}_prediction.png"))
        plt.close(fig)

    print(f"{'MEAN':>12}  {np.mean(metrics):>10.4f}")
    return metrics


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def get_args():
    _src_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _default_data = os.path.join(_src_dir, "data", "raw")
    p = argparse.ArgumentParser("MidcurveNN Phase II")
    p.add_argument("--data",       default=_default_data)
    p.add_argument("--epochs",     type=int,   default=200)
    p.add_argument("--batch-size", type=int,   default=16)
    p.add_argument("--lr",         type=float, default=3e-4)
    p.add_argument("--hidden",     type=int,   default=64)
    p.add_argument("--ratio",      type=float, default=0.6)
    p.add_argument("--num-layers", type=int,   default=3)
    p.add_argument("--heads",      type=int,   default=4)
    p.add_argument("--lpe-k",      type=int,   default=4)
    p.add_argument("--lam-ch",     type=float, default=1.0)
    p.add_argument("--lam-adj",    type=float, default=0.5)
    p.add_argument("--threshold",  type=float, default=0.5)
    p.add_argument("--ckpt-dir",   default="checkpoints")
    p.add_argument("--results-dir",default="results")
    p.add_argument("--seed",       type=int,   default=42)
    p.add_argument("--quick",      action="store_true",
                   help="Smoke test: 10 epochs, no augmentation")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main():
    args = get_args()
    if args.quick:
        args.epochs = 10

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Main] Device: {device}")
    print(f"[Main] Data folder: {args.data}")

    # ── 1. Dataset ────────────────────────────────────────────────────────
    print("\n[Step 1] Loading dataset …")
    dataset_aug = MidcurveGraphDataset(args.data, augment=not args.quick)
    dataset_raw = MidcurveGraphDataset(args.data, augment=False)

    # ── 2. Visualise dataset ──────────────────────────────────────────────
    print("\n[Step 2] Generating dataset visualisations …")
    os.makedirs(args.results_dir, exist_ok=True)

    fig = plot_graph_dataset_summary(
        dataset_raw,
        save_path=os.path.join(args.results_dir, "dataset_overview.png"))
    plt.close(fig)
    print(f"  Saved: {args.results_dir}/dataset_overview.png")

    for shape in ["I", "L", "T", "Plus"]:
        fig = plot_augmentation_gallery(
            dataset_aug, shape_name=shape, max_variants=8,
            save_path=os.path.join(args.results_dir, f"augmentation_{shape}.png"))
        if fig:
            plt.close(fig)
            print(f"  Saved: {args.results_dir}/augmentation_{shape}.png")

    # ── 3. Train ──────────────────────────────────────────────────────────
    print("\n[Step 3] Training …")
    model, history, log_path = run_training(args, dataset_aug, device)

    # ── 4. Training curves ────────────────────────────────────────────────
    print("\n[Step 4] Plotting training curves …")
    fig = plot_training_curves(
        log_path,
        save_path=os.path.join(args.results_dir, "training_curves.png"))
    plt.close(fig)
    print(f"  Saved: {args.results_dir}/training_curves.png")

    # ── 5. Evaluate ───────────────────────────────────────────────────────
    print("\n[Step 5] Evaluating on original shapes …")
    # Reload best checkpoint
    ckpt = torch.load(os.path.join(args.ckpt_dir, "best_model.pt"),
                      map_location=device)
    model.load_state_dict(ckpt["model_state"])

    evaluate_and_plot(model, dataset_raw, device, args)
    print(f"\n[Main] All results saved to: {args.results_dir}/")


if __name__ == "__main__":
    main()
