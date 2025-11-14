import cProfile
import io
import pstats

from app.services.prediction_service import extract_severity


def run_extract_severity():
    """
    Call extract_severity() many times on representative completions.
    """
    sample_completions = [
        '{"severity":"Major"} The co-administration of amiodarone and warfarin '
        'can markedly increase INR and bleeding risk.',

        'Result: {"severity": "moderate"} due to additive QT prolongation.',

        (
            "This interaction is considered minor. The two drugs share hepatic "
            "metabolism but only rarely lead to clinically significant toxicity."
        ),

        (
            "Overall I would rate this as MODERATE severity: there is evidence "
            "of increased serum concentrations but serious events are uncommon."
        ),

        "The drugs have no documented clinically significant interaction.",
    ]

    n_iters = 200_000  
    for i in range(n_iters):
        text = sample_completions[i % len(sample_completions)]
        extract_severity(text)


if __name__ == "__main__":
    print("Running extract_severity() under cProfile...\n")

    profiler = cProfile.Profile()
    profiler.enable()
    run_extract_severity()
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(40)  

    print("==== cProfile stats for extract_severity() ====\n")
    print(s.getvalue())
