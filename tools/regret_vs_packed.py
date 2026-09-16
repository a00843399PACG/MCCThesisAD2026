"""Is the value of algorithm selection governed by the number of packed items rather than by n?

Corollary: the regret of MAXPW against the per-instance oracle is below p_max on every
instance, so relative to the oracle value it is below p_max / v_MAXPW. With m items packed and
profits uniform on {1..2^bp}, v_MAXPW is about m * 2^bp / 2, so the relative regret is bounded
by about 2/m and should fall as 1/m whatever n is.

This pools every campaign, bins instances by m (the items MAXPW packs), and checks:
  * the pointwise bound r/v < 2/m;
  * the slope of mean relative regret against m on a log-log fit;
  * cells that share m but differ in n, which decide whether m or n is the controlling axis.

    /opt/anaconda3/bin/python tools/regret_vs_packed.py
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

VALUES = ["v_def", "v_minw", "v_maxpw", "v_maxp"]
CAMPAIGNS = ["runs/pisinger_main", "runs/holdout_s4", "runs/sweep_s5_lambda",
             "runs/sweep_s5_mu30", "runs/sweep_s5_lambda3_n1000"]


def load(paths):
    frames = []
    for p in paths:
        f = Path(p) / "features.csv"
        if f.exists():
            d = pd.read_csv(f)
            d["campaign"] = Path(p).name
            frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d["vbs"] = d[VALUES].max(axis=1)
    d["r_rel"] = (d["vbs"] - d["v_maxpw"]) / d["vbs"]
    d["pmax"] = 2.0 ** d["bits"]
    d["bound_rel"] = d["pmax"] / d["v_maxpw"]
    d["m"] = d["m_maxpw"]
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaigns", nargs="+", default=CAMPAIGNS)
    args = ap.parse_args()
    d = load(args.campaigns)
    print(f"{len(d)} instances; m from {d.m.min()} to {d.m.max()}")

    print(f"\npointwise: r/v < 2/m holds in {(d.r_rel < 2 / d.m).mean() * 100:.2f}% of instances; "
          f"max r/v * m = {(d.r_rel * d.m).max():.3f}")
    print(f"r/v < p_max/v_MAXPW holds in {(d.r_rel <= d.bound_rel).mean() * 100:.2f}%")

    edges = np.unique(np.round(np.geomspace(d.m.min(), d.m.max() + 1, 12)).astype(int))
    d["bin"] = pd.cut(d.m, edges, right=False)
    g = d.groupby("bin", observed=True).agg(
        instances=("m", "size"), m_mean=("m", "mean"), n_min=("n", "min"), n_max=("n", "max"),
        share_r_positive=("r_rel", lambda x: 100 * (x > 0).mean()),
        mean_regret_pct=("r_rel", lambda x: 100 * x.mean()),
        max_regret_pct=("r_rel", lambda x: 100 * x.max()),
        mean_bound_pct=("bound_rel", lambda x: 100 * x.mean()))
    print("\nby number of packed items:")
    print(g.round(3).to_string())

    fit = g[g.mean_regret_pct > 0]
    slope, intercept = np.polyfit(np.log(fit.m_mean), np.log(fit.mean_regret_pct), 1)
    print(f"\nlog-log fit of mean regret against m: slope {slope:.2f} "
          f"(a 1/m law is -1), intercept {np.exp(intercept):.2f}")

    cells = d.groupby(["campaign", "n", "bits", "alpha"]).agg(
        m=("m", "mean"), mean_regret_pct=("r_rel", lambda x: 100 * x.mean())).reset_index()
    cells.to_csv("runs/regret_vs_packed_cells.csv", index=False)
    ok = cells[cells.mean_regret_pct > 0]
    for axis in ("m", "n"):
        s, _ = np.polyfit(np.log(ok[axis]), np.log(ok.mean_regret_pct), 1)
        r = np.corrcoef(np.log(ok[axis]), np.log(ok.mean_regret_pct))[0, 1]
        print(f"across cells: log regret vs log {axis}: slope {s:.2f}, r^2 {r ** 2:.3f}")

    print("\ncells sharing m within 20% but differing in n:")
    rows = []
    for i, a in cells.iterrows():
        for j, b in cells.iterrows():
            if a.n < b.n and abs(np.log(a.m / b.m)) < np.log(1.2) and b.n / a.n >= 2:
                rows.append({"n_low": int(a.n), "m_low": round(a.m, 1),
                             "regret_low_pct": round(a.mean_regret_pct, 4),
                             "n_high": int(b.n), "m_high": round(b.m, 1),
                             "regret_high_pct": round(b.mean_regret_pct, 4),
                             "n_ratio": round(b.n / a.n, 1)})
    pairs = pd.DataFrame(rows).drop_duplicates()
    print(pairs.sort_values("n_ratio", ascending=False).head(15).to_string(index=False))
    if len(pairs):
        ratio = (pairs.regret_high_pct / pairs.regret_low_pct.replace(0, np.nan)).median()
        print(f"\nmedian regret ratio between matched cells (high n / low n): {ratio:.2f} "
              f"— a value near 1 says m, not n, sets the regret")


if __name__ == "__main__":
    main()
