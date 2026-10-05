# Stage 1 by hand: run the Co-Scientist loop in a chat app (no API)

Google's Co-Scientist uses a Supervisor plus six agents. Here **you** are the
Supervisor: paste each prompt into the Gemini app (berkeley.edu account) in one
conversation, in order. Any chat assistant works.

To run the same loop with code and an API key, use
[`run_coscientist.py`](run_coscientist.py) instead.

**Keep it blind.** Paste only the rows of `data/observations.csv` whose split
is `train`, and only the `group`, `x1`, `x2`, `y` columns. Do not say what the
numbers are. Do not paste `data/orbits.csv` or `data/key.json`.

Research goal used in the demo:

> Find one formula y = f(x1, x2) that predicts y in these noisy measurements.
> Each group shares one value of x2. The formula must also work for groups
> that are not shown, whose x2 is different.

---

## 1. Generation agent

```
You are the Generation agent of a research team. Research goal: <paste goal>.
Data: <paste the training rows>.
Propose 8 distinct, testable hypotheses for a formula y = f(x1, x2). For each
give: the formula with numeric exponents, the reasoning behind it, and one
measurement that could prove it wrong.
Reason only from the numbers. Do not guess what the quantities are.
```

## 2. Reflection agent

```
You are the Reflection agent. Review each hypothesis above like a strict peer
reviewer. Score 1-5 for correctness (does it fit the data? check at least 3
rows numerically, from at least 2 groups), novelty, and testability. Flag any
hypothesis that fits inside one group but would fail for a group with a
different x2.
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
each as a single Python expression for y in terms of x1, x2 and constants
that would be fitted to the data.
```

## 5. Meta-review agent

```
You are the Meta-review agent. Summarize what the team learned, what patterns
the reviews kept flagging, and which ONE hypothesis should go to the code
evolution stage (Stage 2). Write it as a 5-line research overview.
```

**Hand-off:** write the winning expression into the `predict` function in
`02_openevolve/initial_program.py`, fitting its constants inside `fit` (or
keep the naive starting point and let evolution find it).

**Discussion point:** Ranking by debate is only as good as the judge. Stage 2
replaces the judge with a number the data computes, and Stage 3 adds error
bars.
