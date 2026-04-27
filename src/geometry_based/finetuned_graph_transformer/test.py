"""
test.py  –  MidcurveNN Phase III-b
=====================================
Evaluate a trained fine-tuned Graphormer checkpoint on the full dataset.

Run
---
    cd src/geometry_based/finetuned_graph_transformer
    python test.py
    python test.py --ckpt checkpoints/best_model.pt
"""

import argparse
import os
import sys
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC  = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SRC)

from torch_geometric.utils import dense_to_sparse
from geometry_based.graph_transformer.graph_dataset import MidcurveGraphDataset
from geometry_based.graph_transformer.graph_transformer import chamfer_loss
from geometry_based.graph_transformer.prepare_plots import plot_graph_prediction
from model import MidcurveFinetuned


def get_args():
    _default_data = os.path.join(_SRC, "data", "raw")
    p = argparse.ArgumentParser("MidcurveNN Phase III-b  –  Test")
    p.add_argument("--data",       default=_default_data)
    p.add_argument("--ckpt",       default="checkpoints/best_model.pt")
    p.add_argument("--results-dir",default="results")
    p.add_argument("--threshold",  type=float, default=0.5)
    p.add_argument("--max-nodes",  type=int,   default=32)
    p.add_argument("--no-pretrained", action="store_true")
    return p.parse_args()


def evaluate():
    args = get_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Test] Device:     {device}")
    print(f"[Test] Checkpoint: {args.ckpt}")

    # Load model
    model = MidcurveFinetuned(
        max_nodes=args.max_nodes,
        pretrained=not args.no_pretrained)
    if os.path.isfile(args.ckpt):
        ckpt = torch.load(args.ckpt, map_location=device)
        model.load_state_dict(ckpt["model_state"])
        print(f"[Test] Loaded epoch {ckpt['epoch']}")
    else:
        print(f"[Test] WARNING: checkpoint not found at {args.ckpt}. Using random weights.")
    model.to(device).eval()

    dataset = MidcurveGraphDataset(args.data, augment=False)
    os.makedirs(args.results_dir, exist_ok=True)

    chamfer_scores = []
    print(f"\n{'Shape':>12}  {'Chamfer':>10}  {'Nodes-pred':>10}")
    print("-" * 38)

    for i in range(len(dataset)):
        data = dataset.get(i)
        label = data.label

        with torch.no_grad():
            coords_pred, adj_logits = model(
                data.x.to(device),
                data.edge_index.to(device),
                torch.zeros(data.x.size(0), dtype=torch.long, device=device),
            )

        # coords_pred: (1, max_nodes, 2) — batch size 1
        coords_pred = coords_pred[0]   # (max_nodes, 2)
        adj_prob = torch.sigmoid(adj_logits[0])
        adj_prob.fill_diagonal_(0.0)
        ei_pred, _ = dense_to_sparse(adj_prob > args.threshold)

        # Denormalise
        c, s = data.centre, data.scale
        prof_dn   = (data.x.numpy()    * s + c)
        gt_mid_dn = (data.y.numpy()    * s + c)
        pred_dn   = (coords_pred.cpu().numpy() * s + c)

        ch = chamfer_loss(coords_pred.cpu(), data.y).item()
        chamfer_scores.append(ch)
        print(f"{label:>12}  {ch:>10.4f}  {args.max_nodes:>10}")

        fig = plot_graph_prediction(
            label,
            prof_dn, data.edge_index.numpy(),
            gt_mid_dn, data.mid_edge_index.numpy(),
            pred_dn, ei_pred.cpu().numpy() if ei_pred.numel() > 0 else np.empty((2, 0), dtype=int),
            save_path=os.path.join(args.results_dir, f"{label}_finetuned_prediction.png"),
        )
        plt.close(fig)

    mean_ch = float(np.mean(chamfer_scores))
    print(f"{'MEAN':>12}  {mean_ch:>10.4f}")
    print(f"\n[Test] Results saved to: {args.results_dir}/")
    return {"mean_chamfer": mean_ch, "per_shape": chamfer_scores}


if __name__ == "__main__":
    evaluate()
