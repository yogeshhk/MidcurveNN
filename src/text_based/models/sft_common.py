"""
models/sft_common.py -- answer-only-loss supervised fine-tuning shared by qwen_qlora / nemotron_qlora.

Key points (these are the fixes for the legacy trainers):
  * prompt and answer are tokenised SEPARATELY; labels are -100 on every prompt token
  * the answer is followed by the chat EOS token, and its presence is asserted
  * pad_token is NOT set to eos (EOS must never be masked); padding labels are -100 via the collator
  * the prompt comes from prompts.build_messages, the same function used at inference
  * training and evaluation use the same precision (4-bit base + unmerged adapter, or bf16 + merge)

tokenize_example() is pure Python (testable with a stub tokenizer). train() needs torch, transformers,
peft (and bitsandbytes for 4-bit) and is NOT run by the tests.
"""
import json
import os

from text_based import dataset, prompts

IGNORE = -100


def _ids(x):
    """Normalise apply_chat_template output (list | dict-like with input_ids) to a list of ints."""
    if hasattr(x, "get") and x.get("input_ids") is not None:
        x = x["input_ids"]
    if hasattr(x, "tolist"):
        x = x.tolist()
    if x and isinstance(x[0], list):
        x = x[0]
    return [int(i) for i in x]


def tokenize_example(tok, messages, answer, max_len=1024):
    """Return dict(input_ids, labels, attention_mask). Raises if the EOS would be truncated."""
    try:
        prompt_ids = _ids(tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=True))
    except Exception:
        prompt_ids = _ids(tok.apply_chat_template(prompts.merge_system_into_user(messages),
                                                  add_generation_prompt=True, tokenize=True))
    eos_id = tok.eos_token_id
    ans_ids = _ids(tok(answer, add_special_tokens=False))
    ans_ids = ans_ids + [eos_id]
    ids = prompt_ids + ans_ids
    if len(ids) > max_len:
        raise ValueError("example has %d tokens > max_len %d; raise max_len (never truncate the answer)"
                         % (len(ids), max_len))
    labels = [IGNORE] * len(prompt_ids) + ans_ids
    assert labels[-1] == eos_id, "EOS missing from labels"
    assert all(l == IGNORE for l in labels[:len(prompt_ids)])
    return dict(input_ids=ids, labels=labels, attention_mask=[1] * len(ids))


def build_examples(tok, rows, fmt, pose, style, max_len):
    out = []
    for r in rows:
        msgs, ans = prompts.build_messages(r, fmt, pose, (), style)
        out.append(tokenize_example(tok, msgs, ans, max_len))
    return out


def dump_first(tok, ex):
    """Print the full first example and only its label positions (acceptance check)."""
    print("FULL INPUT :", repr(tok.decode(ex["input_ids"])))
    print("LABELS ONLY:", repr(tok.decode([l for l in ex["labels"] if l != IGNORE])))


def train(cfg):
    """cfg keys: model_id, fmt, pose, style, fold, out_dir, epochs, lr, batch, grad_acc, max_len,
    lora_r, bnb_4bit, max_steps (optional smoke), seed."""
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
                              DataCollatorForSeq2Seq, Trainer, TrainingArguments)

    tok = AutoTokenizer.from_pretrained(cfg["model_id"])
    if tok.pad_token_id is None:  # a dedicated pad token if missing; never alias EOS
        tok.add_special_tokens({"pad_token": "<|pad|>"})
    rows = dataset.load_rows(cfg.get("dataset"))
    fold = cfg.get("fold", "pose")
    train_rows = dataset.select(rows, fold, "train")
    val_rows = dataset.select(rows, fold, "val")
    fmt, pose, style = cfg.get("fmt", "mcv2"), cfg.get("pose", "canonical"), cfg.get("style", "fewshot")
    tr = build_examples(tok, train_rows, fmt, pose, style, cfg.get("max_len", 1024))
    va = build_examples(tok, val_rows, fmt, pose, style, cfg.get("max_len", 1024))
    dump_first(tok, tr[0])

    kw = dict(device_map="auto")
    if cfg.get("bnb_4bit", True):
        kw["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16)
    else:
        kw["torch_dtype"] = torch.bfloat16
    model = AutoModelForCausalLM.from_pretrained(cfg["model_id"], **kw)
    model.resize_token_embeddings(len(tok))
    if cfg.get("bnb_4bit", True):
        model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(r=cfg.get("lora_r", 32), lora_alpha=2 * cfg.get("lora_r", 32),
                                             lora_dropout=0.05, target_modules="all-linear",
                                             task_type="CAUSAL_LM"))

    class DS(torch.utils.data.Dataset):
        def __init__(self, ex):
            self.ex = ex

        def __len__(self):
            return len(self.ex)

        def __getitem__(self, i):
            return self.ex[i]

    args = TrainingArguments(
        output_dir=cfg["out_dir"], num_train_epochs=cfg.get("epochs", 8), learning_rate=cfg.get("lr", 1.5e-4),
        per_device_train_batch_size=cfg.get("batch", 4), gradient_accumulation_steps=cfg.get("grad_acc", 4),
        lr_scheduler_type="cosine", warmup_ratio=0.03, bf16=True, logging_steps=10,
        max_steps=cfg.get("max_steps", -1), save_strategy="epoch", report_to=[], seed=cfg.get("seed", 0),
        remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=DS(tr), eval_dataset=DS(va) if va else None,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=IGNORE))
    trainer.train()
    model.save_pretrained(cfg["out_dir"])
    tok.save_pretrained(cfg["out_dir"])
    with open(os.path.join(cfg["out_dir"], "run_config.json"), "w", encoding="utf-8") as fh:
        json.dump({k: v for k, v in cfg.items()}, fh, indent=2, default=str)
    return cfg["out_dir"]
