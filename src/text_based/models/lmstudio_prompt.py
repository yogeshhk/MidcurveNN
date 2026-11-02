"""
models/lmstudio_prompt.py -- any OpenAI-compatible server (LM Studio, llama.cpp, vLLM ...).

    model = build_model({"name": "lmstudio_prompt", "base_url": "http://localhost:1234/v1",
                         "model_id": "gemma-2-2b-it"})
    text = model.generate(messages)

Greedy (temperature 0) by default with a generous max_tokens. If the server's chat template rejects
the system role (Gemma 2), the system text is merged into the first user turn and the call retried.
"""
import time
import urllib.error
import urllib.request

from text_based.models import ServerUnavailable
from text_based import prompts

DEFAULT_URL = "http://localhost:1234/v1"
FRIENDLY = ("Cannot reach an OpenAI-compatible server at %s. Start LM Studio, load a model, and enable the "
            "local server (Developer tab, default port 1234), or pass --base-url.")


def probe_server(base_url=DEFAULT_URL, timeout=3.0):
    """Return the list of model ids, or raise ServerUnavailable (3 s timeout by default)."""
    url = base_url.rstrip("/") + "/models"
    try:
        import json
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m["id"] for m in data.get("data", [])]
    except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
        raise ServerUnavailable(FRIENDLY % base_url + " (%s)" % exc)


class LMStudioPrompt:
    def __init__(self, base_url=DEFAULT_URL, model_id=None, temperature=0.0, max_tokens=2048, timeout=300,
                 api_key="lm-studio", seed=0, response_format=None):
        from openai import OpenAI  # installed in the genai env
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.seed = seed
        self.response_format = response_format
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=timeout, max_retries=0)
        self.model_id = model_id
        self._merge_system = False
        self.last_info = {}

    def list_models(self):
        return probe_server(self.base_url)

    def _resolve_model(self):
        if self.model_id:
            return self.model_id
        ids = [m for m in self.list_models() if "embed" not in m.lower()]
        if not ids:
            raise ServerUnavailable("server at %s lists no chat model; load one in LM Studio" % self.base_url)
        self.model_id = ids[0]
        return self.model_id

    def _call(self, messages):
        import openai
        kw = dict(model=self._resolve_model(), messages=messages, temperature=self.temperature,
                  max_tokens=self.max_tokens, seed=self.seed)
        if self.response_format:
            kw["response_format"] = self.response_format
        try:
            return self.client.chat.completions.create(**kw)
        except openai.APITimeoutError as exc:  # slow generation is a per-item error, not a dead server
            raise TimeoutError("request exceeded %ss: %s" % (self.client.timeout, exc))
        except openai.APIConnectionError as exc:
            raise ServerUnavailable(FRIENDLY % self.base_url + " (%s)" % exc)

    def generate(self, messages):
        import openai
        msgs = prompts.merge_system_into_user(messages) if self._merge_system else messages
        t0 = time.time()
        try:
            resp = self._call(msgs)
        except openai.BadRequestError as exc:
            if self._merge_system or "system" not in str(exc).lower() and "role" not in str(exc).lower():
                raise
            self._merge_system = True
            resp = self._call(prompts.merge_system_into_user(messages))
        choice = resp.choices[0]
        usage = getattr(resp, "usage", None)
        self.last_info = dict(finish_reason=choice.finish_reason,
                              prompt_tokens=getattr(usage, "prompt_tokens", None),
                              completion_tokens=getattr(usage, "completion_tokens", None),
                              latency_s=round(time.time() - t0, 3),
                              system_merged=self._merge_system)
        return choice.message.content or ""


def build_model(cfg):
    return LMStudioPrompt(base_url=cfg.get("base_url") or DEFAULT_URL, model_id=cfg.get("model_id"),
                          temperature=cfg.get("temperature", 0.0), max_tokens=cfg.get("max_tokens", 2048),
                          timeout=cfg.get("timeout", 300), seed=cfg.get("seed", 0),
                          response_format=cfg.get("response_format"))
