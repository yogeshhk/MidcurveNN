import matplotlib.pyplot as plt
import numpy as np
from metrics import GeometricMetrics

def plot_results(input_str, target_str, pred_str, title="Midcurve Prediction"):
    """Plots Input (Blue), Target (Green), and Prediction (Red Dashed)."""
    
    def extract_lines(brep_str):
        try:
            # Use the parser from metrics
            import ast
            import json
            if isinstance(brep_str, str):
                try:
                    data = json.loads(brep_str)
                except:
                    data = ast.literal_eval(brep_str)
            else:
                data = brep_str
                
            points = data['Points']
            lines_idx = data['Lines']
            lines = []
            for line in lines_idx:
                p1 = points[line[0]]
                p2 = points[line[1]]
                lines.append((p1, p2))
            return lines
        except:
            return []

    input_lines = extract_lines(input_str)
    target_lines = extract_lines(target_str)
    pred_lines = extract_lines(pred_str)

    plt.figure(figsize=(8, 8))
    
    # Plot Input Profile
    for line in input_lines:
        p1, p2 = line
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'b-', linewidth=2, label='Input Profile' if line == input_lines[0] else "")

    # Plot Target Midcurve
    for line in target_lines:
        p1, p2 = line
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'g-', linewidth=2, label='Target Midcurve' if line == target_lines[0] else "")

    # Plot Predicted Midcurve
    for line in pred_lines:
        p1, p2 = line
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r--', linewidth=2, label='Predicted Midcurve' if line == pred_lines[0] else "")

    plt.legend()
    plt.title(title)
    plt.grid(True)
    plt.axis('equal')
    plt.savefig('midcurve_result.png')
    print("Plot saved to midcurve_result.png")