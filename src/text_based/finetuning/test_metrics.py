"""
Unit tests for geometric metrics
"""
import pytest
import numpy as np
import json
from metrics_enhanced import GeometricMetrics

class TestGeometricMetrics:
    
    def test_parse_brep_valid_json(self):
        """Test parsing valid JSON"""
        json_str = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]], "Segments": [[0]]}'
        data, points = GeometricMetrics.parse_brep(json_str)
        
        assert data is not None
        assert len(points) == 2
        assert np.array_equal(points, np.array([[0,0], [1,1]]))
    
    def test_parse_brep_invalid(self):
        """Test parsing invalid JSON"""
        json_str = "invalid json"
        data, points = GeometricMetrics.parse_brep(json_str)
        
        assert data is None
        assert len(points) == 0
    
    def test_hausdorff_metric_identical(self):
        """Test Hausdorff distance for identical shapes"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        
        dist = GeometricMetrics.hausdorff_metric(pred, true)
        assert dist < 0.01  # Should be very close to 0
    
    def test_hausdorff_metric_different(self):
        """Test Hausdorff distance for different shapes"""
        pred = '{"Points": [[0,0], [1,0]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0], [0,1]], "Lines": [[0,1]]}'
        
        dist = GeometricMetrics.hausdorff_metric(pred, true)
        assert 0.9 < dist < 1.5  # Should be approximately 1.0
    
    def test_chamfer_distance(self):
        """Test Chamfer distance calculation"""
        set_a = np.array([[0, 0], [1, 1]])
        set_b = np.array([[0, 0.1], [1, 1.1]])
        
        dist = GeometricMetrics.chamfer_distance(set_a, set_b)
        assert 0.05 < dist < 0.15  # Should be around 0.1
    
    def test_mae_metric(self):
        """Test Mean Absolute Error"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0.1], [1,1.1]], "Lines": [[0,1]]}'
        
        mae = GeometricMetrics.mae_metric(pred, true)
        assert 0.05 < mae < 0.15  # Should be around 0.1
    
    def test_rmse_metric(self):
        """Test Root Mean Square Error"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0.1], [1,1.1]], "Lines": [[0,1]]}'
        
        rmse = GeometricMetrics.rmse_metric(pred, true)
        assert rmse > 0  # Should be positive
        assert rmse > GeometricMetrics.mae_metric(pred, true)  # RMSE >= MAE
    
    def test_topology_accuracy_same_junctions(self):
        """Test topology accuracy with same junction count"""
        # Simple line (no junctions)
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0], [2,2]], "Lines": [[0,1]]}'
        
        acc = GeometricMetrics.topology_accuracy(pred, true)
        assert acc == 1.0
    
    def test_topology_accuracy_different_junctions(self):
        """Test topology accuracy with different junction counts"""
        # T-junction vs simple line
        pred = '{"Points": [[0,0], [1,0], [1,1]], "Lines": [[0,1], [1,2]]}'
        true = '{"Points": [[0,0], [1,0], [1,1], [2,0]], "Lines": [[0,1], [1,2], [1,3]]}'
        
        acc = GeometricMetrics.topology_accuracy(pred, true)
        assert 0 <= acc < 1.0  # Should be less than 1 but non-negative
    
    def test_connectivity_score_connected(self):
        """Test connectivity score for fully connected graph"""
        pred = '{"Points": [[0,0], [1,1], [2,2]], "Lines": [[0,1], [1,2]]}'
        
        score = GeometricMetrics.connectivity_score(pred)
        assert score == 1.0
    
    def test_connectivity_score_disconnected(self):
        """Test connectivity score for disconnected graph"""
        pred = '{"Points": [[0,0], [1,1], [2,2], [3,3]], "Lines": [[0,1], [2,3]]}'
        
        score = GeometricMetrics.connectivity_score(pred)
        assert score == 0.5  # Two components
    
    def test_vertex_count_accuracy_same(self):
        """Test vertex count accuracy when counts match"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0], [2,2]], "Lines": [[0,1]]}'
        
        acc = GeometricMetrics.vertex_count_accuracy(pred, true)
        assert acc == 1.0
    
    def test_vertex_count_accuracy_different(self):
        """Test vertex count accuracy when counts differ"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]]}'
        true = '{"Points": [[0,0], [1,1], [2,2]], "Lines": [[0,1], [1,2]]}'
        
        acc = GeometricMetrics.vertex_count_accuracy(pred, true)
        assert 0 <= acc < 1.0
    
    def test_json_validity_valid(self):
        """Test JSON validity for valid input"""
        pred = '{"Points": [[0,0]], "Lines": [[0,0]], "Segments": [[0]]}'
        
        valid = GeometricMetrics.json_validity(pred)
        assert valid == 1.0
    
    def test_json_validity_invalid(self):
        """Test JSON validity for invalid input"""
        pred = "not valid json"
        
        valid = GeometricMetrics.json_validity(pred)
        assert valid == 0.0
    
    def test_coordinate_range_metric_in_range(self):
        """Test coordinate range metric when prediction is in range"""
        pred = '{"Points": [[0.5, 0.5], [1.5, 1.5]], "Lines": [[0,1]]}'
        input_str = '{"Points": [[0,0], [2,2]], "Lines": [[0,1]]}'
        
        score = GeometricMetrics.coordinate_range_metric(pred, input_str)
        assert score == 1.0
    
    def test_coordinate_range_metric_out_of_range(self):
        """Test coordinate range metric when prediction is out of range"""
        pred = '{"Points": [[10, 10], [20, 20]], "Lines": [[0,1]]}'
        input_str = '{"Points": [[0,0], [2,2]], "Lines": [[0,1]]}'
        
        score = GeometricMetrics.coordinate_range_metric(pred, input_str)
        assert score == 0.0
    
    def test_compute_all_metrics(self):
        """Test computing all metrics at once"""
        pred = '{"Points": [[0,0], [1,1]], "Lines": [[0,1]], "Segments": [[0]]}'
        true = '{"Points": [[0,0.1], [1,1.1]], "Lines": [[0,1]], "Segments": [[0]]}'
        input_str = '{"Points": [[0,0], [2,0], [2,2], [0,2]], "Lines": [[0,1],[1,2],[2,3],[3,0]], "Segments": [[0,1,2,3]]}'
        
        metrics = GeometricMetrics.compute_all_metrics(pred, true, input_str)
        
        # Check all expected metrics are present
        expected_keys = [
            "json_validity", "hausdorff", "chamfer", "mae", "rmse",
            "topology_accuracy", "connectivity_score", 
            "vertex_count_accuracy", "coordinate_range", 
            "symmetry_preservation", "combined_score"
        ]
        
        for key in expected_keys:
            assert key in metrics
            assert isinstance(metrics[key], (int, float))
        
        # Check combined score is reasonable
        assert 0 <= metrics["combined_score"] <= 1
    
    def test_json_validity_rate(self):
        """Test JSON validity rate calculation"""
        predictions = [
            '{"Points": [[0,0]], "Lines": [[0,0]], "Segments": [[0]]}',
            'invalid',
            '{"Points": [[1,1]], "Lines": [[0,0]], "Segments": [[0]]}',
            'also invalid'
        ]
        
        rate = GeometricMetrics.json_validity_rate(predictions)
        assert rate == 0.5  # 2 out of 4 valid

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
