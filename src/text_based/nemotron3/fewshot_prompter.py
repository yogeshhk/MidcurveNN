"""
fewshot_prompter.py -- Few-shot prompting with the base Nemotron model (no fine-tuning).

Uses 2 few-shot examples (I-shape, L-shape) to guide the base model's output,
then repairs the JSON to ensure Lines are always populated (avoids isolated-dot results).

Hardware: 4 GB GPU VRAM is sufficient (4-bit model ~2 GB + KV cache).

Usage:
    from fewshot_prompter import FewShotPrompter
    prompter = FewShotPrompter()
    prompter.load_model()
    result = prompter.predict(profile_json)
    prompter.evaluate()

Or as a script:
    cd src/text_based/nemotron3
    conda activate genai
    python fewshot_prompter.py
"""
import os
import sys
import json
import ast
import shutil
import torch
import pandas as pd
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
from config import Config
from metrics import GeometricMetrics

import importlib.util as _ilu
_eval_spec = _ilu.spec_from_file_location("_n3eval", os.path.join(_HERE, "evaluate.py"))
_eval_mod  = _ilu.module_from_spec(_eval_spec)
_eval_spec.loader.exec_module(_eval_mod)
_make_results_grid = _eval_mod.make_results_grid


_FEW_SHOT = [
    {
        "profile":  ('{"Points": [[-3.21, 6.3], [-1.67, 11.06], [-15.93, 15.69], [-17.48, 10.94]],'
                     ' "Lines": [[0, 1], [1, 2], [2, 3], [3, 0]], "Segments": [[0, 1, 2, 3]]}'),
        "midcurve": '{"Points": [[-2.44, 8.68], [-16.7, 13.31]], "Lines": [[0, 1]], "Segments": [[0]]}',
    },
    {
        "profile":  ('{"Points": [[33.0, 33.0], [38.0, 33.0], [38.0, 58.0], [63.0, 58.0],'
                     ' [63.0, 63.0], [33.0, 63.0]], "Lines": [[0, 1], [1, 2], [2, 3], [3, 4],'
                     ' [4, 5], [5, 0]], "Segments": [[0, 1, 2, 3, 4, 5]]}'),
        "midcurve": ('{"Points": [[35.5, 33.0], [35.5, 60.5], [63.0, 60.5]],'
                     ' "Lines": [[0, 1], [1, 2]], "Segments": [[0, 1]]}'),
    },
]

_SYSTEM_PROMPT = (
    "You are a CAD geometry assistant specialised in computing midcurves.\n"
    "Given a 2D closed polygon profile in JSON BRep format, output ONLY the JSON BRep "
    "of its midcurve (medial axis / skeletal centreline).\n\n"
    "Rules:\n"
    "- The midcurve runs through the geometric centre of the profile walls.\n"
    '- Output JSON must contain exactly: "Points" (list of [x,y] coordinates), '
    '"Lines" (list of [start_idx, end_idx] index pairs), "Segments" (list of line-index groups).\n'
    "- For an I/bar shape: 2 points connected by 1 Line.\n"
    "- For an L-shape: 3 points forming an L, connected by 2 Lines.\n"
    "- For a Plus/T-shape: central junction point with 4/3 branches, connected by multiple Lines.\n"
    "- Points must lie at the geometric midpoint between opposite walls.\n"
    "- Lines indices reference the Points list (zero-based).\n"
    "- Output ONLY valid JSON, no explanation or markdown fences."
)


class FewShotPrompter:
    """Base-model few-shot inference for midcurve prediction (no fine-tuning required)."""

    def __init__(self, config=None, n_samples=7, max_new_tokens=128, max_input_len=512):
        self.cfg = config or Config
        self.n_samples = n_samples
        self.max_new_tokens = max_new_tokens
        self.max_input_len = max_input_len
        self.model = None
        self.tokenizer = None

    # ── Model loading ─────────────────────────────────────────────────────────

    def load_model(self, model_id=None):
        """Load base model without adapters. Uses 4-bit on GPU (>=5 GB VRAM), else CPU."""
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

        model_id = model_id or self.cfg.MODEL_ID
        vram_gb = (torch.cuda.get_device_properties(0).total_memory / 1e9
                   if torch.cuda.is_available() else 0)
        use_gpu = vram_gb >= 5.0

        if use_gpu:
            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
            device_map = "auto"
            extra_kw = {"quantization_config": bnb_cfg}
            print(f"Loading {model_id} in 4-bit on GPU ({vram_gb:.1f} GB) ...")
        else:
            try:
                bnb_cfg = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                )
                extra_kw = {"quantization_config": bnb_cfg}
                print(f"Loading {model_id} in 4-bit on CPU (GPU VRAM {vram_gb:.1f} GB < 5 GB) ...")
            except Exception:
                extra_kw = {"torch_dtype": torch.float16}
                print(f"Loading {model_id} in float16 on CPU ...")
            device_map = "cpu"

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map=device_map,
            low_cpu_mem_usage=True,
            **extra_kw,
        )
        self.model.eval()
        print(f"Model loaded. (VRAM {vram_gb:.1f} GB)")

    # ── Prompt construction ───────────────────────────────────────────────────

    def build_prompt(self, profile_json: str) -> list:
        """Return chat messages with two few-shot examples prepended to the query."""
        examples = ""
        for ex in _FEW_SHOT:
            examples += f"Profile: {ex['profile']}\nMidcurve: {ex['midcurve']}\n\n"
        return [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user",   "content": f"{examples}Profile: {profile_json}\nMidcurve:"},
        ]

    # ── Inference ─────────────────────────────────────────────────────────────

    def generate(self, profile_json: str) -> str:
        """Run model and return raw generated string."""
        if self.model is None:
            raise RuntimeError("Call load_model() before generate().")
        messages = self.build_prompt(profile_json)
        try:
            prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except Exception:
            prompt = _SYSTEM_PROMPT + "\n\n" + messages[1]["content"]

        inputs = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=self.max_input_len
        ).to(self.model.device)

        with torch.no_grad():
            out_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=1.0,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )
        new_ids = out_ids[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_ids, skip_special_tokens=True).strip()

    # ── JSON extraction + repair ──────────────────────────────────────────────

    def _extraction_candidates(self, text: str) -> list:
        candidates = [text]
        for fence in ("```json", "```"):
            if fence in text:
                candidates.append(text.split(fence)[-1].split("```")[0].strip())
        start = text.find("{")
        if start != -1:
            depth, end = 0, -1
            for i, ch in enumerate(text[start:], start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end != -1:
                candidates.append(text[start:end + 1])
        return candidates

    def _try_parse(self, text: str):
        """Return parsed dict or None."""
        for candidate in self._extraction_candidates(text):
            for parser in (json.loads, ast.literal_eval):
                try:
                    d = parser(candidate)
                    if isinstance(d, dict) and "Points" in d:
                        return d
                except Exception:
                    pass
        return None

    def _repair_lines(self, data: dict) -> dict:
        """Connect isolated points sequentially when Lines is missing or empty."""
        pts = data.get("Points", [])
        lines = data.get("Lines", [])
        if len(pts) > 1 and not lines:
            lines = [[i, i + 1] for i in range(len(pts) - 1)]
            data["Lines"] = lines
            data["Segments"] = data.get("Segments") or [list(range(len(lines)))]
        return data

    def _parse_and_repair(self, raw: str) -> str:
        """Extract JSON from raw output, repair Lines, return JSON string."""
        data = self._try_parse(raw)
        if data is None:
            return raw
        data = self._repair_lines(data)
        return json.dumps(data)

    # ── Single prediction ─────────────────────────────────────────────────────

    def predict(self, profile_json: str) -> str:
        """Full pipeline: generate -> parse -> repair. Returns JSON string."""
        raw = self.generate(profile_json)
        return self._parse_and_repair(raw)

    # ── Batch evaluation ──────────────────────────────────────────────────────

    def evaluate(self, output_dir=None):
        """Run on N test samples, compute metrics, save CSV and results grid."""
        if self.model is None:
            raise RuntimeError("Call load_model() before evaluate().")

        results_dir = Path(output_dir) if output_dir else Path(self.cfg.BASE_DIR) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(self.cfg.TEST_FILE).head(self.n_samples)
        print(f"Loaded {len(df)} test samples from {self.cfg.TEST_FILE}\n")

        records = []
        for _, row in df.iterrows():
            profile    = str(row["Profile_brep"])
            truth      = str(row["Midcurve_brep"])
            shape_name = str(row.get("ShapeName", f"sample_{len(records)}"))

            print(f"[{len(records)+1}/{self.n_samples}] {shape_name:25s} ... ", end="", flush=True)
            pred = self.predict(profile)
            m    = GeometricMetrics.compute_all_metrics(pred, truth, profile)

            records.append({
                "index":      len(records),
                "shape_name": shape_name,
                "pred":       pred,
                "true":       truth,
                "profile":    profile,
                **m,
                "success":    bool(m["json_validity"] > 0),
                "attempts":   1,
                "demo_model": self.cfg.MODEL_ID,
            })
            print(
                f"valid={m['json_validity']:.0f}  "
                f"H={m['hausdorff']:.2f}  "
                f"C={m['chamfer']:.2f}  "
                f"score={m['combined_score']:.3f}"
            )

        csv_path = results_dir / "evaluation_results.csv"
        out_df = pd.DataFrame(records).drop(
            columns=["pred", "true", "profile"], errors="ignore"
        )
        out_df.to_csv(csv_path, index=False)
        print(f"\nResults CSV : {csv_path}")

        grid_path = str(results_dir / "results_grid.png")
        grid_saved = False
        try:
            _make_results_grid(records, grid_path, n=self.n_samples)
            print(f"Results grid: {grid_path}")
            grid_saved = True
        except Exception as exc:
            print(f"WARNING: grid skipped -- {exc}")

        if grid_saved:
            pub_images = (Path(self.cfg.BASE_DIR).parents[2]
                          / "publications" / "Midcurve_LaTeX" / "images")
            if pub_images.is_dir():
                dest = pub_images / "nemotron_results_grid.png"
                shutil.copy2(grid_path, str(dest))
                print(f"Copied to   : {dest}")
            else:
                print(f"NOTE: publications folder not found at {pub_images} -- skipping copy")

        valid = [r for r in records if r.get("json_validity", 0) > 0]
        total = len(records)
        print(f"\n=== Few-Shot Summary ({self.cfg.MODEL_ID}) ===")
        print(f"Total     : {total}")
        pct = (100.0 * len(valid) / total) if total else 0.0
        print(f"Valid JSON: {len(valid)} ({pct:.1f} %)")
        if valid:
            for key in ("hausdorff", "chamfer", "topology_accuracy",
                        "connectivity_score", "combined_score"):
                vals = [r[key] for r in valid if key in r]
                if vals:
                    print(f"  {key:25s}: {sum(vals) / len(vals):.4f}")
        print()
        print("NOTE: Results use the pre-trained base model (no fine-tuning).")
        print("      For better results, run HFSFTTrainer or UnslothTrainer, then evaluate.py.")


if __name__ == "__main__":
    p = FewShotPrompter()
    p.load_model()
    p.evaluate()
