# Data Pipelines

This folder contains scripts that:

1. Sync raw input datasets from S3  
2. Rebuild the full Synthea × AEOLUS × DDI pipeline  
3. Load the generated tables into PostgreSQL  

The pipeline produces per-patient adverse-event risk tables, a unified DDI reference table, and collapsed per-patient DDI exposures.

---

## Setup

Open a terminal and set your working directory to this folder:

```bash
cd src/data_pipelines
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.\.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

You must have AWS credentials configured for S3, SSM, and Secrets Manager, and network access to the PostgreSQL instance.

---

## 1. Sync Raw Datasets from S3

To download all raw datasets into `data/raw_datasets/`:

```bash
python3 sync_raw_from_s3.py
```

This script:

- Reads S3 config from AWS SSM parameters:  
  `/aidoctors/s3/raw-datasets-bucket`  
  `/aidoctors/s3/raw-datasets-prefix`
- Downloads all files under that prefix
- Reconstructs the folder structure within `data/raw_datasets/`

---

## 2. Rebuild the Synthea × AEOLUS × DDI Pipeline

Run the ETL pipeline:

```bash
python3 rebuild_synthea_aeolus_ddi_pipeline.py
# (use your actual filename if different)
```

This script expects the following under `data/raw_datasets/`:

### Synthea
- `patients.csv`
- `medications.csv`
- `conditions.csv`

### AEOLUS (headerless TSVs)
- `concept*.tsv`
- `standard_drug_outcome_statistics*.tsv`

### DDI Sources
- `ddinter_downloads_code_*.csv`  
- `Mendeley.csv`  
- `CRESCENDDI - Positive Controls.xlsx`  
- `CRESCENDDI - Negative Controls.xlsx` *(optional)*  

### Output Tables (written to `data/datasets_output/`)
- `aeolus_drug_outcome_lookup.csv`
- `rxcui_to_ingredient_map.csv`
- `patient_ae_risk_annotations_rxnav.csv`
- `ae_risk_enriched.csv`
- `ae_risk_topk_per_patient_drug.csv`
- `ddi_ref_unified.csv`
- `patient_ddi_collapsed_from_topk.csv`

---

## 3. Load Pipeline Outputs into PostgreSQL

To create and populate the DB tables:

```bash
python3 load_pipeline_outputs_to_postgres.py
```

This script fetches:

- DB host, port, user, dbname, schema from SSM
- DB password from Secrets Manager (via `/aidoctors/db/password-secret-arn`)

Then it:

- Creates or replaces all pipeline tables
- Loads every output CSV from `data/datasets_output/`
- Converts list columns (e.g., Comorbidities) into valid PostgreSQL array literals

---

## Full End-to-End Workflow

```bash
# 1. Sync raw data
python3 sync_raw_from_s3.py

# 2. Rebuild derived pipeline outputs
python3 rebuild_synthea_aeolus_ddi_pipeline.py

# 3. Load results into PostgreSQL
python3 load_pipeline_outputs_to_postgres.py
```

After this, all datasets exist locally as CSVs and remotely as Postgres tables in the configured schema.

---
