"""Evaluator for OpenEvolve: the metric is the scientist's judge.

A candidate defines fit(train_rows) and returns a function predict(x1, x2).
It only ever sees the training groups, so its constants must come from data.
Fits are scored by mean absolute error in log10(y). The score that drives
evolution uses the held-out groups, so a law that ignores x2 cannot win by
memorizing the training groups.
"""
import csv
import importlib.util
import math
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "observations.csv"


def load_rows(path=DATA):
    with open(path, newline="") as f:
        return [
            {
                "group": r["group"],
                "x1": float(r["x1"]),
                "x2": float(r["x2"]),
                "y": float(r["y"]),
                "split": r["split"],
            }
            for r in csv.DictReader(f)
        ]


def log_error(fn, rows):
    errors = []
    for r in rows:
        pred = fn(r["x1"], r["x2"])
        if not (isinstance(pred, (int, float)) and math.isfinite(pred) and pred > 0):
            return float("inf")
        errors.append(abs(math.log10(pred) - math.log10(r["y"])))
    return sum(errors) / len(errors)


def evaluate(program_path):
    spec = importlib.util.spec_from_file_location("candidate", program_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        rows = load_rows()
        train_rows = [r for r in rows if r["split"] == "train"]
        # Copies with only x1, x2, y: the candidate cannot peek at groups or splits.
        fn = module.fit([{k: r[k] for k in ("x1", "x2", "y")} for r in train_rows])
        train = log_error(fn, train_rows)
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
