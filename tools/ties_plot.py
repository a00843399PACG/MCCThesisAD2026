"""Ties in a campaign: between the target and the rest, between any two heuristics, and in
the item order each heuristic follows. Every chart is written per configuration cell, as a grid,
and pooled.

The four heuristic values are recomputed from each .kp here, independently of characterise.py,
and checked against features.csv. On top of the outcome of the label (fitness > 0 strict, = 0 tie,
< 0 failed) three kinds of tie are counted:

  * pair ties: any two of the four heuristics reach the same profit, whether or not either is
    the target, the winner or the loser;
  * target ties: the target is one side of such a pair;
  * order ties: a heuristic's key is tied between items (Heuristics.order breaks it by index,
    since Arrays.sort on objects is stable), and breaking it the other way changes the value.

    /opt/anaconda3/bin/python tools/ties_plot.py --campaign runs/pisinger_main
"""
import argparse
import concurrent.futures
import itertools
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HEURS = ["DEFAULT", "MAX_PROFIT", "MAX_PROFIT_WEIGHT", "MIN_WEIGHT"]
SHORT = {"DEFAULT": "def", "MAX_PROFIT": "maxp", "MAX_PROFIT_WEIGHT": "maxpw", "MIN_WEIGHT": "minw"}
LABEL = {"DEFAULT": "DEF", "MAX_PROFIT": "MAXP", "MAX_PROFIT_WEIGHT": "MAXPW", "MIN_WEIGHT": "MINW"}
TYPES = [f"{h}_{s}" for h in HEURS for s in ("EASY", "HARD")]
PAIRS = list(itertools.combinations(HEURS, 2))
OUTCOME_COLOURS = {"strict": "#4d7f5e", "tie": "#e0a100", "failed": "#b23a3a"}
PAIR_COLOURS = {"with target": "#e0a100", "others only": "#7a8fb8"}


def keys(w, p):
    """Sort key per heuristic, ascending = packed first (the order of Heuristics.order)."""
    return {"DEFAULT": np.zeros(len(w)), "MAX_PROFIT": -p, "MAX_PROFIT_WEIGHT": -(p / w),
            "MIN_WEIGHT": w.astype(float)}


def greedy(w, p, c, order):
    residual, total = c, 0.0
    for i in order:
        if w[i] <= residual:
            residual -= w[i]
            total += p[i]
    return total


def evaluate(path):
    lines = Path(path).read_text().split("\n")
    c = int(lines[0].split(",")[1])
    data = np.array([l.split(",") for l in lines[1:] if l.strip()], dtype=float)
    w, p = data[:, 0].astype(np.int64), data[:, 1]
    idx = np.arange(len(w))
    wl, pl = w.tolist(), p.tolist()
    row = {}
    for h, k in keys(w, p).items():
        row[f"v_{SHORT[h]}"] = greedy(wl, pl, c, np.lexsort((idx, k)).tolist())
        if h != "DEFAULT":
            reverse = greedy(wl, pl, c, np.lexsort((-idx, k)).tolist())
            row[f"order_tie_{SHORT[h]}"] = reverse != row[f"v_{SHORT[h]}"]
    return row


def plot_grid(table, draw, title, path, dpi, cells_dir, prefix):
    ns = sorted(table["n"].unique())
    cols = [(b, a) for b in sorted(table["bits"].unique()) for a in sorted(table["alpha"].unique())]
    fig, axes = plt.subplots(len(ns), len(cols), figsize=(3.6 * len(cols), 2.9 * len(ns)),
                             sharey=True)
    for (n, bits, alpha), cell in table.groupby(["n", "bits", "alpha"]):
        name = f"n={n} b={bits} α={alpha}"
        draw(axes[ns.index(n), cols.index((bits, alpha))], cell, 6, name)
        one, ax = plt.subplots(figsize=(7, 4.2))
        draw(ax, cell, 8, name)
        ax.legend(fontsize=8, loc="upper right")
        one.tight_layout()
        one.savefig(cells_dir / f"{prefix}_n{n}_b{bits}_a{alpha}.png", dpi=dpi)
        plt.close(one)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=len(labels), fontsize=10)
    fig.suptitle(title, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def stacked(ax, frame, layers, colours, fontsize, title, xticks):
    bottom = np.zeros(len(frame))
    for layer in layers:
        ax.bar(range(len(frame)), frame[layer], bottom=bottom, color=colours[layer], label=layer,
               width=0.8)
        bottom += frame[layer].to_numpy()
    ax.set_xticks(range(len(frame)))
    ax.set_xticklabels(xticks, fontsize=fontsize)
    ax.tick_params(axis="y", labelsize=fontsize)
    ax.set_title(title, fontsize=fontsize + 2)


def type_ticks():
    return [f"{LABEL[t.rsplit('_', 1)[0]]}\n{t.rsplit('_', 1)[1]}" for t in TYPES]


def draw_outcomes(ax, cell, fontsize, name):
    frame = cell.groupby("type")[["strict", "tie", "failed"]].sum().reindex(TYPES, fill_value=0)
    stacked(ax, frame, ["strict", "tie", "failed"], OUTCOME_COLOURS, fontsize,
            f"{name}  ties={frame['tie'].sum()} failed={frame['failed'].sum()}", type_ticks())
    for x, t in enumerate(TYPES):
        if frame.loc[t, "tie"]:
            ax.text(x, frame.loc[t, "strict"] + frame.loc[t, "tie"] / 2, str(frame.loc[t, "tie"]),
                    ha="center", va="center", fontsize=fontsize)


def draw_pair_ties(ax, cell, fontsize, name):
    frame = cell.groupby("type")[["with target", "others only"]].sum().reindex(TYPES, fill_value=0)
    stacked(ax, frame, ["with target", "others only"], PAIR_COLOURS, fontsize,
            f"{name}  any pair tie={frame.sum(axis=1).sum()}", type_ticks())
    for x, total in enumerate(frame.sum(axis=1)):
        if total:
            ax.text(x, total, str(total), ha="center", va="bottom", fontsize=fontsize)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--out", default=None, help="default: <campaign>/ties")
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    out = Path(args.out or Path(args.campaign) / "ties")
    cells_dir = out / "cells"
    cells_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(Path(args.campaign) / "features.csv")
    paths = sorted(Path(args.campaign).rglob("*.kp"))
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        mine = pd.DataFrame(list(pool.map(evaluate, paths, chunksize=64)))
    # features.csv is written in this same sorted(rglob) order, and file names repeat across
    # cells that differ only in alpha, so rows are matched by position and checked by name.
    assert len(mine) == len(df) and list(df["file"]) == [q.name for q in paths]
    mine.columns = [f"{c}_re" if c.startswith("v_") else c for c in mine.columns]
    df = pd.concat([df, mine], axis=1)

    mismatch = sum(int((df[f"v_{s}"] != df[f"v_{s}_re"]).sum()) for s in SHORT.values())
    print(f"recomputed heuristic values that differ from features.csv: {mismatch}")

    df["heur"] = df["type"].str.rsplit("_", n=1).str[0]
    values = df[[f"v_{SHORT[h]}_re" for h in HEURS]].to_numpy()
    for a, b in PAIRS:
        df[f"tie_{SHORT[a]}_{SHORT[b]}"] = values[:, HEURS.index(a)] == values[:, HEURS.index(b)]
    df["distinct_values"] = [len(set(v)) for v in values]
    df["any_pair_tie"] = df["distinct_values"] < 4
    target_col = df["heur"].map(HEURS.index).to_numpy()
    target_v = values[np.arange(len(df)), target_col]
    df["target_in_tie"] = (values == target_v[:, None]).sum(axis=1) > 1
    df["with target"] = df["target_in_tie"].astype(int)
    df["others only"] = (df["any_pair_tie"] & ~df["target_in_tie"]).astype(int)
    df["strict"] = (df["fitness"] > 0).astype(int)
    df["tie"] = (df["fitness"] == 0).astype(int)
    df["failed"] = (df["fitness"] < 0).astype(int)
    order_cols = [f"order_tie_{SHORT[h]}" for h in HEURS if h != "DEFAULT"]
    df["order_tie_any"] = df[order_cols].any(axis=1)

    keep = ["file", "type", "n", "bits", "alpha", "fitness", "strict", "tie", "failed",
            *[f"v_{SHORT[h]}_re" for h in HEURS], "distinct_values", "any_pair_tie",
            "target_in_tie", *[f"tie_{SHORT[a]}_{SHORT[b]}" for a, b in PAIRS],
            *order_cols, "order_tie_any"]
    df[keep].to_csv(out / "instance_ties.csv", index=False)
    group = ["n", "bits", "alpha", "type"]
    summary = df.groupby(group)[["strict", "tie", "failed", "with target", "others only",
                                 *[f"tie_{SHORT[a]}_{SHORT[b]}" for a, b in PAIRS],
                                 *order_cols]].sum().reset_index()
    summary.to_csv(out / "ties.csv", index=False)

    plot_grid(summary, draw_outcomes,
              "Label outcome per type: strict (fitness > 0), tie (= 0), failed (< 0)",
              out / "outcomes_per_cell.png", args.dpi, cells_dir, "outcomes")
    plot_grid(summary, draw_pair_ties,
              "Instances where two or more heuristics reach the same profit",
              out / "pair_ties_per_cell.png", args.dpi, cells_dir, "pairties")

    fig, axes = plt.subplots(1, 3, figsize=(20, 5))
    draw_outcomes(axes[0], summary, 9, "All configurations")
    axes[0].legend(fontsize=8)
    draw_pair_ties(axes[1], summary, 9, "All configurations")
    axes[1].legend(fontsize=8)
    pair_names = [f"{LABEL[a]}={LABEL[b]}" for a, b in PAIRS]
    frame = pd.DataFrame({t: [int(df.loc[df["type"] == t, f"tie_{SHORT[a]}_{SHORT[b]}"].sum())
                              for a, b in PAIRS] for t in TYPES}, index=pair_names)
    im = axes[2].imshow(frame.to_numpy(), cmap="Oranges", aspect="auto")
    for (i, j), v in np.ndenumerate(frame.to_numpy()):
        axes[2].text(j, i, str(v), ha="center", va="center", fontsize=8,
                     color="white" if v > frame.to_numpy().max() / 2 else "black")
    axes[2].set_xticks(range(len(TYPES)))
    axes[2].set_xticklabels(type_ticks(), fontsize=8)
    axes[2].set_yticks(range(len(PAIRS)))
    axes[2].set_yticklabels(pair_names, fontsize=9)
    axes[2].set_title("Which pairs tie, all configurations", fontsize=11)
    fig.colorbar(im, ax=axes[2])
    fig.tight_layout()
    fig.savefig(out / "ties_all.png", dpi=args.dpi)
    plt.close(fig)

    for stale in ["ties_per_cell.png"] + [p.name for p in cells_dir.glob("ties_n*.png")]:
        for f in (out / stale, cells_dir / stale):
            f.unlink(missing_ok=True)

    pd.set_option("display.width", 220)
    print(f"instances: {len(df)}")
    print(f"label outcome: strict {df['strict'].sum()}, tie {df['tie'].sum()}, "
          f"failed {df['failed'].sum()}")
    print(f"any pair tie: {df['any_pair_tie'].sum()}  (with target {df['with target'].sum()}, "
          f"others only {df['others only'].sum()})")
    print("distinct heuristic values:", df["distinct_values"].value_counts().sort_index().to_dict())
    print("order ties that change a value:",
          {c: int(df[c].sum()) for c in order_cols}, "any:", int(df["order_tie_any"].sum()))
    print(frame.to_string())
    print(df.groupby("type")[["strict", "tie", "failed", "with target", "others only",
                              "order_tie_any"]].sum().reindex(TYPES).to_string())


if __name__ == "__main__":
    main()
