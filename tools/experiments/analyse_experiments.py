"""Tables and figures (300 dpi) for the runs of run_experiments.py.

Fitness is shown in units of p_max = 2^bits: the bound v_H < v_MAXPW + p_max means a labelled
type dominated by MAX_PROFIT/WEIGHT can only reach fitness in (0, 1) in these units.

    /opt/anaconda3/bin/python tools/experiments/analyse_experiments.py
"""
import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

TYPES = ["DEFAULT_EASY", "MAX_PROFIT_EASY", "MIN_WEIGHT_EASY", "MAX_PROFIT_WEIGHT_HARD"]
CAMPAIGN_BUDGET = 100_000


def load(folder):
    traces, finals = [], []
    for path in sorted(Path(folder).glob("*.csv")):
        text = path.read_text()
        if "final," not in text:
            continue
        meta = dict(re.findall(r"(\w+)=([^\s]+)", text.splitlines()[0]))
        key = {"init": meta["init"], "type": meta["type"], "n": int(meta["n"]),
               "seed": int(meta["seed"]), "pmax": 2 ** int(meta["bits"])}
        for line in text.splitlines()[1:]:
            parts = line.split(",")
            if parts[0] == "trace":
                traces.append({**key, "evals": int(parts[1]), "best": float(parts[2])})
            elif parts[0] == "first_positive":
                key["first_positive"] = int(parts[1])
            elif parts[0] == "final":
                finals.append({**key, "final": float(parts[1]), "v_def": float(parts[2]),
                               "v_minw": float(parts[3]), "v_maxpw": float(parts[4]),
                               "v_maxp": float(parts[5])})
    traces = pd.DataFrame(traces)
    traces["best_pmax"] = traces["best"] / traces["pmax"]
    return traces, pd.DataFrame(finals)


def at(traces, budget):
    return traces[traces["evals"] == budget].set_index(["init", "type", "n", "seed"])["best_pmax"]


def trajectories(traces, inits, path, title, dpi):
    ns = sorted(traces["n"].unique())
    colours = dict(zip(ns, plt.cm.viridis(np.linspace(0, 0.9, len(ns)))))
    styles = {"random": "-", "seeded": "--"}
    fig, axes = plt.subplots(1, len(TYPES), figsize=(5.2 * len(TYPES), 4.4))
    for ax, t in zip(axes, TYPES):
        for init in inits:
            for n in ns:
                sub = traces[(traces["type"] == t) & (traces["n"] == n) & (traces["init"] == init)]
                if sub.empty:
                    continue
                for _, run in sub.groupby("seed"):
                    ax.plot(run["evals"], run["best_pmax"], styles[init], color=colours[n],
                            alpha=0.25, linewidth=0.7)
                med = sub.groupby("evals")["best_pmax"].median()
                ax.plot(med.index, med.values, styles[init], color=colours[n], linewidth=2,
                        label=f"n={n}" + ("" if len(inits) == 1 else f" {init}"))
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axhline(1, color="grey", linewidth=0.8, linestyle=":")
        ax.axvline(CAMPAIGN_BUDGET, color="red", linewidth=0.8, linestyle=":")
        ax.set_xscale("log")
        ax.set_yscale("symlog", linthresh=1)
        ax.set_xlabel("evaluations")
        ax.set_title(t, fontsize=10)
    axes[0].set_ylabel("best fitness / p_max  (symlog)")
    axes[0].legend(fontsize=7, ncol=1 if len(inits) == 1 else 2)
    fig.suptitle(title + "   (red: campaign budget 100k; black: fitness 0; dotted grey: bound 1)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", default="runs/experiments")
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()
    out = Path(args.runs) / "figures"
    out.mkdir(parents=True, exist_ok=True)
    traces, finals = load(args.runs)
    budget = int(traces["evals"].max())
    print(f"{len(finals)} completed runs, budget {budget}")

    rows = []
    for (init, t, n), runs in finals.groupby(["init", "type", "n"]):
        b100 = at(traces, CAMPAIGN_BUDGET).loc[(init, t, n)]
        bfull = at(traces, budget).loc[(init, t, n)]
        b10k = at(traces, 10_000).loc[(init, t, n)]
        rows.append({
            "init": init, "type": t, "n": n, "runs": len(runs),
            "strict@100k": int((b100 > 0).sum()), f"strict@{budget // 1000}k": int((bfull > 0).sum()),
            "median@10k": b10k.median(), "median@100k": b100.median(),
            f"median@{budget // 1000}k": bfull.median(),
            "gain_100k_to_end": (bfull - b100).median(),
            "gain_10k_to_100k": (b100 - b10k).median(),
            "max@end": bfull.max(),
            "first_positive_median": runs.loc[runs["first_positive"] > 0, "first_positive"].median(),
        })
    summary = pd.DataFrame(rows).sort_values(["init", "type", "n"])
    summary.to_csv(out / "summary.csv", index=False)
    pd.set_option("display.width", 250)
    print(summary.round(3).to_string(index=False))

    trajectories(traces[traces["init"] == "random"], ["random"], out / "exp1_2_trajectory_random.png",
                 "Experiments 1-2: random initial population", args.dpi)
    trajectories(traces[traces["init"] == "seeded"], ["seeded"], out / "exp3_trajectory_seeded.png",
                 "Experiment 3: population seeded on the tie boundary", args.dpi)
    trajectories(traces, ["random", "seeded"], out / "exp3_random_vs_seeded.png",
                 "Random (solid) vs seeded (dashed)", args.dpi)

    fig, axes = plt.subplots(1, len(TYPES), figsize=(5.2 * len(TYPES), 4), sharey=True)
    ns = sorted(summary["n"].unique())
    bars = [("random", CAMPAIGN_BUDGET, "random @100k", "#9bb1d4"),
            ("random", budget, f"random @{budget // 1000}k", "#3b5b92"),
            ("seeded", CAMPAIGN_BUDGET, "seeded @100k", "#f2c57c"),
            ("seeded", budget, f"seeded @{budget // 1000}k", "#c77f00")]
    width = 0.2
    for ax, t in zip(axes, TYPES):
        for i, (init, b, label, colour) in enumerate(bars):
            vals = at(traces, b)
            share = [(vals.loc[(init, t, n)] > 0).mean() if (init, t, n) in vals.index.droplevel(3)
                     else np.nan for n in ns]
            ax.bar(np.arange(len(ns)) + (i - 1.5) * width, share, width, color=colour, label=label)
        ax.set_xticks(range(len(ns)))
        ax.set_xticklabels([f"n={n}" for n in ns])
        ax.set_title(t, fontsize=10)
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("share of runs with a strict instance (fitness > 0)")
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "strict_share.png", dpi=args.dpi)
    plt.close(fig)


if __name__ == "__main__":
    main()
