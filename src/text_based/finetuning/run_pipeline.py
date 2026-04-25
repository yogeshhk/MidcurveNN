#!/usr/bin/env python
"""
Complete pipeline runner for midcurve generation project
Orchestrates: validation → augmentation → training → evaluation → error analysis
"""

import argparse
import os
import sys
from datetime import datetime
import json

def run_command(cmd, description):
    """Run a command and handle errors"""
    print("\n" + "="*80)
    print(f"STEP: {description}")
    print("="*80)
    print(f"Running: {cmd}\n")
    
    exit_code = os.system(cmd)
    
    if exit_code != 0:
        print(f"\n❌ Error: {description} failed with exit code {exit_code}")
        return False
    
    print(f"\n✅ {description} completed successfully")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Run complete midcurve generation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python run_pipeline.py --full
  
  # Run only validation and augmentation
  python run_pipeline.py --validate --augment
  
  # Run training and evaluation
  python run_pipeline.py --train --evaluate
  
  # Compare multiple models
  python run_pipeline.py --compare --models "Qwen/Qwen2.5-Coder-7B-Instruct" "google/gemma-2-9b-it"
        """
    )
    
    # Pipeline steps
    parser.add_argument('--full', action='store_true',
                       help='Run complete pipeline (all steps)')
    parser.add_argument('--validate', action='store_true',
                       help='Run data validation')
    parser.add_argument('--augment', action='store_true',
                       help='Run data augmentation')
    parser.add_argument('--train', action='store_true',
                       help='Run model training')
    parser.add_argument('--evaluate', action='store_true',
                       help='Run model evaluation')
    parser.add_argument('--analyze', action='store_true',
                       help='Run error analysis')
    parser.add_argument('--compare', action='store_true',
                       help='Compare multiple models')
    parser.add_argument('--serve', action='store_true',
                       help='Start API server')
    
    # Configuration
    parser.add_argument('--models', nargs='+',
                       help='Models to compare (space-separated)')
    parser.add_argument('--num_samples', type=int,
                       help='Number of test samples for evaluation')
    parser.add_argument('--output_dir', type=str, default='pipeline_output',
                       help='Output directory for pipeline results')
    
    args = parser.parse_args()
    
    # If no steps specified and not full, show help
    if not any([args.full, args.validate, args.augment, args.train, 
                args.evaluate, args.analyze, args.compare, args.serve]):
        parser.print_help()
        return
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Log pipeline run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(args.output_dir, f"pipeline_log_{timestamp}.txt")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MIDCURVE GENERATION PIPELINE                              ║
║                          Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    steps_completed = []
    steps_failed = []
    
    # Step 1: Data Validation
    if args.full or args.validate:
        if run_command(
            "python data_validator.py",
            "Data Validation"
        ):
            steps_completed.append("Data Validation")
        else:
            steps_failed.append("Data Validation")
            if not args.full:
                return
    
    # Step 2: Data Augmentation
    if args.full or args.augment:
        if run_command(
            "python augmentation.py",
            "Data Augmentation"
        ):
            steps_completed.append("Data Augmentation")
        else:
            steps_failed.append("Data Augmentation")
            if not args.full:
                return
    
    # Step 3: Model Training
    if args.full or args.train:
        if run_command(
            "python train_enhanced.py",
            "Model Training"
        ):
            steps_completed.append("Model Training")
        else:
            steps_failed.append("Model Training")
            if not args.full:
                return
    
    # Step 4: Model Evaluation
    if args.full or args.evaluate:
        eval_cmd = "python evaluate.py --visualize"
        if args.num_samples:
            eval_cmd += f" --num_samples {args.num_samples}"
        
        if run_command(eval_cmd, "Model Evaluation"):
            steps_completed.append("Model Evaluation")
        else:
            steps_failed.append("Model Evaluation")
            if not args.full:
                return
    
    # Step 5: Error Analysis
    if args.full or args.analyze:
        if os.path.exists("evaluation_results.csv"):
            if run_command(
                "python error_analysis.py "
                "--results_file evaluation_results.csv "
                "--test_file midcurve_llm_test.csv",
                "Error Analysis"
            ):
                steps_completed.append("Error Analysis")
            else:
                steps_failed.append("Error Analysis")
        else:
            print("\n⚠️  Skipping Error Analysis: evaluation_results.csv not found")
            print("   Run evaluation first with --evaluate")
    
    # Step 6: Model Comparison
    if args.compare:
        compare_cmd = "python model_comparison.py --train"
        if args.models:
            compare_cmd += f" --models {' '.join(args.models)}"
        
        if run_command(compare_cmd, "Model Comparison"):
            steps_completed.append("Model Comparison")
        else:
            steps_failed.append("Model Comparison")
    
    # Step 7: Start API Server
    if args.serve:
        print("\n" + "="*80)
        print("Starting API Server")
        print("="*80)
        print("\nPress Ctrl+C to stop the server\n")
        os.system("python model_server.py --host 0.0.0.0 --port 8000")
    
    # Final Summary
    print("\n\n")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                         PIPELINE SUMMARY                                     ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n✅ Steps Completed ({len(steps_completed)}):")
    for step in steps_completed:
        print(f"   • {step}")
    
    if steps_failed:
        print(f"\n❌ Steps Failed ({len(steps_failed)}):")
        for step in steps_failed:
            print(f"   • {step}")
    else:
        print("\n🎉 All steps completed successfully!")
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "steps_completed": steps_completed,
        "steps_failed": steps_failed,
        "output_dir": args.output_dir
    }
    
    summary_file = os.path.join(args.output_dir, f"pipeline_summary_{timestamp}.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📄 Summary saved to: {summary_file}")
    
    # Print next steps
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    
    if "Model Training" in steps_completed:
        print("\n1. Review training logs in ./results/")
        print("2. Check model checkpoints")
    
    if "Model Evaluation" in steps_completed:
        print("\n3. Review evaluation results:")
        print("   • evaluation_results.csv")
        print("   • evaluation_summary.json")
        print("   • evaluation_plots/")
    
    if "Error Analysis" in steps_completed:
        print("\n4. Review error analysis:")
        print("   • error_analysis_report.txt")
        print("   • error_analysis_plots/")
        print("   • problematic_samples.csv")
    
    if "Model Comparison" in steps_completed:
        print("\n5. Review model comparison:")
        print("   • model_comparison_*/")
        print("   • Check best_model.txt for recommendation")
    
    print("\n6. Deploy model:")
    print("   python run_pipeline.py --serve")
    
    print("\n7. Run inference:")
    print("   python inference_enhanced.py --single")
    print("   python inference_enhanced.py --num_samples 10")
    
    print("\n" + "="*80)
    print()

if __name__ == "__main__":
    main()
