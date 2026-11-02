"""
models/nemotron_qlora.py -- Nemotron-Mini-4B QLoRA with answer-only loss. Training code only: it is
NOT run by the tests and needs a GPU plus a model download (ask the user first).

The Nemotron chat template may reject a system role; sft_common and FewshotPrompt then merge the
system text into the first user turn.
"""
from text_based.models import sft_common
from text_based.models.fewshot_prompt import FewshotPrompt

DEFAULTS = dict(model_id="nvidia/Nemotron-Mini-4B-Instruct", epochs=8, lr=1.0e-4, batch=2, grad_acc=8,
                max_len=1024, lora_r=32, bnb_4bit=True)


def train(cfg):
    c = dict(DEFAULTS)
    c.update({k: v for k, v in cfg.items() if v is not None})
    return sft_common.train(c)


def build_model(cfg):
    c = dict(DEFAULTS)
    c.update({k: v for k, v in cfg.items() if v is not None})
    return FewshotPrompt(model_id=c["model_id"], max_new_tokens=c.get("max_tokens", 768),
                         load_4bit=c["bnb_4bit"], adapter_dir=c.get("adapter_dir"))
