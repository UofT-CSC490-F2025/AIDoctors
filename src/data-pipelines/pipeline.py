
"""
Rebuilds the full Synthea × AEOLUS × DDI pipeline from raw CSVs.

Inputs (under data/raw_datasets/):
  Synthea:
    - patients.csv
    - medications.csv
    - conditions.csv
  AEOLUS bundle (headerless TSVs):
    - concept*.tsv
    - standard_drug_outcome_statistics*.tsv
  DDI sources:
    - ddinter_downloads_code_*.csv (A,B,D,H,L,P,R,V...)
    - Mendeley.csv
    - CRESCENDDI - Positive Controls.xlsx
    - CRESCENDDI - Negative Controls.xlsx  (optional)

Outputs (under data/datasets_output/):
  - aeolus_drug_outcome_lookup.csv
  - rxcui_to_ingredient_map.csv
  - patient_ae_risk_annotations_rxnav.csv
  - ae_risk_enriched.csv
  - ae_risk_topk_per_patient_drug.csv
  - ddi_ref_unified.csv
  - patient_ddi_collapsed_from_topk.csv
"""

from __future__ import annotations
import os, re, sys, json, time, argparse
from pathlib import Path
from typing import Tuple, List, Dict, Any

import numpy as np
import pandas as pd

# ----------------------------
# Config
# ----------------------------
ROOT = Path(".")
RAW  = ROOT / "data" / "raw_datasets"
OUT  = ROOT / "data" / "datasets_output"
OUT.mkdir(parents=True, exist_ok=True)

AEO_CASE_MIN = 20
AEO_ROR_MIN  = 2.0
TOP_K        = 5

# ----------------------------
# Utils
# ----------------------------
def log(msg: str) -> None:
    print(f"[etl] {msg}", flush=True)

def find_one(base: Path, filename: str) -> Path:
    hits = list(base.rglob(filename))
    if not hits:
        raise FileNotFoundError(f"Could not find {filename} under {base}")
    hits.sort(key=lambda p: len(str(p)))
    return hits[0]

def find_stem_any(base: Path, stem: str) -> Path:
    hits = [p for p in base.rglob("*") if p.is_file() and p.name.lower().startswith(stem.lower())]
    if not hits:
        raise FileNotFoundError(f"Could not find file starting with '{stem}' under {base}")
    hits.sort(key=lambda p: len(str(p)))
    return hits[0]

def to_datetime_utc(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", utc=True)
    return df

def normalize_name(s: str) -> str:
    if pd.isna(s): return ""
    s = s.lower()
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"[^a-z0-9\s\-\+]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def clean_synthea_drug(desc: str) -> str:
    if not isinstance(desc, str): return ""
    s = re.split(r"\d", desc, maxsplit=1)[0].strip()
    return re.sub(r"\s+", " ", s)

# ----------------------------
# Stage 1: Synthea (meds/patients/conditions)
# ----------------------------
def load_synthea() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    meds = pd.read_csv(find_one(RAW, "medications.csv"), low_memory=False)
    patients = pd.read_csv(find_one(RAW, "patients.csv"), low_memory=False)
    conds = pd.read_csv(find_one(RAW, "conditions.csv"), low_memory=False)

    # RxCUI from CODE "RxNorm:12345"
    meds["rxcui"] = meds["CODE"].astype(str).str.extract(r"(\d+)")[0].astype("Int64")
    meds = to_datetime_utc(meds, ["START","STOP"])
    log(f"Synthea meds: rows={len(meds):,}, unique RxCUIs={meds['rxcui'].nunique()}")

    patients["BIRTHDATE"] = pd.to_datetime(patients["BIRTHDATE"], utc=True, errors="coerce")

    return meds, patients, conds

# ----------------------------
# Stage 2: AEOLUS concept + stats → lookup
# ----------------------------
def build_aeolus_lookup() -> pd.DataFrame:
    concept_path = find_stem_any(RAW, "concept")
    stats_path   = find_stem_any(RAW, "standard_drug_outcome_statistics")

    concept_raw = pd.read_csv(concept_path, sep="\t", header=None, dtype=str, low_memory=False)
    concept_raw.columns = [
        "concept_id","concept_name","domain_id","vocabulary_id","concept_class_id",
        "standard_concept","concept_code","valid_start_date","valid_end_date","invalid_reason"
    ]
    concept = concept_raw[["concept_id","concept_name","vocabulary_id","concept_code"]].copy()
    concept["concept_id"] = pd.to_numeric(concept["concept_id"], errors="coerce").astype("Int64")

    rxn = concept[concept["vocabulary_id"].str.upper()=="RXNORM"].copy()
    rxn["rxcui"] = pd.to_numeric(rxn["concept_code"], errors="coerce").astype("Int64")
    rxn = rxn.rename(columns={"concept_id":"drug_concept_id","concept_name":"drug_name"})[
        ["drug_concept_id","drug_name","rxcui"]
    ]

    mdr = concept[concept["vocabulary_id"].str.upper()=="MEDDRA"].copy()
    mdr = mdr.rename(columns={
        "concept_id":"outcome_concept_id",
        "concept_name":"outcome_text",
        "concept_code":"meddra_code"
    })[["outcome_concept_id","outcome_text","meddra_code"]]

    stats = pd.read_csv(stats_path, sep="\t", header=None, dtype=str, low_memory=False)
    stats.columns = [
        "drug_concept_id","outcome_concept_id","snomed_outcome_concept_id",
        "case_count","prr","prr_95_percent_upper_confidence_limit","prr_95_percent_lower_confidence_limit",
        "ror","ror_95_percent_upper_confidence_limit","ror_95_percent_lower_confidence_limit"
    ]
    for c in ["drug_concept_id","outcome_concept_id","case_count","prr","ror"]:
        stats[c] = pd.to_numeric(stats[c], errors="coerce")

    stats_full = (stats
        .merge(rxn, on="drug_concept_id", how="inner")
        .merge(mdr, on="outcome_concept_id", how="left"))

    aeolus_by_rxcui = (stats_full
        .dropna(subset=["rxcui"])
        .astype({"rxcui":"int"})
        .query("case_count >= @AEO_CASE_MIN and ror >= @AEO_ROR_MIN")
        .sort_values(["rxcui","ror"], ascending=[True, False])
        [["rxcui","drug_name","outcome_concept_id","outcome_text","meddra_code","case_count","prr","ror"]]
        .reset_index(drop=True))

    out = OUT / "aeolus_drug_outcome_lookup.csv"
    aeolus_by_rxcui.to_csv(out, index=False)
    log(f"Saved AEOLUS lookup → {out} (rows={len(aeolus_by_rxcui):,}, RxCUIs={aeolus_by_rxcui['rxcui'].nunique():,})")
    return aeolus_by_rxcui

# ----------------------------
# Stage 3: RxCUI product→ingredient mapping
# ----------------------------
def map_product_to_ingredient(meds: pd.DataFrame, use_rxnav: bool=False) -> pd.DataFrame:
    """
    If OUT/rxcui_to_ingredient_map.csv exists, reuse it.
    Otherwise:
      - if use_rxnav=False, fall back to identity mapping (product == ingredient)
      - if use_rxnav=True, call RxNav (online) to get ingredient RxCUI
    """
    cache_path = OUT / "rxcui_to_ingredient_map.csv"
    if cache_path.exists():
        m = pd.read_csv(cache_path)
        log(f"Reusing mapping cache → {cache_path} (rows={len(m):,})")
        return m

    rxcuis = meds["rxcui"].dropna().astype(int).unique().tolist()
    mapping = []

    if not use_rxnav:
        # Offline-friendly fallback: identity map (works for ingredients; products remain same)
        mapping = [{"rxcui": int(r), "ingredient_rxcui": int(r)} for r in rxcuis]
    else:
        import requests
        def get_ing(rxcui: int) -> int|None:
            try:
                url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/related.json?tty=IN"
                resp = requests.get(url, timeout=8)
                if not resp.ok:
                    return None
                data = resp.json()
                for grp in data.get("relatedGroup", {}).get("conceptGroup", []):
                    if grp.get("tty") == "IN" and "conceptProperties" in grp:
                        return int(grp["conceptProperties"][0]["rxcui"])
            except Exception:
                return None
        for r in rxcuis:
            mapping.append({"rxcui": int(r), "ingredient_rxcui": get_ing(int(r))})

    mp = pd.DataFrame(mapping)
    mp.to_csv(cache_path, index=False)
    log(f"Saved product→ingredient map → {cache_path} (rows={len(mp):,})")
    return mp

# ----------------------------
# Stage 4: Patient AE risks (join) + enriched + Top-K
# ----------------------------
def build_patient_ae_tables(meds: pd.DataFrame,
                            patients: pd.DataFrame,
                            conds: pd.DataFrame,
                            aeolus_by_rxcui: pd.DataFrame,
                            prod_ing_map: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    meds_min = (meds.rename(columns={"PATIENT":"patient_uuid"})
                [["patient_uuid","DESCRIPTION","START","STOP","rxcui"]]
                .dropna(subset=["rxcui"]))
    meds_min["rxcui"] = meds_min["rxcui"].astype(int)

    # map to ingredient
    meds_min = meds_min.merge(prod_ing_map, on="rxcui", how="left")
    aeolus_by_rxcui = aeolus_by_rxcui.astype({"rxcui":"int"})
    risk = meds_min.merge(aeolus_by_rxcui, left_on="ingredient_rxcui", right_on="rxcui", how="inner")

    risk["estimated_onset"] = (risk["START"] + pd.to_timedelta(5, unit="D")).dt.tz_convert("UTC")

    risk_ann = (risk.rename(columns={"DESCRIPTION":"synthea_drug_desc","drug_name":"aeolus_drug_name"})[[
        "patient_uuid","rxcui_x","ingredient_rxcui","synthea_drug_desc","aeolus_drug_name",
        "START","STOP","estimated_onset",
        "outcome_concept_id","outcome_text","meddra_code",
        "case_count","prr","ror"
    ]].sort_values(["patient_uuid","ingredient_rxcui","ror"], ascending=[True, True, False]).reset_index(drop=True))

    risk_path = OUT / "patient_ae_risk_annotations_rxnav.csv"
    risk_ann.to_csv(risk_path, index=False)
    log(f"Saved patient AE risks → {risk_path} (rows={len(risk_ann):,})")

    # demographics
    idx_date = risk_ann["START"].dropna().min() if risk_ann["START"].notna().any() else pd.Timestamp.now(tz="UTC")
    age_years = ((idx_date - patients["BIRTHDATE"]).dt.days // 365).astype("Int64")
    demo = patients.rename(columns={"Id":"patient_uuid","GENDER":"Sex"})[["patient_uuid","Sex"]].copy()
    demo["Age"] = age_years

    # comorbidities
    comorb = (conds.groupby("PATIENT")["DESCRIPTION"]
                    .apply(lambda x: sorted({str(v) for v in x if pd.notna(v)}))
                    .reset_index()
                    .rename(columns={"PATIENT":"patient_uuid","DESCRIPTION":"Comorbidities"}))

    enriched = (risk_ann
                .merge(demo, on="patient_uuid", how="left")
                .merge(comorb, on="patient_uuid", how="left"))

    # nice subset/order
    keep_cols = [c for c in [
        "patient_uuid","Age","Sex","Comorbidities",
        "START","STOP",
        "synthea_drug_desc","rxcui_x","ingredient_rxcui",
        "aeolus_drug_name","outcome_text","meddra_code","case_count","prr","ror"
    ] if c in enriched.columns]
    enriched = enriched[keep_cols].copy()
    enriched["ror"] = pd.to_numeric(enriched["ror"], errors="coerce")
    enriched["case_count"] = pd.to_numeric(enriched["case_count"], errors="coerce")
    enriched = enriched.sort_values(["patient_uuid","ror","case_count"], ascending=[True, False, False]).reset_index(drop=True)

    enriched_path = OUT / "ae_risk_enriched.csv"
    enriched.to_csv(enriched_path, index=False)
    log(f"Saved enriched table → {enriched_path} (rows={len(enriched):,})")

    # Top-K per patient×drug
    enriched["synthea_drug"] = enriched["synthea_drug_desc"].astype(str).map(clean_synthea_drug)
    sorted_enriched = enriched.sort_values(["patient_uuid","synthea_drug","ror","case_count"],
                                           ascending=[True, True, False, False])
    topk = (sorted_enriched.groupby(["patient_uuid","synthea_drug"], as_index=False, sort=False)
            .head(TOP_K).reset_index(drop=True))

    topk_path = OUT / "ae_risk_topk_per_patient_drug.csv"
    topk.to_csv(topk_path, index=False)
    log(f"Saved Top-{TOP_K} per patient×drug → {topk_path} (rows={len(topk):,})")

    return risk_ann, enriched, topk

# ----------------------------
# Stage 5: DDI sources → unified reference
# ----------------------------
def build_ddi_reference() -> pd.DataFrame:
    # DDInter chunks
    dd_paths = sorted(RAW.glob("ddinter_downloads_code_*.csv"))
    dd_frames = []
    for p in dd_paths:
        df = pd.read_csv(p, low_memory=False)
        df = df.rename(columns={"Drug_A":"drug1_name","Drug_B":"drug2_name","Level":"ddinter_level"})
        dd_frames.append(df[["drug1_name","drug2_name","ddinter_level"]])
    ddinter = pd.concat(dd_frames, ignore_index=True) if dd_frames else pd.DataFrame(columns=["drug1_name","drug2_name","ddinter_level"])

    # Mendeley
    mendeley = pd.read_csv(find_one(RAW, "Mendeley.csv"), low_memory=False)[["drug1_name","drug2_name","interaction_type"]]
    mendeley = mendeley.rename(columns={"interaction_type":"interaction_type_mendeley"})

    # CrescendDI Positive (Micromedex-like)
    pos = pd.read_excel(find_one(RAW, "CRESCENDDI - Positive Controls.xlsx"))
    cresc_pos = pos.rename(columns={
        "DRUG_1_CONCEPT_NAME":"drug1_name",
        "DRUG_2_CONCEPT_NAME":"drug2_name",
        "EVENT_CONCEPT_NAME":"interaction_type_crescenddi",
        "MICROMEDEX_SEV_LEVEL":"micromedex_sev_level",
        "MICROMEDEX_EVID_LEVEL":"micromedex_evid_level"
    })[["drug1_name","drug2_name","interaction_type_crescenddi","micromedex_sev_level","micromedex_evid_level"]]

    # Merge all
    merged = (ddinter.merge(cresc_pos, on=["drug1_name","drug2_name"], how="outer")
                      .merge(mendeley, on=["drug1_name","drug2_name"], how="outer"))
    merged.columns = [c.lower() for c in merged.columns]

    # normalize + pair key
    merged["drug1_norm"] = merged["drug1_name"].map(normalize_name)
    merged["drug2_norm"] = merged["drug2_name"].map(normalize_name)
    merged["pair_key"]   = merged.apply(lambda r: tuple(sorted([r["drug1_norm"], r["drug2_norm"]])), axis=1)

    # helpers
    def uniq_list(s: pd.Series) -> list:
        vals = [x for x in s.dropna().tolist() if str(x).strip()!=""]
        flat = []
        for v in vals:
            if isinstance(v, (list, tuple)): flat.extend([x for x in v if str(x).strip()!=""])
            else: flat.append(v)
        seen, out = set(), []
        for v in flat:
            if v not in seen:
                seen.add(v); out.append(v)
        return out

    def first_non_null(s: pd.Series):
        for v in s:
            if pd.notna(v) and str(v).strip()!="": return v
        return np.nan

    ddi_ref = (merged.groupby("pair_key", as_index=False)
        .agg({
            "ddinter_level": uniq_list,
            "micromedex_sev_level": uniq_list,
            "micromedex_evid_level": uniq_list,
            "interaction_type_crescenddi": first_non_null,
            "interaction_type_mendeley": uniq_list,
            "drug1_norm": first_non_null,
            "drug2_norm": first_non_null
        }))

    # source coverage / confidence
    ddi_ref["has_ddinter"]    = ddi_ref["ddinter_level"].apply(lambda x: isinstance(x, list) and len(x)>0)
    ddi_ref["has_micromedex"] = ddi_ref["micromedex_sev_level"].apply(lambda x: isinstance(x, list) and len(x)>0)
    ddi_ref["has_mendeley"]   = ddi_ref["interaction_type_mendeley"].apply(lambda x: isinstance(x, list) and len(x)>0)
    ddi_ref["sources_present"] = ddi_ref.apply(
        lambda r: [s for s,f in [("DDInter",r["has_ddinter"]),("Micromedex",r["has_micromedex"]),("Mendeley",r["has_mendeley"])] if f],
        axis=1
    )
    ddi_ref["src_count"] = ddi_ref["sources_present"].apply(len)
    ddi_ref["ddi_confidence"] = ddi_ref["src_count"]/3.0

    # unified one-column severity + one-column mechanism
    def choose_severity(row):
        # priority: Micromedex > DDInter; take first value if list
        for col in ["micromedex_sev_level","ddinter_level"]:
            val = row.get(col)
            if isinstance(val, list) and len(val)>0:
                v = val[0]
                return np.nan if str(v).lower()=="unknown" else v
            elif pd.notna(val) and val not in [[], "[]", "Unknown"]:
                return val
        return np.nan

    def choose_mechanism(row):
        txt = row.get("interaction_type_mendeley")
        if isinstance(txt, list) and len(txt)>0:
            return ", ".join(sorted(set(map(str, txt))))
        return np.nan

    ddi_ref["unified_severity"] = ddi_ref.apply(choose_severity, axis=1)
    ddi_ref["unified_mechanism_text"] = ddi_ref.apply(choose_mechanism, axis=1)

    simplified = ddi_ref[[
        "pair_key","drug1_norm","drug2_norm",
        "unified_severity","unified_mechanism_text",
        "sources_present","ddi_confidence"
    ]].copy()

    out = OUT / "ddi_ref_unified.csv"
    simplified.to_csv(out, index=False)
    log(f"Saved DDI reference (unified) → {out} (rows={len(simplified):,})")

    return simplified

# ----------------------------
# Stage 6: Patient co-exposures + join DDI ref (Collapsed)
# ----------------------------
def build_patient_ddi_collapsed(topk: pd.DataFrame, ddi_ref_unified: pd.DataFrame) -> pd.DataFrame:
    # normalize
    topk = topk.copy()
    topk["drug_norm"] = topk["drug_name"].map(normalize_name)
    demo_cols = [c for c in ["Age","Sex","Comorbidities"] if c in topk.columns]
    base_cols = ["patient_uuid","drug_name","drug_norm","START","STOP"]

    exposures = (topk[base_cols + demo_cols]
                 .dropna(subset=["patient_uuid","drug_name"])
                 .drop_duplicates())

    # find overlaps per patient
    def overlaps(a0, a1, b0, b1):
        if pd.isna(a0) or pd.isna(b0): return False
        a1 = a1 if pd.notna(a1) else pd.Timestamp.max.tz_localize("UTC")
        b1 = b1 if pd.notna(b1) else pd.Timestamp.max.tz_localize("UTC")
        return (a0 <= b1) and (b0 <= a1)

    from itertools import combinations
    rows = []
    for pid, grp in exposures.groupby("patient_uuid"):
        recs = grp.to_dict("records")
        for r1, r2 in combinations(recs, 2):
            if r1["drug_norm"] == r2["drug_norm"]:
                continue
            if overlaps(r1["START"], r1["STOP"], r2["START"], r2["STOP"]):
                rows.append({
                    "patient_uuid": pid,
                    "drug1": r1["drug_name"], "drug2": r2["drug_name"],
                    "drug1_norm": r1["drug_norm"], "drug2_norm": r2["drug_norm"],
                    "overlap_start": max(r1["START"], r2["START"]),
                    "overlap_stop":  min(
                        r1["STOP"] if pd.notna(r1["STOP"]) else pd.Timestamp.max.tz_localize("UTC"),
                        r2["STOP"] if pd.notna(r2["STOP"]) else pd.Timestamp.max.tz_localize("UTC")
                    ),
                    **{k: r1.get(k, np.nan) for k in demo_cols},
                })
    pairs_df = pd.DataFrame(rows)
    if pairs_df.empty:
        log("No overlapping exposures found. Skipping DDI join.")
        return pairs_df

    pairs_df["pair_key"] = pairs_df.apply(lambda r: tuple(sorted([r["drug1_norm"], r["drug2_norm"]])), axis=1)
    ddi_ref_unified["pair_key"] = ddi_ref_unified.apply(lambda r: tuple(sorted([r["drug1_norm"], r["drug2_norm"]])), axis=1)

    collapsed = pairs_df.merge(
        ddi_ref_unified[["pair_key","unified_severity","unified_mechanism_text","ddi_confidence"]],
        on="pair_key", how="left"
    )
    collapsed["ddi_known"] = collapsed["unified_severity"].notna()

    out = OUT / "patient_ddi_collapsed_from_topk.csv"
    collapsed.to_csv(out, index=False)
    log(f"Saved patient DDI (collapsed) → {out} (rows={len(collapsed):,})")

    return collapsed

# ----------------------------
# Main
# ----------------------------
def main():
    ap = argparse.ArgumentParser(description="Rebuild the Synthea×AEOLUS×DDI pipeline.")
    ap.add_argument("--use-rxnav", action="store_true",
                    help="Call RxNav to convert product RxCUI → ingredient RxCUI (requires internet). "
                         "If omitted, uses identity fallback or existing cache.")
    args = ap.parse_args()

    log("Loading Synthea…")
    meds, patients, conds = load_synthea()

    log("Building AEOLUS lookup…")
    aeolus_lookup = build_aeolus_lookup()

    log("Mapping RxCUI product→ingredient…")
    prod_ing_map = map_product_to_ingredient(meds, use_rxnav=args.use_rxnav)

    log("Joining patient AE risks + enriched + Top-K…")
    risk_ann, enriched, topk = build_patient_ae_tables(meds, patients, conds, aeolus_lookup, prod_ing_map)

    log("Building unified DDI reference…")
    ddi_ref_unified = build_ddi_reference()

    log("Constructing per-patient DDI (collapsed) from Top-K…")
    _collapsed = build_patient_ddi_collapsed(topk, ddi_ref_unified)

    log("✔ All done.")

if __name__ == "__main__":
    pd.set_option("display.max_colwidth", 200)
    main()
