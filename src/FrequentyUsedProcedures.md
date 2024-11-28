# Frequently Used Procedures

## Steps to fine-tune Midcurve Brep json dataset with HuggingFace Code T5

https://medium.com/analytics-vidhya/tuning-for-geometry-b5d12d1c2bc1

# Replace the URL with the raw URL of the file on GitHub
url_midcurve_llm = "https://raw.githubusercontent.com/yogeshhk/MidcurveNN/master/src/codeT5/data/midcurve_llm.csv"
url_midcurve_llm_test = "https://raw.githubusercontent.com/yogeshhk/MidcurveNN/master/src/codeT5/data/midcurve_llm_test.csv"
url_midcurve_llm_train = "https://raw.githubusercontent.com/yogeshhk/MidcurveNN/master/src/codeT5/data/midcurve_llm_train.csv"
url_midcurve_llm_val = "https://raw.githubusercontent.com/yogeshhk/MidcurveNN/master/src/codeT5/data/midcurve_llm_val.csv"

# Download the files
wget.download(url_midcurve_llm, 'midcurve_llm.csv')
wget.download(url_midcurve_llm_test, 'midcurve_llm_test.csv')
wget.download(url_midcurve_llm_train, 'midcurve_llm_train.csv')
wget.download(url_midcurve_llm_val, 'midcurve_llm_val.csv')

from transformers import T5ForConditionalGeneration, AdamW, get_linear_schedule_with_warmup
import pytorch_lightning as pl

class CodeT5(pl.LightningModule):
    def __init__(self, lr=5e-5, num_train_epochs=100, warmup_steps=1000):
        super().__init__()
        self.model_name = "Salesforce/codet5-small"
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
        self.save_hyperparameters()

:

trainer = Trainer(max_epochs=100,accelerator="auto", #gpus=1,
                  default_root_dir="./Checkpoints",
                  logger=wandb_logger,
                  callbacks=[early_stop_callback, lr_monitor])
trainer.fit(model)

save_directory = "./Checkpoints" # save in the current working directory, you can change this of course
model.model.save_pretrained(save_directory)
--
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the test dataset
dataset_infr = load_dataset("csv", data_files={"train": base_url + "midcurve_llm_train.csv",
                                          "test": base_url + "midcurve_llm_test.csv",
                                          "validation": base_url + "midcurve_llm_val.csv"})

# Load the trained model
model = T5ForConditionalGeneration.from_pretrained(save_directory)

# Get an example from the test set
test_example = dataset_infr['test'][2]
print("Profile_brep:", test_example['Profile_brep'])

Profile_brep: "{\"Points\": [[-6.96, 1.23], [-9.83, 5.32], [-22.12, -3.28], [-19.25, -7.38]], \"Lines\": [[0, 1], [1, 2], [2, 3], [3, 0]], \"Segments\": [[0, 1, 2, 3]]}"

# Prepare the example for the model
tokenizer = T5Tokenizer.from_pretrained(save_directory)
input_ids = tokenizer(test_example['Profile_brep'], return_tensors='pt').input_ids

# Generate Midcurve
outputs = model.generate(input_ids, max_length=200)
Midcurve_brep_str_Predicted = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Generated Midcurve:", Midcurve_brep_str_Predicted)

Generated Midcurve: [[-8.59, 3.14], [-21.3, -5.26]], \"Lines\": [[0, 1]], \"Segments\": [[0]]}"

# Deep copy the original example
test_example_predicted = copy.deepcopy(test_example)

# Add the missing key to the generated midcurve
Midcurve_brep_str_Predicted_with_key = '"{\\"Points\\": ' + Midcurve_brep_str_Predicted + ', \\"Lines\\": [[0, 1]], \\"Segments\\": [[0]]}"'

# Replace the midcurve in the predicted example
test_example_predicted['Midcurve_brep'] = Midcurve_brep_str_Predicted_with_key

# Print the predicted example
print("Predicted Example:", test_example_predicted)

# Compare with the ground truth
print("Ground Truth:", test_example['Midcurve_brep'])

Use "D:\Yogesh\GitHub\MidcurveNN\src\utils\prepare_plots.py" to plot breps