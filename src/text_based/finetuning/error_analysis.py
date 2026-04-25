import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
from metrics_enhanced import GeometricMetrics
import json
import ast
from typing import Dict, List

class ErrorAnalyzer:
    """Comprehensive error analysis for midcurve predictions"""
    
    def __init__(self, results_file: str, test_file: str):
        """Load results and test data"""
        self.results_df = pd.read_csv(results_file)
        self.test_df = pd.read_csv(test_file)
        
        # Add shape type classification
        self.results_df['shape_type'] = self.test_df['ShapeName'].apply(self._get_shape_type)
        
        # Add transformation type
        self.results_df['transform_type'] = self.test_df['ShapeName'].apply(self._get_transform_type)
    
    def _get_shape_type(self, name: str) -> str:
        """Extract shape type from name"""
        if 'I_' in name or name.startswith('I'):
            return 'I-beam'
        elif 'L_' in name or name.startswith('L'):
            return 'L-shape'
        elif 'T_' in name or name.startswith('T'):
            return 'T-shape'
        elif 'Plus_' in name or name.startswith('Plus'):
            return 'Plus'
        else:
            return 'Other'
    
    def _get_transform_type(self, name: str) -> str:
        """Extract transformation type from name"""
        if 'translated' in name:
            return 'translation'
        elif 'rotated' in name:
            return 'rotation'
        elif 'scaled' in name:
            return 'scaling'
        else:
            return 'none'
    
    def categorize_errors(self) -> Dict:
        """Categorize all errors"""
        error_categories = {
            'json_parsing_failures': [],
            'topological_errors': [],
            'geometric_errors': [],
            'connectivity_errors': [],
            'coordinate_range_errors': []
        }
        
        for idx, row in self.results_df.iterrows():
            shape_name = row.get('shape_name', f'shape_{idx}')
            
            # JSON parsing failures
            if row['json_validity'] == 0:
                error_categories['json_parsing_failures'].append({
                    'name': shape_name,
                    'shape_type': row['shape_type'],
                    'index': idx
                })
            
            # Topological errors (wrong number of junctions)
            if 'topology_accuracy' in row and row['topology_accuracy'] < 0.5:
                error_categories['topological_errors'].append({
                    'name': shape_name,
                    'shape_type': row['shape_type'],
                    'topology_score': row['topology_accuracy'],
                    'index': idx
                })
            
            # Geometric errors (high Hausdorff distance)
            if 'hausdorff' in row and row['hausdorff'] > 10.0:
                error_categories['geometric_errors'].append({
                    'name': shape_name,
                    'shape_type': row['shape_type'],
                    'hausdorff': row['hausdorff'],
                    'index': idx
                })
            
            # Connectivity errors
            if 'connectivity_score' in row and row['connectivity_score'] < 1.0:
                error_categories['connectivity_errors'].append({
                    'name': shape_name,
                    'shape_type': row['shape_type'],
                    'connectivity_score': row['connectivity_score'],
                    'index': idx
                })
            
            # Coordinate range errors
            if 'coordinate_range' in row and row['coordinate_range'] < 1.0:
                error_categories['coordinate_range_errors'].append({
                    'name': shape_name,
                    'shape_type': row['shape_type'],
                    'index': idx
                })
        
        return error_categories
    
    def identify_failure_patterns(self) -> Dict:
        """Identify common failure patterns"""
        patterns = {
            'by_shape_type': {},
            'by_transform_type': {},
            'by_complexity': {},
            'common_error_combinations': []
        }
        
        # Performance by shape type
        for shape_type in self.results_df['shape_type'].unique():
            subset = self.results_df[self.results_df['shape_type'] == shape_type]
            patterns['by_shape_type'][shape_type] = {
                'count': len(subset),
                'mean_score': subset['combined_score'].mean(),
                'failure_rate': (subset['json_validity'] == 0).mean(),
                'mean_hausdorff': subset['hausdorff'].mean()
            }
        
        # Performance by transformation
        for transform_type in self.results_df['transform_type'].unique():
            subset = self.results_df[self.results_df['transform_type'] == transform_type]
            patterns['by_transform_type'][transform_type] = {
                'count': len(subset),
                'mean_score': subset['combined_score'].mean(),
                'failure_rate': (subset['json_validity'] == 0).mean(),
                'mean_hausdorff': subset['hausdorff'].mean()
            }
        
        # Identify samples with multiple error types
        for idx, row in self.results_df.iterrows():
            error_types = []
            
            if row['json_validity'] == 0:
                error_types.append('json_error')
            if row.get('topology_accuracy', 1.0) < 0.5:
                error_types.append('topology_error')
            if row.get('connectivity_score', 1.0) < 1.0:
                error_types.append('connectivity_error')
            if row.get('hausdorff', 0) > 10.0:
                error_types.append('geometric_error')
            
            if len(error_types) > 1:
                patterns['common_error_combinations'].append({
                    'name': row.get('shape_name', f'shape_{idx}'),
                    'errors': error_types,
                    'combined_score': row['combined_score']
                })
        
        return patterns
    
    def analyze_prediction_characteristics(self) -> Dict:
        """Analyze characteristics of predictions"""
        characteristics = {
            'prediction_lengths': [],
            'vertex_count_differences': [],
            'coordinate_ranges': [],
            'generation_patterns': defaultdict(int)
        }
        
        for idx, row in self.results_df.iterrows():
            # Prediction length
            if 'prediction' in row and isinstance(row['prediction'], str):
                characteristics['prediction_lengths'].append(len(row['prediction']))
                
                # Analyze generation patterns (common prefixes/suffixes)
                pred_lower = row['prediction'].lower()
                if pred_lower.startswith('{'):
                    characteristics['generation_patterns']['starts_with_brace'] += 1
                if 'points' in pred_lower:
                    characteristics['generation_patterns']['contains_points'] += 1
                if 'lines' in pred_lower:
                    characteristics['generation_patterns']['contains_lines'] += 1
            
            # Vertex count differences
            if 'vertex_count_accuracy' in row:
                characteristics['vertex_count_differences'].append(
                    1.0 - row['vertex_count_accuracy']
                )
        
        return characteristics
    
    def generate_failure_report(self, output_file: str = 'error_analysis_report.txt'):
        """Generate comprehensive failure report"""
        error_categories = self.categorize_errors()
        failure_patterns = self.identify_failure_patterns()
        pred_characteristics = self.analyze_prediction_characteristics()
        
        with open(output_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("ERROR ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            
            # Error category summary
            f.write("--- ERROR CATEGORIES ---\n\n")
            for category, errors in error_categories.items():
                f.write(f"{category}: {len(errors)} cases\n")
                if len(errors) > 0 and len(errors) <= 10:
                    for error in errors:
                        f.write(f"  - {error['name']}\n")
                elif len(errors) > 10:
                    f.write(f"  (Showing first 10)\n")
                    for error in errors[:10]:
                        f.write(f"  - {error['name']}\n")
                f.write("\n")
            
            # Failure patterns by shape type
            f.write("\n--- PERFORMANCE BY SHAPE TYPE ---\n\n")
            for shape_type, stats in failure_patterns['by_shape_type'].items():
                f.write(f"{shape_type}:\n")
                f.write(f"  Count: {stats['count']}\n")
                f.write(f"  Mean Score: {stats['mean_score']:.4f}\n")
                f.write(f"  Failure Rate: {stats['failure_rate']:.2%}\n")
                f.write(f"  Mean Hausdorff: {stats['mean_hausdorff']:.4f}\n\n")
            
            # Failure patterns by transformation
            f.write("\n--- PERFORMANCE BY TRANSFORMATION ---\n\n")
            for transform, stats in failure_patterns['by_transform_type'].items():
                f.write(f"{transform}:\n")
                f.write(f"  Count: {stats['count']}\n")
                f.write(f"  Mean Score: {stats['mean_score']:.4f}\n")
                f.write(f"  Failure Rate: {stats['failure_rate']:.2%}\n")
                f.write(f"  Mean Hausdorff: {stats['mean_hausdorff']:.4f}\n\n")
            
            # Common error combinations
            f.write("\n--- SAMPLES WITH MULTIPLE ERROR TYPES ---\n\n")
            for combo in failure_patterns['common_error_combinations'][:20]:
                f.write(f"{combo['name']}: {', '.join(combo['errors'])} "
                       f"(score: {combo['combined_score']:.4f})\n")
            
            # Prediction characteristics
            f.write("\n--- PREDICTION CHARACTERISTICS ---\n\n")
            if pred_characteristics['prediction_lengths']:
                f.write(f"Average prediction length: "
                       f"{np.mean(pred_characteristics['prediction_lengths']):.0f} chars\n")
            
            f.write("\nGeneration patterns:\n")
            for pattern, count in pred_characteristics['generation_patterns'].items():
                f.write(f"  {pattern}: {count} ({count/len(self.results_df):.1%})\n")
        
        print(f"Error analysis report saved to {output_file}")
        return error_categories, failure_patterns
    
    def generate_failure_visualizations(self, output_dir: str = 'error_analysis_plots'):
        """Create visualizations of failure patterns"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Error distribution by shape type
        error_categories = self.categorize_errors()
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # JSON failures by shape type
        json_failures = pd.DataFrame(error_categories['json_parsing_failures'])
        if len(json_failures) > 0:
            json_failures['shape_type'].value_counts().plot(kind='bar', ax=axes[0, 0])
            axes[0, 0].set_title('JSON Parsing Failures by Shape Type')
            axes[0, 0].set_ylabel('Count')
            axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Performance by shape type
        shape_scores = self.results_df.groupby('shape_type')['combined_score'].mean()
        shape_scores.plot(kind='bar', ax=axes[0, 1], color='skyblue')
        axes[0, 1].set_title('Mean Combined Score by Shape Type')
        axes[0, 1].set_ylabel('Combined Score')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Performance by transformation
        transform_scores = self.results_df.groupby('transform_type')['combined_score'].mean()
        transform_scores.plot(kind='bar', ax=axes[1, 0], color='lightcoral')
        axes[1, 0].set_title('Mean Combined Score by Transformation')
        axes[1, 0].set_ylabel('Combined Score')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Error correlation
        error_cols = ['json_validity', 'topology_accuracy', 'connectivity_score']
        if all(col in self.results_df.columns for col in error_cols):
            error_data = self.results_df[error_cols].corr()
            sns.heatmap(error_data, annot=True, fmt='.2f', cmap='RdYlGn', ax=axes[1, 1])
            axes[1, 1].set_title('Error Type Correlation')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/error_distribution.png', dpi=150)
        plt.close()
        
        # 2. Hausdorff distance distribution by shape type
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for shape_type in self.results_df['shape_type'].unique():
            subset = self.results_df[self.results_df['shape_type'] == shape_type]
            subset['hausdorff'].hist(bins=30, alpha=0.5, label=shape_type, ax=ax)
        
        ax.set_xlabel('Hausdorff Distance')
        ax.set_ylabel('Count')
        ax.set_title('Hausdorff Distance Distribution by Shape Type')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/hausdorff_by_shape.png', dpi=150)
        plt.close()
        
        # 3. Failure rate heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        pivot_data = self.results_df.pivot_table(
            values='combined_score',
            index='shape_type',
            columns='transform_type',
            aggfunc='mean'
        )
        
        sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='RdYlGn', ax=ax)
        ax.set_title('Mean Combined Score: Shape Type vs Transformation')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/performance_heatmap.png', dpi=150)
        plt.close()
        
        print(f"Error visualizations saved to {output_dir}/")
    
    def identify_problematic_samples(self, n: int = 20) -> pd.DataFrame:
        """Identify most problematic samples for further analysis"""
        problematic = self.results_df.nsmallest(n, 'combined_score')
        
        print(f"\n{'='*80}")
        print(f"TOP {n} MOST PROBLEMATIC SAMPLES")
        print(f"{'='*80}\n")
        
        for idx, row in problematic.iterrows():
            print(f"{row['shape_name']} ({row['shape_type']})")
            print(f"  Combined Score: {row['combined_score']:.4f}")
            print(f"  JSON Valid: {row['json_validity']}")
            print(f"  Hausdorff: {row.get('hausdorff', 'N/A')}")
            print(f"  Topology: {row.get('topology_accuracy', 'N/A')}")
            print()
        
        return problematic

def main():
    """Main error analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze model errors')
    parser.add_argument('--results_file', type=str, required=True,
                       help='Evaluation results CSV file')
    parser.add_argument('--test_file', type=str, required=True,
                       help='Test dataset CSV file')
    parser.add_argument('--output_report', type=str, default='error_analysis_report.txt',
                       help='Output report file')
    parser.add_argument('--output_dir', type=str, default='error_analysis_plots',
                       help='Output directory for plots')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = ErrorAnalyzer(args.results_file, args.test_file)
    
    # Generate report
    error_categories, failure_patterns = analyzer.generate_failure_report(args.output_report)
    
    # Generate visualizations
    analyzer.generate_failure_visualizations(args.output_dir)
    
    # Identify problematic samples
    problematic = analyzer.identify_problematic_samples(20)
    problematic.to_csv('problematic_samples.csv', index=False)
    
    print("\nError analysis complete!")
    print(f"Report: {args.output_report}")
    print(f"Plots: {args.output_dir}/")
    print(f"Problematic samples: problematic_samples.csv")

if __name__ == "__main__":
    main()
