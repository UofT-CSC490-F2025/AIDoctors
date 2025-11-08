import os
import pandas as pd
import re

# Get the directory where this script lives
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build full path to the CSV in the same folder
csv_path = os.path.join(script_dir, "predictions_merged.csv")

# Check that it exists
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"Could not find CSV at {csv_path}")

# Load CSV
df = pd.read_csv(csv_path)

# Regex for a proper sentence ending (., ?, ! possibly followed by quotes or parentheses)
proper_end_regex = re.compile(r'([.!?]["\')\]]?\s*)$')

def ends_properly(text):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return False
    return bool(proper_end_regex.search(text.strip()))

df["ends_properly"] = df["raw"].apply(ends_properly)

num_total = len(df)
num_good = df["ends_properly"].sum()
num_bad = num_total - num_good

print(f"✅ Properly ended sentences: {num_good}/{num_total} ({num_good/num_total:.1%})")
print(f"⚠️  Truncated or incomplete sentences: {num_bad}/{num_total} ({num_bad/num_total:.1%})")

print("\nExamples of truncated sentences:")
print(df.loc[~df["ends_properly"], "raw"].sample(min(10, num_bad)).to_string(index=False))
