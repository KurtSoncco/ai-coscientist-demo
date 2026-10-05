"""Turn the real orbits into the noisy, disguised table the AI tools see.

  - names are hidden: systems become groups A-G, columns become x1, x2, y
  - units are scrambled, so a remembered constant (such as G) is useless
  - measurement noise is added, so the law has to be fitted, not read off

Writes observations.csv (what the tools see) and key.json (how to undo the
disguise, used only at the reveal in 03_tests/hypothesis_tests.py).

Run:  python data/make_dataset.py [--noise 0.03] [--mass-noise 0.10] [--out-dir data]
"""
import argparse
import csv
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 1619  # the year Kepler published the law

# Arbitrary unit changes: x1 = a_km / X1_UNIT_KM, and so on.
X1_UNIT_KM = 7.3e4
X2_UNIT_KG = 4.1e22
Y_UNIT_DAYS = 0.027


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--noise", type=float, default=0.03, help="relative noise on x1 and y")
    parser.add_argument("--mass-noise", type=float, default=0.10, help="relative noise on x2, one draw per group")
    parser.add_argument("--out-dir", type=Path, default=HERE)
    args = parser.parse_args()

    rng = random.Random(SEED)
    with open(HERE / "orbits.csv", newline="") as f:
        orbits = list(csv.DictReader(f))

    systems = sorted({r["system"] for r in orbits})
    rng.shuffle(systems)
    group_of = {s: chr(ord("A") + i) for i, s in enumerate(systems)}
    # One uncertain mass estimate per central body, shared by all its satellites.
    x2_of = {
        s: float(next(r["central_mass_kg"] for r in orbits if r["system"] == s))
        / X2_UNIT_KG
        * math.exp(rng.gauss(0, args.mass_noise))
        for s in systems
    }

    rows = []
    for r in orbits:
        x1 = float(r["semi_major_axis_km"]) / X1_UNIT_KM * math.exp(rng.gauss(0, args.noise))
        y = float(r["period_days"]) / Y_UNIT_DAYS * math.exp(rng.gauss(0, args.noise))
        rows.append(
            {
                "group": group_of[r["system"]],
                "x1": f"{x1:.4g}",
                "x2": f"{x2_of[r['system']]:.4g}",
                "y": f"{y:.4g}",
                "split": r["split"],
            }
        )
    rng.shuffle(rows)
    rows.sort(key=lambda r: r["group"])  # grouped, but in no meaningful order within a group

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with open(args.out_dir / "observations.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["group", "x1", "x2", "y", "split"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    key = {
        "meaning": {
            "x1": "semi-major axis of the orbit",
            "x2": "mass of the central body",
            "y": "orbital period",
        },
        "units": {"x1_km": X1_UNIT_KM, "x2_kg": X2_UNIT_KG, "y_days": Y_UNIT_DAYS},
        "groups": {g: s for s, g in sorted(group_of.items(), key=lambda kv: kv[1])},
        "noise": {"x1_and_y": args.noise, "x2_per_group": args.mass_noise},
        "seed": SEED,
    }
    with open(args.out_dir / "key.json", "w") as f:
        json.dump(key, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(rows)} rows to {args.out_dir / 'observations.csv'} and the key to {args.out_dir / 'key.json'}")


if __name__ == "__main__":
    main()
