import torch

class Config:
    # Model Settings
    MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct" 
    NEW_MODEL_NAME = "Midcurve-Qwen-Coder-v1"
    
    # Alternative models for comparison
    MODELS_TO_COMPARE = [
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "google/gemma-2-9b-it",
        "mistralai/Mistral-7B-Instruct-v0.2"
    ]
    
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, "data")
    
    # Data Settings
    TRAIN_FILE = os.path.join(data_dir, "midcurve_llm_train.csv")
    VAL_FILE = os.path.join(data_dir, "midcurve_llm_val.csv")
    TEST_FILE = os.path.join(data_dir, "midcurve_llm_test.csv")
    
    # Data format (csv or jsonl)
    DATA_FORMAT = "csv"  # or "jsonl" for better format
    
    # Training Hyperparameters
    LORA_R = 16
    LORA_ALPHA = 32  # Increased from 16
    LORA_DROPOUT = 0.05
    BATCH_SIZE = 4
    GRAD_ACC_STEPS = 4
    LEARNING_RATE = 2e-4
    NUM_EPOCHS = 3
    MAX_SEQ_LENGTH = 1024
    
    # Advanced Training Settings
    USE_GRADIENT_CHECKPOINTING = True
    USE_FLASH_ATTENTION_2 = True
    EARLY_STOPPING_PATIENCE = 3
    EARLY_STOPPING_METRIC = "hausdorff_distance"
    LR_SCHEDULER = "cosine_with_restarts"
    MIXED_PRECISION = "bf16"  # or "fp16"
    SEED = 42
    
    # Geometric Loss Settings
    USE_GEOMETRIC_LOSS = True
    GEOMETRIC_LOSS_WEIGHT = 0.1
    TOKEN_LOSS_WEIGHT = 0.9
    
    # Curriculum Learning
    USE_CURRICULUM = True
    CURRICULUM_STAGES = ["simple", "moderate", "complex"]
    
    # Data Augmentation
    AUGMENTATION_NOISE_LEVEL = 0.01  # 1% coordinate noise
    AUGMENTATION_MULTIPLIER = 5  # Generate 5x training data
    
    # Validation & Checkpointing
    VALIDATION_SAMPLES = 10
    SAVE_TOP_K_CHECKPOINTS = 3
    CHECKPOINT_METRICS = ["hausdorff_distance", "json_validity", "combined_score"]
    
    # Inference Settings
    MAX_NEW_TOKENS = 512
    TEMPERATURE = 0.1
    DO_SAMPLE = False
    NUM_BEAMS = 1  # Set >1 for beam search
    
    # Logging
    USE_WANDB = False  # Set to True if wandb available
    WANDB_PROJECT = "midcurve-llm"
    LOG_STEPS = 10
    
    # System Prompt - Enhanced
    SYSTEM_PROMPT = """You are a specialized geometric transformation system that converts 2D polygonal profiles into 1D midcurve (medial axis) representations.

TASK: Given a closed 2D polygon defined by connected line segments, generate the skeletal centerline that:
1. Runs through the geometric center of the shape
2. Maintains proper connectivity between segments
3. Preserves topological structure (junctions, branches)
4. Uses the same JSON B-Rep format as input

INPUT FORMAT: JSON with "Points" (coordinates), "Lines" (point indices), "Segments" (line groupings)
OUTPUT FORMAT: Same JSON structure with medial axis geometry

CRITICAL RULES:
- Output must be valid, parseable JSON
- Midcurve points should lie approximately equidistant from profile boundaries
- Maintain endpoint connectivity in the Lines array
- For junctions, all branches should connect to the junction point
- Use floating-point precision (1-4 decimal places)

Generate ONLY the output JSON, no explanations."""

    # Few-shot examples for complex shapes
    FEW_SHOT_EXAMPLES = [
        {
            "input": '{"Points": [[0.0, 25.0], [25.0, 25.0], [25.0, 0.0], [20.0, 0.0], [20.0, 20.0], [0.0, 20.0]], "Lines": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]], "Segments": [[0, 1, 2, 3, 4, 5]]}',
            "output": '{"Points": [[12.5, 0.0], [12.5, 22.5], [25.0, 22.5], [0.0, 22.5]], "Lines": [[0, 1], [1, 2], [3, 1]], "Segments": [[0], [1], [2]]}'
        }
    ]
