import os
import cProfile
import pstats
import io
import asyncio

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_profile.db")

from app.schemas.prediction import DDIPredictRequest
from app.routers.predictions import predict 


def make_sample_request() -> DDIPredictRequest:
    """
    Build a representative DDIPredictRequest payload.
    You can tweak this to mirror a real case from your dataset.
    """
    return DDIPredictRequest(
        patient_uuid="patient-12345",
        drug1="Warfarin",
        drug2="Aspirin",
        drug1_norm="warfarin",
        drug2_norm="aspirin",
        overlap_start="2024-01-15",
        overlap_stop="2024-02-15",
        Age=65,
        Sex="M",
        Comorbidities=["Hypertension", "Diabetes"],
        unified_severity="Major",
        unified_mechanism_text="Both drugs affect blood clotting mechanisms",
        ddi_confidence=0.95,
        ddi_known=True,
    )


async def run_predict_once():
    req = make_sample_request()
    resp = await predict(req)
    print("Predicted severity:", resp.severity)


def main():
    profiler = cProfile.Profile()

    print("Running predict() under cProfile...\n")
    profiler.enable()
    asyncio.run(run_predict_once())
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(40)  

    print("\n==== cProfile stats for predict() ====\n")
    print(s.getvalue())


if __name__ == "__main__":
    main()
