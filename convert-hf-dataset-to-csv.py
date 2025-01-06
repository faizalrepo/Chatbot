from datasets import load_dataset
import pandas as pd

# Step 1: Download dataset from Hugging Face
dataset = load_dataset("not-faizal/preference-dataset-prep", split="train")

# Step 2: Convert to pandas DataFrame
df = dataset.to_pandas()

# Step 3: Display the first few rows
print(df.head())

# Step 4: Save as .parquet file locally
df.to_parquet("local_file.parquet")

# Step 5: Read the .parquet file (for validation)
df_from_parquet = pd.read_parquet("local_file.parquet")
print(df_from_parquet.head())

# Step 6: Convert to CSV (Optional)
df_from_parquet.to_csv("local_file.csv", index=False)