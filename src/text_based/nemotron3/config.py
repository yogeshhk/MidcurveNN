import os


class Config:
    MODEL_ID       = "nvidia/Nemotron-Mini-4B-Instruct"
    NEW_MODEL_NAME = os.path.join("results", "Midcurve-Nemotron-Mini-v1")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data", "csvs")

    TRAIN_FILE = os.path.join(DATA_DIR, "midcurve_llm_train.csv")
    VAL_FILE   = os.path.join(DATA_DIR, "midcurve_llm_val.csv")
    TEST_FILE  = os.path.join(DATA_DIR, "midcurve_llm_test.csv")

    # LoRA
    LORA_R              = 16
    LORA_ALPHA          = 32
    LORA_DROPOUT        = 0.05
    LORA_TARGET_MODULES = "all-linear"  # PEFT auto-detects all linear layers

    # Training
    BATCH_SIZE     = 4
    GRAD_ACC_STEPS = 8
    LEARNING_RATE  = 2e-4
    NUM_EPOCHS     = 3
    MAX_SEQ_LENGTH = 1024
    SEED           = 42

    # Inference
    MAX_NEW_TOKENS = 512
    TEMPERATURE    = 0.1
    DO_SAMPLE      = False

    SYSTEM_PROMPT = (
        "You are a specialized geometric transformation system that converts "
        "2D polygonal profiles into 1D midcurve (medial axis) representations.\n\n"
        "TASK: Given a closed 2D polygon defined by connected line segments, generate "
        "the skeletal centerline that:\n"
        "1. Runs through the geometric center of the shape\n"
        "2. Maintains proper connectivity between segments\n"
        "3. Preserves topological structure (junctions, branches)\n"
        "4. Uses the same JSON B-Rep format as input\n\n"
        "INPUT FORMAT: JSON with \"Points\" (coordinates), \"Lines\" (point index pairs), "
        "\"Segments\" (line groupings)\n"
        "OUTPUT FORMAT: Same JSON structure with medial axis geometry\n\n"
        "CRITICAL RULES:\n"
        "- Output must be valid, parseable JSON\n"
        "- Midcurve points should lie approximately equidistant from profile boundaries\n"
        "- Maintain endpoint connectivity in the Lines array\n"
        "- For junctions, all branches must connect to the junction point\n"
        "- Use floating-point precision (1-4 decimal places)\n\n"
        "Generate ONLY the output JSON, no explanations."
    )
