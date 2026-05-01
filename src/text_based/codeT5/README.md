# CodeT5 Fine-Tuning

Jupyter notebooks for fine-tuning CodeT5 on midcurve sequence-to-sequence prediction. Designed to run on Google Colab or Kaggle GPU instances (T4/P100).

**Task:** Given a polygon as a JSON coordinate sequence, generate the midcurve coordinate sequence.

**Notebooks:**
- `midcurve_codet5_gdrive.ipynb` — Colab variant using Google Drive for data/checkpoints
- `midcurve_codet5_kaggle.ipynb` — Kaggle variant

**Results:** Evaluation metrics (BLEU, exact match, geometry) stored in `results/evaluation_results_sample.csv` after running evaluation cells.

See `src/text_based/data/csvs/` for the 993-row train/test/val CSV splits used as input.
