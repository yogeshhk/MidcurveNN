"""
unsloth_trainer.py -- Unsloth-accelerated QLoRA fine-tuning (2-4x faster, 70% less VRAM).
                      Falls back to PEFT+transformers when Unsloth is not installed.

Memory settings for 4 GB VRAM:
  - 4-bit quantization  (~2 GB for the 4B model)
  - batch_size=1, gradient_accumulation=16  (effective batch = 16)
  - max_seq_length=1024
  - gradient_checkpointing enabled
  - 8-bit AdamW optimizer

Install Unsloth (Windows, CUDA 12.1):
    pip install "unsloth[cu121-windows]"

Usage:
    from unsloth_trainer import UnslothTrainer
    trainer = UnslothTrainer()
    trainer.run()

Or as a script:
    cd src/text_based/nemotron3
    conda activate genai
    python unsloth_trainer.py
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

try:
    from unsloth import FastLanguageModel
    _HAS_UNSLOTH = True
    print("[Unsloth] Available - using accelerated training (2-4x faster, 70% less VRAM)")
except ImportError:
    _HAS_UNSLOTH = False
    print("[Unsloth] Not installed - falling back to PEFT + transformers")
    print("          To install: pip install unsloth")
    print("          Windows CUDA 12.1: pip install \"unsloth[cu121-windows]\"")

_BATCH_SIZE     = 1
_GRAD_ACC       = 16
_MAX_SEQ_LEN    = 1024
_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj",
                   "gate_proj", "up_proj", "down_proj"]


class UnslothTrainer:
    """QLoRA fine-tuning via Unsloth (fast) or PEFT (fallback)."""

    def __init__(self, config=None):
        self.cfg = config or Config
        self.model = None
        self.tokenizer = None
        self._used_unsloth = False

    # ── Model loading ─────────────────────────────────────────────────────────

    def _load_with_unsloth(self):
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.cfg.MODEL_ID,
            max_seq_length=_MAX_SEQ_LEN,
            dtype=None,
            load_in_4bit=True,
            device_map="auto",
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=self.cfg.LORA_R,
            target_modules=_TARGET_MODULES,
            lora_alpha=self.cfg.LORA_ALPHA,
            lora_dropout=self.cfg.LORA_DROPOUT,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=self.cfg.SEED,
            use_rslora=False,
        )
        model.print_trainable_parameters()
        return model, tokenizer

    def _load_with_peft(self):
        from transformers import (AutoTokenizer, AutoModelForCausalLM,
                                   BitsAndBytesConfig)
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

        bnb = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
        tokenizer = AutoTokenizer.from_pretrained(self.cfg.MODEL_ID)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        model = AutoModelForCausalLM.from_pretrained(
            self.cfg.MODEL_ID,
            quantization_config=bnb,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
        )
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

        lora_cfg = LoraConfig(
            r=self.cfg.LORA_R,
            lora_alpha=self.cfg.LORA_ALPHA,
            lora_dropout=self.cfg.LORA_DROPOUT,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=_TARGET_MODULES,
        )
        model = get_peft_model(model, lora_cfg)
        model.print_trainable_parameters()
        return model, tokenizer

    def load_model(self):
        """Load model with Unsloth if available, otherwise fall back to PEFT."""
        if _HAS_UNSLOTH:
            self.model, self.tokenizer = self._load_with_unsloth()
            self._used_unsloth = True
        else:
            self.model, self.tokenizer = self._load_with_peft()
            self._used_unsloth = False

    # ── Training args ─────────────────────────────────────────────────────────

    def _make_training_args(self, output_dir):
        use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        common = dict(
            output_dir=str(output_dir),
            num_train_epochs=self.cfg.NUM_EPOCHS,
            per_device_train_batch_size=_BATCH_SIZE,
            per_device_eval_batch_size=_BATCH_SIZE,
            gradient_accumulation_steps=_GRAD_ACC,
            gradient_checkpointing=(not self._used_unsloth),
            learning_rate=self.cfg.LEARNING_RATE,
            lr_scheduler_type="cosine",
            warmup_ratio=0.03,
            bf16=use_bf16,
            fp16=(not use_bf16),
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            seed=self.cfg.SEED,
            logging_steps=10,
            report_to="none",
            optim="adamw_8bit",
            dataloader_pin_memory=False,
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

    # ── Train + save ──────────────────────────────────────────────────────────

    def train(self, train_data, val_data, output_dir):
        """Run SFTTrainer on pre-loaded datasets and return the trainer."""
        if self.model is None:
            raise RuntimeError("Call load_model() before train().")

        training_args, has_sft_config = self._make_training_args(output_dir)

        from trl import SFTTrainer
        trainer_kw = dict(
            model=self.model,
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
            trainer = SFTTrainer(processing_class=self.tokenizer, **trainer_kw)
        except TypeError:
            trainer = SFTTrainer(tokenizer=self.tokenizer, **trainer_kw)

        print("Training ...")
        trainer.train()
        return trainer

    def save(self, trainer, output_dir):
        """Save model, tokenizer, and training_config.json."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        tag = "unsloth" if self._used_unsloth else "peft"
        print(f"\nSaving adapter -> {output_dir}")
        trainer.model.save_pretrained(str(output_dir))
        self.tokenizer.save_pretrained(str(output_dir))

        cfg_dict = {k: v for k, v in vars(self.cfg).items()
                    if not k.startswith("_") and not callable(v)}
        cfg_dict.update({
            "trainer_backend": tag,
            "effective_batch_size": _BATCH_SIZE * _GRAD_ACC,
            "lora_r": self.cfg.LORA_R,
            "lora_alpha": self.cfg.LORA_ALPHA,
            "max_seq_length": _MAX_SEQ_LEN,
            "target_modules": _TARGET_MODULES,
        })
        with open(output_dir / "training_config.json", "w") as fh:
            json.dump(cfg_dict, fh, indent=2, default=str)
        print(f"\nDone! Fine-tuned adapter saved: {output_dir}")

    def run(self, output_dir=None):
        """Orchestrator: load model, load data, train, save."""
        tag = "Unsloth" if _HAS_UNSLOTH else "PEFT"
        if output_dir is None:
            output_dir = Path(self.cfg.BASE_DIR) / "results" / f"Midcurve-Nemotron-{tag}-v1"
        ckpt_dir = Path(self.cfg.BASE_DIR) / "results" / f"checkpoints_{tag.lower()}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nModel ID : {self.cfg.MODEL_ID}")
        print(f"Trainer  : {'Unsloth' if _HAS_UNSLOTH else 'PEFT + HuggingFace SFTTrainer'}")
        print(f"Output   : {output_dir}\n")

        self.load_model()

        print("Loading datasets ...")
        ds = MidcurveDataset(self.tokenizer)
        train_data = ds.load_data(self.cfg.TRAIN_FILE)
        val_data = ds.load_data(self.cfg.VAL_FILE)
        print(f"  train={len(train_data)}  val={len(val_data)}")

        trainer = self.train(train_data, val_data, ckpt_dir)
        self.save(trainer, output_dir)
        print(f"\nNext steps:")
        print(f"  python evaluate.py --model_path results/Midcurve-Nemotron-{tag}-v1")


if __name__ == "__main__":
    UnslothTrainer().run()
