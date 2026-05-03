"""
train_unsloth.py  --  QLoRA fine-tuning with Unsloth (2-4x faster, 70% less VRAM).
                       Automatically falls back to PEFT+transformers when Unsloth
                       is not installed.

Memory settings for 4 GB VRAM:
  - 4-bit quantization  (~2 GB for the 4B model)
  - batch_size=1, gradient_accumulation=16  (effective batch = 16)
  - max_seq_length=1024
  - gradient_checkpointing enabled
  - 8-bit AdamW optimizer

Install Unsloth (Windows, CUDA 12.1):
    pip install "unsloth[cu121-windows]"
    # or for CUDA 11.8:
    pip install "unsloth[cu118-windows]"
    # or generic (auto-detects CUDA):
    pip install unsloth

Usage:
    cd src/text_based/nemotron3
    conda activate genai
    python train_unsloth.py

After training, evaluate with:
    python evaluate.py --model_path results/Midcurve-Nemotron-Unsloth-v1
"""
import os
import sys
import json
import torch
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from config import Config
from dataset_loader import MidcurveDataset

# ── Try Unsloth ───────────────────────────────────────────────────────────────
try:
    from unsloth import FastLanguageModel, is_bfloat16_supported
    _HAS_UNSLOTH = True
    print("[Unsloth] Available - using accelerated training (2-4x faster, 70% less VRAM)")
except ImportError:
    _HAS_UNSLOTH = False
    print("[Unsloth] Not installed - falling back to PEFT + transformers")
    print("          To install: pip install unsloth")
    print("          Windows CUDA 12.1: pip install \"unsloth[cu121-windows]\"")

# ── Memory-efficient hyperparameters for 4 GB VRAM ────────────────────────────
_BATCH_SIZE     = 1
_GRAD_ACC       = 16
_MAX_SEQ_LEN    = 1024
_LORA_R         = 16
_LORA_ALPHA     = 32
_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj",
                   "gate_proj", "up_proj", "down_proj"]


# ── Model loading helpers ──────────────────────────────────────────────────────

def _load_with_unsloth():
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=Config.MODEL_ID,
        max_seq_length=_MAX_SEQ_LEN,
        dtype=None,            # auto-detects bfloat16 / float16
        load_in_4bit=True,
        device_map="auto",
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=_LORA_R,
        target_modules=_TARGET_MODULES,
        lora_alpha=_LORA_ALPHA,
        lora_dropout=Config.LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",   # Unsloth's memory-efficient impl
        random_state=Config.SEED,
        use_rslora=False,
    )
    model.print_trainable_parameters()
    return model, tokenizer


def _load_with_peft():
    from transformers import (AutoTokenizer, AutoModelForCausalLM,
                               BitsAndBytesConfig)
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    )
    tokenizer               = AutoTokenizer.from_pretrained(Config.MODEL_ID)
    tokenizer.pad_token     = tokenizer.eos_token
    tokenizer.padding_side  = "right"

    model = AutoModelForCausalLM.from_pretrained(
        Config.MODEL_ID,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    lora_cfg = LoraConfig(
        r=_LORA_R,
        lora_alpha=_LORA_ALPHA,
        lora_dropout=Config.LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=_TARGET_MODULES,
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()
    return model, tokenizer


# ── Training args ──────────────────────────────────────────────────────────────

def _make_training_args(output_dir: str, use_unsloth: bool):
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    common = dict(
        output_dir=output_dir,
        num_train_epochs=Config.NUM_EPOCHS,
        per_device_train_batch_size=_BATCH_SIZE,
        per_device_eval_batch_size=_BATCH_SIZE,
        gradient_accumulation_steps=_GRAD_ACC,
        # gradient_checkpointing handled by Unsloth; enable for PEFT fallback
        gradient_checkpointing=(not use_unsloth),
        learning_rate=Config.LEARNING_RATE,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        bf16=use_bf16,
        fp16=(not use_bf16),
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        seed=Config.SEED,
        logging_steps=10,
        report_to="none",
        optim="adamw_8bit",           # 8-bit optimizer saves ~500 MB VRAM
        dataloader_pin_memory=False,   # reduces CPU->GPU overhead on Windows
    )

    try:
        from trl import SFTConfig
        return SFTConfig(
            **common,
            max_seq_length=_MAX_SEQ_LEN,
            dataset_text_field="text",
            packing=False,
        ), True
    except (ImportError, TypeError):
        from transformers import TrainingArguments
        return TrainingArguments(**common), False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    tag           = "Unsloth" if _HAS_UNSLOTH else "PEFT"
    model_out_dir = Path(Config.BASE_DIR) / "results" / f"Midcurve-Nemotron-{tag}-v1"
    ckpt_dir      = Path(Config.BASE_DIR) / "results" / f"checkpoints_{tag.lower()}"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    model_out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nModel ID : {Config.MODEL_ID}")
    print(f"Trainer  : {'Unsloth' if _HAS_UNSLOTH else 'PEFT + HuggingFace SFTTrainer'}")
    print(f"Output   : {model_out_dir}\n")

    if _HAS_UNSLOTH:
        model, tokenizer = _load_with_unsloth()
    else:
        model, tokenizer = _load_with_peft()

    print("Loading datasets ...")
    ds         = MidcurveDataset(tokenizer)
    train_data = ds.load_data(Config.TRAIN_FILE)
    val_data   = ds.load_data(Config.VAL_FILE)
    print(f"  train={len(train_data)}  val={len(val_data)}")

    training_args, has_sft_config = _make_training_args(str(ckpt_dir), _HAS_UNSLOTH)

    from trl import SFTTrainer
    trainer_kw = dict(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=val_data,
    )
    if not has_sft_config:
        trainer_kw.update(
            max_seq_length=_MAX_SEQ_LEN,
            dataset_text_field="text",
            packing=False,
        )
    try:
        trainer = SFTTrainer(processing_class=tokenizer, **trainer_kw)
    except TypeError:
        trainer = SFTTrainer(tokenizer=tokenizer, **trainer_kw)

    print("Training ...")
    trainer.train()

    print(f"\nSaving adapter -> {model_out_dir}")
    trainer.model.save_pretrained(str(model_out_dir))
    tokenizer.save_pretrained(str(model_out_dir))

    cfg_path = model_out_dir / "training_config.json"
    cfg_dict = {k: v for k, v in vars(Config).items()
                if not k.startswith("_") and not callable(v)}
    cfg_dict.update({
        "trainer_backend": "unsloth" if _HAS_UNSLOTH else "peft",
        "effective_batch_size": _BATCH_SIZE * _GRAD_ACC,
        "lora_r": _LORA_R,
        "lora_alpha": _LORA_ALPHA,
        "max_seq_length": _MAX_SEQ_LEN,
        "target_modules": _TARGET_MODULES,
    })
    with open(cfg_path, "w") as fh:
        json.dump(cfg_dict, fh, indent=2, default=str)

    print(f"\nDone! Fine-tuned adapter saved: {model_out_dir}")
    print(f"\nNext steps:")
    print(f"  python evaluate.py --model_path results/Midcurve-Nemotron-{tag}-v1")


if __name__ == "__main__":
    main()
