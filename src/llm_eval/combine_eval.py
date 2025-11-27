import os, glob, csv
import pandas as pd

OUT_DIR = "llm_eval/outputs"
part_paths = sorted(glob.glob(os.path.join(OUT_DIR, "predictions_part*_of*.csv")))
assert part_paths, "No shard files found (predictions_part*_of*.csv)."

def read_part(path):
    # Use the Python engine to tolerate embedded newlines; read everything as str
    # keep_default_na=False prevents empty strings from turning into NaN
    df = pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        engine="python",
        quoting=csv.QUOTE_MINIMAL,  # can read any quoting style
        on_bad_lines="warn",
    )
    # Normalize column casing
    df.columns = [c.strip().lower() for c in df.columns]
    # Make sure required columns exist
    for col in ["index", "true", "pred", "raw"]:
        if col not in df.columns:
            df[col] = ""
    # Simple length diagnostic
    df["raw_len"] = df["raw"].astype(str).str.len()
    return df

parts = [read_part(p) for p in part_paths]
lens_before = [len(x) for x in parts]
print("Rows per shard:", dict(zip(part_paths, lens_before)), "| total:", sum(lens_before))

merged = pd.concat(parts, ignore_index=True)

# Basic corruption checks
broken_rows = merged["index"].isna() | (merged["true"] == "") & (merged["pred"] == "") & (merged["raw"] == "")
if broken_rows.any():
    print("⚠️ Found", int(broken_rows.sum()), "suspicious blank rows; dropping them.")
    merged = merged.loc[~broken_rows].copy()

# Optional: normalize newlines inside raw
merged["raw"] = merged["raw"].astype(str).str.replace("\r\n", "\n").str.replace("\r", "\n")

# Save with robust quoting so future reads don’t split lines
out_path = os.path.join(OUT_DIR, "predictions_merged.csv")
merged.to_csv(
    out_path,
    index=False,
    quoting=csv.QUOTE_ALL,     # every field quoted
    escapechar="\\",
    lineterminator="\n",
)
print("✅ Merged rows written:", len(merged), "→", out_path)

# Quick sanity: show extreme/odd raw lengths (can reveal truncation)
print("raw_len stats:", merged["raw_len"].astype(int).describe())
print("Longest 3 raw examples:\n", merged.sort_values("raw_len", ascending=False)[["index","raw_len","raw"]].head(3))
