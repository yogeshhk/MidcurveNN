"""
prepare_plots.py — Visualization utilities for the Midcurve Dataset Pipeline.

Provides three levels of visualization:

1. **Single-pair plots** — overlay profile and midcurve on one axis for
   quick inspection.
2. **Grid plots** — display many shapes in a single figure for dataset-wide
   quality checks.
3. **BRep plots** — resolve BRep index references back to coordinates and
   render the topological structure.
4. **Comparison plots** — place profile, actual midcurve, and predicted
   midcurve side-by-side (or overlaid) for model evaluation.
5. **Animation** — cycle through a rotation sequence to verify midcurve
   tracking.
"""

from __future__ import annotations

import math
from typing import Sequence

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------

def _draw_lines(ax: plt.Axes, lines: list, color: str = "black",
                linewidth: float = 1.5, label: str | None = None) -> None:
    """
    Draw a list of ``[[x1,y1],[x2,y2]]`` line segments onto *ax*.

    The *label* is attached only to the first segment so that
    ``ax.legend()`` shows one entry per series.
    """
    for i, seg in enumerate(lines):
        a = np.asarray(seg)
        ax.plot(a[:, 0], a[:, 1], color=color, linewidth=linewidth,
                label=(label if i == 0 else None))


def _draw_point_sequence(ax: plt.Axes, points: list, color: str = "black",
                         close: bool = False, linestyle: str = "solid",
                         linewidth: float = 1.5, label: str | None = None) -> None:
    """
    Draw a sequence of ``(x, y)`` points as a connected polyline on *ax*.

    Parameters
    ----------
    close:
        If ``True``, add an extra segment connecting the last point back to
        the first (for closed polygons).
    label:
        Legend label.
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    if close:
        xs.append(xs[0])
        ys.append(ys[0])
    ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=linewidth,
            label=label)
    ax.scatter(xs, ys, color=color, s=20, zorder=3)


# ---------------------------------------------------------------------------
# BRep-aware plots
# ---------------------------------------------------------------------------

def _resolve_brep_segments(segments: list, lines: list, points: list) -> list:
    """
    Resolve BRep index references to actual coordinate pairs.

    Parameters
    ----------
    segments:
        List of segment definitions (each is a list of line indices).
    lines:
        List of line definitions (each is a pair of point indices).
    points:
        List of ``(x, y)`` coordinate tuples.

    Returns
    -------
    list of lists of ``(x, y)`` coordinate pairs.
    """
    resolved = []
    for segment in segments:
        for line_idx in segment:
            pt_a, pt_b = lines[line_idx]
            resolved.append([points[pt_a], points[pt_b]])
    return resolved


def plot_breps(shapes_brep_dict_list: list) -> None:
    """
    Display each BRep shape dict in its own figure.

    Profile edges are drawn in black (circle markers), midcurve edges in
    red (cross markers).

    Parameters
    ----------
    shapes_brep_dict_list:
        List of BRep dicts with keys ``Profile``, ``Profile_brep``,
        ``Midcurve``, ``Midcurve_brep``, and optionally ``ShapeName``.
    """
    for dct in shapes_brep_dict_list:
        fig, ax = plt.subplots(figsize=(5, 5))

        profile_pts  = dct["Profile"]
        profile_brep = dct["Profile_brep"]
        profile_lines = _resolve_brep_segments(
            profile_brep["Segments"], profile_brep["Lines"], profile_pts
        )
        _draw_lines(ax, profile_lines, color="black", label="Profile")
        ax.scatter([p[0] for p in profile_pts],
                   [p[1] for p in profile_pts],
                   color="black", marker="o", s=30, zorder=3)

        midcurve_pts  = dct["Midcurve"]
        midcurve_brep = dct["Midcurve_brep"]
        midcurve_lines = _resolve_brep_segments(
            midcurve_brep["Segments"], midcurve_brep["Lines"], midcurve_pts
        )
        _draw_lines(ax, midcurve_lines, color="red", label="Midcurve")
        ax.scatter([p[0] for p in midcurve_pts],
                   [p[1] for p in midcurve_pts],
                   color="red", marker="x", s=40, zorder=3)

        ax.set_aspect("equal")
        ax.grid(True, linewidth=0.4)
        ax.legend(fontsize=9)
        ax.set_title(dct.get("ShapeName", "Shape"))
        plt.tight_layout()
        plt.show()


# ---------------------------------------------------------------------------
# Line-list plots
# ---------------------------------------------------------------------------

def plot_lines(lines: list, color: str = "black", ax: plt.Axes | None = None,
               label: str | None = None) -> plt.Axes:
    """
    Plot a list of ``[[x1,y1],[x2,y2]]`` line segments.

    Parameters
    ----------
    lines:
        Line segments to draw.
    color:
        Line colour.
    ax:
        Matplotlib axes.  A new figure/axes is created if ``None``.
    label:
        Optional legend label.

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        _, ax = plt.subplots()
    _draw_lines(ax, lines, color=color, label=label)
    ax.set_aspect("equal")
    return ax


def plot_list_of_lines(
    list_of_lines: list,
    names: Sequence[str],
    colors: str | list = "black",
    figsize: tuple = (15, 5),
) -> tuple[plt.Figure, list]:
    """
    Plot each set of line segments in its own subplot.

    Parameters
    ----------
    list_of_lines:
        Each element is a list of ``[[x1,y1],[x2,y2]]`` segments representing
        one figure.
    names:
        Title for each subplot.
    colors:
        A single colour string or a list with one colour per figure.
    figsize:
        Overall figure dimensions ``(width, height)`` in inches.

    Returns
    -------
    (fig, axes)
    """
    if len(list_of_lines) != len(names):
        raise ValueError("'list_of_lines' and 'names' must have the same length.")

    if isinstance(colors, str):
        color_list = [colors] * len(list_of_lines)
    else:
        color_list = list(colors)
        while len(color_list) < len(list_of_lines):
            color_list += color_list
        color_list = color_list[: len(list_of_lines)]

    fig, axes = plt.subplots(1, len(list_of_lines), figsize=figsize)
    if len(list_of_lines) == 1:
        axes = [axes]

    for ax, lines, name, color in zip(axes, list_of_lines, names, color_list):
        _draw_lines(ax, lines, color=color)
        ax.set_title(name)
        ax.set_aspect("equal")
        ax.grid(True, linewidth=0.4)

    plt.tight_layout()
    return fig, axes


# ---------------------------------------------------------------------------
# Profile + Midcurve overlay
# ---------------------------------------------------------------------------

def plot_profile_midcurve_overlay(
    profile_lines: list,
    midcurve_lines: list,
    title: str = "",
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """
    Draw profile (black) and midcurve (red) as overlaid line segments on
    the same axes.

    Parameters
    ----------
    profile_lines:
        Profile as ``[[x1,y1],[x2,y2]]`` segments.
    midcurve_lines:
        Midcurve as ``[[x1,y1],[x2,y2]]`` segments.
    title:
        Plot title.
    ax:
        Axes to draw on; a new figure/axes is created if ``None``.

    Returns
    -------
    plt.Axes
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(5, 5))
    _draw_lines(ax, profile_lines,  color="black", linewidth=1.5, label="Profile")
    _draw_lines(ax, midcurve_lines, color="red",   linewidth=1.5,
                label="Midcurve")
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.4)
    ax.legend(fontsize=9)
    if title:
        ax.set_title(title)
    return ax


# ---------------------------------------------------------------------------
# Model evaluation: profile vs actual vs predicted
# ---------------------------------------------------------------------------

def plot_prediction_comparison(
    profile_lines: list,
    actual_midcurve_lines: list,
    predicted_midcurve_lines: list,
    title: str = "",
    figsize: tuple = (14, 5),
) -> tuple[plt.Figure, list]:
    """
    Side-by-side comparison of profile, ground-truth midcurve, and model
    prediction.

    Also draws an overlay panel (right) showing actual vs predicted together
    for close inspection.

    Parameters
    ----------
    profile_lines:
        Profile line segments.
    actual_midcurve_lines:
        Ground-truth midcurve segments.
    predicted_midcurve_lines:
        Model-predicted midcurve segments.
    title:
        Overall figure title.
    figsize:
        Figure size.

    Returns
    -------
    (fig, axes)
    """
    fig, axes = plt.subplots(1, 4, figsize=figsize)

    panels = [
        (axes[0], profile_lines,           "red",   "Profile"),
        (axes[1], actual_midcurve_lines,   "blue",  "Actual midcurve"),
        (axes[2], predicted_midcurve_lines,"green", "Predicted midcurve"),
    ]
    for ax, lines, color, label in panels:
        _draw_lines(ax, lines, color=color)
        ax.set_title(label, fontsize=10)
        ax.set_aspect("equal")
        ax.grid(True, linewidth=0.4)

    # Overlay panel: actual vs predicted together
    _draw_lines(axes[3], actual_midcurve_lines,    color="blue",  label="Actual",
                linewidth=2.0)
    _draw_lines(axes[3], predicted_midcurve_lines, color="green", label="Predicted",
                linewidth=1.5)
    axes[3].set_title("Overlay", fontsize=10)
    axes[3].set_aspect("equal")
    axes[3].grid(True, linewidth=0.4)
    axes[3].legend(fontsize=8)

    if title:
        fig.suptitle(title, fontsize=12, y=1.02)

    plt.tight_layout()
    return fig, axes


# ---------------------------------------------------------------------------
# Grid view for dataset quality checks
# ---------------------------------------------------------------------------

def plot_shape_grid(
    shape_dicts: list,
    n_cols: int = 5,
    figsize_per_cell: tuple = (3, 3),
    profile_color: str = "black",
    midcurve_color: str = "red",
    title: str = "Shape dataset overview",
) -> plt.Figure:
    """
    Display a grid of shapes — one subplot per shape — for dataset-wide
    quality inspection.

    Parameters
    ----------
    shape_dicts:
        List of shape dicts with ``Profile``, ``Midcurve``, and
        optionally ``ShapeName``.
    n_cols:
        Number of subplot columns.
    figsize_per_cell:
        ``(width, height)`` in inches for each individual subplot.
    profile_color:
        Colour for profile edges.
    midcurve_color:
        Colour for midcurve edges.
    title:
        Overall figure title.

    Returns
    -------
    plt.Figure
    """
    n = len(shape_dicts)
    n_rows = math.ceil(n / n_cols)
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(figsize_per_cell[0] * n_cols, figsize_per_cell[1] * n_rows),
    )
    axes_flat = np.array(axes).flatten()

    for i, dct in enumerate(shape_dicts):
        ax = axes_flat[i]
        _draw_point_sequence(ax, dct["Profile"],  color=profile_color,
                             close=True,  linestyle="solid")
        _draw_point_sequence(ax, dct["Midcurve"], color=midcurve_color,
                             close=False, linestyle="dashed")
        ax.set_aspect("equal")
        ax.grid(True, linewidth=0.3)
        ax.tick_params(labelsize=6)
        ax.set_title(dct.get("ShapeName", f"Shape {i}"), fontsize=7)

    # Hide unused axes
    for ax in axes_flat[n:]:
        ax.set_visible(False)

    fig.suptitle(title, fontsize=12)
    plt.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Rotation animation
# ---------------------------------------------------------------------------

def animate_rotation(
    shape_dicts_rotated: list,
    interval_ms: int = 50,
    profile_color: str = "black",
    midcurve_color: str = "red",
    title: str = "Rotation sequence",
) -> animation.FuncAnimation:
    """
    Animate a sequence of rotated shape dicts to verify that the midcurve
    tracks correctly through the full rotation.

    Parameters
    ----------
    shape_dicts_rotated:
        Ordered list of shape dicts, each representing one rotation step.
    interval_ms:
        Delay between frames in milliseconds.
    profile_color:
        Colour for the profile polygon.
    midcurve_color:
        Colour for the midcurve skeleton.
    title:
        Figure title (updated each frame with the shape name).

    Returns
    -------
    matplotlib.animation.FuncAnimation
        Call ``plt.show()`` or ``.save()`` on the returned object.

    Example
    -------
    ::

        anim = animate_rotation(rotated_shapes)
        plt.show()           # interactive
        anim.save("rot.gif") # save to file
    """
    fig, ax = plt.subplots(figsize=(5, 5))

    # Determine axis limits from all frames
    all_pts = [p for d in shape_dicts_rotated
               for p in d["Profile"] + d["Midcurve"]]
    all_pts_arr = np.array(all_pts)
    margin = 5
    xlim = (all_pts_arr[:, 0].min() - margin, all_pts_arr[:, 0].max() + margin)
    ylim = (all_pts_arr[:, 1].min() - margin, all_pts_arr[:, 1].max() + margin)

    (profile_line,)  = ax.plot([], [], color=profile_color,  linewidth=1.5)
    (midcurve_line,) = ax.plot([], [], color=midcurve_color, linewidth=1.5,
                               linestyle="dashed")
    profile_scat  = ax.scatter([], [], color=profile_color,  s=20, zorder=3)
    midcurve_scat = ax.scatter([], [], color=midcurve_color, s=25, marker="x",
                               zorder=3)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_aspect("equal")
    ax.grid(True, linewidth=0.4)
    title_obj = ax.set_title(title)

    def _update(frame_idx: int):
        dct = shape_dicts_rotated[frame_idx]

        # Profile (closed)
        ppts = dct["Profile"] + [dct["Profile"][0]]
        px   = [p[0] for p in ppts]
        py   = [p[1] for p in ppts]
        profile_line.set_data(px, py)
        profile_scat.set_offsets(np.c_[px[:-1], py[:-1]])

        # Midcurve (open)
        mpts = dct["Midcurve"]
        mx   = [p[0] for p in mpts]
        my   = [p[1] for p in mpts]
        midcurve_line.set_data(mx, my)
        midcurve_scat.set_offsets(np.c_[mx, my])

        title_obj.set_text(dct.get("ShapeName", f"Frame {frame_idx}"))
        return profile_line, midcurve_line, profile_scat, midcurve_scat, title_obj

    anim = animation.FuncAnimation(
        fig,
        _update,
        frames=len(shape_dicts_rotated),
        interval=interval_ms,
        blit=True,
    )
    return anim


# ---------------------------------------------------------------------------
# Interactive HTML export (Plotly)
# ---------------------------------------------------------------------------

def export_plotly_html(
    shape_dicts: list,
    output_path: str = "midcurve_shapes.html",
) -> None:
    """
    Export an interactive Plotly figure to an HTML file.

    Each shape becomes a pair of traces (profile and midcurve) grouped into
    one Plotly ``legendgroup``.  Hovering over any point shows its coordinates.

    Requires: ``pip install plotly``

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
        raise ImportError(
            "Plotly is required for HTML export: pip install plotly"
        )

    fig = go.Figure()
    for dct in shape_dicts:
        name = dct.get("ShapeName", "shape")

        profile = dct["Profile"] + [dct["Profile"][0]]   # close polygon
        px = [p[0] for p in profile]
        py = [p[1] for p in profile]

        midcurve = dct["Midcurve"]
        mx = [p[0] for p in midcurve]
        my = [p[1] for p in midcurve]

        fig.add_trace(go.Scatter(
            x=px, y=py,
            mode="lines+markers",
            name=f"{name} — profile",
            legendgroup=name,
            line=dict(color="black", width=1.5),
            marker=dict(size=5),
            hovertemplate="(%{x}, %{y})<extra>%{fullData.name}</extra>",
        ))
        fig.add_trace(go.Scatter(
            x=mx, y=my,
            mode="lines+markers",
            name=f"{name} — midcurve",
            legendgroup=name,
            line=dict(color="red", width=1.5, dash="dash"),
            marker=dict(size=5, symbol="x"),
            hovertemplate="(%{x}, %{y})<extra>%{fullData.name}</extra>",
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


# ---------------------------------------------------------------------------
# Demo / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    profile = [
        ((-5.65, -4.26), (-10.6, -3.56)),
        ((-10.6, -3.56), (-14.08, -28.32)),
        ((-14.08, -28.32), (-38.83, -24.84)),
        ((-38.83, -24.84), (-39.53, -29.79)),
        ((-39.53, -29.79), (-9.82, -33.96)),
        ((-9.82, -33.96), (-5.65, -4.26)),
    ]
    actual_midcurve = [
        ((-8.12, -3.91), (-11.95, -31.14)),
        ((-11.95, -31.14), (-39.18, -27.31)),
    ]
    predicted_midcurve = [
        ((-8.13, -3.91), (-11.95, -31.14)),
        ((-11.95, -31.14), (-39.18, -27.32)),
    ]

    fig, axes = plot_prediction_comparison(
        profile, actual_midcurve, predicted_midcurve,
        title="Example prediction",
    )
    plt.show()
