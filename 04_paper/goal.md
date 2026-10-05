# Stage 4: from results to a pseudo-paper with OpenScience

[OpenScience](https://github.com/synthetic-sciences/openscience) is an
open-source research agent: it reads the project folder, runs code, and writes
up what it finds. Here it gets the Stage 3 results and the 17th-century
sources, and must produce a short paper.

This is the first stage that is **not blind**. The agent is told what the
variables are, and is asked to compare the blind result with the literature.

No key, or no Node.js? Use the offline fallback, which fills the same paper
skeleton from `results/results.json` with template text:

```bash
uv run python 04_paper/make_paper.py        # writes paper/report.md
```

## Setup (once)

OpenScience is a Node.js tool, installed separately from the Python
environment.

```bash
npm install -g @synsci/openscience
export OPENAI_API_KEY=your-key     # read from the environment; or run `openscience keys add`
openscience models openai          # lists the models your key can use
```

Run Stage 3 first so `results/` exists:

```bash
uv run python 03_tests/hypothesis_tests.py
```

## Run

From the repo root, in one shot:

```bash
openscience run --workspace project --delegation off -m openai/gpt-4.1-mini \
  "$(sed -n '/^```text$/,/^```$/p' 04_paper/goal.md | sed '1d;$d')"
```

`--workspace project` lets the agent read and write files in this repo. Its
shell commands stay in OpenScience's sandbox. Or open the workspace in the
browser with `openscience web .` and paste the prompt.

Our test run took about 40 seconds and is saved, unedited, as
[`paper/openscience_report.md`](../paper/openscience_report.md), with an audit
of its errors in [`paper/README.md`](../paper/README.md).

## Prompt

```text
You are writing a short research paper from results that already exist.

Read these files first:
- results/results.json and results/model_comparison.md  (all numbers)
- results/fig_pred_vs_obs.png                           (the figure)
- data/key.json                                         (what x1, x2, y and the groups are)
- literature/README.md                                  (three 17th-century sources)
- 03_tests/hypothesis_tests.py                          (the method)

Write paper/report.md with these sections:
1. Abstract (under 120 words).
2. Introduction: what Galileo (1610), Kepler (1619) and Newton (1687) each
   claimed. Quote only passages that appear in literature/README.md and cite
   them by their keys [G1610], [K1619], [N1687].
3. Hypotheses: H1 to H4 as formulas, and which historical claim each one is.
4. Methods: blind protocol (disguised names and units, added noise),
   train and held-out groups, least squares in log space, bootstrap, F-test.
5. Results: the model comparison table, the figure, the exponent intervals,
   both tests of whether x2 matters, and the estimate of G with both intervals.
6. Discussion: does the blind result agree with Kepler? With Newton? Explain
   why the two intervals for G differ and which one to trust.
7. Limitations, including what you could not verify.
8. AI-use statement: which tools produced which parts.

Rules:
- Every number must be copied from results/results.json. Do not compute new
  numbers unless you run code and save it under paper/.
- Do not add references beyond the three in literature/README.md.
- If a result disagrees with a historical claim, say so plainly.
```

## What to point out while replaying the recording

- Which files it opened, and whether it ran any code of its own.
- Whether each quotation matches `literature/README.md` word for word.
- Whether each number matches `results/results.json`. Pick three and check.
- Whether it noticed that the row-resampling interval for G is too narrow.
- Compare with `paper/example_report.md`, the template version: what did the
  agent add, and is the addition supported?
- Then read the audit in `paper/README.md`. Did you catch the same errors?
