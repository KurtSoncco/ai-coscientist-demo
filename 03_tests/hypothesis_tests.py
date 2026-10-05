"""Stage 3: test the competing hypotheses, then reveal what the data was.

No LLM and no key. Everything is ordinary least squares on log10 values.

  1. Competing hypotheses, fitted on the training groups, judged on held-out groups
  2. Uncertainty: bootstrap intervals for the exponents of the winning law
  3. Significance: does x2 matter at all?
  4. Reveal: undo the disguise and estimate the gravitational constant G

Run:  python 03_tests/hypothesis_tests.py [--data data/observations.csv] [--out results]
"""
import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "02_openevolve"))
sys.path.insert(0, str(ROOT / "data"))
from evaluator import evaluate, load_rows  # noqa: E402
from reveal import G_ACCEPTED, implied_g, load_key  # noqa: E402

N_BOOT = 5000
SEED = 1687  # the year of Newton's Principia
EVOLVED = ROOT / "02_openevolve" / "openevolve_output" / "best" / "best_program.py"

# name, description, design-matrix columns (free exponents), fixed exponents (p, q)
HYPOTHESES = [
    ("H1", "y = c * x1", [], (1.0, 0.0)),
    ("H2", "y = c * x1^p", ["x1"], (0.0, 0.0)),
    ("H3", "y = c * x1^p * x2^q", ["x1", "x2"], (0.0, 0.0)),
    ("H4", "y = c * x1^(3/2) * x2^(-1/2)", [], (1.5, -0.5)),
]
GROUP_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]


def logs(rows):
    return {k: np.log10([r[k] for r in rows]) for k in ("x1", "x2", "y")}


def fit(free, fixed, d):
    """Least squares in log space. Returns (log10 c, p, q)."""
    target = d["y"] - fixed[0] * d["x1"] - fixed[1] * d["x2"]
    design = np.column_stack([np.ones_like(target)] + [d[name] for name in free])
    coef, *_ = np.linalg.lstsq(design, target, rcond=None)
    p = coef[1 + free.index("x1")] if "x1" in free else fixed[0]
    q = coef[1 + free.index("x2")] if "x2" in free else fixed[1]
    return float(coef[0]), float(p), float(q)


def residuals(params, d):
    log_c, p, q = params
    return d["y"] - (log_c + p * d["x1"] + q * d["x2"])


def percentile_interval(values):
    return [float(v) for v in np.percentile(values, [2.5, 97.5])]


def compare_hypotheses(train, test):
    n = len(train["y"])
    table = []
    for name, formula, free, fixed in HYPOTHESES:
        params = fit(free, fixed, train)
        k = 1 + len(free)
        rss = float(np.sum(residuals(params, train) ** 2))
        table.append(
            {
                "name": name,
                "formula": formula,
                "free_parameters": k,
                "log10_c": params[0],
                "p": params[1],
                "q": params[2],
                "train_log_error": float(np.mean(np.abs(residuals(params, train)))),
                "test_log_error": float(np.mean(np.abs(residuals(params, test)))),
                "aic": n * math.log(rss / n) + 2 * k,
                "bic": n * math.log(rss / n) + k * math.log(n),
            }
        )
    return table


def bootstrap(rows, rng):
    """Refit H3 (exponents) and H4 (constant) on resampled data, two ways.

    'rows' treats every observation as independent. 'groups' resamples whole
    groups, which is the honest choice here: all rows in a group share one x2.
    """
    groups = sorted({r["group"] for r in rows})
    by_group = {g: [r for r in rows if r["group"] == g] for g in groups}
    draws = {"rows": [], "groups": []}
    for _ in range(N_BOOT):
        draws["rows"].append([rows[i] for i in rng.integers(0, len(rows), len(rows))])
        while True:
            picked = rng.choice(groups, len(groups))
            if len(set(picked)) >= 3:  # fewer distinct x2 values cannot pin down q
                break
        draws["groups"].append([r for g in picked for r in by_group[g]])

    out = {}
    for how, samples in draws.items():
        h3 = np.array([fit(["x1", "x2"], (0.0, 0.0), logs(s)) for s in samples])
        h4 = np.array([fit([], (1.5, -0.5), logs(s))[0] for s in samples])
        out[how] = {"p": h3[:, 1], "q": h3[:, 2], "log10_c_h4": h4}
    return out


def mass_tests(rows, d):
    """Is x2 needed? Null hypothesis: q = 0."""
    n = len(rows)
    rss2 = float(np.sum(residuals(fit(["x1"], (0.0, 0.0), d), d) ** 2))
    rss3 = float(np.sum(residuals(fit(["x1", "x2"], (0.0, 0.0), d), d) ** 2))
    f_stat = (rss2 - rss3) / (rss3 / (n - 3))

    # Conservative check with one data point per group: fit a common slope in
    # x1 with a separate intercept per group, then regress intercepts on x2.
    groups = sorted({r["group"] for r in rows})
    dummies = np.column_stack([[1.0 if r["group"] == g else 0.0 for r in rows] for g in groups])
    coef, *_ = np.linalg.lstsq(np.column_stack([d["x1"], dummies]), d["y"], rcond=None)
    log_x2 = np.array([math.log10(next(r["x2"] for r in rows if r["group"] == g)) for g in groups])
    line = stats.linregress(log_x2, coef[1:])

    return {
        "f_test": {
            "null": "q = 0 (H2 is enough)",
            "f": f_stat,
            "df": [1, n - 3],
            "p_value": float(stats.f.sf(f_stat, 1, n - 3)),
            "caveat": "treats all rows as independent, but rows in a group share one x2",
        },
        "group_level": {
            "null": "group intercepts do not depend on x2",
            "n_groups": len(groups),
            "common_slope_p": float(coef[0]),
            "q": float(line.slope),
            "q_stderr": float(line.stderr),
            "p_value": float(line.pvalue),
        },
    }


def figure(rows, table, path):
    by_name = {h["name"]: h for h in table}
    groups = sorted({r["group"] for r in rows})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharex=True, sharey=True, facecolor="#fcfcfb")
    for ax, name in zip(axes, ("H2", "H3")):
        h = by_name[name]
        for g, color in zip(groups, GROUP_COLORS):
            for split, marker, face in (("train", "o", color), ("test", "D", "#fcfcfb")):
                pts = [r for r in rows if r["group"] == g and r["split"] == split]
                if not pts:
                    continue
                pred = [10 ** h["log10_c"] * r["x1"] ** h["p"] * r["x2"] ** h["q"] for r in pts]
                ax.scatter(
                    [r["y"] for r in pts], pred, s=42, marker=marker, facecolor=face,
                    edgecolor=color, linewidth=1.6, zorder=3,
                    label=f"{g} ({split})" if name == "H3" else None,
                )
        lims = [min(r["y"] for r in rows) / 3, max(r["y"] for r in rows) * 3]
        ax.plot(lims, lims, color="#898781", linewidth=1, zorder=1)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_facecolor("#fcfcfb")
        ax.grid(True, color="#e6e5e0", linewidth=0.6, zorder=0)
        ax.tick_params(colors="#52514e", labelsize=9)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color("#898781")
        ax.set_title(
            f"{name}: {h['formula']}\nheld-out error {h['test_log_error']:.3f} dex",
            fontsize=10, color="#0b0b0b", loc="left",
        )
        ax.set_xlabel("observed y", color="#52514e")
    axes[0].set_ylabel("predicted y", color="#52514e")
    axes[1].legend(
        title="group (filled = train, open = test)", fontsize=8, title_fontsize=8,
        loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, labelcolor="#52514e",
    )
    fig.suptitle("Predicted against observed: without and with x2", fontsize=12, color="#0b0b0b", x=0.02, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "observations.csv")
    parser.add_argument("--out", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rows = load_rows(args.data)
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    everything = logs(rows)

    # 1. Model selection uses the split. Steps 2-4 then use every row, as one
    #    does for the final estimate once the form of the law has been chosen.
    table = compare_hypotheses(logs(train), logs(test))
    best = min(table, key=lambda h: h["test_log_error"])

    boot = bootstrap(rows, np.random.default_rng(SEED))
    h3_all = fit(["x1", "x2"], (0.0, 0.0), everything)
    exponents = {
        "fitted_on": "all rows",
        "p": h3_all[1],
        "q": h3_all[2],
        "intervals_95": {
            how: {"p": percentile_interval(b["p"]), "q": percentile_interval(b["q"])}
            for how, b in boot.items()
        },
    }
    for interval in exponents["intervals_95"].values():
        interval["contains_3_2"] = interval["p"][0] <= 1.5 <= interval["p"][1]
        interval["contains_minus_1_2"] = interval["q"][0] <= -0.5 <= interval["q"][1]

    key_path = args.data.with_name("key.json")
    key = load_key(key_path)
    log_c_h4 = fit([], (1.5, -0.5), everything)[0]
    reveal = {
        "meaning": key["meaning"],
        "groups": key["groups"],
        "noise": key["noise"],
        "law": "T = 2*pi*sqrt(a^3 / (G*M))",
        "g_estimate": implied_g(10**log_c_h4, key),
        "g_accepted": G_ACCEPTED,
        "g_intervals_95": {
            how: sorted(implied_g(10**c, key) for c in np.percentile(b["log10_c_h4"], [2.5, 97.5]))
            for how, b in boot.items()
        },
    }
    reveal["g_relative_error"] = reveal["g_estimate"] / G_ACCEPTED - 1

    results = {
        "data": {
            "file": str(args.data.relative_to(ROOT)) if args.data.is_relative_to(ROOT) else str(args.data),
            "n_rows": len(rows),
            "n_train": len(train),
            "n_test": len(test),
            "train_groups": sorted({r["group"] for r in train}),
            "test_groups": sorted({r["group"] for r in test}),
        },
        "hypotheses": table,
        "best_on_held_out": best["name"],
        "exponents": exponents,
        "mass_tests": mass_tests(rows, everything),
        "bootstrap": {"resamples": N_BOOT, "seed": SEED},
        "reveal": reveal,
    }
    if EVOLVED.exists():
        results["openevolve_best"] = evaluate(str(EVOLVED))

    with open(args.out / "results.json", "w") as f:
        json.dump(results, f, indent=2)
        f.write("\n")

    lines = [
        "| Hypothesis | Formula | Free parameters | Train error (dex) | Held-out error (dex) | AIC | BIC |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for h in table:
        lines.append(
            f"| {h['name']} | `{h['formula']}` | {h['free_parameters']} | {h['train_log_error']:.3f} "
            f"| {h['test_log_error']:.3f} | {h['aic']:.1f} | {h['bic']:.1f} |"
        )
    (args.out / "model_comparison.md").write_text("\n".join(lines) + "\n")
    figure(rows, table, args.out / "fig_pred_vs_obs.png")

    # Console summary
    print("1. Competing hypotheses (fitted on train, lower is better)\n")
    print(f"   {'':4}{'formula':30}{'train':>8}{'held-out':>10}{'BIC':>9}")
    for h in table:
        print(f"   {h['name']:4}{h['formula']:30}{h['train_log_error']:8.3f}{h['test_log_error']:10.3f}{h['bic']:9.1f}")
    print(f"\n   Best on held-out groups: {best['name']}")

    print("\n2. Exponents of H3, fitted on all rows, with 95% bootstrap intervals\n")
    for how, iv in exponents["intervals_95"].items():
        print(
            f"   resampling {how:7}: p = {exponents['p']:.3f} [{iv['p'][0]:.3f}, {iv['p'][1]:.3f}]"
            f"   q = {exponents['q']:.3f} [{iv['q'][0]:.3f}, {iv['q'][1]:.3f}]"
            f"   contains 3/2 and -1/2: {iv['contains_3_2'] and iv['contains_minus_1_2']}"
        )

    mt = results["mass_tests"]
    print("\n3. Does x2 matter? Null hypothesis: it does not\n")
    print(f"   F-test, H2 against H3:  F({mt['f_test']['df'][0]}, {mt['f_test']['df'][1]}) = {mt['f_test']['f']:.0f},  p = {mt['f_test']['p_value']:.1e}")
    print(
        f"   Group-level check ({mt['group_level']['n_groups']} groups):  q = {mt['group_level']['q']:.3f} "
        f"+/- {mt['group_level']['q_stderr']:.3f},  p = {mt['group_level']['p_value']:.1e}"
    )

    print("\n4. Reveal\n")
    print(f"   x1 = {key['meaning']['x1']},  x2 = {key['meaning']['x2']},  y = {key['meaning']['y']}")
    print(f"   groups: {', '.join(f'{g} = {s}' for g, s in key['groups'].items())}")
    print(f"   G = {reveal['g_estimate']:.3e}  (accepted {G_ACCEPTED:.3e}, {100 * reveal['g_relative_error']:+.1f}%)")
    for how, iv in reveal["g_intervals_95"].items():
        inside = iv[0] <= G_ACCEPTED <= iv[1]
        print(f"   95% interval resampling {how:7}: [{iv[0]:.3e}, {iv[1]:.3e}]   contains accepted value: {inside}")
    print(f"\nWrote results.json, model_comparison.md and fig_pred_vs_obs.png to {args.out}")


if __name__ == "__main__":
    main()
