"""
models/fewshot_prompt.py -- local Hugging Face generation of a (base or tuned) causal LM.

Lazy imports: torch / transformers are only imported when the model is loaded. Nothing is
downloaded unless you call generate() with a model id that is not cached yet.
Greedy decoding, no repetition penalty, NO prompt truncation, explicit EOS.
"""
import time

from text_based.common import prompts


class FewshotPrompt:
    def __init__(self, model_id, max_new_tokens=768, device_map="auto", load_4bit=False, adapter_dir=None):
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.device_map = device_map
        self.load_4bit = load_4bit
        self.adapter_dir = adapter_dir
        self.tok = None
        self.model = None
        self.last_info = {}

    def load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tok = AutoTokenizer.from_pretrained(self.model_id)
        kw = dict(device_map=self.device_map)
        if self.load_4bit:
            from transformers import BitsAndBytesConfig
            kw["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16)
        else:
            kw["torch_dtype"] = torch.bfloat16
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, **kw)
        if self.adapter_dir:
            from peft import PeftModel
            self.model = PeftModel.from_pretrained(self.model, self.adapter_dir)  # unmerged, same precision
        self.model.eval()

    def _prompt_ids(self, messages):
        try:
            return self.tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
        except Exception:
            return self.tok.apply_chat_template(prompts.merge_system_into_user(messages),
                                                add_generation_prompt=True, return_tensors="pt")

    def generate(self, messages):
        import torch
        if self.model is None:
            self.load()
        ids = self._prompt_ids(messages).to(self.model.device)
        t0 = time.time()
        with torch.no_grad():
            out = self.model.generate(ids, max_new_tokens=self.max_new_tokens, do_sample=False,
                                      eos_token_id=self.tok.eos_token_id,
                                      pad_token_id=self.tok.pad_token_id or self.tok.eos_token_id)
        new = out[0][ids.shape[1]:]
        self.last_info = dict(finish_reason="stop" if int(new[-1]) == self.tok.eos_token_id else "length",
                              prompt_tokens=int(ids.shape[1]), completion_tokens=int(len(new)),
                              latency_s=round(time.time() - t0, 3))
        return self.tok.decode(new, skip_special_tokens=True).strip()


def build_model(cfg):
    return FewshotPrompt(model_id=cfg.get("model_id") or "Qwen/Qwen2.5-Coder-1.5B-Instruct",
                         max_new_tokens=cfg.get("max_tokens", 768), load_4bit=cfg.get("load_4bit", False),
                         adapter_dir=cfg.get("adapter_dir"))
