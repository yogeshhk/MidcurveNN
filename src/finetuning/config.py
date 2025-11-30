import torch

class Config:
    # Model Settings
    MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct" 
    NEW_MODEL_NAME = "Midcurve-Qwen-Coder-v1"
    
    # Data Settings
    TRAIN_FILE = "midcurve_llm_train.csv"
    VAL_FILE = "midcurve_llm_val.csv"
    TEST_FILE = "midcurve_llm_test.csv"
    
    # Training Hyperparameters
    LORA_R = 16
    LORA_ALPHA = 16
    LORA_DROPOUT = 0.05
    BATCH_SIZE = 4
    GRAD_ACC_STEPS = 4
    LEARNING_RATE = 2e-4
    NUM_EPOCHS = 3
    MAX_SEQ_LENGTH = 1024
    
    # System Prompt
    SYSTEM_PROMPT = """You are a geometric transformation program. 
    Your task is to transform a 2D polygonal profile (input) into a 1D polyline profile (midcurve). 
    The input and output are provided in JSON B-Rep format containing Points, Lines, and Segments.
    Ensure the output JSON is valid and geometrically accurate."""