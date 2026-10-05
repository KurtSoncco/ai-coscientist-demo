"""Stage 1 with code: run the Co-Scientist agent loop on the disguised data.

Open Coscientist (https://github.com/jataware/open-coscientist) runs the
Generation, Reflection, Ranking, Evolution and Meta-review agents for you.
No literature server is attached, so the agents work blind: they see only
x1, x2 and y from the training groups.

Needs one key in the environment: OPENAI_API_KEY, ANTHROPIC_API_KEY or GEMINI_API_KEY.

Run:  python 01_hypotheses/run_coscientist.py --model gpt-4.1-mini
      python 01_hypotheses/run_coscientist.py --model gemini/gemini-2.5-flash
      python 01_hypotheses/run_coscientist.py --model anthropic/claude-haiku-4-5-20251001
"""
import argparse
import asyncio
import csv
import json
from pathlib import Path

from open_coscientist import HypothesisGenerator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "observations.csv"

GOAL = """Find a single formula y = f(x1, x2) that predicts y in the measurements below.

The measurements are noisy and in arbitrary units. Each group shares one value
of x2. The formula must also work for groups that are not shown, whose x2 is
different, so say explicitly how y depends on x2.

Reason only from these numbers. State each hypothesis as an explicit formula
with numeric exponents, and say what measurement would prove it wrong.

group,x1,x2,y
{table}
"""


def training_table():
    with open(DATA, newline="") as f:
        return "\n".join(
            f"{r['group']},{r['x1']},{r['x2']},{r['y']}" for r in csv.DictReader(f) if r["split"] == "train"
        )


async def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--model", default="gemini/gemini-2.5-flash", help="any LiteLLM model name")
    parser.add_argument("--hypotheses", type=int, default=4, help="initial hypotheses (more = more API calls)")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "hypotheses.json")
    args = parser.parse_args()

    generator = HypothesisGenerator(
        model_name=args.model,
        max_iterations=1,
        initial_hypotheses_count=args.hypotheses,
        evolution_max_count=2,
    )
    result = await generator.generate_hypotheses(
        research_goal=GOAL.format(table=training_table()),
        opts={"enable_literature_review_node": False},  # keep this stage blind
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2, default=str)
        f.write("\n")

    ranked = sorted(result["hypotheses"], key=lambda h: h.get("elo_rating", 0), reverse=True)
    print("\nFinal ranking (Elo)\n")
    for i, h in enumerate(ranked, 1):
        print(f"{i}. [{h.get('elo_rating', '-')}] {' '.join(h['text'].split())[:300]}\n")
    print(f"Saved the full run (reviews, matchups, meta-review) to {args.out}")


if __name__ == "__main__":
    asyncio.run(main())
