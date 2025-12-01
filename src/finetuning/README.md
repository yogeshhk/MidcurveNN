# Midcurve Generation using Fine-Tuned LLMs

Comprehensive implementation of LLM-based geometric transformation for automated midcurve extraction from 2D polygonal profiles.

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install Flash Attention 2 for faster training
pip install flash-attn --no-build-isolation
```

### Basic Usage

```bash
# 1. Validate your dataset
python data_validator.py

# 2. (Optional) Augment training data
python augmentation.py

# 3. Train the model
python train_enhanced.py

# 4. Run inference
python inference_enhanced.py --single

# 5. Evaluate the model
python evaluate.py --model_path Midcurve-Qwen-Coder-v1 --visualize

# 6. Analyze errors
python error_analysis.py --results_file evaluation_results.csv --test_file midcurve_llm_test.csv
```

## 📁 Project Structure

```
.
├── config_enhanced.py          # Enhanced configuration with all settings
├── data_validator.py           # Data quality validation
├── augmentation.py             # Geometric data augmentation
├── dataset_loader.py           # Dataset loading utilities
├── metrics_enhanced.py         # Comprehensive evaluation metrics
├── train_enhanced.py           # Enhanced training script
├── inference_enhanced.py       # Inference with validation & repair
├── evaluate.py                 # Comprehensive evaluation
├── model_comparison.py         # Compare multiple base models
├── error_analysis.py           # Detailed error analysis
├── model_server.py            # FastAPI production server
├── visualize.py               # Visualization utilities
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

All configuration is in `config_enhanced.py`. Key settings:

```python
# Model selection
MODEL_ID = "Qwen/Qwen2.5-Coder-7B-Instruct"

# Training hyperparameters
LORA_R = 16
LORA_ALPHA = 32
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3

# Advanced features
USE_GRADIENT_CHECKPOINTING = True
USE_FLASH_ATTENTION_2 = True
EARLY_STOPPING_PATIENCE = 3

# Data augmentation
AUGMENTATION_MULTIPLIER = 5
AUGMENTATION_NOISE_LEVEL = 0.01
```

## 📊 Data Preparation

### Data Validation

```bash
python data_validator.py
```

This will:
- Check JSON parsing success rate
- Validate closed profiles
- Verify graph connectivity
- Detect coordinate range issues
- Generate validation report

### Data Augmentation

```bash
python augmentation.py
```

Augmentation strategies:
- **Noise injection**: Add Gaussian noise to coordinates (1% by default)
- **Non-uniform scaling**: Apply different X/Y scale factors
- **Precision variation**: Vary decimal places (1-4)
- **Geometric transformations**: Already in dataset (rotation, translation, scaling)

## 🎯 Training

### Basic Training

```bash
python train_enhanced.py
```

### With Weights & Biases Logging

```bash
# First, login to wandb
wandb login

# Update config
# Set USE_WANDB = True in config_enhanced.py

python train_enhanced.py
```

### Training Features

- ✅ Gradient checkpointing for memory efficiency
- ✅ Flash Attention 2 support
- ✅ 4-bit quantization with QLoRA
- ✅ Cosine learning rate schedule with restarts
- ✅ Early stopping based on geometric metrics
- ✅ Custom validation callback
- ✅ Automatic checkpoint management

## 🔍 Evaluation

### Comprehensive Evaluation

```bash
python evaluate.py \
    --model_path Midcurve-Qwen-Coder-v1 \
    --test_file midcurve_llm_test.csv \
    --output_file evaluation_results.csv \
    --visualize
```

### Metrics Computed

**Geometric Metrics:**
- Hausdorff distance
- Chamfer distance
- MAE (Mean Absolute Error)
- RMSE (Root Mean Square Error)

**Topological Metrics:**
- Topology accuracy (junction count)
- Connectivity score
- Vertex count accuracy

**Quality Metrics:**
- JSON validity rate
- Coordinate range validation
- Symmetry preservation
- Combined score (weighted average)

### Output Files

- `evaluation_results.csv`: Per-sample results
- `evaluation_summary.json`: Summary statistics
- `evaluation_plots/`: Visualization plots
- `prediction_viz/`: Individual prediction visualizations

## 📈 Model Comparison

Compare multiple base models:

```bash
python model_comparison.py --train --test_file midcurve_llm_test.csv
```

Models compared:
- Qwen/Qwen2.5-Coder-7B-Instruct
- google/gemma-2-9b-it
- mistralai/Mistral-7B-Instruct-v0.2

Output:
- Training logs for each model
- Evaluation results for each model
- Comparison visualizations
- Best model recommendation

## 🐛 Error Analysis

Detailed error analysis:

```bash
python error_analysis.py \
    --results_file evaluation_results.csv \
    --test_file midcurve_llm_test.csv
```

Analysis includes:
- Error categorization (JSON, topology, geometry, connectivity)
- Failure patterns by shape type
- Failure patterns by transformation type
- Common error combinations
- Prediction characteristics
- Visualizations of failure patterns

Output:
- `error_analysis_report.txt`: Comprehensive text report
- `error_analysis_plots/`: Error distribution visualizations
- `problematic_samples.csv`: Most problematic cases

## 🚀 Production Deployment

### API Server

Start the FastAPI server:

```bash
python model_server.py --host 0.0.0.0 --port 8000
```

### API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Validate Profile:**
```bash
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "points": [[0,0], [10,0], [10,25], [35,25], [35,30], [0,30]],
    "lines": [[0,1], [1,2], [2,3], [3,4], [4,5], [5,0]],
    "segments": [[0,1,2,3,4,5]]
  }'
```

**Predict Midcurve:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "points": [[0,0], [10,0], [10,25], [35,25], [35,30], [0,30]],
      "lines": [[0,1], [1,2], [2,3], [3,4], [4,5], [5,0]],
      "segments": [[0,1,2,3,4,5]]
    },
    "validate_input": true,
    "return_confidence": true
  }'
```

### API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

## 📝 Advanced Features

### Constrained Generation

The inference pipeline includes:
- **Output validation**: Checks JSON structure, connectivity, coordinate range
- **Automatic repair**: Attempts to fix disconnected components
- **Retry mechanism**: Up to 3 attempts with increasing temperature
- **Confidence scoring**: Returns confidence score for each prediction

### Curriculum Learning

Enable in `config_enhanced.py`:

```python
USE_CURRICULUM = True
CURRICULUM_STAGES = ["simple", "moderate", "complex"]
```

Train progressively on increasing difficulty.

### Geometric Loss

Enable geometric-aware loss:

```python
USE_GEOMETRIC_LOSS = True
GEOMETRIC_LOSS_WEIGHT = 0.1
TOKEN_LOSS_WEIGHT = 0.9
```

Combines token prediction loss with geometric accuracy.

## 🧪 Testing

Run validation tests:

```bash
# Test data validation
python data_validator.py

# Test single inference
python inference_enhanced.py --single

# Test batch inference (10 samples)
python inference_enhanced.py --num_samples 10
```

## 📊 Performance Benchmarks

Expected performance (on test set):

| Metric | Simple Shapes | Moderate | Complex |
|--------|--------------|----------|---------|
| JSON Validity | >95% | >90% | >85% |
| Mean Hausdorff | <0.5 | <1.5 | <3.0 |
| Topology Accuracy | >90% | >85% | >70% |
| Combined Score | >0.8 | >0.7 | >0.6 |

## 🔬 Research & Experiments

### Model Comparison

```bash
python model_comparison.py --train
```

### Ablation Studies

Modify `config_enhanced.py` to test:
- Different LoRA ranks (8, 16, 32, 64)
- Different learning rates (1e-5 to 5e-4)
- With/without gradient checkpointing
- With/without geometric loss
- Different augmentation levels

### Hyperparameter Search

Use wandb sweeps:

```bash
wandb sweep sweep_config.yaml
wandb agent <sweep_id>
```

## 🐛 Troubleshooting

### CUDA Out of Memory

- Reduce `BATCH_SIZE`
- Increase `GRAD_ACC_STEPS`
- Enable `USE_GRADIENT_CHECKPOINTING`
- Reduce `MAX_SEQ_LENGTH`

### Poor Performance

- Check data quality with `data_validator.py`
- Increase training data with `augmentation.py`
- Try different base models with `model_comparison.py`
- Analyze errors with `error_analysis.py`

### Slow Training

- Enable `USE_FLASH_ATTENTION_2`
- Use mixed precision: `MIXED_PRECISION = "bf16"`
- Increase `BATCH_SIZE` and adjust `GRAD_ACC_STEPS`

### API Server Issues

- Check model is loaded: `curl http://localhost:8000/health`
- Validate input format: Use `/validate` endpoint first
- Check logs for detailed error messages

## 📚 References

1. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022
2. Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs", NeurIPS 2023
3. Blum, H., "A transformation for extracting new descriptors of shape", 1967

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional geometric augmentation strategies
- Better output validation and repair mechanisms
- Support for 3D geometries
- Integration with CAD software
- Additional base model support

## 📄 License

This project is for research purposes. Check individual model licenses before commercial use.

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainers.

## 🎓 Citation

If you use this code in your research, please cite:

```bibtex
@misc{midcurve-llm-2024,
  title={Fine-Tuning Large Language Models for Automated Midcurve Generation},
  author={Anonymous},
  year={2024},
  howpublished={\url{https://github.com/...}}
}
```
