import torch
import pandas as pd
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from config_enhanced import Config
from metrics_enhanced import GeometricMetrics
from visualize import plot_results
import json
from tqdm import tqdm
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def __init__(self, model_path: str, base_model_id: str = None):
        """Initialize evaluator with trained model"""
        if base_model_id is None:
            base_model_id = Config.MODEL_ID
        
        print(f"Loading base model: {base_model_id}")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            device_map="auto",
            torch_dtype=torch.float16
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_id)
        
        print(f"Loading fine-tuned adapters: {model_path}")
        self.model = PeftModel.from_pretrained(self.base_model, model_path)
        self.model = self.model.merge_and_unload()
        self.model.eval()
        
        print("Model loaded successfully")
    
    def generate_prediction(self, profile_input: str) -> str:
        """Generate midcurve prediction for a profile"""
        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": profile_input}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs.input_ids,
                max_new_tokens=Config.MAX_NEW_TOKENS,
                do_sample=Config.DO_SAMPLE,
                temperature=Config.TEMPERATURE,
                num_beams=Config.NUM_BEAMS
            )
        
        generated_ids = [
            output_ids[len(input_ids):] 
            for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        response = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True)[0]
        
        return response.strip()
    
    def evaluate_dataset(self, test_file: str, output_file: str = None):
        """Evaluate model on test dataset"""
        df = pd.read_csv(test_file)
        results = []
        
        print(f"Evaluating on {len(df)} test samples...")
        
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            profile_input = str(row['Profile_brep'])
            ground_truth = str(row['Midcurve_brep'])
            
            # Generate prediction
            try:
                prediction = self.generate_prediction(profile_input)
                
                # Compute metrics
                metrics = GeometricMetrics.compute_all_metrics(
                    prediction, ground_truth, profile_input)
                
                # Store results
                result = {
                    "index": idx,
                    "shape_name": row.get('ShapeName', f'shape_{idx}'),
                    "prediction": prediction,
                    "ground_truth": ground_truth,
                    **metrics
                }
                
                results.append(result)
                
            except Exception as e:
                print(f"Error processing index {idx}: {e}")
                results.append({
                    "index": idx,
                    "shape_name": row.get('ShapeName', f'shape_{idx}'),
                    "error": str(e),
                    "json_validity": 0.0,
                    "combined_score": 0.0
                })
        
        results_df = pd.DataFrame(results)
        
        if output_file:
            results_df.to_csv(output_file, index=False)
            print(f"Results saved to {output_file}")
        
        return results_df
    
    def analyze_results(self, results_df: pd.DataFrame):
        """Analyze and print evaluation results"""
        print("\n" + "="*60)
        print("EVALUATION RESULTS")
        print("="*60)
        
        # Overall metrics
        print("\n--- Overall Performance ---")
        metric_columns = [
            "json_validity", "hausdorff", "chamfer", "mae", "rmse",
            "topology_accuracy", "connectivity_score", 
            "vertex_count_accuracy", "combined_score"
        ]
        
        for metric in metric_columns:
            if metric in results_df.columns:
                mean_val = results_df[metric].mean()
                std_val = results_df[metric].std()
                print(f"{metric:.<30} {mean_val:.4f} ± {std_val:.4f}")
        
        # Success rates
        print("\n--- Success Rates ---")
        json_valid = (results_df["json_validity"] > 0).sum()
        print(f"JSON Parsing Success: {json_valid}/{len(results_df)} ({100*json_valid/len(results_df):.1f}%)")
        
        high_quality = (results_df["combined_score"] > 0.7).sum()
        print(f"High Quality (score > 0.7): {high_quality}/{len(results_df)} ({100*high_quality/len(results_df):.1f}%)")
        
        # Identify failure cases
        print("\n--- Failure Cases ---")
        failures = results_df[results_df["json_validity"] == 0]
        print(f"Total failures: {len(failures)}")
        
        if len(failures) > 0:
            print("Failed samples:")
            for idx, row in failures.head(5).iterrows():
                print(f"  - {row['shape_name']}")
        
        # Best and worst cases
        print("\n--- Best Predictions ---")
        best = results_df.nlargest(5, "combined_score")
        for idx, row in best.iterrows():
            print(f"  - {row['shape_name']}: {row['combined_score']:.4f}")
        
        print("\n--- Worst Predictions ---")
        worst = results_df.nsmallest(5, "combined_score")
        for idx, row in worst.iterrows():
            print(f"  - {row['shape_name']}: {row['combined_score']:.4f}")
        
        return self.compute_summary_statistics(results_df)
    
    def compute_summary_statistics(self, results_df: pd.DataFrame):
        """Compute summary statistics"""
        summary = {
            "total_samples": len(results_df),
            "json_validity_rate": results_df["json_validity"].mean(),
            "mean_hausdorff": results_df["hausdorff"].mean(),
            "median_hausdorff": results_df["hausdorff"].median(),
            "mean_combined_score": results_df["combined_score"].mean(),
            "high_quality_rate": (results_df["combined_score"] > 0.7).mean(),
        }
        
        return summary
    
    def evaluate_by_complexity(self, results_df: pd.DataFrame, test_file: str):
        """Evaluate performance by shape complexity"""
        df = pd.read_csv(test_file)
        
        # Categorize by shape type (extract from shape name)
        def get_shape_type(name):
            if 'I_' in name:
                return 'I-beam'
            elif 'L_' in name:
                return 'L-shape'
            elif 'T_' in name:
                return 'T-shape'
            elif 'Plus_' in name:
                return 'Plus'
            else:
                return 'Other'
        
        results_df['shape_type'] = df['ShapeName'].apply(get_shape_type)
        
        print("\n--- Performance by Shape Type ---")
        for shape_type in results_df['shape_type'].unique():
            subset = results_df[results_df['shape_type'] == shape_type]
            print(f"\n{shape_type} ({len(subset)} samples):")
            print(f"  Mean Combined Score: {subset['combined_score'].mean():.4f}")
            print(f"  Mean Hausdorff: {subset['hausdorff'].mean():.4f}")
            print(f"  JSON Validity: {subset['json_validity'].mean():.4f}")
    
    def create_visualizations(self, results_df: pd.DataFrame, output_dir: str = "evaluation_plots"):
        """Create visualization plots"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Distribution of metrics
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        metrics_to_plot = [
            "hausdorff", "chamfer", "mae", 
            "topology_accuracy", "connectivity_score", "combined_score"
        ]
        
        for idx, metric in enumerate(metrics_to_plot):
            ax = axes[idx // 3, idx % 3]
            results_df[metric].hist(bins=30, ax=ax, edgecolor='black')
            ax.set_title(f'{metric} Distribution')
            ax.set_xlabel(metric)
            ax.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/metric_distributions.png", dpi=150)
        plt.close()
        
        # 2. Correlation heatmap
        numeric_cols = results_df.select_dtypes(include=[np.number]).columns
        correlation_matrix = results_df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
        plt.title('Metric Correlation Heatmap')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/correlation_heatmap.png", dpi=150)
        plt.close()
        
        # 3. Performance by shape type
        if 'shape_type' in results_df.columns:
            plt.figure(figsize=(12, 6))
            results_df.boxplot(column='combined_score', by='shape_type')
            plt.title('Combined Score by Shape Type')
            plt.suptitle('')
            plt.ylabel('Combined Score')
            plt.xlabel('Shape Type')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{output_dir}/performance_by_shape.png", dpi=150)
            plt.close()
        
        # 4. Scatter: Hausdorff vs Combined Score
        plt.figure(figsize=(10, 6))
        plt.scatter(results_df['hausdorff'], results_df['combined_score'], alpha=0.5)
        plt.xlabel('Hausdorff Distance')
        plt.ylabel('Combined Score')
        plt.title('Hausdorff Distance vs Combined Score')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/hausdorff_vs_score.png", dpi=150)
        plt.close()
        
        print(f"\nVisualizations saved to {output_dir}/")
    
    def visualize_predictions(self, results_df: pd.DataFrame, test_file: str, 
                             num_samples: int = 5, output_dir: str = "prediction_viz"):
        """Visualize individual predictions"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        df = pd.read_csv(test_file)
        
        # Visualize best, worst, and median cases
        best_idx = results_df['combined_score'].nlargest(num_samples).index
        worst_idx = results_df['combined_score'].nsmallest(num_samples).index
        median_idx = results_df.iloc[(results_df['combined_score'] - results_df['combined_score'].median()).abs().argsort()[:num_samples]].index
        
        for category, indices in [('best', best_idx), ('worst', worst_idx), ('median', median_idx)]:
            for i, idx in enumerate(indices):
                row = results_df.iloc[idx]
                original_row = df.iloc[row['index']]
                
                try:
                    plot_results(
                        str(original_row['Profile_brep']),
                        row['ground_truth'],
                        row['prediction'],
                        title=f"{category.capitalize()} #{i+1}: {row['shape_name']} (Score: {row['combined_score']:.3f})"
                    )
                    
                    plt.savefig(f"{output_dir}/{category}_{i+1}_{row['shape_name']}.png", dpi=150)
                    plt.close()
                except Exception as e:
                    print(f"Error visualizing {row['shape_name']}: {e}")
        
        print(f"\nPrediction visualizations saved to {output_dir}/")

def main():
    """Main evaluation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate trained midcurve model')
    parser.add_argument('--model_path', type=str, default=Config.NEW_MODEL_NAME,
                       help='Path to trained model')
    parser.add_argument('--test_file', type=str, default=Config.TEST_FILE,
                       help='Path to test dataset')
    parser.add_argument('--output_file', type=str, default='evaluation_results.csv',
                       help='Output file for results')
    parser.add_argument('--visualize', action='store_true',
                       help='Create visualizations')
    
    args = parser.parse_args()
    
    # Initialize evaluator
    evaluator = ModelEvaluator(args.model_path)
    
    # Run evaluation
    results_df = evaluator.evaluate_dataset(args.test_file, args.output_file)
    
    # Analyze results
    summary = evaluator.analyze_results(results_df)
    
    # Performance by complexity
    evaluator.evaluate_by_complexity(results_df, args.test_file)
    
    # Create visualizations
    if args.visualize:
        evaluator.create_visualizations(results_df)
        evaluator.visualize_predictions(results_df, args.test_file)
    
    # Save summary
    with open('evaluation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\nEvaluation complete!")
    print(f"Results saved to: {args.output_file}")
    print(f"Summary saved to: evaluation_summary.json")

if __name__ == "__main__":
    main()
