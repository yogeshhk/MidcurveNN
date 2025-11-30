import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig, 
    TrainingArguments
)
from peft import LoraConfig
from trl import SFTTrainer
from config import Config
from dataset_loader import MidcurveDataset

def train():
    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right" # Fix for fp16 training

    # 2. Load Dataset
    data_handler = MidcurveDataset(tokenizer)
    train_dataset = data_handler.load_data(Config.TRAIN_FILE)
    val_dataset = data_handler.load_data(Config.VAL_FILE)

    # 3. Quantization Config (4-bit for local consumer GPU)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    # 4. Load Model
    model = AutoModelForCausalLM.from_pretrained(
        Config.MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto"
    )

    # 5. LoRA Configuration
    peft_config = LoraConfig(
        lora_alpha=Config.LORA_ALPHA,
        lora_dropout=Config.LORA_DROPOUT,
        r=Config.LORA_R,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"] 
    )

    # 6. Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=Config.NUM_EPOCHS,
        per_device_train_batch_size=Config.BATCH_SIZE,
        gradient_accumulation_steps=Config.GRAD_ACC_STEPS,
        logging_steps=10,
        save_strategy="epoch",
        learning_rate=Config.LEARNING_RATE,
        fp16=True,
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        group_by_length=True,
        report_to="none" # or "wandb"
    )

    # 7. Trainer
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

    # 8. Train & Save
    print("Starting Training...")
    trainer.train()
    
    print("Saving Model...")
    trainer.model.save_pretrained(Config.NEW_MODEL_NAME)
    tokenizer.save_pretrained(Config.NEW_MODEL_NAME)

if __name__ == "__main__":
    train()