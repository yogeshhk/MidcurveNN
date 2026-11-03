"""
Example Usage Script for Midcurve Generation
Demonstrates all major functionality
"""

import json
import numpy as np
from config_enhanced import Config
from data_validator import DataValidator
from metrics_enhanced import GeometricMetrics
from augmentation import GeometricAugmentation

def example_1_data_validation():
    """Example 1: Validate dataset quality"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Data Validation")
    print("="*80)
    
    # Validate training data
    stats = DataValidator.validate_dataset(Config.TRAIN_FILE)
    
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {stats['total_samples']}")
    print(f"  Valid profiles: {stats['valid_profile_parse']}")
    print(f"  Valid midcurves: {stats['valid_midcurve_parse']}")
    print(f"  Closed profiles: {stats['closed_profiles']}")
    print(f"  Connected midcurves: {stats['connected_midcurves']}")
    
    # Clean dataset if needed
    if stats['total_samples'] != stats['valid_profile_parse']:
        print("\n⚠️  Found invalid samples. Cleaning dataset...")
        DataValidator.clean_dataset(
            Config.TRAIN_FILE,
            Config.TRAIN_FILE.replace('.csv', '_cleaned.csv')
        )

def example_2_data_augmentation():
    """Example 2: Augment training data"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Data Augmentation")
    print("="*80)
    
    # Example profile
    profile_brep = {
        "Points": [[0.0, 0.0], [10.0, 0.0], [10.0, 25.0], [35.0, 25.0], [35.0, 30.0], [0.0, 30.0]],
        "Lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
        "Segments": [[0, 1, 2, 3, 4, 5]]
    }
    
    midcurve_brep = {
        "Points": [[5.0, 0.0], [5.0, 27.5], [35.0, 27.5], [0.0, 27.5]],
        "Lines": [[0, 1], [1, 2], [3, 1]],
        "Segments": [[0], [1], [2]]
    }
    
    profile_str = json.dumps(profile_brep)
    midcurve_str = json.dumps(midcurve_brep)
    
    print("\nOriginal profile:")
    print(f"  Points: {len(profile_brep['Points'])}")
    print(f"  Lines: {len(profile_brep['Lines'])}")
    
    # Apply different augmentations
    augmentation_types = ["noise", "non_uniform_scale", "precision"]
    
    for aug_type in augmentation_types:
        aug_profile, aug_midcurve = GeometricAugmentation.augment_pair(
            profile_str, midcurve_str, aug_type
        )
        
        aug_data = json.loads(aug_profile)
        print(f"\n{aug_type} augmentation:")
        print(f"  First point: {aug_data['Points'][0]}")

def example_3_compute_metrics():
    """Example 3: Compute geometric metrics"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Computing Metrics")
    print("="*80)
    
    # Example prediction and ground truth
    prediction = '{"Points": [[5.0, 0.0], [5.0, 27.0], [35.0, 27.0]], "Lines": [[0, 1], [1, 2]], "Segments": [[0, 1]]}'
    ground_truth = '{"Points": [[5.0, 0.0], [5.0, 27.5], [35.0, 27.5]], "Lines": [[0, 1], [1, 2]], "Segments": [[0, 1]]}'
    input_profile = '{"Points": [[0.0, 0.0], [10.0, 0.0], [10.0, 25.0], [35.0, 25.0], [35.0, 30.0], [0.0, 30.0]], "Lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "Segments": [[0, 1, 2, 3, 4, 5]]}'
    
    # Compute all metrics
    metrics = GeometricMetrics.compute_all_metrics(
        prediction, ground_truth, input_profile
    )
    
    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

def example_4_inference():
    """Example 4: Run inference (requires trained model)"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Inference")
    print("="*80)
    
    try:
        from inference_enhanced import MidcurveInference
        
        # Initialize inference
        inferencer = MidcurveInference()
        
        # Example input
        input_profile = '{"Points": [[0.0, 0.0], [10.0, 0.0], [10.0, 25.0], [35.0, 25.0], [35.0, 30.0], [0.0, 30.0]], "Lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "Segments": [[0, 1, 2, 3, 4, 5]]}'
        
        # Generate prediction
        prediction, metadata = inferencer.constrained_generation(input_profile)
        
        print(f"\nPrediction: {prediction[:100]}...")
        print(f"Metadata: {metadata}")
    
    except Exception as e:
        print(f"\n⚠️  Inference not available: {e}")
        print("   Train model first with: python train_enhanced.py")

def example_5_api_usage():
    """Example 5: API client usage"""
    print("\n" + "="*80)
    print("EXAMPLE 5: API Client Usage")
    print("="*80)
    
    try:
        import requests
        
        # API endpoint
        api_url = "http://localhost:8000"
        
        # Check health
        try:
            response = requests.get(f"{api_url}/health", timeout=2)
            print(f"\nAPI Status: {response.json()}")
        except:
            print("\n⚠️  API server not running")
            print("   Start with: python model_server.py")
            return
        
        # Example profile
        profile_data = {
            "profile": {
                "points": [[0, 0], [10, 0], [10, 25], [35, 25], [35, 30], [0, 30]],
                "lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]],
                "segments": [[0, 1, 2, 3, 4, 5]]
            },
            "validate_input": True,
            "return_confidence": True
        }
        
        # Make prediction request
        response = requests.post(
            f"{api_url}/predict",
            json=profile_data,
            timeout=30
        )
        
        result = response.json()
        
        if result['success']:
            print("\n✅ Prediction successful!")
            print(f"   Processing time: {result['processing_time_ms']:.2f}ms")
            if result['confidence_score']:
                print(f"   Confidence: {result['confidence_score']:.4f}")
            print(f"   Midcurve points: {len(result['midcurve']['points'])}")
        else:
            print(f"\n❌ Prediction failed: {result['error']}")
    
    except ImportError:
        print("\n⚠️  requests library not installed")
        print("   Install with: pip install requests")

def example_6_batch_evaluation():
    """Example 6: Batch evaluation"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Batch Evaluation")
    print("="*80)
    
    try:
        from evaluate import ModelEvaluator
        
        # Initialize evaluator
        evaluator = ModelEvaluator(Config.NEW_MODEL_NAME)
        
        # Run evaluation on test set
        results_df = evaluator.evaluate_dataset(
            Config.TEST_FILE,
            'example_evaluation_results.csv'
        )
        
        # Analyze results
        summary = evaluator.analyze_results(results_df)
        
        print("\nEvaluation Summary:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"\n⚠️  Evaluation not available: {e}")
        print("   Train model first with: python train_enhanced.py")

def example_7_error_analysis():
    """Example 7: Error analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Error Analysis")
    print("="*80)
    
    try:
        from error_analysis import ErrorAnalyzer
        import os
        
        if not os.path.exists('evaluation_results.csv'):
            print("\n⚠️  evaluation_results.csv not found")
            print("   Run evaluation first with: python evaluate.py")
            return
        
        # Initialize analyzer
        analyzer = ErrorAnalyzer('evaluation_results.csv', Config.TEST_FILE)
        
        # Categorize errors
        error_categories = analyzer.categorize_errors()
        
        print("\nError Categories:")
        for category, errors in error_categories.items():
            print(f"  {category}: {len(errors)} cases")
        
        # Identify failure patterns
        patterns = analyzer.identify_failure_patterns()
        
        print("\nPerformance by Shape Type:")
        for shape_type, stats in patterns['by_shape_type'].items():
            print(f"  {shape_type}:")
            print(f"    Mean score: {stats['mean_score']:.4f}")
            print(f"    Failure rate: {stats['failure_rate']:.2%}")
    
    except Exception as e:
        print(f"\n⚠️  Error analysis not available: {e}")

def main():
    """Run all examples"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MIDCURVE GENERATION EXAMPLES                              ║
║                  Demonstrating All Major Features                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    examples = [
        ("Data Validation", example_1_data_validation),
        ("Data Augmentation", example_2_data_augmentation),
        ("Computing Metrics", example_3_compute_metrics),
        ("Inference", example_4_inference),
        ("API Usage", example_5_api_usage),
        ("Batch Evaluation", example_6_batch_evaluation),
        ("Error Analysis", example_7_error_analysis),
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Review the examples above")
    print("  2. Try modifying the parameters")
    print("  3. Run the full pipeline: python run_pipeline.py --full")
    print("  4. Check documentation: README_COMPREHENSIVE.md")
    print()

if __name__ == "__main__":
    main()
