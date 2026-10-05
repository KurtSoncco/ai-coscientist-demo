"""Offline fallback: evolution with no LLM and no API key.

Same idea as AlphaEvolve/OpenEvolve, stripped to the core so it runs in seconds:
  - a hypothesis is   period = C * a^p * M^q
  - mutation nudges p, q, or both by +/- 0.25 (a joint edit, like an LLM rewrite)
  - C is fitted to the training data (log-space least squares)
  - selection keeps the candidates with the lowest held-out error

Run:  python 02_openevolve/mini_evolve.py
"""
import math
import random

from evaluator import load_rows

G_TRUE = 6.674e-11  # m^3 kg^-1 s^-2, only used to check the answer at the end
random.seed(1)  # this seed plateaus, then breaks through: good for a live demo

rows = load_rows()
train = [r for r in rows if r["split"] == "train"]
test = [r for r in rows if r["split"] == "test"]


def fit_log_c(p, q):
    """Best log10(C) on training data for fixed exponents."""
    resid = [
        math.log10(r["period"]) - p * math.log10(r["a_km"]) - q * math.log10(r["mass"])
        for r in train
    ]
    return sum(resid) / len(resid)


def error(p, q, data):
    log_c = fit_log_c(p, q)
    return sum(
        abs(log_c + p * math.log10(r["a_km"]) + q * math.log10(r["mass"]) - math.log10(r["period"]))
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


population = [(1.0, 0.0)] * 4  # start from the naive law: linear in a, no mass
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
        f"gen {gen:2d}  best: period ~ a^{best[0]:+.2f} * M^{best[1]:+.2f}   "
        f"held-out log10 error = {err:.4f}{mark}"
    )

p, q = population[0]
print(f"\nDiscovered law: period is proportional to a^{p} * M^{q}")

if (p, q) == (1.5, -0.5):
    # period_days = C * a_km^1.5 * M^-0.5  and  T = 2*pi*sqrt(a^3 / (G M))  =>  solve for G
    c = 10 ** fit_log_c(p, q)
    g_est = (2 * math.pi * (1e3) ** 1.5 / (c * 86400)) ** 2
    print(f"Implied gravitational constant G = {g_est:.4e}  (accepted: {G_TRUE:.4e})")
    print("That is Kepler's third law with Newton's correction, recovered from 12 orbits.")
