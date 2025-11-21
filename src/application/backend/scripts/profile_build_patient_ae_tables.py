import cProfile
import io
import pstats
from time import perf_counter
from pathlib import Path
import importlib.util
import pandas as pd


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[4]  

DATA_PIPELINES_DIR = ROOT / "src" / "data-pipelines"
RAW_DIR = ROOT / "data" / "raw_datasets"
OUT_DIR = ROOT / "data" / "datasets_output"


pipeline_path = DATA_PIPELINES_DIR / "pipeline.py"

spec = importlib.util.spec_from_file_location("pipeline_module", pipeline_path)
pipeline_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pipeline_module)  

build_patient_ae_tables = pipeline_module.build_patient_ae_tables  
load_synthea = pipeline_module.load_synthea  


meds, patients, conds = load_synthea()

# AEOLUS lookup (Stage 2 output)
aeolus_path = OUT_DIR / "aeolus_drug_outcome_lookup.csv"

aeolus_by_rxcui = pd.read_csv(aeolus_path, low_memory=False)

# Product→ingredient mapping (Stage 3 output)
map_path = OUT_DIR / "rxcui_to_ingredient_map.csv"

prod_ing_map = pd.read_csv(map_path, low_memory=False)


def run_once():
    """Execute once so cProfile can time build_patient_ae_tables internals."""
    _risk_ann, _enriched, _topk = build_patient_ae_tables(
        meds=meds,
        patients=patients,
        conds=conds,
        aeolus_by_rxcui=aeolus_by_rxcui,
        prod_ing_map=prod_ing_map,
    )


def main():
    print("Running build_patient_ae_tables() under cProfile...")

    pr = cProfile.Profile()
    pr.enable()
    t0 = perf_counter()
    run_once()
    t1 = perf_counter()
    pr.disable()

    duration = t1 - t0
    print(f"\n⏱ Runtime (no profiling): {duration:.3f} seconds\n")

    # Format output
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats("cumulative")
    ps.print_stats(40)

    # Save to file
    out_path = SCRIPT_PATH.parent / "build_patient_ae_tables_cprofile.txt"
    with out_path.open("w") as f:
        f.write(s.getvalue())

    print("==== cProfile stats for build_patient_ae_tables() ====\n")
    print(s.getvalue())
    print(f"\n📄 Saved to: {out_path}\n")


if __name__ == "__main__":
    main()
