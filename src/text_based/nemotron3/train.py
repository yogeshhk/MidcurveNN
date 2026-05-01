"""
train.py  --  QLoRA fine-tuning of nvidia/Nemotron-Mini-4B-Instruct
              on the MidcurveNN BRep text-to-text task.

Usage:
    cd src/text_based/nemotron3
    conda activate genai
    python train.py
"""
import os
import sys
import json
import torch
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config
from dataset_loader import MidcurveDataset

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

try:
    from trl import SFTConfig, SFTTrainer
    _HAS_SFT_CONFIG = True
except ImportError:
    from trl import SFTTrainer
    from transformers import TrainingArguments
    _HAS_SFT_CONFIG = False


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def _bnb_config():
    """Returns a 4-bit BitsAndBytesConfig, or None if unavailable."""
    try:
        from transformers import BitsAndBytesConfig
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    except Exception as exc:
        print(f"WARNING: 4-bit BitsAndBytes config unavailable ({exc}); "
              "model will load in float16")
        return None


def load_model_and_tokenizer():
    print(f"Loading tokenizer: {Config.MODEL_ID}")
    tokenizer               = AutoTokenizer.from_pretrained(Config.MODEL_ID)
    tokenizer.pad_token     = tokenizer.eos_token
    tokenizer.padding_side  = "right"

    bnb = _bnb_config()
    load_kwargs = dict(device_map="auto",
                       torch_dtype=torch.bfloat16 if bnb else torch.float16)
    if bnb:
        load_kwargs["quantization_config"] = bnb
        print("4-bit QLoRA enabled")

    print(f"Loading model: {Config.MODEL_ID}")
    model = AutoModelForCausalLM.from_pretrained(Config.MODEL_ID, **load_kwargs)
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=True
    )

    lora_cfg = LoraConfig(
        r=Config.LORA_R,
        lora_alpha=Config.LORA_ALPHA,
        lora_dropout=Config.LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=Config.LORA_TARGET_MODULES,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    return model, tokenizer


# ---------------------------------------------------------------------------
# Training args
# ---------------------------------------------------------------------------

def _make_args(output_dir):
    common = dict(
        output_dir=str(output_dir),
        num_train_epochs=Config.NUM_EPOCHS,
        per_device_train_batch_size=Config.BATCH_SIZE,
        per_device_eval_batch_size=Config.BATCH_SIZE,
        gradient_accumulation_steps=Config.GRAD_ACC_STEPS,
        learning_rate=Config.LEARNING_RATE,
        lr_scheduler_type="cosine",
        bf16=True,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        seed=Config.SEED,
        logging_steps=10,
        report_to="none",
    )
    if _HAS_SFT_CONFIG:
        return SFTConfig(
            **common,
            max_seq_length=Config.MAX_SEQ_LENGTH,
            dataset_text_field="text",
            packing=False,
        )
    else:
        from transformers import TrainingArguments
        return TrainingArguments(**common)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ckpt_dir      = Path(Config.BASE_DIR) / "results" / "checkpoints"
    model_out_dir = Path(Config.BASE_DIR) / Config.NEW_MODEL_NAME
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    model_out_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model_and_tokenizer()

    print("Loading datasets …")
    ds          = MidcurveDataset(tokenizer)
    train_data  = ds.load_data(Config.TRAIN_FILE)
    val_data    = ds.load_data(Config.VAL_FILE)
    print(f"  train={len(train_data)}  val={len(val_data)}")

    args = _make_args(ckpt_dir)

    # SFTTrainer accepted `tokenizer` up to TRL ~0.11 and `processing_class`
    # from 0.12+; try new name first, fall back to old.
    trainer_kwargs = dict(
        model=model,
        args=args,
        train_dataset=train_data,
        eval_dataset=val_data,
    )
    if not _HAS_SFT_CONFIG:
        trainer_kwargs.update(
            max_seq_length=Config.MAX_SEQ_LENGTH,
            dataset_text_field="text",
            packing=False,
        )

    try:
        trainer = SFTTrainer(processing_class=tokenizer, **trainer_kwargs)
    except TypeError:
        trainer = SFTTrainer(tokenizer=tokenizer, **trainer_kwargs)

    print("Training …")
    trainer.train()

    print(f"Saving model → {model_out_dir}")
    trainer.model.save_pretrained(str(model_out_dir))
    tokenizer.save_pretrained(str(model_out_dir))

    cfg_path = model_out_dir / "training_config.json"
    cfg_dict = {k: v for k, v in vars(Config).items()
                if not k.startswith("_") and not callable(v)}
    with open(cfg_path, "w") as fh:
        json.dump(cfg_dict, fh, indent=2, default=str)

    print(f"Done. Fine-tuned model saved to: {model_out_dir}")


if __name__ == "__main__":
    main()
