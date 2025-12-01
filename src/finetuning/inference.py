import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from config_enhanced import Config
from metrics_enhanced import GeometricMetrics
from visualize import plot_results
import pandas as pd
import json
import ast
import numpy as np
from typing import Optional, Tuple

class MidcurveInference:
    """Enhanced inference with validation and correction"""
    
    def __init__(self, model_path: str = None, base_model_id: str = None):
        if model_path is None:
            model_path = Config.NEW_MODEL_NAME
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
    
    def parse_brep(self, json_str):
        """Parse B-Rep JSON safely"""
        try:
            if isinstance(json_str, str):
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    return ast.literal_eval(json_str)
            return json_str
        except:
            return None
    
    def validate_output(self, generated_text: str, input_profile: str) -> Tuple[Optional[dict], list]:
        """Validate generated output"""
        issues = []
        
        # Try to extract JSON from text
        try:
            # Find JSON boundaries
            if '{' in generated_text and '}' in generated_text:
                start_idx = generated_text.index('{')
                end_idx = generated_text.rindex('}') + 1
                json_str = generated_text[start_idx:end_idx]
                parsed = self.parse_brep(json_str)
            else:
                parsed = self.parse_brep(generated_text)
            
            if parsed is None:
                return None, ["Could not parse JSON"]
        
        except Exception as e:
            return None, [f"Parse error: {str(e)}"]
        
        # Check structure
        if not all(k in parsed for k in ["Points", "Lines", "Segments"]):
            return None, ["Missing required keys"]
        
        # Check connectivity
        if GeometricMetrics.connectivity_score(json.dumps(parsed)) < 1.0:
            issues.append("Disconnected components")
        
        # Check coordinate range
        input_data = self.parse_brep(input_profile)
        if input_data:
            input_points = np.array(input_data["Points"])
            output_points = np.array(parsed["Points"])
            
            input_range = input_points.max(axis=0) - input_points.min(axis=0)
            output_range = output_points.max(axis=0) - output_points.min(axis=0)
            
            # Check if output is way out of bounds
            if np.any(output_range > input_range * 2):
                issues.append("Output coordinates out of reasonable range")
        
        if len(issues) > 0:
            return parsed, issues
        
        return parsed, None
    
    def repair_connectivity(self, data: dict) -> dict:
        """Attempt to repair disconnected graph"""
        # This is a simplified repair - could be more sophisticated
        lines = data.get("Lines", [])
        points = np.array(data.get("Points", []))
        
        if len(lines) == 0 or len(points) == 0:
            return data
        
        # Find connected components
        adj = {i: [] for i in range(len(points))}
        for line in lines:
            if len(line) >= 2:
                p1, p2 = line[0], line[1]
                if p1 < len(points) and p2 < len(points):
                    adj[p1].append(p2)
                    adj[p2].append(p1)
        
        # BFS to find components
        visited = set()
        components = []
        
        for start in range(len(points)):
            if start not in visited:
                component = []
                queue = [start]
                visited.add(start)
                
                while queue:
                    node = queue.pop(0)
                    component.append(node)
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        # If multiple components, try to connect them
        if len(components) > 1:
            new_lines = lines.copy()
            
            # Connect each component to the next via nearest points
            for i in range(len(components) - 1):
                comp1_points = points[components[i]]
                comp2_points = points[components[i + 1]]
                
                # Find nearest pair
                min_dist = float('inf')
                best_pair = None
                
                for p1_idx in components[i]:
                    for p2_idx in components[i + 1]:
                        dist = np.linalg.norm(points[p1_idx] - points[p2_idx])
                        if dist < min_dist:
                            min_dist = dist
                            best_pair = (p1_idx, p2_idx)
                
                if best_pair:
                    new_lines.append(list(best_pair))
            
            data["Lines"] = new_lines
        
        return data
    
    def constrained_generation(self, profile_input: str, 
                              max_retries: int = 3) -> Tuple[str, dict]:
        """Generate with retries and validation"""
        
        for attempt in range(max_retries):
            # Format prompt
            messages = [
                {"role": "system", "content": Config.SYSTEM_PROMPT},
                {"role": "user", "content": profile_input}
            ]
            
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True)
            
            inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
            
            # Generate
            generated_ids = self.model.generate(
                inputs.input_ids,
                max_new_tokens=Config.MAX_NEW_TOKENS,
                do_sample=attempt > 0,  # Use sampling on retries
                temperature=0.1 + (attempt * 0.1),
                num_beams=Config.NUM_BEAMS,
                early_stopping=True
            )
            
            generated_ids = [
                output_ids[len(input_ids):] 
                for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True)[0]
            
            # Validate
            parsed, issues = self.validate_output(response, profile_input)
            
            if parsed is not None and issues is None:
                # Success!
                return response, {"attempts": attempt + 1, "success": True}
            
            elif parsed is not None and issues:
                # Partial success - try to repair
                if "Disconnected components" in issues:
                    repaired = self.repair_connectivity(parsed)
                    if GeometricMetrics.connectivity_score(json.dumps(repaired)) == 1.0:
                        return json.dumps(repaired), {
                            "attempts": attempt + 1, 
                            "success": True,
                            "repaired": True
                        }
        
        # All attempts failed
        return response, {"attempts": max_retries, "success": False}
    
    def run_inference_single(self, profile_input: str, ground_truth: str = None):
        """Run inference on single example"""
        print("-" * 60)
        print("Input Profile:", profile_input[:100], "...")
        print("-" * 60)
        
        # Generate
        response, metadata = self.constrained_generation(profile_input)
        
        print("Generated Midcurve:", response[:200])
        print("-" * 60)
        print(f"Generation metadata: {metadata}")
        print("-" * 60)
        
        # Compute metrics if ground truth available
        if ground_truth:
            metrics = GeometricMetrics.compute_all_metrics(
                response, ground_truth, profile_input)
            
            print("\nMetrics:")
            for key, value in metrics.items():
                print(f"  {key}: {value:.4f}")
            
            # Visualize
            plot_results(profile_input, ground_truth, response)
            
            return response, metrics
        
        return response, None
    
    def run_batch_inference(self, test_file: str, num_samples: int = None,
                           output_file: str = "batch_inference_results.csv"):
        """Run inference on batch of examples"""
        df = pd.read_csv(test_file)
        
        if num_samples:
            df = df.head(num_samples)
        
        results = []
        
        for idx, row in df.iterrows():
            print(f"\nProcessing {idx + 1}/{len(df)}: {row.get('ShapeName', 'Unknown')}")
            
            profile_input = str(row['Profile_brep'])
            ground_truth = str(row['Midcurve_brep'])
            
            try:
                response, metadata = self.constrained_generation(profile_input)
                
                metrics = GeometricMetrics.compute_all_metrics(
                    response, ground_truth, profile_input)
                
                results.append({
                    "index": idx,
                    "shape_name": row.get('ShapeName', f'shape_{idx}'),
                    "prediction": response,
                    **metadata,
                    **metrics
                })
            
            except Exception as e:
                print(f"Error: {e}")
                results.append({
                    "index": idx,
                    "shape_name": row.get('ShapeName', f'shape_{idx}'),
                    "error": str(e),
                    "success": False
                })
        
        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)
        
        print(f"\nResults saved to {output_file}")
        
        # Summary
        success_rate = results_df['success'].mean() if 'success' in results_df.columns else 0
        print(f"\nSuccess rate: {success_rate:.1%}")
        
        if 'combined_score' in results_df.columns:
            print(f"Mean combined score: {results_df['combined_score'].mean():.4f}")
        
        return results_df

def main():
    """Main inference function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run midcurve inference')
    parser.add_argument('--model_path', type=str, default=Config.NEW_MODEL_NAME,
                       help='Path to trained model')
    parser.add_argument('--test_file', type=str, default=Config.TEST_FILE,
                       help='Test dataset file')
    parser.add_argument('--num_samples', type=int, default=None,
                       help='Number of samples to process')
    parser.add_argument('--output_file', type=str, default='inference_results.csv',
                       help='Output file for results')
    parser.add_argument('--single', action='store_true',
                       help='Run on single example (first in test file)')
    
    args = parser.parse_args()
    
    # Initialize inference
    inferencer = MidcurveInference(args.model_path)
    
    if args.single:
        # Run on single example
        df = pd.read_csv(args.test_file)
        row = df.iloc[0]
        
        inferencer.run_inference_single(
            str(row['Profile_brep']),
            str(row['Midcurve_brep'])
        )
    else:
        # Run batch inference
        inferencer.run_batch_inference(
            args.test_file,
            args.num_samples,
            args.output_file
        )

if __name__ == "__main__":
    main()
