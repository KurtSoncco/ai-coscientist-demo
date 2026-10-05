# AI Co-Scientist Demo: Rediscovering Kepler's Law on a Free Tier

A 30-minute, three-tool walk through the AI research pipeline, built for
UC Berkeley students who have no paid AI plan.

**The question:** from 16 real orbits (8 planets plus moons of Jupiter, Saturn
and Earth), can AI tools find a law that predicts orbital period, and does it
generalize to systems it never saw?

The twist: Kepler's planets-only law (`T² ∝ a³`) fits the Sun's planets almost
perfectly and fails badly on Saturn's moons. Only a law that includes the
central mass, `T = 2π √(a³ / GM)`, passes the held-out test.

| Stage | Tool | Mirrors | Cost |
| --- | --- | --- | --- |
| 1. Literature → hypotheses | Gemini app (Berkeley account) | Google Co-Scientist's agent loop | Free, campus license |
| 2. Hypothesis → evidence | [OpenEvolve](https://github.com/algorithmicsuperintelligence/openevolve) | DeepMind AlphaEvolve | Free Gemini API key |
| 3. Evidence → paper | [OpenScience](https://github.com/synthetic-sciences/openscience) | Claude Science, Sakana AI Scientist | Same free key |

## Repo layout

```
data/orbits.csv                 16 orbits; split=train (Sun, Jupiter) / test (Saturn, Earth)
01_hypotheses/prompts.md        five prompts = Generation, Reflection, Ranking, Evolution, Meta-review
02_openevolve/initial_program.py  naive starting law (linear in distance, ignores mass)
02_openevolve/evaluator.py      the judge: log10 error on held-out systems -> combined_score
02_openevolve/config.yaml       OpenEvolve on the free Gemini tier
02_openevolve/mini_evolve.py    offline fallback, no LLM, no key, runs in 1 second
03_openscience/goal.md          setup + prompt for the end-to-end write-up
```

## Quick start

```bash
git clone <this repo> && cd ai-coscientist-demo
pip install -r requirements.txt

# Works with no key at all: evolution without an LLM
python 02_openevolve/mini_evolve.py

# Score any hypothesis file
python 02_openevolve/evaluator.py 02_openevolve/initial_program.py
```

Expected `mini_evolve.py` output: stuck at `a^1.25 · M^-0.25` for 8
generations, then a joint mutation escapes to `a^1.5 · M^-0.5` and recovers
G ≈ 6.68e-11 (accepted 6.674e-11).

## Stage 1 — Co-Scientist loop by hand (no API)

Open the Gemini app with your Berkeley account, paste `data/orbits.csv`, and
run the five prompts in `01_hypotheses/prompts.md` in order. You act as the
Supervisor; Gemini plays each agent in turn.

## Stage 2 — Evolve the code with OpenEvolve

1. Get a free API key at [Google AI Studio](https://aistudio.google.com) (no credit card).
2. Run:

```bash
export GEMINI_API_KEY=your-key        # never commit it
openevolve-run 02_openevolve/initial_program.py 02_openevolve/evaluator.py \
  --config 02_openevolve/config.yaml --iterations 30
```

The best program lands in `openevolve_output/best/`. A perfect law scores
about 0.999; the naive start scores 0.38; Kepler's planets-only law scores 0.33.

## Stage 3 — Write it up with OpenScience

Follow `03_openscience/goal.md`. Record this run in advance; it makes many
calls and can hit the free tier's daily limit.

## Rules for using AI co-scientists

- **The evaluator is the science.** Evolution only optimizes what you measure.
  Here the held-out split is what forces the mass term.
- **Verify every citation and number.** Click the sources; rerun the code.
- **Keep unpublished data off free tiers.** Google may use free-tier prompts;
  use a local open-weight model for private data.
- **Disclose AI use** per your course and venue policy. You own every claim.

## Data sources

Orbital elements and masses are standard published values (NASA planetary and
satellite fact sheets), rounded to 4–5 significant figures.
