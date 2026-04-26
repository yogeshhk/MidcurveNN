# Contributing to MidcurveNN

Thank you for your interest in contributing. This is a research project, so contributions that improve correctness, reproducibility, or documentation are especially welcome.

## Getting Started

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/MidcurveNN.git
cd MidcurveNN

# 2. Create conda environment
cd src
conda env create -f environment.yml
conda activate midcurvenn

# 3. Install extra deps for text-based (Phase III)
pip install peft>=0.7.0 trl>=0.7.0 bitsandbytes>=0.41.0 accelerate>=0.25.0

# 4. Generate training data
python utils/prepare_data.py
```

## Running Tests

```bash
cd src

# All tests (auto-discovered via pytest.ini)
python -m pytest

# Per-approach
python -m pytest image_based/testing/test_image_based.py -v
python -m pytest geometry_based/testing/test_geometry_based.py -v
python -m pytest text_based/testing/test_text_based.py -v

# Benchmark
python testing/benchmark.py --approaches geometry text
```

Tests that require optional dependencies (TensorFlow, PyTorch Geometric, GPU) skip automatically when those packages are not available.

## Adding a New Shape

1. Add `<shape>.dat` and `<shape>.mid` to `src/data/raw/` (one `x y` coordinate per line).
2. Add a hand-authored `<shape>.json` to `src/text_based/data/brep/` following the BRep schema in `src/text_based/README.md`.
3. Regenerate datasets:
   ```bash
   python utils/prepare_data.py
   cd src/text_based/utils && python create_brep_csvs.py
   ```

## Adding a New Neural Network Approach

1. Create a subdirectory under the appropriate phase folder (`image_based/`, `geometry_based/`, or `text_based/`).
2. Add a `main_*.py` or `train.py` entry point.
3. Add tests in `<phase>/testing/test_<approach>.py`.
4. Update the phase-level `README.md` table.

## Code Style

- Python 3.10, PEP 8 formatting.
- Prefer readability over cleverness — this is an academic codebase.
- Add comments only when the **why** is non-obvious.
- Match import conventions of the surrounding file.

## Reporting Issues

Please open a GitHub Issue with:
- Your OS and Python/conda environment (`conda env export`)
- The exact command you ran and the full error output
- Which phase (I / II / III) is affected

## Pull Requests

- One logical change per PR.
- Reference the related issue.
- Include a description of what changed and why.
- All existing tests must pass (skips are OK; failures are not).
