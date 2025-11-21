import cProfile
import pstats
import io
import sys
from pathlib import Path
from types import SimpleNamespace

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent  # .../app/backend
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.prediction_service import build_prompt  


def make_dummy_payload():
    return SimpleNamespace(
        Age=72,
        Sex="Male",
        Comorbidities=["Chronic kidney disease", "Atrial fibrillation", "Hypertension"],
        overlap_start="2024-01-01",
        overlap_stop="2024-02-15",
        drug1="warfarin",
        drug2="amiodarone",
        drug1_norm="warfarin",
        drug2_norm="amiodarone",
        ddi_known=True,
        ddi_confidence=3,
        unified_mechanism_text=(
            "Amiodarone inhibits CYP2C9-mediated metabolism of warfarin, "
            "increasing INR and bleeding risk; effect is concentration-"
            "dependent and accentuated in renal impairment."
        ),

        patient_uuid="dummy-patient-123",
        unified_severity=None,
    )


def run_build_prompt():
    """
    Call build_prompt() many times so cProfile has enough signal.

    We reuse a single payload so we measure just string formatting,
    not object construction.
    """
    payload = make_dummy_payload()

    # Warm-up
    build_prompt(payload)

    # Main loop
    for _ in range(100000):
        build_prompt(payload)


if __name__ == "__main__":
    print("Running build_prompt() under cProfile...")

    profiler = cProfile.Profile()
    profiler.enable()
    run_build_prompt()
    profiler.disable()

    stats_stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stats_stream).sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(40)

    # Save to file next to this script
    out_path = CURRENT_DIR / "build_prompt_cprofile.txt"
    with out_path.open("w") as f:
        f.write("==== cProfile stats for build_prompt() ====\n\n")
        f.write(stats_stream.getvalue())

    print("\n==== cProfile stats for build_prompt() ====\n")
    print(stats_stream.getvalue())
    print(f"\nProfile written to: {out_path}")
