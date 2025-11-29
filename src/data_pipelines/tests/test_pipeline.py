import sys
from pathlib import Path

# Ensure the directory containing pipeline.py is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

import numpy as np
import pandas as pd
import datetime as dt

import argparse
import runpy


import pipeline  


# ---------------------------
# Helper utilities: find_* and to_datetime_utc
# ---------------------------

def test_find_one_and_find_stem_any(tmp_path):
    base = tmp_path / "raw"
    base.mkdir()

    # nested paths to exercise rglob / shortest-path logic
    sub = base / "subdir"
    sub.mkdir()

    f1 = base / "patients.csv"
    f1.write_text("dummy\n")

    f2 = sub / "concept_foo.tsv"
    f2.write_text("dummy\n")

    # find_one should locate patients.csv
    found_patients = pipeline.find_one(base, "patients.csv")
    assert found_patients == f1

    # find_stem_any should locate concept_foo.tsv by prefix
    found_concept = pipeline.find_stem_any(base, "concept")
    assert found_concept == f2

    # error branches
    with pytest.raises(FileNotFoundError):
        pipeline.find_one(base, "does_not_exist.csv")
    with pytest.raises(FileNotFoundError):
        pipeline.find_stem_any(base, "nope")




def test_to_datetime_utc():
    df = pd.DataFrame(
        {
            "time_str": ["2020-01-01", "2020-01-02"],
            "other": [1, 2],
        }
    )
    out = pipeline.to_datetime_utc(df.copy(), ["time_str", "missing_col"])

    assert "time_str" in out.columns
    assert str(out["time_str"].dtype).startswith("datetime64[ns, UTC]")
    # untouched column
    assert list(out["other"]) == [1, 2]


# ---------------------------
# Stage 1: load_synthea
# ---------------------------

def test_load_synthea(tmp_path, monkeypatch):
    raw = tmp_path / "raw_datasets"
    raw.mkdir()

    # medications.csv
    meds_df = pd.DataFrame(
        {
            "PATIENT": ["p1"],
            "CODE": ["RxNorm:12345"],
            "START": ["2020-01-01"],
            "STOP": ["2020-01-10"],
        }
    )
    meds_df.to_csv(raw / "medications.csv", index=False)

    # patients.csv
    patients_df = pd.DataFrame(
        {
            "Id": ["p1"],
            "GENDER": ["F"],
            "BIRTHDATE": ["1980-01-01"],
        }
    )
    patients_df.to_csv(raw / "patients.csv", index=False)

    # conditions.csv
    conds_df = pd.DataFrame(
        {
            "PATIENT": ["p1"],
            "DESCRIPTION": ["Hypertension"],
        }
    )
    conds_df.to_csv(raw / "conditions.csv", index=False)

    # point RAW & OUT at tmp dirs
    monkeypatch.setattr(pipeline, "RAW", raw)
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    meds, patients, conds = pipeline.load_synthea()

    # rxcui extracted from CODE
    assert "rxcui" in meds.columns
    assert meds["rxcui"].iloc[0] == 12345

    # datetimes UTC
    assert str(meds["START"].dtype).startswith("datetime64[ns, UTC]")
    # birthdate parsed
    assert str(patients["BIRTHDATE"].dtype).startswith("datetime64[ns, UTC]")
    # conds passed through
    assert conds.equals(conds_df)


# ---------------------------
# Stage 2: build_aeolus_lookup
# ---------------------------

def test_build_aeolus_lookup(tmp_path, monkeypatch):
    raw = tmp_path / "raw_datasets"
    raw.mkdir()
    monkeypatch.setattr(pipeline, "RAW", raw)

    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    # concept*.tsv (headerless)
    concept_path = raw / "concept_test.tsv"
    concept_df = pd.DataFrame(
        [
            # RxNorm drug
            [1, "Metformin", "Drug", "RxNorm", "class", "Y", "111", "", "", ""],
            # MedDRA outcome
            [2, "Lactic acidosis", "Condition", "MEDDRA", "class", "Y", "LA001", "", "", ""],
        ],
        columns=[
            "concept_id",
            "concept_name",
            "domain_id",
            "vocabulary_id",
            "concept_class_id",
            "standard_concept",
            "concept_code",
            "valid_start_date",
            "valid_end_date",
            "invalid_reason",
        ],
    )
    concept_df.to_csv(concept_path, sep="\t", header=False, index=False)

    # standard_drug_outcome_statistics*.tsv (headerless)
    stats_path = raw / "standard_drug_outcome_statistics_test.tsv"
    stats_df = pd.DataFrame(
        [
            # drug_concept_id, outcome_concept_id, snomed, case_count, prr, prr_uc, prr_lc, ror, ror_uc, ror_lc
            [1, 2, 0, 50, 3.0, 0, 0, 4.0, 0, 0],
        ]
    )
    stats_df.to_csv(stats_path, sep="\t", header=False, index=False)

    lookup = pipeline.build_aeolus_lookup()

    assert not lookup.empty
    assert set(["rxcui", "drug_name", "outcome_text", "case_count", "prr", "ror"]).issubset(
        lookup.columns
    )
    row = lookup.iloc[0]
    assert row["rxcui"] == 111
    assert row["drug_name"] == "Metformin"
    assert row["outcome_text"] == "Lactic acidosis"

    # file written
    assert (out_dir / "aeolus_drug_outcome_lookup.csv").exists()



# ---------------------------
# Stage 3: map_product_to_ingredient
# ---------------------------

def test_map_product_to_ingredient_uses_cache(tmp_path, monkeypatch):
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    cache_path = out_dir / "rxcui_to_ingredient_map.csv"
    cached = pd.DataFrame({"rxcui": [111], "ingredient_rxcui": [999]})
    cached.to_csv(cache_path, index=False)

    meds = pd.DataFrame({"rxcui": [111]})

    mp = pipeline.map_product_to_ingredient(meds)
    # should just read cache
    assert len(mp) == 1
    assert mp.iloc[0]["ingredient_rxcui"] == 999


def test_map_product_to_ingredient_calls_rxnav(tmp_path, monkeypatch):
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    # ensure no cache file exists
    cache_path = out_dir / "rxcui_to_ingredient_map.csv"
    assert not cache_path.exists()

    meds = pd.DataFrame({"rxcui": [111, 222]})

    # fake requests.get
    class FakeResp:
        def __init__(self, rxcui):
            self.rxcui = rxcui
            self.ok = True

        def json(self):
            if self.rxcui == 111:
                return {
                    "relatedGroup": {
                        "conceptGroup": [
                            {
                                "tty": "IN",
                                "conceptProperties": [{"rxcui": "999"}],
                            }
                        ]
                    }
                }
            # no IN group -> trigger fallback to self
            return {"relatedGroup": {"conceptGroup": []}}

    def fake_get(url, timeout=8):
        # url .../{rxcui}/related.json
        rxcui = int(url.split("/")[5])
        return FakeResp(rxcui)

    monkeypatch.setattr("requests.get", fake_get)

    mp = pipeline.map_product_to_ingredient(meds)

    # rxcui 111 should map to 999; 222 should map to itself (fallback)
    mp = mp.sort_values("rxcui").reset_index(drop=True)
    assert list(mp["rxcui"]) == [111, 222]
    assert list(mp["ingredient_rxcui"]) == [999, 222]

    # cache file created
    assert cache_path.exists()



# ---------------------------
# Stage 5: build_ddi_reference
# ---------------------------

def test_build_ddi_reference(tmp_path, monkeypatch):
    raw = tmp_path / "raw_datasets"
    raw.mkdir()
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()

    monkeypatch.setattr(pipeline, "RAW", raw)
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    # ddinter_downloads_code_*.csv
    dd_df = pd.DataFrame(
        {
            "Drug_A": ["Drug A"],
            "Drug_B": ["Drug B"],
            "Level": ["Major"],
        }
    )
    dd_df.to_csv(raw / "ddinter_downloads_code_A.csv", index=False)

    # Mendeley.csv
    mend_df = pd.DataFrame(
        {
            "drug1_name": ["Drug A"],
            "drug2_name": ["Drug B"],
            "interaction_type": ["Increased risk of X"],
        }
    )
    mend_df.to_csv(raw / "Mendeley.csv", index=False)

    # CRESCENDDI - Positive Controls.xlsx
    pos_df = pd.DataFrame(
        {
            "DRUG_1_CONCEPT_NAME": ["Drug A"],
            "DRUG_2_CONCEPT_NAME": ["Drug B"],
            "EVENT_CONCEPT_NAME": ["Some interaction"],
            "MICROMEDEX_SEV_LEVEL": ["Contraindicated"],
            "MICROMEDEX_EVID_LEVEL": ["High"],
        }
    )
    pos_path = raw / "CRESCENDDI - Positive Controls.xlsx"
    pos_df.to_excel(pos_path, index=False)

    ddi_ref_unified = pipeline.build_ddi_reference()

    assert not ddi_ref_unified.empty
    row = ddi_ref_unified.iloc[0]
    # normalized names
    assert row["drug1_norm"] == pipeline.normalize_name("Drug A")
    assert row["drug2_norm"] == pipeline.normalize_name("Drug B")
    # unified severity should prefer Micromedex
    assert row["unified_severity"] == "Contraindicated"
    # mechanism text from Mendeley
    assert "Increased risk of X" in (row["unified_mechanism_text"] or "")

    out_file = out_dir / "ddi_ref_unified.csv"
    assert out_file.exists()



def test_build_patient_ddi_collapsed_no_overlap(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    # Two exposures that do NOT overlap
    topk = pd.DataFrame(
        {
            "patient_uuid": ["p1", "p1"],
            "synthea_drug": ["Drug A 10mg", "Drug B 20mg"],
            "START": [_ts("2020-01-01"), _ts("2020-02-01")],
            "STOP": [_ts("2020-01-15"), _ts("2020-02-10")],
        }
    )

    ddi_ref_unified = pd.DataFrame(
        columns=[
            "drug1_norm",
            "drug2_norm",
            "unified_severity",
            "unified_mechanism_text",
            "sources_present",
            "ddi_confidence",
        ]
    )

    collapsed = pipeline.build_patient_ddi_collapsed(topk, ddi_ref_unified)

    # Early-return path: no overlapping exposures
    assert collapsed.empty


# ---------------------------
# Basic utility functions
# ---------------------------

def test_uniq_nonempty():
    s = pd.Series(["a", "", None, "b", "a", "  c  ", " ", np.nan])
    out = pipeline._uniq_nonempty(s)
    assert out == ["a", "b", "c"]


def test_first_non_null():
    s = pd.Series([None, "", "   ", np.nan, " foo ", "bar"])
    out = pipeline._first_non_null(s)
    # should return the first non-empty, non-NaN, stripped string
    assert out == "foo"


def test_normalize_name_basic():
    assert pipeline.normalize_name("Metformin [tablet] 500mg") == "metformin 500mg"
    assert pipeline.normalize_name("  HELLO+WORLD!! ") == "hello+world"
    assert pipeline.normalize_name(np.nan) == ""


def test_clean_synthea_drug():
    assert pipeline.clean_synthea_drug("Metformin 500mg tablet") == "Metformin"
    assert pipeline.clean_synthea_drug("Aspirin 81 mg chewable") == "Aspirin"
    # non-string input -> empty string
    assert pipeline.clean_synthea_drug(123) == ""


# ---------------------------
# Stage 4: build_patient_ae_tables
# ---------------------------

def _ts(s: str):
    """Helper: make UTC timestamp."""
    return pd.Timestamp(s, tz="UTC")


def test_build_patient_ae_tables_minimal(tmp_path, monkeypatch):
    """
    End-to-end-ish unit test for build_patient_ae_tables using tiny in-memory DataFrames.
    """

    # Patch OUT to a tmp directory so tests don't write into real repo
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    # Minimal meds with 1 patient, 1 drug
    meds = pd.DataFrame(
        {
            "PATIENT": ["p1"],
            "DESCRIPTION": ["Metformin 500mg tablet"],
            "START": [_ts("2020-01-01")],
            "STOP": [_ts("2020-01-10")],
            "CODE": ["RxNorm:111"],   # used in load_synthea, but here we pass rxcui directly
            "rxcui": [111],
        }
    )

    # Minimal patients table
    patients = pd.DataFrame(
        {
            "Id": ["p1"],
            "GENDER": ["M"],
            "BIRTHDATE": [_ts("1980-01-01")],
        }
    )

    # Minimal conditions: 2 comorbidities, one duplicated
    conds = pd.DataFrame(
        {
            "PATIENT": ["p1", "p1", "p1"],
            "DESCRIPTION": ["Hypertension", "Diabetes", "Hypertension"],
        }
    )

    # aeolus_by_rxcui: single RxCUI with some signal
    aeolus_by_rxcui = pd.DataFrame(
        {
            "rxcui": [111],
            "drug_name": ["Metformin"],
            "outcome_concept_id": [1],
            "outcome_text": ["Lactic acidosis"],
            "meddra_code": ["X123"],
            "case_count": [100],
            "prr": [3.0],
            "ror": [4.0],
        }
    )

    # product->ingredient map: 1:1 mapping
    prod_ing_map = pd.DataFrame(
        {
            "rxcui": [111],
            "ingredient_rxcui": [111],
        }
    )

    risk_ann, enriched, topk = pipeline.build_patient_ae_tables(
        meds=meds,
        patients=patients,
        conds=conds,
        aeolus_by_rxcui=aeolus_by_rxcui,
        prod_ing_map=prod_ing_map,
    )

    # --- risk_ann checks ---
    assert not risk_ann.empty
    # estimated_onset should be START + 5 days
    assert risk_ann.loc[0, "estimated_onset"] == _ts("2020-01-06")
    assert "aeolus_drug_name" in risk_ann.columns
    assert risk_ann.loc[0, "aeolus_drug_name"] == "Metformin"

    # --- enriched checks ---
    assert not enriched.empty
    # Age approx 40 at index date (2020 vs 1980)
    assert enriched["Age"].iloc[0] == 40
    assert enriched["Sex"].iloc[0] == "M"
    # Comorbidities aggregated as unique list
    comorbs = enriched["Comorbidities"].iloc[0]
    assert isinstance(comorbs, list)
    assert set(comorbs) == {"Hypertension", "Diabetes"}

    # --- topk checks ---
    assert not topk.empty
    # synthea_drug column added and cleaned
    assert "synthea_drug" in topk.columns
    # Since we only have one outcome, Top-K per patient×drug is 1
    n_per_group = (
        topk.groupby(["patient_uuid", "synthea_drug"])
        .size()
        .iloc[0]
    )
    assert n_per_group <= pipeline.TOP_K


# ---------------------------
# Stage 6: build_patient_ddi_collapsed
# ---------------------------

def test_build_patient_ddi_collapsed_overlap(tmp_path, monkeypatch):
    """
    Test that overlapping exposures produce a collapsed DDI row,
    joined correctly to ddi_ref_unified.
    """

    # Patch OUT to tmp_path again
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    # Construct a 'topk' table with 1 patient and 2 overlapping drugs
    topk = pd.DataFrame(
        {
            "patient_uuid": ["p1", "p1"],
            "synthea_drug": ["Drug A 10mg", "Drug B 20mg"],
            "START": [_ts("2020-01-01"), _ts("2020-01-05")],
            "STOP": [_ts("2020-01-20"), _ts("2020-01-15")],
            "Age": [40, 40],
            "Sex": ["M", "M"],
            "Comorbidities": [["Hypertension"], ["Hypertension"]],
        }
    )

    # DDI ref with normalized names
    ddi_ref_unified = pd.DataFrame(
        {
            "drug1_norm": [pipeline.normalize_name("Drug A 10mg")],
            "drug2_norm": [pipeline.normalize_name("Drug B 20mg")],
            "unified_severity": ["Major"],
            "unified_mechanism_text": ["Increased risk of lactic acidosis"],
            "sources_present": [["DDInter", "Micromedex"]],
            "ddi_confidence": [2 / 3.0],
        }
    )

    collapsed = pipeline.build_patient_ddi_collapsed(topk, ddi_ref_unified)

    # Should have produced exactly one pair row
    assert len(collapsed) == 1
    row = collapsed.iloc[0]

    # Check fields
        # Check fields
    assert row["patient_uuid"] == "p1"
    assert row["ddi_known"]       
    assert row["unified_severity"] == "Major"
    assert row["unified_mechanism_text"] == "Increased risk of lactic acidosis"


    # Overlap period must be within the intersection of the two intervals
    assert row["overlap_start"] == _ts("2020-01-05")
    assert row["overlap_stop"] == _ts("2020-01-15")



def test_map_product_to_ingredient_http_error(tmp_path, monkeypatch):
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    meds = pd.DataFrame({"rxcui": [111]})

    class FakeResp:
        ok = False

        def json(self):
            raise RuntimeError("should not be called")

    def fake_get(url, timeout=8):
        return FakeResp()

    monkeypatch.setattr("requests.get", fake_get)

    mp = pipeline.map_product_to_ingredient(meds)
    # on HTTP error, get_ing returns None → fallback to self
    assert list(mp["rxcui"]) == [111]
    assert list(mp["ingredient_rxcui"]) == [111]


def test_map_product_to_ingredient_exception(tmp_path, monkeypatch):
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    meds = pd.DataFrame({"rxcui": [111]})

    def fake_get(url, timeout=8):
        raise ValueError("boom")

    monkeypatch.setattr("requests.get", fake_get)

    mp = pipeline.map_product_to_ingredient(meds)
    # exception branch in get_ing → fallback to self
    assert list(mp["ingredient_rxcui"]) == [111]


def test_build_patient_ae_tables_no_risk_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    # meds: rxcui 111
    meds = pd.DataFrame(
        {
            "PATIENT": ["p1"],
            "DESCRIPTION": ["Foo 10mg"],
            "START": [_ts("2020-01-01")],
            "STOP": [_ts("2020-01-10")],
            "CODE": ["RxNorm:111"],
            "rxcui": [111],
        }
    )

    # patients with valid BIRTHDATE
    patients = pd.DataFrame(
        {"Id": ["p1"], "GENDER": ["F"], "BIRTHDATE": [_ts("1980-01-01")]}
    )

    # no conditions
    conds = pd.DataFrame(columns=["PATIENT", "DESCRIPTION"])

    # aeolus_by_rxcui that does NOT match rxcui 111 → empty inner join
    aeolus_by_rxcui = pd.DataFrame(
        {
            "rxcui": [222],  # different
            "drug_name": ["OtherDrug"],
            "outcome_concept_id": [1],
            "outcome_text": ["Something"],
            "meddra_code": ["X"],
            "case_count": [100],
            "prr": [3.0],
            "ror": [4.0],
        }
    )

    prod_ing_map = pd.DataFrame({"rxcui": [111], "ingredient_rxcui": [111]})

    risk_ann, enriched, topk = pipeline.build_patient_ae_tables(
        meds, patients, conds, aeolus_by_rxcui, prod_ing_map
    )

    # all three should just be empty but constructed without error
    assert risk_ann.empty
    assert enriched.empty
    assert topk.empty


def test_build_patient_ddi_collapsed_missing_drug_col(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    topk = pd.DataFrame(
        {
            "patient_uuid": ["p1"],
            "START": [_ts("2020-01-01")],
            "STOP": [_ts("2020-01-10")],
        }
    )

    ddi_ref_unified = pd.DataFrame(
        columns=[
            "drug1_norm",
            "drug2_norm",
            "unified_severity",
            "unified_mechanism_text",
            "sources_present",
            "ddi_confidence",
        ]
    )

    with pytest.raises(KeyError):
        pipeline.build_patient_ddi_collapsed(topk, ddi_ref_unified)


def test_build_patient_ddi_collapsed_open_ended(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "OUT", tmp_path)

    topk = pd.DataFrame(
        {
            "patient_uuid": ["p1", "p1"],
            "synthea_drug": ["Drug A", "Drug B"],
            "START": [_ts("2020-01-01"), _ts("2020-01-10")],
            "STOP": [pd.NaT, pd.NaT],  # open-ended
        }
    )

    ddi_ref_unified = pd.DataFrame(
        {
            "drug1_norm": [pipeline.normalize_name("Drug A")],
            "drug2_norm": [pipeline.normalize_name("Drug B")],
            "unified_severity": ["Minor"],
            "unified_mechanism_text": ["Some mechanism"],
            "sources_present": [["DDInter"]],
            "ddi_confidence": [1 / 3.0],
        }
    )

    collapsed = pipeline.build_patient_ddi_collapsed(topk, ddi_ref_unified)
    assert len(collapsed) == 1
    row = collapsed.iloc[0]
    assert row["overlap_start"] == _ts("2020-01-10")
    assert pd.isna(row["overlap_stop"]) is False


def test_build_ddi_reference_edge_branches(tmp_path, monkeypatch):
    raw = tmp_path / "raw_datasets"
    raw.mkdir()
    out_dir = tmp_path / "datasets_output"
    out_dir.mkdir()

    monkeypatch.setattr(pipeline, "RAW", raw)
    monkeypatch.setattr(pipeline, "OUT", out_dir)

    # ddinter: three different patterns
    dd_df = pd.DataFrame(
        {
            "Drug_A": ["Drug A", "Drug C", "Drug G"],
            "Drug_B": ["Drug B", "Drug D", "Drug H"],
            "Level": ["Unknown", "", "Minor"],  # Unknown, empty, normal
        }
    )
    dd_df.to_csv(raw / "ddinter_downloads_code_X.csv", index=False)

    # Mendeley: two pairs, one with no DDInter/Micromedex (E/F)
    mend_df = pd.DataFrame(
        {
            "drug1_name": ["Drug A", "Drug E"],
            "drug2_name": ["Drug B", "Drug F"],
            "interaction_type": ["Risk AB", "Risk EF"],
        }
    )
    mend_df.to_csv(raw / "Mendeley.csv", index=False)

    # Positive controls: Micromedex for C/D only
    pos_df = pd.DataFrame(
        {
            "DRUG_1_CONCEPT_NAME": ["Drug C"],
            "DRUG_2_CONCEPT_NAME": ["Drug D"],
            "EVENT_CONCEPT_NAME": [""],
            "MICROMEDEX_SEV_LEVEL": ["Moderate"],
            "MICROMEDEX_EVID_LEVEL": ["Low"],
        }
    )
    pos_df.to_excel(raw / "CRESCENDDI - Positive Controls.xlsx", index=False)

    ref = pipeline.build_ddi_reference()

    # Make lookup by (drug1_norm, drug2_norm)
    def key(d1, d2):
        return tuple(sorted([pipeline.normalize_name(d1), pipeline.normalize_name(d2)]))

    ref_k = {tuple(row["pair_key"]): row for _, row in ref.iterrows()}

    # A/B: ddinter Unknown + Mendeley → unified_severity should be NaN
    ab = ref_k[key("Drug A", "Drug B")]
    assert pd.isna(ab["unified_severity"])
    assert "Risk AB" in (ab["unified_mechanism_text"] or "")

    # E/F: Mendeley only, no ddinter/micromedex → fall-through np.nan severity
    ef = ref_k[key("Drug E", "Drug F")]
    assert pd.isna(ef["unified_severity"])
    assert "Risk EF" in (ef["unified_mechanism_text"] or "")

    # G/H: ddinter only, no Mendeley → mechanism branch that returns np.nan
    gh = ref_k[key("Drug G", "Drug H")]
    assert pd.isna(gh["unified_mechanism_text"])


def test_main_smoke(monkeypatch, tmp_path):
    # fake RAW/OUT so any accidental file ops stay in tmp
    monkeypatch.setattr(pipeline, "RAW", tmp_path / "raw_datasets")
    monkeypatch.setattr(pipeline, "OUT", tmp_path / "datasets_output")

    # stub out each stage to avoid heavy I/O and to verify wiring
    monkeypatch.setattr(pipeline, "load_synthea", lambda: ("meds", "patients", "conds"))
    monkeypatch.setattr(pipeline, "build_aeolus_lookup", lambda: "lookup")
    monkeypatch.setattr(
        pipeline, "map_product_to_ingredient", lambda meds: "prod_ing"
    )

    def fake_build_patient_ae_tables(meds, patients, conds, aeolus, prod_ing):
        assert meds == "meds"
        assert patients == "patients"
        assert conds == "conds"
        assert aeolus == "lookup"
        assert prod_ing == "prod_ing"
        return "risk", "enriched", "topk"

    monkeypatch.setattr(pipeline, "build_patient_ae_tables", fake_build_patient_ae_tables)
    monkeypatch.setattr(pipeline, "build_ddi_reference", lambda: "ddi_ref")

    def fake_build_patient_ddi_collapsed(topk, ref):
        assert topk == "topk"
        assert ref == "ddi_ref"
        return "collapsed"

    monkeypatch.setattr(pipeline, "build_patient_ddi_collapsed", fake_build_patient_ddi_collapsed)

    # avoid argparse inspecting real sys.argv
    monkeypatch.setattr(
        argparse.ArgumentParser, "parse_args", lambda self: argparse.Namespace()
    )

    pipeline.main()  # should run without raising
