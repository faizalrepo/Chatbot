from datasets import load_dataset
import pandas as pd
import json

# Step 1: Load dataset from Hugging Face
dataset = load_dataset("not-faizal/test-dataset-prep")

# Step 2: Convert to DataFrame
df = pd.DataFrame(dataset['train'])

# Step 3: Save to CSV first
csv_file = 'ft-prompt-response.csv'
df.to_csv(csv_file, index=False)
print(f"\nCSV saved to {csv_file}")

# Step 4: Convert to JSONL format with filtering
jsonl_data = []

for _, row in df.iterrows():
    if row['correctness'] >= 3.0 and row['helpfulness'] >= 3.0 and row['coherence'] >= 3.0:
        jsonl_data.append({
            "messages": [
                {"role": "user", "content": row['question']},
                {"role": "assistant", "content": row['response']}
            ]
        })

# Step 5: Save to JSONL
jsonl_file = 'ft-data.jsonl'
with open(jsonl_file, 'w') as f:
    for entry in jsonl_data:
        f.write(json.dumps(entry) + '\n')

print(f"\nConversion complete. JSONL saved to {jsonl_file}\n")