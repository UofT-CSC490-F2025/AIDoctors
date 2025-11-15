import cProfile, io, pstats
from time import perf_counter
from pathlib import Path
import importlib.util

SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[4]
DATA_PIPELINES_DIR = ROOT / "src" / "data-pipelines"

pipeline_path = DATA_PIPELINES_DIR / "pipeline.py"
spec = importlib.util.spec_from_file_location("pipeline_module", pipeline_path)
pipeline_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(pipeline_module)  # type: ignore

build_ddi_reference = pipeline_module.build_ddi_reference  # type: ignore

def run_once():
    _ddi_ref = build_ddi_reference()

def main():
    print("Running build_ddi_reference() under cProfile...")
    pr = cProfile.Profile()
    pr.enable()
    t0 = perf_counter()
    run_once()
    t1 = perf_counter()
    pr.disable()

    print(f"\n⏱ Runtime (no profiling): {t1 - t0:.3f} seconds\n")

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats("cumulative")
    ps.print_stats(40)

    out_path = SCRIPT_PATH.parent / "build_ddi_reference_cprofile.txt"
    out_path.write_text(s.getvalue())

    print("==== cProfile stats for build_ddi_reference() ====\n")
    print(s.getvalue())
    print(f"\n📄 Saved to: {out_path}\n")

if __name__ == "__main__":
    main()
