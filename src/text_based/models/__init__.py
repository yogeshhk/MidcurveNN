"""
models/__init__.py -- REGISTRY of text-track models.

Every model module exposes build_model(cfg) returning an object with generate(messages) -> str
(and optionally last_info, a dict with finish_reason / prompt_tokens / completion_tokens / latency_s).
Modules are imported lazily so that heavy dependencies (torch, transformers, peft) are only needed
for the model that is actually requested.
"""
import importlib


class ServerUnavailable(RuntimeError):
    """Raised when an OpenAI-compatible server cannot be reached."""


REGISTRY = {
    "lmstudio_prompt": "text_based.models.lmstudio_prompt",
    "fewshot_prompt": "text_based.models.fewshot_prompt",
    "qwen_qlora": "text_based.models.qwen_qlora",
    "nemotron_qlora": "text_based.models.nemotron_qlora",
}


def build_model(cfg):
    """cfg is a dict with at least 'name' (a REGISTRY key); other keys go to the model."""
    name = cfg.get("name")
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    return importlib.import_module(REGISTRY[name]).build_model(cfg)
