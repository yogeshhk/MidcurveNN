import json
import numpy as np
import ast
from typing import Tuple, Dict, List
import pandas as pd

class DataValidator:
    """Validates geometric data quality before training"""
    
    @staticmethod
    def parse_brep_safe(json_str) -> Tuple[bool, Dict]:
        """Safely parse B-Rep with error handling"""
        try:
            if isinstance(json_str, str):
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    data = ast.literal_eval(json_str)
            else:
                data = json_str
            
            # Check required keys
            if not all(k in data for k in ["Points", "Lines", "Segments"]):
                return False, {}
            
            return True, data
        except Exception as e:
            return False, {}
    
    @staticmethod
    def is_closed_profile(data: Dict) -> bool:
        """Check if profile forms closed polygon"""
        if not data or "Lines" not in data:
            return False
        
        lines = data["Lines"]
        if len(lines) < 3:
            return False
        
        # Build connectivity graph
        point_connections = {}
        for line in lines:
            p1, p2 = line[0], line[1]
            point_connections[p1] = point_connections.get(p1, 0) + 1
            point_connections[p2] = point_connections.get(p2, 0) + 1
        
        # For closed polygon, each point should connect to exactly 2 lines
        return all(count == 2 for count in point_connections.values())
    
    @staticmethod
    def is_connected_graph(data: Dict) -> bool:
        """Check if graph is fully connected"""
        if not data or "Lines" not in data or "Points" not in data:
            return False
        
        lines = data["Lines"]
        points = data["Points"]
        
        if len(lines) == 0:
            return False
        
        # Build adjacency list
        adj = {i: [] for i in range(len(points))}
        for line in lines:
            p1, p2 = line[0], line[1]
            adj[p1].append(p2)
            adj[p2].append(p1)
        
        # BFS to check connectivity
        visited = set()
        queue = [0]
        visited.add(0)
        
        while queue:
            node = queue.pop(0)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # Check if all points with connections are visited
        points_with_connections = set()
        for line in lines:
            points_with_connections.add(line[0])
            points_with_connections.add(line[1])
        
        return len(visited) == len(points_with_connections)
    
    @staticmethod
    def get_coordinate_stats(data: Dict) -> Dict:
        """Get statistics about coordinates"""
        if not data or "Points" not in data:
            return {}
        
        points = np.array(data["Points"])
        return {
            "min": points.min(axis=0).tolist(),
            "max": points.max(axis=0).tolist(),
            "mean": points.mean(axis=0).tolist(),
            "std": points.std(axis=0).tolist(),
            "range": (points.max(axis=0) - points.min(axis=0)).tolist()
        }
    
    @staticmethod
    def detect_duplicate_points(data: Dict, tolerance: float = 1e-6) -> List[int]:
        """Find duplicate points within tolerance"""
        if not data or "Points" not in data:
            return []
        
        points = np.array(data["Points"])
        duplicates = []
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if np.linalg.norm(points[i] - points[j]) < tolerance:
                    duplicates.append((i, j))
        
        return duplicates
    
    @staticmethod
    def validate_dataset(file_path: str) -> Dict:
        """Validate entire dataset and return statistics"""
        df = pd.read_csv(file_path)
        
        stats = {
            "total_samples": len(df),
            "valid_profile_parse": 0,
            "valid_midcurve_parse": 0,
            "closed_profiles": 0,
            "connected_midcurves": 0,
            "profile_coord_ranges": [],
            "midcurve_coord_ranges": [],
            "invalid_samples": []
        }
        
        for idx, row in df.iterrows():
            # Validate profile
            profile_valid, profile_data = DataValidator.parse_brep_safe(row['Profile_brep'])
            if profile_valid:
                stats["valid_profile_parse"] += 1
                if DataValidator.is_closed_profile(profile_data):
                    stats["closed_profiles"] += 1
                coord_stats = DataValidator.get_coordinate_stats(profile_data)
                if coord_stats:
                    stats["profile_coord_ranges"].append(coord_stats["range"])
            else:
                stats["invalid_samples"].append({
                    "index": idx,
                    "reason": "Invalid profile JSON"
                })
            
            # Validate midcurve
            midcurve_valid, midcurve_data = DataValidator.parse_brep_safe(row['Midcurve_brep'])
            if midcurve_valid:
                stats["valid_midcurve_parse"] += 1
                if DataValidator.is_connected_graph(midcurve_data):
                    stats["connected_midcurves"] += 1
                coord_stats = DataValidator.get_coordinate_stats(midcurve_data)
                if coord_stats:
                    stats["midcurve_coord_ranges"].append(coord_stats["range"])
            else:
                stats["invalid_samples"].append({
                    "index": idx,
                    "reason": "Invalid midcurve JSON"
                })
        
        # Calculate average ranges
        if stats["profile_coord_ranges"]:
            stats["avg_profile_range"] = np.mean(stats["profile_coord_ranges"], axis=0).tolist()
        if stats["midcurve_coord_ranges"]:
            stats["avg_midcurve_range"] = np.mean(stats["midcurve_coord_ranges"], axis=0).tolist()
        
        return stats
    
    @staticmethod
    def clean_dataset(input_file: str, output_file: str):
        """Remove invalid samples and save cleaned dataset"""
        df = pd.read_csv(input_file)
        valid_indices = []
        
        for idx, row in df.iterrows():
            profile_valid, profile_data = DataValidator.parse_brep_safe(row['Profile_brep'])
            midcurve_valid, midcurve_data = DataValidator.parse_brep_safe(row['Midcurve_brep'])
            
            if profile_valid and midcurve_valid:
                if DataValidator.is_closed_profile(profile_data) and \
                   DataValidator.is_connected_graph(midcurve_data):
                    valid_indices.append(idx)
        
        cleaned_df = df.iloc[valid_indices]
        cleaned_df.to_csv(output_file, index=False)
        
        print(f"Cleaned dataset: {len(valid_indices)}/{len(df)} samples retained")
        return cleaned_df

if __name__ == "__main__":
    # Example usage
    from config_enhanced import Config
    
    print("Validating training data...")
    stats = DataValidator.validate_dataset(Config.TRAIN_FILE)
    
    print(f"\nDataset Statistics:")
    print(f"Total samples: {stats['total_samples']}")
    print(f"Valid profile parse: {stats['valid_profile_parse']}")
    print(f"Valid midcurve parse: {stats['valid_midcurve_parse']}")
    print(f"Closed profiles: {stats['closed_profiles']}")
    print(f"Connected midcurves: {stats['connected_midcurves']}")
    print(f"Invalid samples: {len(stats['invalid_samples'])}")
