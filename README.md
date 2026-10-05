# AI Co-Scientist Demo: Rediscovering Kepler's Law on a Free Tier

A 30-minute, three-tool walk through the AI research pipeline, built for
UC Berkeley students who have no paid AI plan.

**The question:** from 16 real orbits (8 planets plus moons of Jupiter, Saturn
and Earth), can AI tools find a law that predicts orbital period, and does it
generalize to systems it never saw?

**The twist:** Kepler's planets-only law (`T² ∝ a³`) fits the Sun's planets
almost perfectly and fails badly on Saturn's moons. Only a law that includes
the central mass, `T = 2π √(a³ / GM)`, passes the held-out test.

## Contents

- [Quick start](#quick-start)
- [The pipeline](#the-pipeline)
- [Repo layout](#repo-layout)
- [Stage 1: Co-Scientist loop by hand](#stage-1-co-scientist-loop-by-hand)
- [Stage 2: Evolve the code with OpenEvolve](#stage-2-evolve-the-code-with-openevolve)
- [Stage 3: Write it up with OpenScience](#stage-3-write-it-up-with-openscience)
- [How scoring works](#how-scoring-works)
- [Rules for using AI co-scientists](#rules-for-using-ai-co-scientists)
- [Troubleshooting](#troubleshooting)
- [Data sources](#data-sources)

## Quick start

You need [uv](https://docs.astral.sh/uv/) and nothing else. uv installs a
matching Python if you do not have one (3.10 or newer).

```bash
# Install uv (skip if you already have it)
curl -LsSf https://astral.sh/uv/install.sh | sh          # macOS / Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows

git clone https://github.com/KurtSoncco/ai-coscientist-demo.git
cd ai-coscientist-demo

# Create .venv/ and install the locked dependencies
uv sync

# Works with no API key: evolution without an LLM, about 1 second
uv run python 02_openevolve/mini_evolve.py

# Score any hypothesis file
uv run python 02_openevolve/evaluator.py 02_openevolve/initial_program.py
```

`uv sync` creates a virtual environment in `.venv/` from `pyproject.toml` and
`uv.lock`, so everyone in the room gets the same package versions. `uv run`
uses that environment without activating it. To activate it yourself:

```bash
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### Expected output

`mini_evolve.py` sits at `a^1.25 · M^-0.25` for 8 generations, then a joint
mutation escapes to `a^1.5 · M^-0.5`:

```
gen  1  best: period ~ a^+1.25 * M^-0.25   held-out log10 error = 0.2382  <- new best
...
gen  8  best: period ~ a^+1.25 * M^-0.25   held-out log10 error = 0.2382
gen  9  best: period ~ a^+1.50 * M^-0.50   held-out log10 error = 0.0006  <- new best
...
Discovered law: period is proportional to a^1.5 * M^-0.5
Implied gravitational constant G = 6.6835e-11  (accepted: 6.6740e-11)
```

`evaluator.py` on the naive starting program prints a `combined_score` of
about 0.38.

### Without uv

The two commands above use only the Python standard library, so plain
`python 02_openevolve/mini_evolve.py` works. For Stage 2, install the one
dependency into a virtual environment of your own:

```bash
python -m venv .venv && source .venv/bin/activate
pip install openevolve
```

## The pipeline

| Stage | Tool | Mirrors | Cost |
| --- | --- | --- | --- |
| 1. Literature → hypotheses | Gemini app (Berkeley account) | Google Co-Scientist's agent loop | Free, campus license |
| 2. Hypothesis → evidence | [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | DeepMind AlphaEvolve | Free Gemini API key |
| 3. Evidence → paper | [OpenScience](https://github.com/synthetic-sciences/openscience) | Claude Science, Sakana AI Scientist | Same free key |

Each stage hands one thing to the next: Stage 1 produces a candidate formula,
Stage 2 tests and improves it against data, Stage 3 turns the result into a
short report.

## Repo layout

```
data/orbits.csv                   16 orbits; split=train (Sun, Jupiter) / test (Saturn, Earth)
01_hypotheses/prompts.md          five prompts: Generation, Reflection, Ranking, Evolution, Meta-review
02_openevolve/initial_program.py  naive starting law (linear in distance, ignores mass)
02_openevolve/evaluator.py        the judge: log10 error on held-out systems -> combined_score
02_openevolve/config.yaml         OpenEvolve on the free Gemini tier
02_openevolve/mini_evolve.py      offline fallback: no LLM, no key, runs in 1 second
03_openscience/goal.md            setup and prompt for the end-to-end write-up
pyproject.toml, uv.lock           dependencies, pinned for reproducible installs
```

## Stage 1: Co-Scientist loop by hand

No API and no install. Open the Gemini app with your Berkeley account, paste
`data/orbits.csv`, and run the five prompts in
[`01_hypotheses/prompts.md`](01_hypotheses/prompts.md) in order. You act as
the Supervisor; Gemini plays each agent in turn.

To carry the result forward, paste the winning expression into
`02_openevolve/initial_program.py`, or keep the naive starting point and let
evolution find the law.

## Stage 2: Evolve the code with OpenEvolve

1. Get a free API key at [Google AI Studio](https://aistudio.google.com) (no
   credit card).
2. Run:

```bash
export GEMINI_API_KEY=your-key        # never commit it
uv run openevolve-run 02_openevolve/initial_program.py 02_openevolve/evaluator.py \
  --config 02_openevolve/config.yaml --iterations 30
```

The best program lands in `openevolve_output/best/`. OpenEvolve may only
rewrite the code between the `EVOLVE-BLOCK` markers in `initial_program.py`.

Reference scores:

| Hypothesis | `combined_score` |
| --- | --- |
| Correct law, `T = 2π √(a³ / GM)` | about 0.999 |
| Naive start, linear in distance | 0.38 |
| Kepler's planets-only law | 0.33 |

No key, or the free tier is out of quota? Run `mini_evolve.py` instead. It
shows the same plateau-then-breakthrough behavior with random mutations in
place of an LLM.

## Stage 3: Write it up with OpenScience

Follow [`03_openscience/goal.md`](03_openscience/goal.md). OpenScience is a
Node.js tool, so it needs `npm` and is installed separately from the Python
environment. Record this run in advance: it makes many calls and can hit the
free tier's daily limit.

## How scoring works

`evaluator.py` loads a candidate's `predict_period_days(a_km, central_mass_kg)`
and measures the mean absolute error in `log10(period)`:

- **Train** rows are the Sun's 8 planets and Jupiter's 4 moons.
- **Test** rows are 3 of Saturn's moons and Earth's Moon.
- `combined_score = 1 / (1 + test_error)`, so 1.0 is perfect and being off by
  one order of magnitude gives 0.5.
- A candidate that crashes or returns a non-positive or non-finite value
  scores 0.

Only the test error drives evolution. A law that ignores the central mass can
fit the training systems and still lose, which is what forces the mass term.

## Rules for using AI co-scientists

- **The evaluator is the science.** Evolution only optimizes what you measure.
  Here the held-out split is what forces the mass term.
- **Verify every citation and number.** Click the sources; rerun the code.
- **Keep unpublished data off free tiers.** Google may use free-tier prompts;
  use a local open-weight model for private data.
- **Disclose AI use** per your course and venue policy. You own every claim.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `uv: command not found` | Install uv (see [Quick start](#quick-start)) and open a new terminal. |
| `openevolve-run: command not found` | Prefix it with `uv run`, or activate `.venv` first. |
| Authentication error in Stage 2 | `GEMINI_API_KEY` is not set in this terminal; export it again. |
| HTTP 429 or quota errors | The free tier's limit is used up. Lower `--iterations`, wait, or use `mini_evolve.py`. |
| Model not found | Change `llm.models[0].name` in `02_openevolve/config.yaml` to a Gemini model your key can use. |

## Data sources

Orbital elements and masses are standard published values (NASA planetary and
satellite fact sheets), rounded to 4–5 significant figures.
