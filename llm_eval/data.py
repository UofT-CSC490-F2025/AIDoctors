from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from .config import CSV_PATH, RANDOM_STATE, VAL_TEST_FRACTION, TEST_FRACTION_OF_TEMP

VALID_LABELS = ["Minor", "Moderate", "Major"]

def load_and_prepare() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower()

    df["unified_severity_clean"] = df["unified_severity"].astype(str).str.strip().str.capitalize()
    df = df[df["unified_severity_clean"].isin(VALID_LABELS)].copy()

    for col in ["overlap_start", "overlap_stop"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if {"overlap_start", "overlap_stop"}.issubset(df.columns):
        df["overlap_days"] = (df["overlap_stop"] - df["overlap_start"]).dt.days
        df["overlap_days"] = df["overlap_days"].clip(lower=0).fillna(0)
    else:
        df["overlap_days"] = 0

    if "comorbidities_len" not in df.columns:
        df["comorbidities_len"] = df["comorbidities"].astype(str).apply(
            lambda x: len([t for t in x.split(",") if t.strip()]) if pd.notna(x) else 0
        )

    for col in ["age", "ddi_confidence", "comorbidities_len", "overlap_days"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "ddi_known" in df.columns:
        df["ddi_known"] = (
            df["ddi_known"].map({True: 1, False: 0, "True": 1, "False": 0}).fillna(0).astype(int)
        )

    if "unified_mechanism_text" in df.columns:
        df["unified_mechanism_text"] = df["unified_mechanism_text"].fillna("").astype(str)

    before = len(df)
    df = df.drop_duplicates()
    key_cols = [c for c in ["drug1_norm", "drug2_norm", "age", "sex", "comorbidities_len",
                            "ddi_confidence", "ddi_known", "overlap_start", "overlap_stop",
                            "unified_severity_clean"] if c in df.columns]
    if key_cols:
        df = df.drop_duplicates(subset=key_cols)

    print(f"[data] rows kept: {len(df)} (removed {before - len(df)})")
    return df

def split_indices(df: pd.DataFrame) -> Tuple[pd.Index, pd.Index, pd.Index, np.ndarray, np.ndarray, np.ndarray, LabelEncoder]:
    y = df["unified_severity_clean"].copy()
    idx = df.index.to_series()
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    idx_train, idx_temp, y_train, y_temp = train_test_split(
        idx, y_enc, test_size=VAL_TEST_FRACTION, stratify=y_enc, random_state=RANDOM_STATE
    )
    idx_val, idx_test, y_val, y_test = train_test_split(
        idx_temp, y_temp, test_size=TEST_FRACTION_OF_TEMP, stratify=y_temp, random_state=RANDOM_STATE
    )
    print(f"[split] train/val/test: {len(idx_train)}/{len(idx_val)}/{len(idx_test)}")
    print(f"[split] label mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    return idx_train, idx_val, idx_test, y_train, y_val, y_test, le
