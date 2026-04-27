"""
prepare_plots.py  –  MidcurveNN
================================
Visualization utilities for Phase I (image-based) and Phase III (graph-based).

Phase III additions
------------------
  plot_graph_pair()               – single profile + midcurve graph panel
  plot_graph_dataset_summary()    – grid of all loaded shapes
  plot_augmentation_gallery()     – show a shape across several transforms
  plot_graph_prediction()         – profile | GT | prediction three-panel
  plot_training_curves()          – train/val loss from CSV log
  plot_adjacency_matrix()         – heatmap of adj logits vs ground truth
  plot_node_degree_histogram()    – degree distribution of a graph
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
import json
import os

# ---------------------------------------------------------------------------
# ─── PHASE I utilities (unchanged) ─────────────────────────────────────────
# ---------------------------------------------------------------------------
# from config import JSON_FOLDER
JSON_FOLDER = "."


def plot_results(original_imgs, computed_imgs, size=(100, 100)):
    n = len(original_imgs)
    plt.figure(figsize=(20, 4))
    for i in range(n):
        ax = plt.subplot(2, n, i + 1)
        plt.imshow(original_imgs[i].reshape(size[0], size[1]), cmap='gray_r')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        ax = plt.subplot(2, n, i + 1 + n)
        plt.imshow(computed_imgs[i].reshape(size[0], size[1]), cmap='gray_r')
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    plt.show()


def plot_jsons(datafolder=JSON_FOLDER):
    for file in os.listdir(datafolder):
        if file.endswith(".json"):
            with open(os.path.join(JSON_FOLDER, file)) as json_file:
                shape_dict = json.load(json_file)
            profile_lines = shape_dict['Profile_lines']
            midcurve_lines = shape_dict['Midcurve_lines']
            plot_lines(profile_lines, 'black')
            plot_lines(midcurve_lines, 'red')
        plt.axis('equal')
        plt.show()


def plot_segments(segments, lines, points, color='blue', marker='o'):
    x_coords, y_coords = zip(*points)
    for segment in segments:
        for line_idx in segment:
            line = lines[line_idx]
            x_segment = [x_coords[i] for i in line]
            y_segment = [y_coords[i] for i in line]
            plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=color,
                     marker=marker)


def plot_breps(shapes_brep_dict_list):
    for dct in shapes_brep_dict_list:
        profile_point_list = dct['Profile']
        profile_brep = dct['Profile_brep']
        profile_segments = profile_brep["Segments"]
        profile_lines = profile_brep["Lines"]
        plot_segments(profile_segments, profile_lines, profile_point_list, 'black', 'o')

        midcurve_point_list = dct['Midcurve']
        midcurve_brep = dct['Midcurve_brep']
        midcurve_segments = midcurve_brep["Segments"]
        midcurve_lines = midcurve_brep["Lines"]
        plot_segments(midcurve_segments, midcurve_lines, midcurve_point_list, 'red', 'x')
        plt.axis('equal')
        plt.show()


def plot_lines(lines, color='black'):
    for line in lines:
        a = np.asarray(line)
        x = a[:, 0].T
        y = a[:, 1].T
        plt.plot(x, y, c=color)


def plot_list_of_lines(list_of_lines, names, color='black', figsize=(15, 5)):
    """
    Plot each geometrical figure in its own subplot with a given name as title.
    """
    if len(list_of_lines) != len(names):
        raise ValueError("The lengths of 'list_of_lines' and 'names' must be the same.")

    if isinstance(color, str):
        colors = [color] * len(list_of_lines)
    elif len(color) >= len(list_of_lines):
        colors = color
    else:
        colors = color * (len(list_of_lines) // len(color) + 1)
        colors = colors[:len(list_of_lines)]

    fig, axes = plt.subplots(1, len(list_of_lines), figsize=figsize)
    if len(list_of_lines) == 1:
        axes = [axes]

    for i, (lines, name, line_color) in enumerate(zip(list_of_lines, names, colors)):
        for line in lines:
            a = np.asarray(line)
            x = a[:, 0].T
            y = a[:, 1].T
            axes[i].plot(x, y, c=line_color)
        axes[i].set_title(name)
        axes[i].axis('equal')

    plt.tight_layout()
    return fig, axes


# ---------------------------------------------------------------------------
# ─── PHASE II utilities ─────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

# Colour palette
_PROFILE_COLOR  = "#2166ac"   # blue
_MIDCURVE_COLOR = "#d73027"   # red
_PRED_COLOR     = "#1a9641"   # green
_FAINT_COLOR    = "#aaaaaa"   # grey


def _draw_graph_on_ax(ax, node_xy: np.ndarray, edge_index: np.ndarray,
                      node_color="blue", edge_color=None,
                      node_size=60, edge_lw=1.8, alpha=1.0,
                      marker="o", label="", annotate_nodes=False):
    """
    Low-level: draw a graph (nodes + edges) on a given matplotlib Axes.

    Parameters
    ----------
    node_xy     : (N, 2) float array of node coordinates
    edge_index  : (2, E) int array  [source; target]
    annotate_nodes : if True, write node index next to each node
    """
    if edge_color is None:
        edge_color = node_color

    if edge_index is not None and edge_index.shape[1] > 0:
        seen = set()
        for u, v in edge_index.T:
            key = (min(u, v), max(u, v))
            if key in seen:
                continue
            seen.add(key)
            ax.plot([node_xy[u, 0], node_xy[v, 0]],
                    [node_xy[u, 1], node_xy[v, 1]],
                    color=edge_color, lw=edge_lw, alpha=alpha, zorder=3)

    sc = ax.scatter(node_xy[:, 0], node_xy[:, 1],
                    c=node_color, s=node_size, marker=marker,
                    alpha=alpha, zorder=5, label=label,
                    edgecolors="white", linewidths=0.5)

    if annotate_nodes:
        for idx, (xv, yv) in enumerate(node_xy):
            ax.annotate(str(idx), (xv, yv),
                        textcoords="offset points", xytext=(4, 4),
                        fontsize=7, color=node_color, zorder=6)
    return sc


def plot_graph_pair(profile_pts, profile_edges,
                    midcurve_pts, midcurve_edges,
                    title="", figsize=(10, 4),
                    annotate=False, save_path=None):
    """
    Plot one input–output pair side by side.

    Parameters
    ----------
    profile_pts    : (N, 2) ndarray  – profile polygon node coordinates
    profile_edges  : (2, E) ndarray  – profile edge index
    midcurve_pts   : (M, 2) ndarray  – midcurve node coordinates
    midcurve_edges : (2, F) ndarray  – midcurve edge index
    title          : str             – suptitle
    annotate       : bool            – label node indices
    save_path      : str or None     – if given, save figure to this path
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    _draw_graph_on_ax(ax1, profile_pts, profile_edges,
                      node_color=_PROFILE_COLOR, node_size=80,
                      edge_lw=2.0, label="Profile", annotate_nodes=annotate)
    ax1.set_title("Input Profile (Graph)", fontsize=11)
    ax1.set_aspect("equal"); ax1.grid(alpha=0.25)

    _draw_graph_on_ax(ax2, midcurve_pts, midcurve_edges,
                      node_color=_MIDCURVE_COLOR, node_size=80,
                      edge_lw=2.0, marker="s", label="Midcurve",
                      annotate_nodes=annotate)
    ax2.set_title("Ground-Truth Midcurve (Graph)", fontsize=11)
    ax2.set_aspect("equal"); ax2.grid(alpha=0.25)

    if title:
        plt.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_graph_dataset_summary(dataset, max_shapes=12,
                               figsize=None, save_path=None):
    """
    Grid overview of all shapes in a MidcurveGraphDataset (non-augmented).
    Each cell shows profile (blue) + midcurve (red) overlaid.

    Parameters
    ----------
    dataset   : MidcurveGraphDataset  (loaded with augment=False)
    max_shapes: int – maximum number of shapes to display
    save_path : str or None
    """
    n = min(len(dataset), max_shapes)
    ncols = min(n, 4)
    nrows = (n + ncols - 1) // ncols
    if figsize is None:
        figsize = (ncols * 4, nrows * 3.5)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.array(axes).reshape(-1)

    for i in range(n):
        data = dataset.get(i)
        ax = axes[i]

        prof_xy = data.x.numpy()
        mid_xy  = data.y.numpy()
        ei_p    = data.edge_index.numpy()
        ei_m    = data.mid_edge_index.numpy()

        _draw_graph_on_ax(ax, prof_xy, ei_p,
                          node_color=_PROFILE_COLOR, node_size=40, edge_lw=1.5)
        _draw_graph_on_ax(ax, mid_xy, ei_m,
                          node_color=_MIDCURVE_COLOR, node_size=60, edge_lw=2.0,
                          marker="s")

        ax.set_title(data.label, fontsize=9, fontweight="bold")
        ax.set_aspect("equal"); ax.grid(alpha=0.2)

        p_patch = mpatches.Patch(color=_PROFILE_COLOR,  label="Profile")
        m_patch = mpatches.Patch(color=_MIDCURVE_COLOR, label="Midcurve")
        ax.legend(handles=[p_patch, m_patch], fontsize=7, loc="best")

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("MidcurveNN Phase III – Dataset Overview", fontsize=14,
                 fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_augmentation_gallery(dataset, shape_name="I", max_variants=12,
                               figsize=None, save_path=None):
    """
    Show a single shape across several augmented variants.

    Parameters
    ----------
    dataset    : MidcurveGraphDataset (loaded with augment=True)
    shape_name : str – base shape name (e.g. 'I', 'L', 'T', 'Plus')
    max_variants : int – how many variants to display
    """
    variants = [dataset.get(i) for i in range(len(dataset))
                if dataset.get(i).label.startswith(shape_name)][:max_variants]

    n = len(variants)
    if n == 0:
        print(f"[WARN] No variants found for shape '{shape_name}'")
        return None

    ncols = min(n, 4)
    nrows = (n + ncols - 1) // ncols
    if figsize is None:
        figsize = (ncols * 3.5, nrows * 3)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.array(axes).reshape(-1)

    for i, data in enumerate(variants):
        ax = axes[i]
        _draw_graph_on_ax(ax, data.x.numpy(), data.edge_index.numpy(),
                          node_color=_PROFILE_COLOR, node_size=30, edge_lw=1.2)
        _draw_graph_on_ax(ax, data.y.numpy(), data.mid_edge_index.numpy(),
                          node_color=_MIDCURVE_COLOR, node_size=45, edge_lw=1.8,
                          marker="s")
        short_label = data.label.replace(shape_name + "_", "")
        ax.set_title(short_label or "original", fontsize=8)
        ax.set_aspect("equal"); ax.grid(alpha=0.2)

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle(f"Augmentation Gallery – Shape '{shape_name}'",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_graph_prediction(shape_name,
                          profile_xy, profile_edges,
                          gt_mid_xy, gt_mid_edges,
                          pred_mid_xy, pred_mid_edges,
                          figsize=(16, 5), save_path=None):
    """
    Three-panel figure: profile | ground truth | prediction.

    Parameters
    ----------
    All *_xy     : (N, 2) ndarray
    All *_edges  : (2, E) ndarray  (may be empty)
    save_path    : str or None
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)

    # Panel 1 – Input Profile
    ax = axes[0]
    _draw_graph_on_ax(ax, profile_xy, profile_edges,
                      node_color=_PROFILE_COLOR, node_size=60, edge_lw=2.0,
                      label="Profile", annotate_nodes=True)
    ax.set_title("Input Profile", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.25)

    # Panel 2 – Ground Truth Midcurve
    ax = axes[1]
    _draw_graph_on_ax(ax, gt_mid_xy, gt_mid_edges,
                      node_color=_MIDCURVE_COLOR, node_size=80, edge_lw=2.5,
                      marker="s", label="GT Midcurve", annotate_nodes=True)
    ax.set_title("Ground-Truth Midcurve", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.25)

    # Panel 3 – Prediction (overlaid on profile)
    ax = axes[2]
    # Faint profile background
    _draw_graph_on_ax(ax, profile_xy, profile_edges,
                      node_color=_FAINT_COLOR, edge_color=_FAINT_COLOR,
                      node_size=20, edge_lw=0.7, alpha=0.45)
    # GT for reference
    _draw_graph_on_ax(ax, gt_mid_xy, gt_mid_edges,
                      node_color=_MIDCURVE_COLOR, node_size=50, edge_lw=1.2,
                      marker="s", alpha=0.4, label="GT (ref)")
    # Prediction
    _draw_graph_on_ax(ax, pred_mid_xy, pred_mid_edges,
                      node_color=_PRED_COLOR, node_size=100, edge_lw=2.5,
                      marker="*", label="Predicted")
    ax.set_title("Predicted Midcurve", fontsize=11)
    ax.set_aspect("equal"); ax.grid(alpha=0.25)
    ax.legend(fontsize=8, loc="best")

    plt.suptitle(f"MidcurveNN Phase III – {shape_name}",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_training_curves(log_csv: str, figsize=(13, 4), save_path=None):
    """
    Plot training and validation loss curves from a CSV training log.

    The CSV must have columns:
      epoch, train_loss, train_chamfer, train_adj, val_loss, val_chamfer, val_adj, lr
    """
    import csv
    epochs, tr, vl, tr_ch, vl_ch, tr_adj, vl_adj, lrs = ([] for _ in range(8))

    with open(log_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            epochs.append(int(row["epoch"]))
            tr.append(float(row["train_loss"]))
            vl.append(float(row["val_loss"]))
            tr_ch.append(float(row["train_chamfer"]))
            vl_ch.append(float(row["val_chamfer"]))
            tr_adj.append(float(row["train_adj"]))
            vl_adj.append(float(row["val_adj"]))
            lrs.append(float(row["lr"]))

    fig, axes = plt.subplots(1, 3, figsize=figsize)

    axes[0].plot(epochs, tr, label="Train", color=_PROFILE_COLOR, lw=1.5)
    axes[0].plot(epochs, vl, label="Val",   color=_MIDCURVE_COLOR, lw=1.5, ls="--")
    axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
    axes[0].set_title("Total Loss"); axes[0].legend(); axes[0].grid(alpha=0.3)

    axes[1].plot(epochs, tr_ch, label="Train", color=_PROFILE_COLOR, lw=1.5)
    axes[1].plot(epochs, vl_ch, label="Val",   color=_MIDCURVE_COLOR, lw=1.5, ls="--")
    axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Chamfer Distance")
    axes[1].set_title("Chamfer Loss"); axes[1].legend(); axes[1].grid(alpha=0.3)

    axes[2].plot(epochs, tr_adj, label="Train", color=_PROFILE_COLOR, lw=1.5)
    axes[2].plot(epochs, vl_adj, label="Val",   color=_MIDCURVE_COLOR, lw=1.5, ls="--")
    axes[2].set_xlabel("Epoch"); axes[2].set_ylabel("Binary CE")
    axes[2].set_title("Adjacency BCE Loss"); axes[2].legend(); axes[2].grid(alpha=0.3)

    plt.suptitle("MidcurveNN Phase III – Training Curves", fontsize=13,
                 fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_adjacency_matrix(adj_logits_np: np.ndarray,
                          gt_adj_np: np.ndarray = None,
                          title="", figsize=(10, 4), save_path=None):
    """
    Show predicted adjacency (probability) and optionally ground-truth adjacency
    as side-by-side heatmaps.

    Parameters
    ----------
    adj_logits_np : (k, k) ndarray – raw logits from the model
    gt_adj_np     : (k, k) ndarray or None – ground truth adjacency
    """
    adj_prob = 1.0 / (1.0 + np.exp(-adj_logits_np))   # sigmoid

    if gt_adj_np is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        im1 = ax1.imshow(adj_prob, vmin=0, vmax=1, cmap="Blues", aspect="auto")
        ax1.set_title("Predicted Adjacency (σ(logits))")
        plt.colorbar(im1, ax=ax1)
        im2 = ax2.imshow(gt_adj_np, vmin=0, vmax=1, cmap="Reds", aspect="auto")
        ax2.set_title("Ground-Truth Adjacency")
        plt.colorbar(im2, ax=ax2)
    else:
        fig, ax1 = plt.subplots(figsize=(figsize[0] // 2, figsize[1]))
        im1 = ax1.imshow(adj_prob, vmin=0, vmax=1, cmap="Blues", aspect="auto")
        ax1.set_title("Predicted Adjacency (σ(logits))")
        plt.colorbar(im1, ax=ax1)

    if title:
        plt.suptitle(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_node_degree_histogram(edge_index_np: np.ndarray, num_nodes: int,
                               title="Node Degree Distribution",
                               color=_PROFILE_COLOR, figsize=(6, 4),
                               save_path=None):
    """
    Bar chart of node degree distribution for a graph.

    Parameters
    ----------
    edge_index_np : (2, E) int ndarray
    num_nodes     : int
    """
    degrees = np.zeros(num_nodes, dtype=int)
    if edge_index_np.shape[1] > 0:
        for u in edge_index_np[0]:
            degrees[u] += 1

    unique_degs, counts = np.unique(degrees, return_counts=True)
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(unique_degs, counts, color=color, edgecolor="white", alpha=0.85)
    ax.set_xlabel("Degree"); ax.set_ylabel("Number of Nodes")
    ax.set_title(title); ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


# ---------------------------------------------------------------------------
# ─── Demo / quick test ──────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # ── Original Phase I demo (preserved) ────────────────────────────────────
    profile          = [((-5.65, -4.26), (-10.6, -3.56), (-14.08, -28.32),
                         (-38.83, -24.84), (-39.53, -29.79), (-9.82, -33.96),
                         (-5.65, -4.26))]
    actual_midcurve  = [((-8.12, -3.91), (-11.95, -31.14), (-39.18, -27.31))]
    predicted_midcurve = [((-8.13, -3.91), (-11.95, -31.14), (-39.18, -27.32))]

    fig, axes = plot_list_of_lines(
        [profile, actual_midcurve, predicted_midcurve],
        ["profile", "actual_midcurve", "predicted_midcurve"],
        color=['red', 'blue', 'green'])
    plt.show()

    # ── Phase III demo (graph-based) ──────────────────────────────────────────
    # Manually build the I-shape graph for demo purposes
    profile_pts = np.array([[5, 5], [10, 5], [10, 20], [5, 20]], dtype=float)
    n = len(profile_pts)
    src = list(range(n)) + [(i + 1) % n for i in range(n)]
    dst = [(i + 1) % n for i in range(n)] + list(range(n))
    profile_edges = np.array([src, dst])

    midcurve_pts = np.array([[7.5, 5], [7.5, 20]], dtype=float)
    mid_edges = np.array([[0, 1], [1, 0]])

    fig = plot_graph_pair(
        profile_pts, profile_edges,
        midcurve_pts, mid_edges,
        title="I-Shape – Graph Pair Demo",
        annotate=True)
    plt.show()

    # Degree histogram demo
    fig = plot_node_degree_histogram(profile_edges, num_nodes=n,
                                     title="I-Shape Profile: Node Degree")
    plt.show()

    # Adjacency matrix demo
    fake_logits = np.random.randn(4, 4)
    gt_adj = np.array([[0, 1, 0, 1],
                        [1, 0, 1, 0],
                        [0, 1, 0, 1],
                        [1, 0, 1, 0]], dtype=float)
    fig = plot_adjacency_matrix(fake_logits, gt_adj,
                                title="Demo: Adjacency Heatmap")
    plt.show()
