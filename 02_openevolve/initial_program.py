"""Starting hypothesis for OpenEvolve: a deliberately naive law.

OpenEvolve may only rewrite the code between the EVOLVE-BLOCK markers.
"""
import math  # noqa: F401  (available to evolved code)


# EVOLVE-BLOCK-START
def fit(train_rows):
    """Learn a formula for y from x1 and x2.

    train_rows is a list of dicts with keys "x1", "x2", "y" (all positive).
    Return a function predict(x1, x2) -> y. Any constant in the formula must
    be estimated here from train_rows.

    Naive guess: y grows linearly with x1 and ignores x2.
    """
    c = math.exp(sum(math.log(r["y"] / r["x1"]) for r in train_rows) / len(train_rows))

    def predict(x1: float, x2: float) -> float:
        return c * x1

    return predict
# EVOLVE-BLOCK-END
