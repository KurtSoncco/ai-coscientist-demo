"""Evaluator for OpenEvolve: the metric is the scientist's judge.

Fits are scored by mean absolute error in log10(period). The score that drives
evolution uses the held-out systems (Saturn's moons and Earth's Moon), so a law
that ignores the central mass cannot win by memorizing the training systems.
"""
import csv
import importlib.util
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "orbits.csv"


def load_rows():
    with open(DATA, newline="") as f:
        return [
            {
                "body": r["body"],
                "a_km": float(r["semi_major_axis_km"]),
                "mass": float(r["central_mass_kg"]),
                "period": float(r["period_days"]),
                "split": r["split"],
            }
            for r in csv.DictReader(f)
        ]


def log_error(fn, rows):
    errors = []
    for r in rows:
        pred = fn(r["a_km"], r["mass"])
        if not (isinstance(pred, (int, float)) and math.isfinite(pred) and pred > 0):
            return float("inf")
        errors.append(abs(math.log10(pred) - math.log10(r["period"])))
    return sum(errors) / len(errors)


def evaluate(program_path):
    spec = importlib.util.spec_from_file_location("candidate", program_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        fn = module.predict_period_days
        rows = load_rows()
        train = log_error(fn, [r for r in rows if r["split"] == "train"])
        test = log_error(fn, [r for r in rows if r["split"] == "test"])
    except Exception as exc:  # broken candidates score zero, never crash the run
        return {"combined_score": 0.0, "error": str(exc)}

    if not math.isfinite(test):
        return {"combined_score": 0.0, "train_log_error": train, "test_log_error": test}

    # 1.0 = perfect; an error of one order of magnitude gives 0.5.
    return {
        "combined_score": 1.0 / (1.0 + test),
        "train_log_error": train,
        "test_log_error": test,
    }


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("initial_program.py")
    print(evaluate(str(target)))
