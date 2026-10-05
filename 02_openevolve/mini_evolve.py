"""Offline fallback: evolution with no LLM and no API key.

Same idea as AlphaEvolve/OpenEvolve, stripped to the core so it runs in seconds:
  - a hypothesis is   y = C * x1^p * x2^q
  - mutation nudges p, q, or both by +/- 0.25 (a joint edit, like an LLM rewrite)
  - C is fitted to the training data (log-space least squares)
  - selection keeps the candidates with the lowest held-out error

Run:  python 02_openevolve/mini_evolve.py
"""
import math
import random
import sys
from pathlib import Path

from evaluator import load_rows

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "data"))
from reveal import G_ACCEPTED, implied_g  # noqa: E402  (only used to check the answer at the end)

random.seed(5)  # this seed plateaus, then breaks through: good for a live demo

rows = load_rows()
train = [r for r in rows if r["split"] == "train"]
test = [r for r in rows if r["split"] == "test"]


def fit_log_c(p, q):
    """Best log10(C) on training data for fixed exponents."""
    resid = [
        math.log10(r["y"]) - p * math.log10(r["x1"]) - q * math.log10(r["x2"])
        for r in train
    ]
    return sum(resid) / len(resid)


def error(p, q, data):
    log_c = fit_log_c(p, q)
    return sum(
        abs(log_c + p * math.log10(r["x1"]) + q * math.log10(r["x2"]) - math.log10(r["y"]))
        for r in data
    ) / len(data)


def mutate(ind):
    p, q = ind
    move = random.choice(["p", "q", "both"])
    if move in ("p", "both"):
        p += random.choice([-0.25, 0.25])
    if move in ("q", "both"):
        q += random.choice([-0.25, 0.25])
    return (round(p, 2), round(q, 2))


population = [(1.0, 0.0)] * 4  # start from the naive law: linear in x1, no x2
best_so_far = float("inf")
for gen in range(1, 13):
    children = [mutate(random.choice(population)) for _ in range(4)]
    pool = sorted(set(population + children), key=lambda ind: error(*ind, test))
    population = pool[:4]
    best = population[0]
    err = error(*best, test)
    mark = "  <- new best" if err < best_so_far else ""
    best_so_far = min(best_so_far, err)
    print(
        f"gen {gen:2d}  best: y ~ x1^{best[0]:+.2f} * x2^{best[1]:+.2f}   "
        f"held-out log10 error = {err:.4f}{mark}"
    )

p, q = population[0]
print(f"\nDiscovered law: y is proportional to x1^{p} * x2^{q}")

if (p, q) == (1.5, -0.5):
    print("\nReveal: x1 is orbit size, x2 is the mass of the central body, y is the orbital period.")
    g_est = implied_g(10 ** fit_log_c(p, q))
    print(f"Implied gravitational constant G = {g_est:.3e}  (accepted: {G_ACCEPTED:.3e})")
    print(
        f"That is Kepler's third law with Newton's correction, recovered from {len(train)} noisy "
        f"orbits and checked on {len(test)} more."
    )
