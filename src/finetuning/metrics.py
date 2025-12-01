import numpy as np
import json
import ast
from scipy.spatial.distance import directed_hausdorff
from typing import Dict, List, Tuple

class GeometricMetrics:
    @staticmethod
    def parse_brep(json_str):
        """Safely parses the B-Rep string/JSON."""
        try:
            if isinstance(json_str, str):
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    data = ast.literal_eval(json_str)
            else:
                data = json_str
                
            # Extract coordinates from points list
            points = np.array(data.get("Points", []))
            return data, points
        except Exception as e:
            return None, np.array([])

    @staticmethod
    def chamfer_distance(set_a, set_b):
        """Computes Chamfer Distance between two point clouds."""
        if len(set_a) == 0 or len(set_b) == 0:
            return float('inf')
            
        dist_matrix = np.linalg.norm(set_a[:, None] - set_b[None, :], axis=2)
        term1 = np.mean(np.min(dist_matrix, axis=1))
        term2 = np.mean(np.min(dist_matrix, axis=0))
        return term1 + term2

    @staticmethod
    def hausdorff_metric(pred_str, true_str):
        """Calculates Hausdorff distance between prediction and truth."""
        _, pred_points = GeometricMetrics.parse_brep(pred_str)
        _, true_points = GeometricMetrics.parse_brep(true_str)
        
        if len(pred_points) == 0 or len(true_points) == 0:
            return 1000.0
            
        d_ab = directed_hausdorff(pred_points, true_points)[0]
        d_ba = directed_hausdorff(true_points, pred_points)[0]
        return max(d_ab, d_ba)
    
    @staticmethod
    def mae_metric(pred_str, true_str):
        """Mean Absolute Error on coordinates"""
        _, pred_points = GeometricMetrics.parse_brep(pred_str)
        _, true_points = GeometricMetrics.parse_brep(true_str)
        
        if len(pred_points) == 0 or len(true_points) == 0:
            return 1000.0
        
        # If different number of points, use closest point matching
        if len(pred_points) != len(true_points):
            # Use Chamfer-style matching
            dist_matrix = np.linalg.norm(pred_points[:, None] - true_points[None, :], axis=2)
            min_dists = np.min(dist_matrix, axis=1)
            return np.mean(min_dists)
        
        return np.mean(np.abs(pred_points - true_points))
    
    @staticmethod
    def rmse_metric(pred_str, true_str):
        """Root Mean Square Error on coordinates"""
        _, pred_points = GeometricMetrics.parse_brep(pred_str)
        _, true_points = GeometricMetrics.parse_brep(true_str)
        
        if len(pred_points) == 0 or len(true_points) == 0:
            return 1000.0
        
        if len(pred_points) != len(true_points):
            dist_matrix = np.linalg.norm(pred_points[:, None] - true_points[None, :], axis=2)
            min_dists = np.min(dist_matrix, axis=1)
            return np.sqrt(np.mean(min_dists ** 2))
        
        return np.sqrt(np.mean((pred_points - true_points) ** 2))
    
    @staticmethod
    def topology_accuracy(pred_str, true_str):
        """Checks if topology matches (junction points)"""
        pred_data, _ = GeometricMetrics.parse_brep(pred_str)
        true_data, _ = GeometricMetrics.parse_brep(true_str)
        
        if not pred_data or not true_data:
            return 0.0
        
        # Count degree of each point (number of connections)
        def get_junction_count(data):
            lines = data.get("Lines", [])
            point_degree = {}
            for line in lines:
                for pt in line:
                    point_degree[pt] = point_degree.get(pt, 0) + 1
            # Junction points have degree > 2
            junctions = sum(1 for deg in point_degree.values() if deg > 2)
            return junctions
        
        pred_junctions = get_junction_count(pred_data)
        true_junctions = get_junction_count(true_data)
        
        if true_junctions == 0 and pred_junctions == 0:
            return 1.0
        if true_junctions == 0:
            return 0.0
        
        return 1.0 - abs(pred_junctions - true_junctions) / max(pred_junctions, true_junctions)
    
    @staticmethod
    def connectivity_score(pred_str):
        """Validates that predicted midcurve forms connected graph"""
        pred_data, pred_points = GeometricMetrics.parse_brep(pred_str)
        
        if not pred_data or len(pred_points) == 0:
            return 0.0
        
        lines = pred_data.get("Lines", [])
        if len(lines) == 0:
            return 0.0
        
        # Build adjacency list
        adj = {i: [] for i in range(len(pred_points))}
        for line in lines:
            if len(line) >= 2:
                p1, p2 = line[0], line[1]
                if p1 < len(pred_points) and p2 < len(pred_points):
                    adj[p1].append(p2)
                    adj[p2].append(p1)
        
        # BFS to find connected components
        visited = set()
        components = 0
        
        for start in range(len(pred_points)):
            if start not in visited:
                components += 1
                queue = [start]
                visited.add(start)
                
                while queue:
                    node = queue.pop(0)
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        
        # Fully connected = 1 component
        return 1.0 / components
    
    @staticmethod
    def vertex_count_accuracy(pred_str, true_str):
        """Compares number of vertices"""
        _, pred_points = GeometricMetrics.parse_brep(pred_str)
        _, true_points = GeometricMetrics.parse_brep(true_str)
        
        if len(true_points) == 0:
            return 0.0
        
        return 1.0 - abs(len(pred_points) - len(true_points)) / len(true_points)
    
    @staticmethod
    def json_validity(pred_str):
        """Checks if prediction is valid JSON"""
        pred_data, pred_points = GeometricMetrics.parse_brep(pred_str)
        return 1.0 if pred_data is not None else 0.0
    
    @staticmethod
    def coordinate_range_metric(pred_str, input_str):
        """Checks if predicted coordinates are in reasonable range"""
        _, pred_points = GeometricMetrics.parse_brep(pred_str)
        _, input_points = GeometricMetrics.parse_brep(input_str)
        
        if len(pred_points) == 0 or len(input_points) == 0:
            return 0.0
        
        # Get bounding boxes
        input_min = input_points.min(axis=0)
        input_max = input_points.max(axis=0)
        pred_min = pred_points.min(axis=0)
        pred_max = pred_points.max(axis=0)
        
        # Check if prediction is within 1.5x input range
        input_range = input_max - input_min
        pred_range = pred_max - pred_min
        
        # Penalize if prediction is way outside input bounds
        buffer = input_range * 0.5
        in_range = np.all(pred_min >= input_min - buffer) and \
                   np.all(pred_max <= input_max + buffer)
        
        return 1.0 if in_range else 0.0
    
    @staticmethod
    def symmetry_preservation(pred_str, input_str):
        """Checks if midcurve preserves input symmetries"""
        pred_data, pred_points = GeometricMetrics.parse_brep(pred_str)
        input_data, input_points = GeometricMetrics.parse_brep(input_str)
        
        if len(pred_points) == 0 or len(input_points) == 0:
            return 0.0
        
        # Simple check: compare coordinate std deviation
        # Symmetric shapes should have similar spread
        input_std = np.std(input_points, axis=0)
        pred_std = np.std(pred_points, axis=0)
        
        if np.any(input_std == 0):
            return 1.0
        
        ratio = np.abs(pred_std / input_std - 1.0)
        score = np.exp(-np.mean(ratio))
        
        return score
    
    @staticmethod
    def compute_all_metrics(pred_str, true_str, input_str=None):
        """Compute all metrics at once"""
        metrics = {
            "json_validity": GeometricMetrics.json_validity(pred_str),
            "hausdorff": GeometricMetrics.hausdorff_metric(pred_str, true_str),
            "chamfer": GeometricMetrics.chamfer_distance(
                *[GeometricMetrics.parse_brep(s)[1] for s in [pred_str, true_str]]
            ),
            "mae": GeometricMetrics.mae_metric(pred_str, true_str),
            "rmse": GeometricMetrics.rmse_metric(pred_str, true_str),
            "topology_accuracy": GeometricMetrics.topology_accuracy(pred_str, true_str),
            "connectivity_score": GeometricMetrics.connectivity_score(pred_str),
            "vertex_count_accuracy": GeometricMetrics.vertex_count_accuracy(pred_str, true_str),
        }
        
        if input_str:
            metrics["coordinate_range"] = GeometricMetrics.coordinate_range_metric(pred_str, input_str)
            metrics["symmetry_preservation"] = GeometricMetrics.symmetry_preservation(pred_str, input_str)
        
        # Combined score (weighted average of normalized metrics)
        # Lower is better for distance metrics, higher for accuracy metrics
        if metrics["json_validity"] > 0:
            distance_score = 1.0 / (1.0 + metrics["hausdorff"] / 10.0)
            topology_score = metrics["topology_accuracy"]
            connectivity_score = metrics["connectivity_score"]
            
            metrics["combined_score"] = (
                0.4 * distance_score + 
                0.3 * topology_score + 
                0.3 * connectivity_score
            )
        else:
            metrics["combined_score"] = 0.0
        
        return metrics
    
    @staticmethod
    def json_validity_rate(predictions_list: List[str]):
        """Percentage of predictions that parse as valid JSON"""
        valid_count = sum(1 for p in predictions_list 
                         if GeometricMetrics.json_validity(p) > 0)
        return valid_count / len(predictions_list) if predictions_list else 0.0
