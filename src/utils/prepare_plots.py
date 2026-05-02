import matplotlib.pyplot as plt
import numpy as np
import json
import os
import matplotlib.gridspec as gridspec
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
            # for line in profile_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='black')
            # for line in midcurve_lines:
            #     a = np.asarray(line)
            #     x = a[:, 0].T
            #     y = a[:, 1].T
            #     plt.plot(x, y, c='red')
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
        profile_x_coords, profile_y_coords = zip(*profile_point_list)
        profile_brep = dct['Profile_brep']
        profile_segments = profile_brep["Segments"]
        profile_lines = profile_brep["Lines"]
        profile_segment_color = 'black'
        # Plot Profile segments
        # for segment in profile_segments:
        #     for line_idx in segment:
        #         line = profile_lines[line_idx]
        #         x_segment = [profile_x_coords[i] for i in line]
        #         y_segment = [profile_y_coords[i] for i in line]
        #         plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=profile_segment_color,
        #                  marker='o')
        plot_segments(profile_segments, profile_lines, profile_point_list, profile_segment_color, 'o')

        midcurve_point_list = dct['Midcurve']
        midcurve_x_coords, midcurve_y_coords = zip(*midcurve_point_list)
        midcurve_brep = dct['Midcurve_brep']
        midcurve_segments = midcurve_brep["Segments"]
        midcurve_lines = midcurve_brep["Lines"]
        midcurve_segment_color = 'red'

        # Plot Midcurve segments
        # for segment in midcurve_segments:
        #     for line_idx in segment:
        #         line = midcurve_lines[line_idx]
        #         x_segment = [midcurve_x_coords[i] for i in line]
        #         y_segment = [midcurve_y_coords[i] for i in line]
        #         plt.plot(x_segment + [x_segment[0]], y_segment + [y_segment[0]], color=midcurve_segment_color,
        #                  marker='x')
        plot_segments(midcurve_segments, midcurve_lines, midcurve_point_list, midcurve_segment_color, 'x')
        plt.axis('equal')
        plt.show()


def plot_lines(lines, color='black'):
    for line in lines:
        a = np.asarray(line)
        x = a[:, 0].T
        y = a[:, 1].T
        plt.plot(x, y, c=color)

def _squeeze_to_2d(arr):
    """Reduce any numpy array to 2-D (H, W) suitable for imshow."""
    arr = np.asarray(arr)
    if arr.ndim == 3:
        if arr.shape[2] == 1:
            return arr[:, :, 0]
        # CoordConv inputs: channels = [x_coord, y_coord, profile] — profile is last
        return arr[:, :, -1]
    return arr


def save_results_grid_images(inputs, ground_truths, predictions, save_path,
                              n=7, title="Midcurve Prediction Results",
                              row_labels=None):
    """
    Save a results PNG grid: 3 rows x n cols.
    Row 0 = Input Profile, Row 1 = Ground Truth, Row 2 = Predicted.
    Columns are individual samples, matching the reference visualisation style.

    inputs, ground_truths, predictions: lists or arrays whose elements are 2-D or 3-D
        numpy arrays (H, W) or (H, W, C).  All values should be in [0, 1].
    save_path: full path for the output PNG.
    n: number of sample columns (capped at len(inputs)).
    row_labels: unused, kept for backward compatibility.
    """
    n = min(n, len(inputs))
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    fig, axes = plt.subplots(3, n, figsize=(n * 2.5, 7.5))
    if n == 1:
        axes = axes[:, np.newaxis]

    row_titles = ["Input (Profile)", "Ground Truth", "Predicted"]
    row_data   = [inputs, ground_truths, predictions]

    for row, (label, data) in enumerate(zip(row_titles, row_data)):
        axes[row, 0].set_ylabel(label, fontsize=10, fontweight="bold",
                                 rotation=90, va="center", labelpad=8)
        for col in range(n):
            img = _squeeze_to_2d(data[col])
            # Auto-scale per cell so low-contrast predictions (e.g. CNN) remain visible
            axes[row, col].imshow(img, cmap="gray_r",
                                  interpolation="nearest",
                                  vmin=img.min(), vmax=img.max())
            axes[row, col].axis("off")

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Results] grid saved -> {save_path}")


def _draw_geo_panel(ax, coords, edge_index, color, alpha=1.0,
                    marker="o", node_size=40, lw=1.5, linestyle="-"):
    """Draw nodes and edges on a single geometry subplot."""
    if edge_index is not None and edge_index.shape[1] > 0:
        for u, v in edge_index.T:
            ax.plot([coords[u, 0], coords[v, 0]],
                    [coords[u, 1], coords[v, 1]],
                    color=color, lw=lw, alpha=alpha, linestyle=linestyle)
    ax.scatter(coords[:, 0], coords[:, 1],
               c=color, s=node_size, marker=marker, alpha=alpha, zorder=5)


def save_results_grid_geometry(profiles, gt_midcurves, pred_midcurves,
                                profile_edges, gt_edges, pred_edges,
                                save_path, n=5,
                                title="Midcurve Prediction Results (Geometry)",
                                row_labels=None):
    """
    Save a geometry results PNG grid: n rows × 3 cols.
      Col 0: input profile polygon (blue).
      Col 1: ground-truth midcurve (red dashed).
      Col 2: predicted midcurve overlaid on profile (green + grey profile + faint red GT).

    profiles, gt_midcurves, pred_midcurves: lists of (N, 2) numpy float arrays.
    profile_edges, gt_edges, pred_edges: lists of (2, E) numpy int arrays.
    save_path: full path for the output PNG.
    """
    n = min(n, len(profiles))
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    fig, axes = plt.subplots(n, 3, figsize=(12, n * 3.5 + 0.6))
    if n == 1:
        axes = axes[np.newaxis, :]

    col_titles = ["Input (Profile)", "Ground Truth", "Predicted"]
    for col, label in enumerate(col_titles):
        axes[0, col].set_title(label, fontsize=11, fontweight="bold")

    _empty_edges = np.empty((2, 0), dtype=int)

    for row in range(n):
        pe = profile_edges[row] if profile_edges[row] is not None else _empty_edges
        ge = gt_edges[row]      if gt_edges[row]      is not None else _empty_edges
        de = pred_edges[row]    if pred_edges[row]     is not None else _empty_edges

        _draw_geo_panel(axes[row, 0], profiles[row], pe, "#2c7bb6")
        _draw_geo_panel(axes[row, 1], gt_midcurves[row], ge, "#d7191c", linestyle="--")
        _draw_geo_panel(axes[row, 2], profiles[row],    pe, "#aaaaaa", alpha=0.35, lw=0.8)
        _draw_geo_panel(axes[row, 2], pred_midcurves[row], de, "#1a9641", marker="*", node_size=70)
        _draw_geo_panel(axes[row, 2], gt_midcurves[row],  ge, "#d7191c", alpha=0.3,
                        linestyle="--", lw=1.0)

        for col in range(3):
            axes[row, col].set_aspect("equal")
            axes[row, col].grid(alpha=0.25)
            axes[row, col].tick_params(labelsize=7)

        if row_labels and row < len(row_labels):
            axes[row, 0].set_ylabel(str(row_labels[row]), fontsize=8,
                                    rotation=0, labelpad=50, va="center")

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Results] geometry grid saved -> {save_path}")


def _draw_brep_panel(ax, brep_str, title, color):
    """Plot a BRep JSON (Points + Lines) onto a single matplotlib Axes."""
    import json as _json
    import ast as _ast
    data = None
    try:
        if isinstance(brep_str, dict):
            data = brep_str
        elif isinstance(brep_str, str):
            try:
                candidate = _json.loads(brep_str)
            except (_json.JSONDecodeError, TypeError, ValueError):
                candidate = _ast.literal_eval(brep_str)
            if isinstance(candidate, str):
                candidate = _json.loads(candidate)
            if isinstance(candidate, dict):
                data = candidate
    except Exception:
        pass

    ax.set_title(title, fontsize=8)
    if data is None:
        msg = "no\nprediction" if brep_str is None else "parse\nerror"
        ax.text(0.5, 0.5, msg, ha="center", va="center",
                transform=ax.transAxes, color="gray", fontsize=8)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return

    pts   = data.get("Points", [])
    lines = data.get("Lines",  [])

    if not pts:
        return

    # Normalise flat [x, y, x, y, ...] to [[x, y], ...]
    if isinstance(pts[0], (int, float)):
        if len(pts) % 2 == 0:
            pts = [[pts[i], pts[i + 1]] for i in range(0, len(pts), 2)]
        else:
            ax.text(0.5, 0.5, "bad\nformat", ha="center", va="center",
                    transform=ax.transAxes, color="orange", fontsize=7)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            return

    try:
        for ln in lines:
            if isinstance(ln, (list, tuple)) and len(ln) >= 2:
                i0, i1 = int(ln[0]), int(ln[1])
                if i0 < len(pts) and i1 < len(pts):
                    x0, y0 = pts[i0]
                    x1, y1 = pts[i1]
                    ax.plot([x0, x1], [y0, y1], color=color, linewidth=1.5, zorder=2)
    except Exception:
        pass

    try:
        xs, ys = zip(*pts)
        ax.scatter(xs, ys, color=color, s=18, zorder=3)
    except Exception:
        pass

    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.25)
    ax.tick_params(labelsize=6)


def save_results_grid_brep(profiles, gt_midcurves, pred_midcurves,
                            save_path, n=7, shape_names=None, scores=None,
                            title="Midcurve Prediction Results (Text/BRep)"):
    """
    Save a results PNG grid for BRep JSON text-based approaches: n rows x 3 cols.
      Col 0: input profile polygon (blue).
      Col 1: ground-truth midcurve (green).
      Col 2: predicted midcurve (red).

    profiles, gt_midcurves, pred_midcurves: lists of BRep JSON strings or dicts.
    save_path: full path for the output PNG.
    n: number of sample rows (capped at len(profiles)).
    shape_names: optional list of shape name strings for row labels.
    scores: optional list of combined scores per sample.
    """
    n = min(n, len(profiles))
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    fig, axes = plt.subplots(n, 3, figsize=(13, 3.5 * n + 0.8), squeeze=False)

    col_labels = ["Input (Profile)", "Ground Truth", "Predicted"]
    colors     = ["steelblue", "forestgreen", "firebrick"]
    for col, label in enumerate(col_labels):
        axes[0, col].set_title(label, fontsize=10, fontweight="bold")

    for row in range(n):
        name  = shape_names[row] if shape_names and row < len(shape_names) else f"sample_{row}"
        score = scores[row]      if scores is not None and row < len(scores) else None
        pred_lbl = f"Predicted\n{name}"
        if score is not None:
            pred_lbl += f"\n(score={score:.2f})"

        _draw_brep_panel(axes[row, 0], profiles[row],      f"Profile\n{name}",      colors[0])
        _draw_brep_panel(axes[row, 1], gt_midcurves[row],  f"GT Midcurve\n{name}",  colors[1])
        _draw_brep_panel(axes[row, 2], pred_midcurves[row], pred_lbl,                colors[2])

    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[Results] BRep grid saved -> {save_path}")


def plot_list_of_lines(list_of_lines, names, color='black', figsize=(15, 5)):
    """
    Plot each geometrical figure in its own subplot with a given name as title.
    
    Parameters:
    -----------
    list_of_lines : list
        List where each element is a set of lines comprising a geometrical figure.
        Each figure is a list of line coordinates where each line is a tuple of points.
    names : list
        List of names for each figure (used as subplot titles).
    color : str or list, optional
        Color to use for plotting lines. Can be a single color for all figures
        or a list of colors (one per figure). Default: 'black'.
    figsize : tuple, optional
        Figure size (width, height) in inches (default: (15, 5)).
    """
    # Check if list_of_lines and names have the same length
    if len(list_of_lines) != len(names):
        raise ValueError("The lengths of 'list_of_lines' and 'names' must be the same.")
    
    # Handle colors
    if isinstance(color, str):
        colors = [color] * len(list_of_lines)
    elif len(color) >= len(list_of_lines):
        colors = color
    else:
        colors = color * (len(list_of_lines) // len(color) + 1)
        colors = colors[:len(list_of_lines)]
    
    # Create subplots
    fig, axes = plt.subplots(1, len(list_of_lines), figsize=figsize)
    
    # Handle case where there's only one figure
    if len(list_of_lines) == 1:
        axes = [axes]
    
    # Plot each figure in its own subplot
    for i, (lines, name, line_color) in enumerate(zip(list_of_lines, names, colors)):
        for line in lines:
            a = np.asarray(line)
            x = a[:, 0].T
            y = a[:, 1].T
            axes[i].plot(x, y, c=line_color)
        
        axes[i].set_title(name)
        axes[i].axis('equal')
    
    # Adjust layout
    plt.tight_layout()
    
    return fig, axes



if __name__ == "__main__":
    chatgpt_lines = [((2.5, 0), (2.5, 22.5)), ((2.5, 22.5), (2.5, 45.0)), ((2.5, 22.5), (25.0, 22.5)),
                     ((2.5, 22.5), (12.5, 22.5)), ((2.5, 22.5), (0, 22.5)), ((2.5, 22.5), (25.0, 22.5))]
    perplexity_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (12.5, 45.0)), ((12.5, 22.5), (0, 22.5)),
                        ((12.5, 22.5), (25.0, 22.5))]
    bard_liens = [((12.5, 0), (12.5, 25.0)), ((12.5, 25.0), (25.0, 25.0)), ((25.0, 25.0), (25.0, 0))]
    huggingface_chat_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (25.0, 22.5)), ((25.0, 22.5), (25.0, 25.0))]
    gpt4_lines = [((12.5, 0), (12.5, 22.5)), ((12.5, 22.5), (0, 22.5)), ((12.5, 22.5), (25.0, 22.5))]
    claude_lines = [((12.5, 0.0), (12.5, 22.5)), ((12.5, 22.5), (12.5, 25.0)), ((12.5, 22.5), (0.0, 22.5)),
                    ((12.5, 22.5), (25.0, 22.5))]
    gemini_pro_lines = [((12.5,0), (12.5, 22.5)), ((12.5, 22.5),(12.5,45.0)), ((12.5, 22.5), (0,22.5))]


    profile =  [((-5.65, -4.26), (-10.6, -3.56), (-14.08, -28.32), (-38.83, -24.84), (-39.53, -29.79), (-9.82, -33.96), (-5.65, -4.26))]
    actual_midcurve = [((-8.12, -3.91), (-11.95, -31.14), (-39.18, -27.31))]
    predicted_midcurve = [((-8.13, -3.91), (-11.95, -31.14), (-39.18, -27.32))] # gemini 3 19 Nov 2025
    
    
    list_of_lines = [profile, actual_midcurve, predicted_midcurve]
    figure_names = ["profile", "actual_midcurve", "predicted_midcurve"]
    
    fig, axes = plot_list_of_lines(list_of_lines, figure_names, color=['red', 'blue','green'])
    plt.show()
        
    # plot_lines(test_lines, 'red')
    # plt.axis('equal')
    # plt.show()
    # # plot_jsons()
