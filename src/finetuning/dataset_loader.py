import pandas as pd
from datasets import Dataset
from config import Config

class MidcurveDataset:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def format_chat_template(self, row):
        """Converts a row of CSV to Qwen/Gemma chat format"""
        # Ensure data is string
        profile_json = str(row['Profile_brep'])
        midcurve_json = str(row['Midcurve_brep'])

        messages = [
            {"role": "system", "content": Config.SYSTEM_PROMPT},
            {"role": "user", "content": profile_json},
            {"role": "assistant", "content": midcurve_json}
        ]
        
        # Apply the chat template provided by the tokenizer
        text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=False
        )
        return {"text": text}

    def load_data(self, file_path):
        df = pd.read_csv(file_path)
        # Filter only necessary columns to save memory
        df = df[['Profile_brep', 'Midcurve_brep']]
        dataset = Dataset.from_pandas(df)
        dataset = dataset.map(self.format_chat_template)
        return dataset