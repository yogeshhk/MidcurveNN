"""
graph_dataset.py  –  MidcurveNN Phase II
=========================================
Loads .dat (profile polygon) and .mid (midcurve polyline) file pairs,
converts them into PyTorch Geometric Data objects, and augments the
dataset with geometric transformations (rotate, scale, translate, mirror).

Graph Construction
------------------
Profile  : closed polygon  → ring of edges  (last node → first node closed)
Midcurve : open/branched polyline → chain edges  (nodes listed in order,
           consecutive pairs are connected; branch points appear multiple times)

Node features  : normalised (x, y) coordinates  → dim 2
Edge features  : Euclidean length of segment    → dim 1
"""

import os
import math
import numpy as np
import torch
from torch_geometric.data import Data, Dataset


# ---------------------------------------------------------------------------
# File I/O helpers
# ---------------------------------------------------------------------------

def read_point_file(filepath: str):
    """Read a .dat or .mid file → list of (x, y) tuples."""
    points = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                x, y = map(float, line.split())
                points.append((x, y))
    return points


def _build_polygon_edges(n: int):
    """Closed polygon: 0-1, 1-2, …, (n-1)-0."""
    src = list(range(n)) + list(range(1, n)) + [0]
    dst = list(range(1, n)) + [0] + list(range(n))
    # Undirected: both directions
    src_ud = list(range(n)) + [i % n for i in range(1, n + 1)]
    dst_ud = [i % n for i in range(1, n + 1)] + list(range(n))
    return torch.tensor(src_ud, dtype=torch.long), torch.tensor(dst_ud, dtype=torch.long)


def _build_polyline_edges(points):
    """
    Open/branched polyline: consecutive listed points form edges.
    Unique node index based on coordinates; shared coords = branch node.
    Returns unique_points, edge_index (2 x E), undirected.
    """
    coord_to_idx = {}
    unique_pts = []
    node_indices = []
    for pt in points:
        key = (round(pt[0], 6), round(pt[1], 6))
        if key not in coord_to_idx:
            coord_to_idx[key] = len(unique_pts)
            unique_pts.append(pt)
        node_indices.append(coord_to_idx[key])

    src, dst = [], []
    for i in range(len(node_indices) - 1):
        u, v = node_indices[i], node_indices[i + 1]
        if u != v:          # skip self-loops (degenerate repeated coord)
            src += [u, v]
            dst += [v, u]

    edge_index = torch.tensor([src, dst], dtype=torch.long)
    return unique_pts, edge_index


def _node_tensor(points):
    return torch.tensor(points, dtype=torch.float)


def _edge_attr(x: torch.Tensor, edge_index: torch.Tensor):
    """Edge feature = Euclidean length (scalar)."""
    if edge_index.numel() == 0:
        return torch.zeros((0, 1), dtype=torch.float)
    row, col = edge_index
    diff = x[row] - x[col]
    lengths = diff.norm(dim=1, keepdim=True)
    return lengths


def _normalise(x: torch.Tensor):
    """Centre + scale so coords fit roughly in [-1, 1]."""
    centre = x.mean(dim=0)
    x = x - centre
    scale = x.abs().max().clamp(min=1e-6)
    x = x / scale
    return x, centre, scale


# ---------------------------------------------------------------------------
# Single sample → PyG Data
# ---------------------------------------------------------------------------

def build_graph_pair(profile_pts, midcurve_pts, label=""):
    """
    Returns a PyG Data object that bundles profile graph (input)
    and midcurve graph (target) into one object.

    Fields
    ------
    x            : profile node features  [N_p, 2]
    edge_index   : profile edges          [2, E_p]
    edge_attr    : profile edge lengths   [E_p, 1]
    y            : midcurve node coords   [N_m, 2]
    mid_edge_index : midcurve edges       [2, E_m]
    label        : str name
    """
    # --- profile ---
    n_p = len(profile_pts)
    x_raw = _node_tensor(profile_pts)
    ei_p_src, ei_p_dst = _build_polygon_edges(n_p)
    edge_index_p = torch.stack([ei_p_src, ei_p_dst], dim=0)

    # normalise profile; apply same transform to midcurve for consistency
    centre = x_raw.mean(dim=0)
    scale = (x_raw - centre).abs().max().clamp(min=1e-6)
    x_norm = (x_raw - centre) / scale

    ea_p = _edge_attr(x_norm, edge_index_p)

    # --- midcurve ---
    unique_mid_pts, edge_index_m = _build_polyline_edges(midcurve_pts)
    y_raw = _node_tensor(unique_mid_pts)
    y_norm = (y_raw - centre) / scale   # same coordinate system
    ea_m = _edge_attr(y_norm, edge_index_m)

    return Data(
        x=x_norm,                    # [N_p, 2]  profile nodes (normalised)
        edge_index=edge_index_p,     # [2, E_p]  profile edges
        edge_attr=ea_p,              # [E_p, 1]  profile edge lengths
        y=y_norm,                    # [N_m, 2]  midcurve nodes (normalised)
        mid_edge_index=edge_index_m, # [2, E_m]  midcurve edges
        mid_edge_attr=ea_m,          # [E_m, 1]  midcurve edge lengths
        num_profile_nodes=torch.tensor(n_p),
        num_mid_nodes=torch.tensor(len(unique_mid_pts)),
        centre=centre,
        scale=scale,
        label=label,
    )


# ---------------------------------------------------------------------------
# Geometric augmentation helpers  (operate on raw point lists)
# ---------------------------------------------------------------------------

def _rotate(pts, theta_deg):
    th = math.radians(theta_deg)
    c, s = math.cos(th), math.sin(th)
    return [(round(c * x - s * y, 4), round(s * x + c * y, 4)) for x, y in pts]


def _scale(pts, factor):
    return [(round(x * factor, 4), round(y * factor, 4)) for x, y in pts]


def _translate(pts, dx, dy):
    return [(round(x + dx, 4), round(y + dy, 4)) for x, y in pts]


def _mirror_x(pts):   # flip over X-axis
    return [(round(x, 4), round(-y, 4)) for x, y in pts]


def _mirror_y(pts):   # flip over Y-axis
    return [( round(-x, 4), round(y, 4)) for x, y in pts]


def augment_pair(profile_pts, midcurve_pts, name):
    """
    Yield (profile_pts, midcurve_pts, variant_label) for the original
    sample plus rotations, scales, translations, mirrors.
    Both profile and midcurve receive identical transforms.
    """
    yield profile_pts, midcurve_pts, name

    # Rotations: 30° steps
    for angle in range(30, 360, 30):
        yield (_rotate(profile_pts, angle),
               _rotate(midcurve_pts, angle),
               f"{name}_rot{angle}")

    # Uniform scales
    for factor in [0.5, 0.75, 1.5, 2.0]:
        yield (_scale(profile_pts, factor),
               _scale(midcurve_pts, factor),
               f"{name}_scale{factor}")

    # Translations
    for dx in [-20, -10, 10, 20]:
        for dy in [-20, -10, 10, 20]:
            yield (_translate(profile_pts, dx, dy),
                   _translate(midcurve_pts, dx, dy),
                   f"{name}_t{dx}_{dy}")

    # Mirrors
    yield _mirror_x(profile_pts), _mirror_x(midcurve_pts), f"{name}_mirX"
    yield _mirror_y(profile_pts), _mirror_y(midcurve_pts), f"{name}_mirY"


# ---------------------------------------------------------------------------
# Dataset class
# ---------------------------------------------------------------------------

class MidcurveGraphDataset(Dataset):
    """
    PyTorch Geometric Dataset for the MidcurveNN Phase II task.

    Parameters
    ----------
    raw_folder : str
        Folder containing .dat and .mid file pairs (e.g. I.dat + I.mid).
    augment : bool
        If True, geometric augmentations are applied to multiply data.
    """

    def __init__(self, raw_folder: str, augment: bool = True):
        super().__init__()
        self._samples = []          # list of Data objects
        self._load(raw_folder, augment)

    def _load(self, folder, augment):
        shape_names = set()
        for fname in os.listdir(folder):
            if fname.endswith(".dat"):
                shape_names.add(os.path.splitext(fname)[0])

        for name in sorted(shape_names):
            dat_path = os.path.join(folder, f"{name}.dat")
            mid_path = os.path.join(folder, f"{name}.mid")
            if not os.path.exists(mid_path):
                print(f"[WARN] No .mid for {name}, skipping.")
                continue

            profile_pts  = read_point_file(dat_path)
            midcurve_pts = read_point_file(mid_path)

            if augment:
                for p_pts, m_pts, label in augment_pair(profile_pts, midcurve_pts, name):
                    self._samples.append(build_graph_pair(p_pts, m_pts, label))
            else:
                self._samples.append(build_graph_pair(profile_pts, midcurve_pts, name))

        print(f"[Dataset] Loaded {len(self._samples)} samples "
              f"from {len(shape_names)} shapes (augment={augment}).")

    def len(self):
        return len(self._samples)

    def get(self, idx):
        return self._samples[idx]


# ---------------------------------------------------------------------------
# Quick smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ds = MidcurveGraphDataset("data/raw", augment=True)
    sample = ds.get(0)
    print(sample)
    print("Profile nodes :", sample.x.shape)
    print("Profile edges :", sample.edge_index.shape)
    print("Midcurve nodes:", sample.y.shape)
    print("Midcurve edges:", sample.mid_edge_index.shape)
