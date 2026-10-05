# Stage 3 — From result to write-up with OpenScience

OpenScience runs the whole loop in one session: literature, hypothesis, code,
experiment, analysis, write-up. Here it gets the same data and must produce a
short paper.

## Setup (once)

```bash
npm install -g @synsci/openscience
openscience keys add          # paste your GEMINI_API_KEY (Google provider)
openscience .                 # open this repo as the project
```

Pick a Gemini Flash model in the model selector. The free tier has low daily
limits, so record this run before the demo.

## Prompt to paste

```
Goal: discover and validate a law for orbital periods using data/orbits.csv.

1. Briefly review what is known about orbital period scaling (cite sources).
2. Propose at least two competing hypotheses, including one that ignores the
   central mass.
3. Fit each on rows with split=train and report log10 error on split=test.
4. Make one figure: predicted vs observed period, log-log, colored by system.
5. Estimate the gravitational constant G from the best fit, with uncertainty.
6. Write a 1-page report (report.md): question, method, results table, figure,
   limitations. Every number must trace to code you ran.
```

## What to point out while replaying the recording

- Where it searched, what code it ran, and whether the figure matches the code.
- Whether its citations are real (click two of them).
- Compare its G with `02_openevolve/mini_evolve.py` (6.68e-11).
- What it could not know: is 16 orbits enough? What would a referee ask?
