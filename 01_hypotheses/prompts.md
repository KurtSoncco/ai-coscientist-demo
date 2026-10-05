# Stage 1 — Run the Co-Scientist loop by hand (Gemini app, no API)

Google's Co-Scientist uses a Supervisor plus six agents. Here **you** are the
Supervisor: paste each prompt into the Gemini app (berkeley.edu account) in one
conversation, in order. Attach or paste `data/orbits.csv` first.

Research goal used in the demo:

> Find a law that predicts the orbital period of a body from its orbit size and
> the mass of what it orbits. It must work for the Sun's planets AND for moons
> of Jupiter, Saturn and Earth.

---

## 1. Generation agent

```
You are the Generation agent of a research team. Research goal: <paste goal>.
Data: <paste orbits.csv>.
Propose 8 distinct, testable hypotheses for a formula
period = f(semi_major_axis, central_mass). For each give: the formula, the
reasoning behind it, and one prediction that could prove it wrong.
Do not use any physics law you know by name; reason from the data.
```

## 2. Reflection agent

```
You are the Reflection agent. Review each hypothesis above like a strict peer
reviewer. Score 1-5 for correctness (does it fit the data? check at least 3
rows numerically), novelty, and testability. Flag any hypothesis that fits the
planets but would fail for moons.
```

## 3. Ranking agent (tournament)

```
You are the Ranking agent. Run a pairwise tournament: compare the hypotheses
two at a time in a short debate, pick a winner of each match, and keep an Elo
score starting at 1200 (K = 32). Show the final leaderboard.
```

## 4. Evolution agent

```
You are the Evolution agent. Take the top 3 hypotheses. Improve them: combine
their strengths, fix their weaknesses, simplify. Return 3 evolved hypotheses,
each as a single Python expression for period_days(a_km, M_kg).
```

## 5. Meta-review agent

```
You are the Meta-review agent. Summarize what the team learned, what patterns
the reviews kept flagging, and which ONE hypothesis should go to the code
evolution stage (Stage 2). Write it as a 5-line research overview.
```

**Hand-off:** paste the winning expression into
`02_openevolve/initial_program.py` (or keep the naive starting point and let
evolution find it).

**Discussion point:** Ranking by debate is only as good as the judge. Stage 2
replaces the judge with a number the data computes.
