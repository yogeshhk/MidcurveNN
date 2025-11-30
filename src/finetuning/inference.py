import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from config import Config
from metrics import GeometricMetrics
from visualize import plot_results
import pandas as pd

def run_inference():
    # Load Base Model
    base_model = AutoModelForCausalLM.from_pretrained(
        Config.MODEL_ID,
        device_map="auto",
        torch_dtype=torch.float16
    )
    tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_ID)

    # Load Fine-tuned Adapters
    model = PeftModel.from_pretrained(base_model, Config.NEW_MODEL_NAME)
    model = model.merge_and_unload() # Optional: Merge for faster inference

    # Load a test example
    df = pd.read_csv(Config.TEST_FILE)
    example_row = df.iloc[0]
    profile_input = str(example_row['Profile_brep'])
    ground_truth = str(example_row['Midcurve_brep'])

    # Format Prompt
    messages = [
        {"role": "system", "content": Config.SYSTEM_PROMPT},
        {"role": "user", "content": profile_input}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    inputs = tokenizer([text], return_tensors="pt").to("cuda")

    # Generate
    generated_ids = model.generate(
        inputs.input_ids,
        max_new_tokens=512,
        do_sample=False, # Deterministic for geometry
        temperature=0.1
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    print("-" * 50)
    print("Input Profile:", profile_input[:100], "...")
    print("-" * 50)
    print("Generated Midcurve:", response)
    print("-" * 50)

    # Metrics
    hausdorff = GeometricMetrics.hausdorff_metric(response, ground_truth)
    print(f"Hausdorff Distance: {hausdorff:.4f}")

    # Plot
    plot_results(profile_input, ground_truth, response)

if __name__ == "__main__":
    run_inference()