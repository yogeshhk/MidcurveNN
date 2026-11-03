"""
methods/__init__.py -- REGISTRY of text-track models.

Every model module exposes build_model(cfg) returning an object with generate(messages) -> str
(and optionally last_info, a dict with finish_reason / prompt_tokens / completion_tokens / latency_s).
Modules are imported lazily so that heavy dependencies (torch, transformers, peft) are only needed
for the model that is actually requested.

Layout: methods/<method>/model.py for methods with only new code (fewshot_prompt, lmstudio_prompt);
methods/<method>/enhanced/model.py for qwen_qlora and nemotron_qlora, whose older implementations
(finetuning/, nemotron3/) sit at the top level of their method folder. code_t5, ludwig and manual_prompt hold
older notebooks/scripts only and are not registry entries.
"""
import importlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))


class ServerUnavailable(RuntimeError):
    """Raised when an OpenAI-compatible server cannot be reached."""


REGISTRY = {
    "lmstudio_prompt": "text_based.methods.lmstudio_prompt.model",
    "fewshot_prompt": "text_based.methods.fewshot_prompt.model",
    "qwen_qlora": "text_based.methods.qwen_qlora.enhanced.model",
    "nemotron_qlora": "text_based.methods.nemotron_qlora.enhanced.model",
}


def runs_dir(name):
    """Run root of a registry model: the `runs/` folder next to its model.py."""
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    parts = REGISTRY[name].split(".")[2:-1]          # drop 'text_based', 'methods' and 'model'
    return os.path.join(HERE, *parts, "runs")


def build_model(cfg):
    """cfg is a dict with at least 'name' (a REGISTRY key); other keys go to the model."""
    name = cfg.get("name")
    if name not in REGISTRY:
        raise KeyError("unknown model %r; choose from %s" % (name, sorted(REGISTRY)))
    return importlib.import_module(REGISTRY[name]).build_model(cfg)
