"""
hf_sft_trainer.py -- QLoRA fine-tuning using PEFT + HuggingFace SFTTrainer.

Usage:
    from hf_sft_trainer import HFSFTTrainer
    trainer = HFSFTTrainer()
    trainer.run()

Or as a script:
    cd src/text_based/nemotron3
    conda activate genai
    python hf_sft_trainer.py
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

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

try:
    from trl import SFTConfig, SFTTrainer
    _HAS_SFT_CONFIG = True
except ImportError:
    from trl import SFTTrainer
    _HAS_SFT_CONFIG = False


class HFSFTTrainer:
    """QLoRA fine-tuning using PEFT + HuggingFace SFTTrainer."""

    def __init__(self, config=None):
        self.cfg = config or Config
        self.model = None
        self.tokenizer = None

    # ── Model loading ─────────────────────────────────────────────────────────

    def _bnb_config(self):
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

    def load_model(self):
        """Load base model with 4-bit quantization and attach LoRA adapters."""
        print(f"Loading tokenizer: {self.cfg.MODEL_ID}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.cfg.MODEL_ID)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

        bnb = self._bnb_config()
        load_kwargs = dict(
            device_map="auto",
            torch_dtype=torch.bfloat16 if bnb else torch.float16,
        )
        if bnb:
            load_kwargs["quantization_config"] = bnb
            print("4-bit QLoRA enabled")

        print(f"Loading model: {self.cfg.MODEL_ID}")
        self.model = AutoModelForCausalLM.from_pretrained(self.cfg.MODEL_ID, **load_kwargs)
        self.model = prepare_model_for_kbit_training(
            self.model, use_gradient_checkpointing=True
        )

        lora_cfg = LoraConfig(
            r=self.cfg.LORA_R,
            lora_alpha=self.cfg.LORA_ALPHA,
            lora_dropout=self.cfg.LORA_DROPOUT,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=self.cfg.LORA_TARGET_MODULES,
        )
        self.model = get_peft_model(self.model, lora_cfg)
        self.model.print_trainable_parameters()

    # ── Training args ─────────────────────────────────────────────────────────

    def _make_training_args(self, output_dir):
        use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        common = dict(
            output_dir=str(output_dir),
            num_train_epochs=self.cfg.NUM_EPOCHS,
            per_device_train_batch_size=self.cfg.BATCH_SIZE,
            per_device_eval_batch_size=self.cfg.BATCH_SIZE,
            gradient_accumulation_steps=self.cfg.GRAD_ACC_STEPS,
            gradient_checkpointing=True,
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
        if _HAS_SFT_CONFIG:
            return SFTConfig(
                **common,
                max_seq_length=self.cfg.MAX_SEQ_LENGTH,
                dataset_text_field="text",
                packing=False,
            )
        from transformers import TrainingArguments
        return TrainingArguments(**common)

    # ── Train + save ──────────────────────────────────────────────────────────

    def train(self, train_data, val_data, output_dir):
        """Run SFTTrainer on pre-loaded datasets and return the trainer."""
        if self.model is None:
            raise RuntimeError("Call load_model() before train().")

        args = self._make_training_args(output_dir)
        trainer_kwargs = dict(
            model=self.model,
            args=args,
            train_dataset=train_data,
            eval_dataset=val_data,
        )
        if not _HAS_SFT_CONFIG:
            trainer_kwargs.update(
                max_seq_length=self.cfg.MAX_SEQ_LENGTH,
                dataset_text_field="text",
                packing=False,
            )
        try:
            trainer = SFTTrainer(processing_class=self.tokenizer, **trainer_kwargs)
        except TypeError:
            trainer = SFTTrainer(tokenizer=self.tokenizer, **trainer_kwargs)

        print("Training ...")
        trainer.train()
        return trainer

    def save(self, trainer, output_dir):
        """Save model, tokenizer, and training_config.json."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Saving model -> {output_dir}")
        trainer.model.save_pretrained(str(output_dir))
        self.tokenizer.save_pretrained(str(output_dir))

        cfg_dict = {k: v for k, v in vars(self.cfg).items()
                    if not k.startswith("_") and not callable(v)}
        with open(output_dir / "training_config.json", "w") as fh:
            json.dump(cfg_dict, fh, indent=2, default=str)
        print(f"Done. Fine-tuned model saved to: {output_dir}")

    def run(self, output_dir=None):
        """Orchestrator: load model, load data, train, save."""
        if output_dir is None:
            output_dir = Path(self.cfg.BASE_DIR) / self.cfg.NEW_MODEL_NAME
        ckpt_dir = Path(self.cfg.BASE_DIR) / "results" / "checkpoints"
        ckpt_dir.mkdir(parents=True, exist_ok=True)

        self.load_model()

        print("Loading datasets ...")
        ds = MidcurveDataset(self.tokenizer)
        train_data = ds.load_data(self.cfg.TRAIN_FILE)
        val_data = ds.load_data(self.cfg.VAL_FILE)
        print(f"  train={len(train_data)}  val={len(val_data)}")

        trainer = self.train(train_data, val_data, ckpt_dir)
        self.save(trainer, output_dir)


if __name__ == "__main__":
    HFSFTTrainer().run()
