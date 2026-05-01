# Few-Shot Prompting

Scripts and results for LLM-based midcurve prediction via few-shot prompting — no fine-tuning required. Tests multiple LLMs (GPT-4, Claude, Gemini) using polygon B-Rep JSON as input context.

**Approach:** Provide 2-3 solved polygon→midcurve examples in the prompt, then ask the LLM to predict the midcurve for a new shape. Output is parsed as B-Rep JSON.

**Scripts:**
- `prompt_llm.py` — send prompts to LLM APIs and collect responses
- Comparison screenshots stored in this folder

**Input format:** B-Rep JSON from `src/text_based/data/brep/` (I, L, T, Plus base shapes)

No training required. Results are qualitative; see screenshots for LLM comparison.
