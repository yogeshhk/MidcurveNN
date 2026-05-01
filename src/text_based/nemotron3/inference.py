"""
inference.py  --  Load fine-tuned Nemotron-Mini and predict midcurves.

Usage:
    cd src/text_based/nemotron3
    conda activate genai
    python inference.py --single          # one sample from the val set
    python inference.py --all             # full val set
    python inference.py --model_path /path/to/adapter
"""
import os
import sys
import json
import ast
import argparse
import torch
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


def _bnb_config():
    try:
        from transformers import BitsAndBytesConfig
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    except Exception:
        return None


class NemotronInference:
    def __init__(self):
        self.model     = None
        self.tokenizer = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_model(self, model_path=None):
        model_path = str(model_path or Path(Config.BASE_DIR) / Config.NEW_MODEL_NAME)
        if not os.path.isdir(model_path):
            raise FileNotFoundError(
                f"Fine-tuned model not found: {model_path}\n"
                "Run train.py first."
            )

        print(f"Loading tokenizer from {model_path}")
        self.tokenizer              = AutoTokenizer.from_pretrained(model_path)
        self.tokenizer.pad_token    = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        bnb = _bnb_config()
        load_kwargs = dict(
            device_map="auto",
            torch_dtype=torch.bfloat16 if bnb else torch.float16,
        )
        if bnb:
            load_kwargs["quantization_config"] = bnb

        print(f"Loading base model: {Config.MODEL_ID}")
        base = AutoModelForCausalLM.from_pretrained(Config.MODEL_ID, **load_kwargs)

        print("Attaching LoRA adapters …")
        self.model = PeftModel.from_pretrained(base, model_path)
        self.model.eval()
        print("Model ready.")

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate_raw(self, profile_brep_json):
        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user",   "content": str(profile_brep_json)},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            out_ids = self.model.generate(
                **inputs,
                max_new_tokens=Config.MAX_NEW_TOKENS,
                do_sample=Config.DO_SAMPLE,
                temperature=Config.TEMPERATURE,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_ids = out_ids[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    # ------------------------------------------------------------------
    # Validation & repair
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(text):
        try:
            return json.loads(text), None
        except json.JSONDecodeError:
            pass
        try:
            return ast.literal_eval(text), None
        except Exception as exc:
            return None, str(exc)

    @staticmethod
    def _check_structure(data):
        missing = {"Points", "Lines", "Segments"} - set(data.keys())
        if missing:
            return f"missing keys: {missing}"
        if not data.get("Points"):
            return "empty Points"
        return None

    @staticmethod
    def _is_connected(data):
        pts   = data.get("Points", [])
        lines = data.get("Lines",  [])
        if not pts:
            return True
        adj = {i: [] for i in range(len(pts))}
        for ln in lines:
            if len(ln) >= 2 and ln[0] < len(pts) and ln[1] < len(pts):
                adj[ln[0]].append(ln[1])
                adj[ln[1]].append(ln[0])
        visited, q = {0}, [0]
        while q:
            n = q.pop()
            for nb in adj[n]:
                if nb not in visited:
                    visited.add(nb); q.append(nb)
        return len(visited) == len(pts)

    @staticmethod
    def _repair(data):
        pts   = data["Points"]
        lines = list(data["Lines"])
        adj   = {i: set() for i in range(len(pts))}
        for ln in lines:
            if len(ln) >= 2:
                adj[ln[0]].add(ln[1]); adj[ln[1]].add(ln[0])

        def _component(start):
            seen, q = {start}, [start]
            while q:
                n = q.pop()
                for nb in adj[n]:
                    if nb not in seen:
                        seen.add(nb); q.append(nb)
            return seen

        all_nodes = set(range(len(pts)))
        visited   = _component(0)
        while visited != all_nodes:
            unvisited = all_nodes - visited
            v, u = min(
                ((v, u) for v in visited for u in unvisited),
                key=lambda vu: sum(
                    (pts[vu[0]][k] - pts[vu[1]][k]) ** 2 for k in range(2)
                ),
            )
            lines.append([v, u])
            adj[v].add(u); adj[u].add(v)
            visited = _component(0)

        data["Lines"] = lines
        return data

    # ------------------------------------------------------------------
    # Public predict
    # ------------------------------------------------------------------

    def predict(self, profile_brep_json, max_retries=3):
        last_raw = ""
        for attempt in range(1, max_retries + 1):
            raw   = self.generate_raw(profile_brep_json)
            last_raw = raw
            data, err = self._parse(raw)

            if err:
                continue

            if self._check_structure(data):
                continue

            if not self._is_connected(data):
                data = self._repair(data)
                return json.dumps(data), {
                    "success": True, "attempts": attempt, "repaired": True
                }

            return raw, {"success": True, "attempts": attempt, "repaired": False}

        return last_raw, {"success": False, "attempts": max_retries}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Run Nemotron-Mini midcurve inference."
    )
    ap.add_argument("--single",     action="store_true",
                    help="One example from the val set")
    ap.add_argument("--all",        action="store_true",
                    help="Full val set")
    ap.add_argument("--model_path", default=None,
                    help="Path to LoRA adapter directory")
    args = ap.parse_args()

    inf = NemotronInference()
    inf.load_model(args.model_path)

    import pandas as pd
    df   = pd.read_csv(Config.VAL_FILE)
    rows = df.iloc[:1] if (args.single or not args.all) else df

    for i, row in rows.iterrows():
        profile = str(row["Profile_brep"])
        truth   = str(row["Midcurve_brep"])
        pred, meta = inf.predict(profile)

        print(f"\n--- Sample {i}  ({row.get('ShapeName', '?')}) ---")
        print(f"Input : {profile[:120]} …")
        print(f"Truth : {truth[:120]} …")
        print(f"Pred  : {pred[:120]} …")
        print(f"Meta  : {meta}")


if __name__ == "__main__":
    main()
