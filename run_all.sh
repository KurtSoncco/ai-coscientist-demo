#!/usr/bin/env bash
# Run the pipeline in order. Stages that need an LLM are skipped when no key is set.
#
#   ./run_all.sh                       # offline stages only if no key is exported
#   OPENAI_API_KEY=... ./run_all.sh    # also runs Open Coscientist and OpenEvolve
set -euo pipefail
cd "$(dirname "$0")"

if [ -n "${OPENAI_API_KEY:-}" ]; then
  model="gpt-4.1-mini"; config="02_openevolve/config.openai.yaml"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  model="anthropic/claude-haiku-4-5-20251001"; config="02_openevolve/config.anthropic.yaml"
elif [ -n "${GEMINI_API_KEY:-}" ]; then
  model="gemini/gemini-2.5-flash"; config="02_openevolve/config.yaml"
else
  model=""; config=""
fi

echo "== Data: noisy, disguised observations"
uv run python data/make_dataset.py

if [ -n "$model" ]; then
  echo "== Stage 1: Open Coscientist ($model)"
  uv run python 01_hypotheses/run_coscientist.py --model "$model" \
    || echo "Stage 1 failed (rate limit?). Continuing."
  echo "== Stage 2: OpenEvolve"
  uv run openevolve-run 02_openevolve/initial_program.py 02_openevolve/evaluator.py \
    --config "$config" --iterations 30 --log-level WARNING \
    || echo "Stage 2 failed (rate limit?). Continuing."
else
  echo "== Stage 1: skipped, no API key (see 01_hypotheses/prompts.md for the by-hand route)"
  echo "== Stage 2: no API key, running the offline evolution instead"
  uv run python 02_openevolve/mini_evolve.py
fi

echo "== Stage 3: hypothesis tests and reveal"
uv run python 03_tests/hypothesis_tests.py

echo "== Stage 4: pseudo-paper (template version; see 04_paper/goal.md for OpenScience)"
uv run python 04_paper/make_paper.py
