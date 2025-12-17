# Local Model Fine-tuning Guide

This guide explains how to fine-tune MidcurveLLM using a local model (e.g., a downloaded SafeTensors model or a custom pre-trained checkpoint).

## Prerequisites

1.  **Environment**: Ensure you have run the setup and installed dependencies.
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\pip install -r src/finetuning/requirements.txt
    ```

2.  **Model**: Have your local model directory ready (containing `config.json`, `model.safetensors`/`pytorch_model.bin`, `tokenizer.json`, etc.).

## Running Fine-tuning

We provide a helper script `run_finetuning.ps1` to simplify the process.

### With a Local Model

Run the following command in PowerShell:

```powershell
.\run_finetuning.ps1 -ModelPath "C:\Path\To\Your\Local\Model"
```

This will:
1.  Activate the virtual environment.
2.  Override the default `MODEL_ID` in configuration.
3.  Start the training process using the data in `src/finetuning/data`.

### With Default HuggingFace Model

To use the default model defined in `config.py` (e.g., `Qwen/Qwen2.5-Coder-7B-Instruct`):

```powershell
.\run_finetuning.ps1
```

## Manual Usage

You can also run the python script directly:

```powershell
.\.venv\Scripts\python src/finetuning/train.py --model_path "C:\Path\To\Model"
```

## Configuration

The default configuration is located in `src/finetuning/config.py`.
Data files are expected in `src/finetuning/data`.
