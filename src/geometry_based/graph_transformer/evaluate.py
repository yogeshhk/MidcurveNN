"""
evaluate.py  –  MidcurveNN Phase II
=====================================
Load a trained checkpoint and run inference on all shapes in the data folder.
Prints quantitative metrics and saves visualisation figures.

Usage
-----
    python evaluate.py                                       # uses best_model.pt
    python evaluate.py --ckpt checkpoints/last_model.pt
    python evaluate.py --data data/raw --threshold 0.4
"""

import argparse
import os
import math
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from torch_geometric.utils import dense_to_sparse

from graph_dataset import MidcurveGraphDataset, read_point_file, build_graph_pair
from graph_transformer import MidcurveGraphTransformer, chamfer_loss


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_model(ckpt_path: str, device):
    ckpt = torch.load(ckpt_path, map_location=device)
    a = ckpt["args"]
    model = MidcurveGraphTransformer(
        node_in=2, edge_in=1,
        hidden=a["hidden"],
        ratio=a["ratio"],
        num_layers=a["num_layers"],
        heads=a["heads"],
        lpe_k=a["lpe_k"],
    ).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"[Eval] Loaded checkpoint: {ckpt_path}  (epoch {ckpt['epoch']})")
    return model


def denormalise(coords: torch.Tensor, centre: torch.Tensor, scale: torch.Tensor):
    """Undo the normalisation applied in graph_dataset.py."""
    return coords * scale + centre


def predict_single(model, data, device, threshold=0.5):
    """Run model on a single Data sample. Returns (pred_coords, pred_edge_index)."""
    data = data.to(device)
    with torch.no_grad():
        coords_pred, adj_logits, _, _ = model(
            data.x, data.edge_index, data.edge_attr)

    adj_prob = torch.sigmoid(adj_logits)
    adj_prob.fill_diagonal_(0.0)
    edge_index_pred, _ = dense_to_sparse(adj_prob > threshold)

    # Denormalise
    coords_denorm = denormalise(coords_pred, data.centre, data.scale)
    y_denorm      = denormalise(data.y,       data.centre, data.scale)
    x_denorm      = denormalise(data.x,       data.centre, data.scale)

    return (coords_pred, adj_logits, edge_index_pred,
            coords_denorm, y_denorm, x_denorm)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def compute_metrics(coords_pred, y_gt, adj_logits, mid_edge_index_gt, num_gt_nodes):
    """Return dict of scalar metrics for one sample."""
    ch = chamfer_loss(coords_pred, y_gt).item()

    # Adjacency accuracy (on predicted k×k vs cropped gt)
    from graph_transformer import adjacency_bce_loss
    adj_bce = adjacency_bce_loss(adj_logits, mid_edge_index_gt,
                                  num_gt_nodes).item()

    return {"chamfer": ch, "adj_bce": adj_bce}


# ---------------------------------------------------------------------------
# Plotting (extends prepare_plots.py style)
# ---------------------------------------------------------------------------

def plot_prediction(shape_name, x_denorm, profile_edge_index,
                    y_denorm, mid_edge_index_gt,
                    coords_denorm, edge_index_pred,
                    save_path=None):
    """
    Three-panel figure:
      Left   – input profile polygon
      Centre – ground-truth midcurve
      Right  – predicted midcurve overlaid on profile
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    x_np = x_denorm.cpu().numpy()
    y_np = y_denorm.cpu().numpy()
    p_np = coords_denorm.cpu().numpy()

    # ── Panel 1: Profile polygon ──────────────────────────────────────────
    ax = axes[0]
    _draw_graph(ax, x_np, profile_edge_index.cpu().numpy(), color="#2c7bb6",
                node_size=40, edge_lw=1.5, label="Profile")
    ax.set_title(f"{shape_name} – Input Profile", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)

    # ── Panel 2: Ground-truth midcurve ────────────────────────────────────
    ax = axes[1]
    _draw_graph(ax, y_np,
                mid_edge_index_gt.cpu().numpy() if mid_edge_index_gt.numel() > 0 else np.empty((2, 0), dtype=int),
                color="#d7191c", node_size=60, edge_lw=2.5, label="GT Midcurve")
    ax.set_title(f"{shape_name} – Ground Truth Midcurve", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)

    # ── Panel 3: Prediction ───────────────────────────────────────────────
    ax = axes[2]
    _draw_graph(ax, x_np, profile_edge_index.cpu().numpy(),
                color="#aaaaaa", node_size=20, edge_lw=0.8, label="Profile")
    _draw_graph(ax, p_np,
                edge_index_pred.cpu().numpy() if edge_index_pred.numel() > 0 else np.empty((2, 0), dtype=int),
                color="#1a9641", node_size=80, edge_lw=2.5, marker="*",
                label="Predicted")
    # Ground truth for reference (faint)
    _draw_graph(ax, y_np,
                mid_edge_index_gt.cpu().numpy() if mid_edge_index_gt.numel() > 0 else np.empty((2, 0), dtype=int),
                color="#d7191c", node_size=40, edge_lw=1.0, alpha=0.4,
                label="GT (ref)")
    ax.set_title(f"{shape_name} – Predicted Midcurve", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="best")

    plt.suptitle(f"MidcurveNN Phase II – {shape_name}", fontsize=13, fontweight="bold")
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  [Plot] saved → {save_path}")
    return fig


def _draw_graph(ax, node_xy, edge_index, color="blue", node_size=40,
                edge_lw=1.5, alpha=1.0, marker="o", label=""):
    """Draw nodes + edges on axes ax."""
    if edge_index.shape[1] > 0:
        for u, v in edge_index.T:
            ax.plot([node_xy[u, 0], node_xy[v, 0]],
                    [node_xy[u, 1], node_xy[v, 1]],
                    color=color, lw=edge_lw, alpha=alpha)
    ax.scatter(node_xy[:, 0], node_xy[:, 1],
               c=color, s=node_size, marker=marker,
               alpha=alpha, zorder=5, label=label)


def plot_training_curves(log_csv: str, save_path=None):
    """Plot train/val loss curves from the CSV training log."""
    import csv
    epochs, tr, vl, tr_ch, vl_ch = [], [], [], [], []
    with open(log_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            epochs.append(int(row["epoch"]))
            tr.append(float(row["train_loss"]))
            vl.append(float(row["val_loss"]))
            tr_ch.append(float(row["train_chamfer"]))
            vl_ch.append(float(row["val_chamfer"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(epochs, tr, label="Train total", color="#2c7bb6")
    ax1.plot(epochs, vl, label="Val total",   color="#d7191c", linestyle="--")
    ax1.set_xlabel("Epoch"); ax1.set_ylabel("Loss")
    ax1.set_title("Total Loss (Chamfer + Adj BCE)"); ax1.legend(); ax1.grid(alpha=0.3)

    ax2.plot(epochs, tr_ch, label="Train Chamfer", color="#2c7bb6")
    ax2.plot(epochs, vl_ch, label="Val Chamfer",   color="#d7191c", linestyle="--")
    ax2.set_xlabel("Epoch"); ax2.set_ylabel("Chamfer Distance")
    ax2.set_title("Chamfer Distance"); ax2.legend(); ax2.grid(alpha=0.3)

    plt.suptitle("MidcurveNN Phase II – Training Curves", fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  [Plot] Training curves → {save_path}")
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def evaluate(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.ckpt, device)

    os.makedirs(args.out_dir, exist_ok=True)

    # Training curves (if log present)
    log_csv = os.path.join(os.path.dirname(args.ckpt), "training_log.csv")
    if os.path.exists(log_csv):
        plot_training_curves(log_csv,
                             save_path=os.path.join(args.out_dir, "training_curves.png"))

    # Per-shape evaluation (on original, non-augmented data)
    dataset = MidcurveGraphDataset(args.data, augment=False)
    all_metrics = []

    print(f"\n{'Shape':>12}  {'Chamfer':>10}  {'Adj BCE':>10}")
    print("-" * 38)

    for i in range(len(dataset)):
        data = dataset.get(i)
        label = data.label

        (coords_pred, adj_logits, edge_index_pred,
         coords_denorm, y_denorm, x_denorm) = predict_single(
            model, data, device, threshold=args.threshold)

        metrics = compute_metrics(
            coords_pred, data.y.to(device),
            adj_logits,
            data.mid_edge_index.to(device),
            data.y.size(0))
        all_metrics.append(metrics)

        print(f"{label:>12}  {metrics['chamfer']:>10.4f}  {metrics['adj_bce']:>10.4f}")

        fig = plot_prediction(
            label, x_denorm, data.edge_index,
            y_denorm, data.mid_edge_index,
            coords_denorm, edge_index_pred,
            save_path=os.path.join(args.out_dir, f"{label}_prediction.png"))
        plt.close(fig)

    mean_ch  = np.mean([m["chamfer"]  for m in all_metrics])
    mean_adj = np.mean([m["adj_bce"]  for m in all_metrics])
    print("-" * 38)
    print(f"{'MEAN':>12}  {mean_ch:>10.4f}  {mean_adj:>10.4f}")


def get_args():
    p = argparse.ArgumentParser("MidcurveNN Phase II – Evaluation")
    p.add_argument("--ckpt",      default="checkpoints/best_model.pt")
    p.add_argument("--data",      default="data/raw")
    p.add_argument("--out-dir",   default="results")
    p.add_argument("--threshold", type=float, default=0.5)
    return p.parse_args()


if __name__ == "__main__":
    args = get_args()
    evaluate(args)
