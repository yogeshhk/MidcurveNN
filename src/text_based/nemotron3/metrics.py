"""
Re-exports GeometricMetrics from the sibling finetuning/ module.
Provides a minimal inline fallback so this module is importable
even without scipy or a GPU.
"""
import os
import sys

_HERE       = os.path.dirname(os.path.abspath(__file__))
_FINETUNING = os.path.realpath(os.path.join(_HERE, "..", "finetuning"))

if os.path.isdir(_FINETUNING) and _FINETUNING not in sys.path:
    sys.path.insert(0, _FINETUNING)

try:
    from metrics import GeometricMetrics  # noqa: F401  (re-export)
except ImportError:
    import json
    import ast
    import numpy as np

    class GeometricMetrics:
        @staticmethod
        def parse_brep(s):
            try:
                try:
                    data = json.loads(s) if isinstance(s, str) else s
                except (json.JSONDecodeError, ValueError):
                    data = ast.literal_eval(s)
                if isinstance(data, str):
                    data = json.loads(data)
                if not isinstance(data, dict):
                    return None, np.array([])
                raw_pts = data.get("Points", [])
                pts     = np.array(raw_pts, dtype=float)
                # Ensure shape is (N, 2); reshape flat lists like [x,y,x,y,...]
                if pts.ndim == 1:
                    if len(pts) >= 2 and len(pts) % 2 == 0:
                        pts = pts.reshape(-1, 2)
                    else:
                        pts = np.array([])
                return data, pts
            except Exception:
                return None, np.array([])

        @staticmethod
        def chamfer_distance(set_a, set_b):
            try:
                a = np.asarray(set_a, float)
                b = np.asarray(set_b, float)
                if len(a) == 0 or len(b) == 0 or a.ndim != 2 or b.ndim != 2:
                    return float("inf")
                d = np.linalg.norm(a[:, None] - b[None, :], axis=2)
                return float(np.mean(np.min(d, axis=1)) + np.mean(np.min(d, axis=0)))
            except Exception:
                return float("inf")

        @staticmethod
        def hausdorff_metric(pred, true):
            _, a = GeometricMetrics.parse_brep(pred)
            _, b = GeometricMetrics.parse_brep(true)
            if len(a) == 0 or len(b) == 0 or a.ndim != 2 or b.ndim != 2:
                return 1000.0
            try:
                from scipy.spatial.distance import directed_hausdorff
                return float(max(
                    directed_hausdorff(a, b)[0],
                    directed_hausdorff(b, a)[0],
                ))
            except Exception:
                try:
                    d = np.linalg.norm(a[:, None] - b[None, :], axis=2)
                    return float(max(np.min(d, axis=1).max(), np.min(d, axis=0).max()))
                except Exception:
                    return 1000.0

        @staticmethod
        def connectivity_score(pred_str):
            data, pts = GeometricMetrics.parse_brep(pred_str)
            if data is None or len(pts) == 0:
                return 0.0
            lines = data.get("Lines", [])
            adj   = {i: [] for i in range(len(pts))}
            for ln in lines:
                if len(ln) >= 2 and ln[0] < len(pts) and ln[1] < len(pts):
                    adj[ln[0]].append(ln[1])
                    adj[ln[1]].append(ln[0])
            visited, q = {0}, [0]
            while q:
                n = q.pop()
                for nb in adj[n]:
                    if nb not in visited:
                        visited.add(nb)
                        q.append(nb)
            comps = sum(1 for i in range(len(pts)) if i not in visited) + 1
            return 1.0 / comps

        @staticmethod
        def topology_accuracy(pred_str, true_str):
            def _junctions(d):
                deg = {}
                for ln in d.get("Lines", []):
                    for p in ln:
                        deg[p] = deg.get(p, 0) + 1
                return sum(1 for v in deg.values() if v > 2)

            pred_d, _ = GeometricMetrics.parse_brep(pred_str)
            true_d, _ = GeometricMetrics.parse_brep(true_str)
            if not pred_d or not true_d:
                return 0.0
            pj, tj = _junctions(pred_d), _junctions(true_d)
            if tj == 0 and pj == 0:
                return 1.0
            if tj == 0:
                return 0.0
            return 1.0 - abs(pj - tj) / max(pj, tj)

        @staticmethod
        def json_validity(pred_str):
            d, _ = GeometricMetrics.parse_brep(pred_str)
            return 1.0 if d is not None else 0.0

        @staticmethod
        def compute_all_metrics(pred_str, true_str, input_str=None):
            _, pa = GeometricMetrics.parse_brep(pred_str)
            _, ta = GeometricMetrics.parse_brep(true_str)
            m = {
                "json_validity":      GeometricMetrics.json_validity(pred_str),
                "hausdorff":          GeometricMetrics.hausdorff_metric(pred_str, true_str),
                "chamfer":            GeometricMetrics.chamfer_distance(pa, ta),
                "topology_accuracy":  GeometricMetrics.topology_accuracy(pred_str, true_str),
                "connectivity_score": GeometricMetrics.connectivity_score(pred_str),
            }
            if m["json_validity"] > 0:
                m["combined_score"] = (
                    0.4 * (1.0 / (1.0 + m["hausdorff"] / 10.0))
                    + 0.3 * m["topology_accuracy"]
                    + 0.3 * m["connectivity_score"]
                )
            else:
                m["combined_score"] = 0.0
            return m
