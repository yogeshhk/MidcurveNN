import numpy as np
import json
import ast
from scipy.spatial.distance import directed_hausdorff

class GeometricMetrics:
    @staticmethod
    def parse_brep(json_str):
        """Safely parses the B-Rep string/JSON."""
        try:
            # Handle potential single quotes or python-style dict strings
            if isinstance(json_str, str):
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    data = ast.literal_eval(json_str)
            else:
                data = json_str
                
            # Extract coordinates from points list
            points = np.array(data.get("Points", []))
            return points
        except Exception as e:
            return np.array([])

    @staticmethod
    def chamfer_distance(set_a, set_b):
        """Computes Chamfer Distance between two point clouds."""
        if len(set_a) == 0 or len(set_b) == 0:
            return float('inf')
            
        # Euclidean distance matrix
        dist_matrix = np.linalg.norm(set_a[:, None] - set_b[None, :], axis=2)
        
        # Average minimum distance from A to B and B to A
        term1 = np.mean(np.min(dist_matrix, axis=1))
        term2 = np.mean(np.min(dist_matrix, axis=0))
        return term1 + term2

    @staticmethod
    def hausdorff_metric(pred_str, true_str):
        """Calculates Hausdorff distance between prediction and truth."""
        pred_points = GeometricMetrics.parse_brep(pred_str)
        true_points = GeometricMetrics.parse_brep(true_str)
        
        if len(pred_points) == 0 or len(true_points) == 0:
            return 1000.0 # High penalty for invalid JSON
            
        d_ab = directed_hausdorff(pred_points, true_points)[0]
        d_ba = directed_hausdorff(true_points, pred_points)[0]
        return max(d_ab, d_ba)