"""
models/qwen_qlora.py -- Qwen2.5-Coder QLoRA with answer-only loss. Training code only: it is NOT run
by the tests and needs a GPU plus a model download (ask the user first).

    python run.py train --model qwen_qlora --format mcv2 [--max-steps 5]
    python run.py eval  --model qwen_qlora --format mcv2 --adapter-dir runs/qwen_qlora__mcv2
"""
from text_based.common import sft_common
from text_based.methods.fewshot_prompt.model import FewshotPrompt

DEFAULTS = dict(model_id="Qwen/Qwen2.5-Coder-1.5B-Instruct", epochs=8, lr=1.5e-4, batch=4, grad_acc=4,
                max_len=1024, lora_r=32, bnb_4bit=True)


def train(cfg):
    c = dict(DEFAULTS)
    c.update({k: v for k, v in cfg.items() if v is not None})
    return sft_common.train(c)


def build_model(cfg):
    """Inference with the adapter in the SAME precision as training (4-bit base, unmerged)."""
    c = dict(DEFAULTS)
    c.update({k: v for k, v in cfg.items() if v is not None})
    return FewshotPrompt(model_id=c["model_id"], max_new_tokens=c.get("max_tokens", 768),
                         load_4bit=c["bnb_4bit"], adapter_dir=c.get("adapter_dir"))
