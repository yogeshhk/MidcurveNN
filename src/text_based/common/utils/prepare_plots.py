"""
prepare_plots.py — All visualization utilities for the Midcurve Pipeline.

Provides four levels of visualization:

1. **Single shape** — overlay profile and midcurve on one axis using the
   BRep structure for exact topological rendering.
2. **Grid view** — many shapes in one figure for dataset-wide quality checks.
3. **Comparison** — profile / actual midcurve / predicted midcurve side-by-side
   with an overlay panel, for model evaluation.
4. **Animation** — cycle through a rotation sequence to verify midcurve tracks
   correctly through a full rotation.
5. **Interactive HTML export** — Plotly-based, shareable without a Python env.

All functions accept the standard shape dict format (with BRep sub-dicts).
The flat ``Profile`` / ``Midcurve`` point lists are used for quick drawing;
the BRep ``Lines`` / ``Segments`` are used when topological accuracy matters.
"""

from __future__ import annotations

import math
from typing import Sequence

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


# ---------------------------------------------------------------------------
# Internal drawing primitives
# ---------------------------------------------------------------------------

def _draw_brep(ax: plt.Axes, brep: dict, color: str,
               marker: str = "o", linewidth: float = 1.5,
               label: str | None = None) -> None:
    """
    Resolve a BRep dict into actual coordinate segments and draw them.

    ``Lines`` and ``Segments`` drive the drawing so that the rendered result
    exactly matches the authored topology — disconnected components, branches,
    and multi-segment chains all render correctly.

    Parameters
    ----------
    ax:
        Target Matplotlib axes.
    brep:
        A BRep sub-dict with ``Points``, ``Lines``, ``Segments``.
    color:
        Line and marker colour.
    marker:
        Marker style for vertices.
    linewidth:
        Stroke width.
    label:
        Legend label (attached to the first line only).
    """
    points   = brep["Points"]
    lines    = brep["Lines"]
    segments = brep["Segments"]

    first = True
    for segment in segments:
        for line_idx in segment:
            i, j = lines[line_idx]
            x = [points[i][0], points[j][0]]
            y = [points[i][1], points[j][1]]
            ax.plot(x, y, color=color, linewidth=linewidth,
                    label=(label if first else None))
            first = False

    # Draw all vertices once (deduped by set of index tuples)
    drawn = set()
    for segment in segments:
        for line_idx in segment:
            for idx in lines[line_idx]:
                if idx not in drawn:
                    ax.scatter(points[idx][0], points[idx][1],
                               color=color, s=22, marker=marker, zorder=4)
                    drawn.add(idx)


def _ax_setup(ax: plt.Axes, title: str = "") -> None:
    """Apply standard axis formatting."""
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3, alpha=0.6)
    if title:
        ax.set_title(title, fontsize=9)


# ---------------------------------------------------------------------------
# Single-shape plot  (moved from prepare_data.py)
# ---------------------------------------------------------------------------

def plot_shape(shape_dict: dict, ax: plt.Axes | None = None) -> plt.Axes:
    """
    Draw one shape dict — profile in black, midcurve in red — using the
    BRep topology for exact rendering.

    This function replaces ``plot_profile_dict`` from the old
    ``prepare_data.py`` and should be imported from here instead.

    Parameters
    ----------
    shape_dict:
        A shape dict with ``Profile_brep``, ``Midcurve_brep``, and
        optionally ``ShapeName``.
    ax:
        Axes to draw on.  A new figure/axes is created if ``None``.

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(4, 4))

    _draw_brep(ax, shape_dict["Profile_brep"],
               color="black", marker="o", label="Profile")
    _draw_brep(ax, shape_dict["Midcurve_brep"],
               color="red",   marker="x", label="Midcurve")

    ax.legend(fontsize=8)
    _ax_setup(ax, title=shape_dict.get("ShapeName", ""))
    return ax


def show_shape(shape_dict: dict) -> None:
    """
    Convenience wrapper: plot a single shape dict and call ``plt.show()``.

    Parameters
    ----------
    shape_dict:
        A shape dict with ``Profile_brep`` and ``Midcurve_brep``.
    """
    plot_shape(shape_dict)
    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Grid view — dataset quality check
# ---------------------------------------------------------------------------

def plot_shape_grid(
    shape_dicts: list,
    n_cols: int = 5,
    cell_size: tuple = (3, 3),
    title: str = "Shape dataset overview",
) -> plt.Figure:
    """
    Display a grid of shapes — one subplot per shape — for dataset-wide
    quality inspection.

    Parameters
    ----------
    shape_dicts:
        List of shape dicts.
    n_cols:
        Number of subplot columns.
    cell_size:
        ``(width, height)`` in inches per subplot cell.
    title:
        Overall figure super-title.

    Returns
    -------
    plt.Figure
    """
    n      = len(shape_dicts)
    n_rows = math.ceil(n / n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(cell_size[0] * n_cols, cell_size[1] * n_rows),
    )
    axes_flat = np.array(axes).flatten()

    for i, dct in enumerate(shape_dicts):
        plot_shape(dct, ax=axes_flat[i])

    for ax in axes_flat[n:]:
        ax.set_visible(False)

    fig.suptitle(title, fontsize=11)
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Comparison plot — model evaluation
# ---------------------------------------------------------------------------

def plot_prediction_comparison(
    shape_dict: dict,
    predicted_midcurve_brep: dict,
    figsize: tuple = (16, 4),
) -> tuple[plt.Figure, list]:
    """
    Four-panel comparison: profile | actual midcurve | predicted midcurve |
    overlay of actual vs predicted.

    Parameters
    ----------
    shape_dict:
        Ground-truth shape dict (provides both profile and actual midcurve).
    predicted_midcurve_brep:
        A ``Midcurve_brep``-style dict for the model's prediction.
    figsize:
        Overall figure dimensions.

    Returns
    -------
    (fig, axes)  — list of 4 Axes objects.
    """
    fig, axes = plt.subplots(1, 4, figsize=figsize)
    name = shape_dict.get("ShapeName", "shape")

    _draw_brep(axes[0], shape_dict["Profile_brep"],  color="black")
    _ax_setup(axes[0], title=f"{name} — profile")

    _draw_brep(axes[1], shape_dict["Midcurve_brep"], color="blue")
    _ax_setup(axes[1], title="actual midcurve")

    _draw_brep(axes[2], predicted_midcurve_brep,     color="green")
    _ax_setup(axes[2], title="predicted midcurve")

    # Overlay panel
    _draw_brep(axes[3], shape_dict["Midcurve_brep"],
               color="blue",  linewidth=2.0, label="actual")
    _draw_brep(axes[3], predicted_midcurve_brep,
               color="green", linewidth=1.5, label="predicted")
    axes[3].legend(fontsize=8)
    _ax_setup(axes[3], title="overlay")

    plt.tight_layout()
    return fig, list(axes)


# ---------------------------------------------------------------------------
# Rotation animation
# ---------------------------------------------------------------------------

def animate_rotation(
    rotated_shape_dicts: list,
    interval_ms: int = 50,
    title: str = "Rotation sequence",
) -> animation.FuncAnimation:
    """
    Animate a sequence of rotated shape dicts to verify that the midcurve
    tracks correctly through a full rotation.

    Parameters
    ----------
    rotated_shape_dicts:
        Ordered list of shape dicts, one per rotation step.
    interval_ms:
        Delay between frames in milliseconds.
    title:
        Figure title (updated each frame with the ShapeName).

    Returns
    -------
    matplotlib.animation.FuncAnimation
        Call ``plt.show()`` for interactive display or ``.save()`` to export.

    Example
    -------
    ::

        anim = animate_rotation(rotated_shapes)
        plt.show()
        # or: anim.save("rotation.gif", writer="pillow")
    """
    fig, ax = plt.subplots(figsize=(5, 5))

    # Fixed axis limits computed from all frames so the view doesn't jump
    all_pts = []
    for d in rotated_shape_dicts:
        all_pts += d["Profile"] + d["Midcurve"]
    arr = np.array(all_pts)
    margin = max((arr.max(axis=0) - arr.min(axis=0)).max() * 0.1, 2.0)
    ax.set_xlim(arr[:, 0].min() - margin, arr[:, 0].max() + margin)
    ax.set_ylim(arr[:, 1].min() - margin, arr[:, 1].max() + margin)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.3)
    title_text = ax.set_title(title)

    profile_artists:  list = []
    midcurve_artists: list = []

    def _clear_artists(artist_list: list) -> None:
        for a in artist_list:
            a.remove()
        artist_list.clear()

    def _update(frame_idx: int):
        _clear_artists(profile_artists)
        _clear_artists(midcurve_artists)

        dct = rotated_shape_dicts[frame_idx]
        _draw_brep_into(ax, dct["Profile_brep"],  "black", profile_artists)
        _draw_brep_into(ax, dct["Midcurve_brep"], "red",   midcurve_artists)
        title_text.set_text(dct.get("ShapeName", f"frame {frame_idx}"))
        return profile_artists + midcurve_artists + [title_text]

    anim = animation.FuncAnimation(
        fig, _update,
        frames=len(rotated_shape_dicts),
        interval=interval_ms,
        blit=False,   # blit=True breaks with dynamic remove()
    )
    return anim


def _draw_brep_into(ax: plt.Axes, brep: dict,
                    color: str, artist_list: list) -> None:
    """
    Draw a BRep onto *ax* and append all created artists to *artist_list*
    so the caller can remove them on the next animation frame.
    """
    points   = brep["Points"]
    lines    = brep["Lines"]
    segments = brep["Segments"]

    drawn_pts: set = set()
    for segment in segments:
        for line_idx in segment:
            i, j = lines[line_idx]
            ln, = ax.plot(
                [points[i][0], points[j][0]],
                [points[i][1], points[j][1]],
                color=color, linewidth=1.5,
            )
            artist_list.append(ln)
            for idx in (i, j):
                if idx not in drawn_pts:
                    sc = ax.scatter(points[idx][0], points[idx][1],
                                    color=color, s=22, zorder=4)
                    artist_list.append(sc)
                    drawn_pts.add(idx)


# ---------------------------------------------------------------------------
# Interactive HTML export (Plotly)
# ---------------------------------------------------------------------------

def export_plotly_html(
    shape_dicts: list,
    output_path: str = "midcurve_shapes.html",
) -> None:
    """
    Export an interactive Plotly figure to an HTML file.

    Each shape becomes a legend group with two traces — profile (black solid)
    and midcurve (red dashed).  Clicking a legend entry toggles both traces.
    Hovering shows point coordinates.

    Requires ``pip install plotly``.

    Parameters
    ----------
    shape_dicts:
        List of shape dicts.
    output_path:
        Destination HTML file path.
    """
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("Plotly is required: pip install plotly")

    fig = go.Figure()

    for dct in shape_dicts:
        name   = dct.get("ShapeName", "shape")
        p_brep = dct["Profile_brep"]
        m_brep = dct["Midcurve_brep"]

        # Build coordinate lists from BRep (None separates disconnected segments)
        p_xs, p_ys = _brep_to_xy_lists(p_brep)
        m_xs, m_ys = _brep_to_xy_lists(m_brep)

        fig.add_trace(go.Scatter(
            x=p_xs, y=p_ys,
            mode="lines+markers",
            name=f"{name} — profile",
            legendgroup=name,
            line=dict(color="black", width=1.5),
            marker=dict(size=5),
            hovertemplate="(%{x:.2f}, %{y:.2f})<extra>%{fullData.name}</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=m_xs, y=m_ys,
            mode="lines+markers",
            name=f"{name} — midcurve",
            legendgroup=name,
            line=dict(color="red", width=1.5, dash="dash"),
            marker=dict(size=5, symbol="x"),
            hovertemplate="(%{x:.2f}, %{y:.2f})<extra>%{fullData.name}</extra>",
        ))

    fig.update_layout(
        title="Midcurve Shape Explorer",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(constrain="domain"),
        template="simple_white",
        legend=dict(groupclick="togglegroup"),
    )
    fig.write_html(output_path)
    print(f"Interactive HTML written to: {output_path}")


def _brep_to_xy_lists(brep: dict) -> tuple[list, list]:
    """
    Convert a BRep dict to flat x/y lists with ``None`` separators between
    disconnected segments, suitable for a single Plotly ``Scatter`` trace.
    """
    points   = brep["Points"]
    lines    = brep["Lines"]
    segments = brep["Segments"]

    xs, ys = [], []
    for seg_idx, segment in enumerate(segments):
        if seg_idx > 0:
            xs.append(None)
            ys.append(None)
        for line_idx in segment:
            i, j = lines[line_idx]
            xs += [points[i][0], points[j][0], None]
            ys += [points[i][1], points[j][1], None]

    return xs, ys
