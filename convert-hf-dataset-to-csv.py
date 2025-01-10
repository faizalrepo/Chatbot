from datasets import load_dataset
import pandas as pd

# Step 1: Download dataset from Hugging Face
dataset = load_dataset("not-faizal/preference-dataset-prep", split="train")

# Step 2: Convert to pandas DataFrame
df = dataset.to_pandas()

# Step 3: Filter the DataFrame
filtered_df = df[(df['helpfulness'] >= 3.0) | (df['correctness'] >= 3.0)]

# Step 4: Save as CSV and JSONL
filtered_df.to_csv("converted_filtered_data.csv", index=False)
filtered_df.to_json("converted_filtered_data.jsonl", orient="records", lines=True)

# Step 5: Display the first few rows (Optional)
print(filtered_df.head())
