import os
import sys

import pandas as pd
from datasets import Dataset

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config


class MidcurveDataset:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def _format_row(self, row):
        messages = [
            {"role": "system",    "content": Config.SYSTEM_PROMPT},
            {"role": "user",      "content": str(row["Profile_brep"])},
            {"role": "assistant", "content": str(row["Midcurve_brep"])},
        ]
        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=False
        )
        return {"text": text}

    def load_data(self, file_path):
        df      = pd.read_csv(file_path)[["Profile_brep", "Midcurve_brep"]]
        df      = df.reset_index(drop=True)
        dataset = Dataset.from_pandas(df, preserve_index=False)
        return dataset.map(
            self._format_row,
            remove_columns=["Profile_brep", "Midcurve_brep"],
        )
