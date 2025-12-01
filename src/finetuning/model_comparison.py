import torch
import pandas as pd
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, PeftModel
from trl import SFTTrainer
from config_enhanced import Config
from dataset_loader import MidcurveDataset
from evaluate import ModelEvaluator
import json
import os
from datetime import datetime

class ModelComparison:
    """Compare multiple base models for midcurve generation"""
    
    def __init__(self, models_to_compare=None):
        if models_to_compare is None:
            self.models_to_compare = Config.MODELS_TO_COMPARE
        else:
            self.models_to_compare = models_to_compare
        
        self.results = {}
    
    def train_model(self, model_id: str, output_dir: str):
        """Train a single model"""
        print(f"\n{'='*60}")
        print(f"Training model: {model_id}")
        print(f"{'='*60}\n")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        
        # Load datasets
        data_handler = MidcurveDataset(tokenizer)
        train_dataset = data_handler.load_data(Config.TRAIN_FILE)
        val_dataset = data_handler.load_data(Config.VAL_FILE)
        
        # Quantization config
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # LoRA configuration
        peft_config = LoraConfig(
            lora_alpha=Config.LORA_ALPHA,
            lora_dropout=Config.LORA_DROPOUT,
            r=Config.LORA_R,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", 
                          "gate_proj", "up_proj", "down_proj"]
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=Config.NUM_EPOCHS,
            per_device_train_batch_size=Config.BATCH_SIZE,
            gradient_accumulation_steps=Config.GRAD_ACC_STEPS,
            logging_steps=Config.LOG_STEPS,
            save_strategy="epoch",
            learning_rate=Config.LEARNING_RATE,
            fp16=True,
            max_grad_norm=0.3,
            warmup_ratio=0.03,
            group_by_length=True,
            report_to="none",
            gradient_checkpointing=Config.USE_GRADIENT_CHECKPOINTING,
        )
        
        # Trainer
        trainer = SFTTrainer(
            model=model,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            peft_config=peft_config,
            dataset_text_field="text",
            max_seq_length=Config.MAX_SEQ_LENGTH,
            tokenizer=tokenizer,
            args=training_args,
        )
        
        # Train
        print("Starting training...")
        trainer.train()
        
        # Save
        print("Saving model...")
        trainer.model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        return output_dir
    
    def evaluate_model(self, model_path: str, base_model_id: str, test_file: str):
        """Evaluate a trained model"""
        print(f"\n{'='*60}")
        print(f"Evaluating model: {model_path}")
        print(f"{'='*60}\n")
        
        evaluator = ModelEvaluator(model_path, base_model_id)
        results_df = evaluator.evaluate_dataset(
            test_file, 
            f"{model_path}/evaluation_results.csv"
        )
        
        summary = evaluator.analyze_results(results_df)
        
        return summary, results_df
    
    def compare_models(self, train: bool = True, test_file: str = None):
        """Compare all models"""
        if test_file is None:
            test_file = Config.TEST_FILE
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_dir = f"model_comparison_{timestamp}"
        os.makedirs(comparison_dir, exist_ok=True)
        
        for model_id in self.models_to_compare:
            model_name = model_id.split('/')[-1]
            output_dir = os.path.join(comparison_dir, model_name)
            
            try:
                if train:
                    # Train model
                    trained_path = self.train_model(model_id, output_dir)
                else:
                    trained_path = output_dir
                
                # Evaluate model
                summary, results_df = self.evaluate_model(
                    trained_path, model_id, test_file)
                
                self.results[model_name] = {
                    "model_id": model_id,
                    "summary": summary,
                    "results_df": results_df
                }
                
                # Save individual results
                with open(f"{output_dir}/summary.json", 'w') as f:
                    json.dump(summary, f, indent=2)
                
            except Exception as e:
                print(f"Error with model {model_id}: {e}")
                self.results[model_name] = {
                    "model_id": model_id,
                    "error": str(e)
                }
        
        # Create comparison report
        self.create_comparison_report(comparison_dir)
        
        return self.results
    
    def create_comparison_report(self, comparison_dir: str):
        """Create comprehensive comparison report"""
        print(f"\n{'='*60}")
        print("MODEL COMPARISON SUMMARY")
        print(f"{'='*60}\n")
        
        # Create comparison table
        comparison_data = []
        
        for model_name, data in self.results.items():
            if "error" in data:
                print(f"{model_name}: ERROR - {data['error']}")
                continue
            
            summary = data['summary']
            comparison_data.append({
                "Model": model_name,
                "JSON Validity": f"{summary['json_validity_rate']:.3f}",
                "Mean Hausdorff": f"{summary['mean_hausdorff']:.3f}",
                "Median Hausdorff": f"{summary['median_hausdorff']:.3f}",
                "Mean Combined Score": f"{summary['mean_combined_score']:.3f}",
                "High Quality Rate": f"{summary['high_quality_rate']:.3f}",
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        print(comparison_df.to_string(index=False))
        
        # Save comparison table
        comparison_df.to_csv(f"{comparison_dir}/comparison_summary.csv", index=False)
        
        # Create visualizations
        self.create_comparison_visualizations(comparison_df, comparison_dir)
        
        # Determine best model
        if len(comparison_data) > 0:
            best_model_idx = comparison_df['Mean Combined Score'].astype(float).argmax()
            best_model = comparison_df.iloc[best_model_idx]['Model']
            
            print(f"\n{'='*60}")
            print(f"BEST MODEL: {best_model}")
            print(f"{'='*60}\n")
            
            with open(f"{comparison_dir}/best_model.txt", 'w') as f:
                f.write(f"Best Model: {best_model}\n")
                f.write(f"Combined Score: {comparison_df.iloc[best_model_idx]['Mean Combined Score']}\n")
    
    def create_comparison_visualizations(self, comparison_df: pd.DataFrame, 
                                        comparison_dir: str):
        """Create comparison visualizations"""
        import matplotlib.pyplot as plt
        
        # Bar chart comparison
        metrics = ["JSON Validity", "Mean Combined Score", "High Quality Rate"]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            values = comparison_df[metric].astype(float)
            models = comparison_df['Model']
            
            ax.bar(range(len(models)), values)
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels(models, rotation=45, ha='right')
            ax.set_ylabel(metric)
            ax.set_title(metric)
            ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f"{comparison_dir}/comparison_metrics.png", dpi=150)
        plt.close()
        
        # Radar chart
        from math import pi
        
        categories = ["JSON Validity", "Combined Score", "High Quality Rate"]
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='polar')
        
        angles = [n / float(len(categories)) * 2 * pi for n in range(len(categories))]
        angles += angles[:1]
        
        for idx, row in comparison_df.iterrows():
            values = [
                float(row["JSON Validity"]),
                float(row["Mean Combined Score"]),
                float(row["High Quality Rate"])
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=row['Model'])
            ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)
        
        plt.title('Model Comparison - Radar Chart', size=16, pad=20)
        plt.tight_layout()
        plt.savefig(f"{comparison_dir}/comparison_radar.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Comparison visualizations saved to {comparison_dir}/")

def main():
    """Main comparison function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare multiple models')
    parser.add_argument('--train', action='store_true',
                       help='Train models (if False, evaluate existing)')
    parser.add_argument('--test_file', type=str, default=Config.TEST_FILE,
                       help='Test dataset file')
    parser.add_argument('--models', nargs='+', default=None,
                       help='List of models to compare')
    
    args = parser.parse_args()
    
    comparator = ModelComparison(args.models)
    results = comparator.compare_models(train=args.train, test_file=args.test_file)
    
    print("\nModel comparison complete!")

if __name__ == "__main__":
    main()
