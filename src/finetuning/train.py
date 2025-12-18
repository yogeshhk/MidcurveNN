import torch
import argparse
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig, 
    TrainingArguments,
    TrainerCallback
)
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer
from config import Config
from dataset_loader import MidcurveDataset
from metrics import GeometricMetrics
import numpy as np
import pandas as pd
from typing import Dict
import os

# Optional: Import wandb if available
try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    print("wandb not available. Install with: pip install wandb")

class GeometricValidationCallback(TrainerCallback):
    """Custom callback for geometric validation during training"""
    
    def __init__(self, eval_dataset, tokenizer, validation_samples=10):
        self.eval_dataset = eval_dataset
        self.tokenizer = tokenizer
        self.validation_samples = validation_samples
        self.best_metric = float('inf')
    
    def on_epoch_end(self, args, state, control, model, **kwargs):
        """Run geometric validation at epoch end"""
        print("\n" + "="*60)
        print(f"Running Geometric Validation (Epoch {state.epoch})")
        print("="*60)
        
        model.eval()
        metrics_list = []
        
        # Sample random examples
        indices = np.random.choice(
            len(self.eval_dataset), 
            min(self.validation_samples, len(self.eval_dataset)),
            replace=False
        )
        
        for idx in indices:
            try:
                example = self.eval_dataset[int(idx)]
                text = example['text']
                
                # Extract profile and ground truth from formatted text
                # This is simplified - in practice, need proper parsing
                inputs = self.tokenizer([text], return_tensors="pt").to(model.device)
                
                with torch.no_grad():
                    outputs = model.generate(
                        inputs.input_ids,
                        max_new_tokens=256,
                        do_sample=False,
                        temperature=0.1
                    )
                
                # Decode and compute metrics
                # This is a placeholder - actual implementation needs proper extraction
                
            except Exception as e:
                print(f"Error in validation sample {idx}: {e}")
                continue
        
        if metrics_list:
            avg_metrics = {
                key: np.mean([m[key] for m in metrics_list if key in m])
                for key in metrics_list[0].keys()
            }
            
            print("\nValidation Metrics:")
            for key, value in avg_metrics.items():
                print(f"  {key}: {value:.4f}")
            
            # Log to wandb if available
            if WANDB_AVAILABLE and Config.USE_WANDB:
                wandb.log({f"val_{k}": v for k, v in avg_metrics.items()})
        
        model.train()

def setup_wandb():
    """Initialize Weights & Biases logging"""
    if WANDB_AVAILABLE and Config.USE_WANDB:
        wandb.init(
            project=Config.WANDB_PROJECT,
            config={
                "model_id": Config.MODEL_ID,
                "lora_r": Config.LORA_R,
                "lora_alpha": Config.LORA_ALPHA,
                "learning_rate": Config.LEARNING_RATE,
                "batch_size": Config.BATCH_SIZE,
                "num_epochs": Config.NUM_EPOCHS,
            }
        )

def train():
    """Enhanced training function with all improvements"""
    parser = argparse.ArgumentParser(description="MidcurveLLM Fine-tuning")
    parser.add_argument("--model_path", type=str, help="Path to local model or HuggingFace model ID")
    parser.add_argument("--smoke_test", action="store_true", help="Run a quick smoke test (1 epoch, few steps)")
    args = parser.parse_args()

    if args.model_path:
        print(f"Overriding MODEL_ID with: {args.model_path}")
        Config.MODEL_ID = args.model_path
        
    if args.smoke_test:
        print("SMOKE TEST MODE ENABLED: Reducing epochs and steps.")
        Config.NUM_EPOCHS = 1
        Config.MAX_SEQ_LENGTH = 128
        Config.LOG_STEPS = 1


    # Set seed for reproducibility
    torch.manual_seed(Config.SEED)
    np.random.seed(Config.SEED)
    
    # Setup logging
    setup_wandb()
    
    # 1. Load Tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    # 2. Load Dataset
    print("Loading datasets...")
    data_handler = MidcurveDataset(tokenizer)
    train_dataset = data_handler.load_data(Config.TRAIN_FILE)
    val_dataset = data_handler.load_data(Config.VAL_FILE)
    
    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    
    # 3. Quantization Config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if Config.MIXED_PRECISION == "bf16" else torch.float16,
        bnb_4bit_use_double_quant=True,  # Nested quantization
    )
    
    # 4. Load Model
    print(f"Loading model: {Config.MODEL_ID}")
    model = AutoModelForCausalLM.from_pretrained(
        Config.MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        use_cache=False if Config.USE_GRADIENT_CHECKPOINTING else True,
        attn_implementation="flash_attention_2" if Config.USE_FLASH_ATTENTION_2 else "sdpa"
    )
    
    # Enable gradient checkpointing
    if Config.USE_GRADIENT_CHECKPOINTING:
        model.gradient_checkpointing_enable()
    
    # 5. LoRA Configuration
    print("Configuring LoRA...")
    peft_config = LoraConfig(
        lora_alpha=Config.LORA_ALPHA,
        lora_dropout=Config.LORA_DROPOUT,
        r=Config.LORA_R,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", 
                       "gate_proj", "up_proj", "down_proj"]
    )
    
    # 6. Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=Config.NUM_EPOCHS,
        per_device_train_batch_size=Config.BATCH_SIZE,
        per_device_eval_batch_size=Config.BATCH_SIZE,
        gradient_accumulation_steps=Config.GRAD_ACC_STEPS,
        
        # Optimization
        optim="paged_adamw_8bit",
        learning_rate=Config.LEARNING_RATE,
        weight_decay=0.01,
        max_grad_norm=0.3,
        
        # Learning rate schedule
        lr_scheduler_type="cosine_with_restarts" if Config.LR_SCHEDULER == "cosine_with_restarts" else "cosine",
        warmup_ratio=0.03,
        
        # Precision
        fp16=Config.MIXED_PRECISION == "fp16",
        bf16=Config.MIXED_PRECISION == "bf16",
        
        # Logging & Evaluation
        logging_steps=Config.LOG_STEPS,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=Config.SAVE_TOP_K_CHECKPOINTS,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        
        # Other
        group_by_length=True,
        report_to="wandb" if (WANDB_AVAILABLE and Config.USE_WANDB) else "none",
        seed=Config.SEED,
        gradient_checkpointing=Config.USE_GRADIENT_CHECKPOINTING,
    )
    
    # 7. Initialize Trainer
    print("Initializing trainer...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=Config.MAX_SEQ_LENGTH,
        tokenizer=tokenizer,
        args=training_args,
        callbacks=[GeometricValidationCallback(val_dataset, tokenizer, Config.VALIDATION_SAMPLES)]
    )
    
    # 8. Train
    print("\n" + "="*60)
    print("Starting Training")
    print("="*60 + "\n")
    
    trainer.train()
    
    # 9. Save final model
    print("\n" + "="*60)
    print("Saving Model")
    print("="*60)
    
    final_model_dir = Config.NEW_MODEL_NAME
    trainer.model.save_pretrained(final_model_dir)
    tokenizer.save_pretrained(final_model_dir)
    
    # Save training config
    import json
    config_dict = {k: v for k, v in vars(Config).items() if not k.startswith('_')}
    with open(f"{final_model_dir}/training_config.json", 'w') as f:
        json.dump(config_dict, f, indent=2, default=str)
    
    print(f"Model saved to: {final_model_dir}")
    
    # Close wandb
    if WANDB_AVAILABLE and Config.USE_WANDB:
        wandb.finish()
    
    print("\nTraining complete!")

if __name__ == "__main__":
    train()
