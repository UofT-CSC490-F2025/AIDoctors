import os
from pathlib import Path
import sys
import pandas as pd
import psycopg2
import io

import numpy as np

def coerce_intlike(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
            # round just in case and cast to pandas Int64 (nullable)
            df[c] = df[c].round(0).astype("Int64")
    return df

def df_to_csv_buffer(df) -> io.StringIO:
    # ensure int-like columns won’t print as x.0
    return io.StringIO(
        df.to_csv(index=False, header=False, na_rep="", float_format="%.0f")
    )


OUT = Path("data/datasets_output")

TABLES = [
    ("aeolus_drug_outcome_lookup",      "aeolus_drug_outcome_lookup.csv"),
    ("rxcui_to_ingredient_map",         "rxcui_to_ingredient_map.csv"),
    ("patient_ae_risk_annotations_rxnav","patient_ae_risk_annotations_rxnav.csv"),
    ("ae_risk_enriched",                "ae_risk_enriched.csv"),
    ("ae_risk_topk_per_patient_drug",   "ae_risk_topk_per_patient_drug.csv"),
    ("ddi_ref_unified",                 "ddi_ref_unified.csv"),
    ("patient_ddi_collapsed_from_topk", "patient_ddi_collapsed_from_topk.csv"),
]

DDL = {
"aeolus_drug_outcome_lookup": """
CREATE TABLE IF NOT EXISTS aeolus_drug_outcome_lookup (
  rxcui                INTEGER,
  drug_name            TEXT,
  outcome_concept_id   BIGINT,
  outcome_text         TEXT,
  meddra_code          TEXT,
  case_count           INTEGER,
  prr                  DOUBLE PRECISION,
  ror                  DOUBLE PRECISION
);
""",
"rxcui_to_ingredient_map": """
CREATE TABLE IF NOT EXISTS rxcui_to_ingredient_map (
  rxcui              INTEGER,
  ingredient_rxcui   INTEGER
);
""",
"patient_ae_risk_annotations_rxnav": """
CREATE TABLE IF NOT EXISTS patient_ae_risk_annotations_rxnav (
  patient_uuid           TEXT,
  rxcui_x                INTEGER,
  ingredient_rxcui       INTEGER,
  synthea_drug_desc      TEXT,
  aeolus_drug_name       TEXT,
  START                  TIMESTAMPTZ,
  STOP                   TIMESTAMPTZ,
  estimated_onset        TIMESTAMPTZ,
  outcome_concept_id     BIGINT,
  outcome_text           TEXT,
  meddra_code            TEXT,
  case_count             INTEGER,
  prr                    DOUBLE PRECISION,
  ror                    DOUBLE PRECISION
);
""",
"ae_risk_enriched": """
CREATE TABLE IF NOT EXISTS ae_risk_enriched (
  patient_uuid       TEXT,
  Age                INTEGER,
  Sex                TEXT,
  Comorbidities      TEXT,            -- JSON-like string list
  START              TIMESTAMPTZ,
  STOP               TIMESTAMPTZ,
  synthea_drug_desc  TEXT,
  rxcui_x            INTEGER,
  ingredient_rxcui   INTEGER,
  aeolus_drug_name   TEXT,
  outcome_text       TEXT,
  meddra_code        TEXT,
  case_count         INTEGER,
  prr                DOUBLE PRECISION,
  ror                DOUBLE PRECISION,
  synthea_drug       TEXT
);
""",
"ae_risk_topk_per_patient_drug": """
CREATE TABLE IF NOT EXISTS ae_risk_topk_per_patient_drug (
  patient_uuid       TEXT,
  Age                INTEGER,
  Sex                TEXT,
  Comorbidities      TEXT,
  START              TIMESTAMPTZ,
  STOP               TIMESTAMPTZ,
  synthea_drug_desc  TEXT,
  rxcui_x            INTEGER,
  ingredient_rxcui   INTEGER,
  aeolus_drug_name   TEXT,
  outcome_text       TEXT,
  meddra_code        TEXT,
  case_count         INTEGER,
  prr                DOUBLE PRECISION,
  ror                DOUBLE PRECISION,
  synthea_drug       TEXT
);
""",
"ddi_ref_unified": """
CREATE TABLE IF NOT EXISTS ddi_ref_unified (
  pair_key               TEXT,
  drug1_norm             TEXT,
  drug2_norm             TEXT,
  unified_severity       TEXT,
  unified_mechanism_text TEXT,
  sources_present        TEXT,    -- JSON-like string list
  ddi_confidence         DOUBLE PRECISION
);
""",
"patient_ddi_collapsed_from_topk": """
CREATE TABLE IF NOT EXISTS patient_ddi_collapsed_from_topk (
  patient_uuid           TEXT,
  drug1                  TEXT,
  drug2                  TEXT,
  drug1_norm             TEXT,
  drug2_norm             TEXT,
  overlap_start          TIMESTAMPTZ,
  overlap_stop           TIMESTAMPTZ,
  Age                    INTEGER,
  Sex                    TEXT,
  Comorbidities          TEXT,
  pair_key               TEXT,
  unified_severity       TEXT,
  unified_mechanism_text TEXT,
  ddi_confidence         DOUBLE PRECISION,
  ddi_known              BOOLEAN
);
"""
}

def connect():
    try:
        print(f"[loader] Attempting connection to Postgres at {os.getenv('PGHOST', 'db')}:{os.getenv('PGPORT', '5432')}...")
        conn = psycopg2.connect(
            host=os.getenv("PGHOST", "db"),
            port=os.getenv("PGPORT", "5432"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", "postgres"),
            dbname=os.getenv("PGDATABASE", "ddi"),
        )
        conn.autocommit = True
        print("[loader] ✅ Connection successful.")
        return conn
    except Exception as e:
        print(f"[loader] ❌ Failed to connect to Postgres: {type(e).__name__}: {e}")
        sys.exit(1)

def copy_df(cur, df: pd.DataFrame, table: str):
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    cur.copy_expert(f"COPY {table} FROM STDIN WITH (FORMAT csv, NULL '')", buf)

def main():
    print("[loader] Connecting to Postgres...")
    conn = connect()
    print("[loader] Connection established ✅")

    schema = os.getenv("PGSCHEMA", "public")
    with conn.cursor() as cur:
        print(f"[loader] Using schema: {schema}")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}; SET search_path TO {schema};")

        for tbl, _ in TABLES:
            print(f"[loader] Creating table: {tbl}")
            cur.execute(DDL[tbl])

        for tbl, _ in TABLES:
            cur.execute(f"TRUNCATE TABLE {schema}.{tbl};")

        for tbl, fname in TABLES:
            csv_path = OUT / fname
            if not csv_path.exists():
                print(f"[loader] Skipping {tbl} (missing {csv_path})")
                continue

            df = pd.read_csv(csv_path, low_memory=False)
            print(f"[loader] Loading {tbl} ({len(df):,} rows)")

            if tbl == "rxcui_to_ingredient_map":
                df = coerce_intlike(df, ["rxcui", "ingredient_rxcui"])
                buf = df_to_csv_buffer(df)
                cur.copy_expert(f"COPY {schema}.{tbl} FROM STDIN WITH (FORMAT csv, NULL '')", buf)
                continue

            copy_df(cur, df, f"{schema}.{tbl}")

    print("[loader] ✅ Load complete.")


if __name__ == "__main__":
    main()