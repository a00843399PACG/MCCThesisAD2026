"""Robustness of the feature-space results to the choice of feature map.

The generator itself exposes four features (KP.getFeature): mean weight, mean profit and mean
profit-per-weight, each divided by its maximum, and the weight-profit correlation rescaled to
[0, 1]. This recomputes them for every instance and repeats, with them in place of the seven
features, the two measurements the thesis draws from feature space: the signal/noise split of the
type separation (feature_separation.py) and the cost-sensitive selector (selection_gap.py).

    /opt/anaconda3/bin/python tools/feature4_robustness.py --campaign runs/pisinger_main
"""
import argparse
import concurrent.futures
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import silhouette_score
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler

FEAT4 = ["norm_mean_weight", "norm_mean_profit", "norm_mean_ratio", "norm_correlation"]
VALUES = ["v_def", "v_minw", "v_maxpw", "v_maxp"]


def feat4(path):
    lines = Path(path).read_text().split("\n")
    data = np.array([l.split(",") for l in lines[1:] if l.strip()], dtype=float)
    w, p = data[:, 0], data[:, 1]
    ratio = p / w
    r = np.corrcoef(w, p)[0, 1] if w.std() > 0 and p.std() > 0 else 0.0
    return [w.mean() / w.max(), p.mean() / p.max(), ratio.mean() / ratio.max(), r / 2 + 0.5]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--jobs", type=int, default=4)
    args = ap.parse_args()
    root = Path(args.campaign)
    table = pd.read_csv(root / "features.csv")
    paths = sorted(root.rglob("*.kp"))
    assert [q.name for q in paths] == list(table["file"])
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        f4 = pd.DataFrame(list(pool.map(feat4, paths, chunksize=64)), columns=FEAT4)
    df = pd.concat([table, f4], axis=1)
    df["seed"] = df["file"].str.extract(r"_s(\d+)_")[0].astype(int)
    df.to_csv(root / "pca" / "feat4.csv", index=False)

    sep = []
    for (n, bits, alpha), cell in df.groupby(["n", "bits", "alpha"]):
        within = float(cell.groupby("type")[FEAT4].std().to_numpy().mean())
        cent = cell.groupby("type")[FEAT4].mean().to_numpy()
        between = float(np.mean([np.linalg.norm(cent[i] - cent[j])
                                 for i in range(8) for j in range(i + 1, 8)]))
        X = StandardScaler().fit_transform(cell[FEAT4])
        sep.append({"n": n, "within": within, "between": between,
                    "sil_type": silhouette_score(X, cell["type"])})
    sep = pd.DataFrame(sep).groupby("n").mean()
    sep["within_sqrt_n"] = sep["within"] * np.sqrt(sep.index)

    gap = []
    for n, cell in df.groupby("n"):
        values = cell[VALUES].to_numpy()
        vbs = values.max(axis=1)
        sbs = int(np.argmax(values.sum(axis=0)))
        regret = (vbs[:, None] - values) / vbs[:, None]
        X = cell[FEAT4 + ["alpha_real"]].to_numpy()
        pick = np.empty(len(cell), dtype=int)
        for train, test in GroupKFold(5).split(X, groups=cell["seed"]):
            reg = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=0, n_jobs=args.jobs)
            reg.fit(X[train], regret[train])
            pick[test] = reg.predict(X[test]).argmin(axis=1)
        v_sel = values[np.arange(len(cell)), pick]
        g_sbs = (vbs - values[:, sbs]).sum()
        gap.append({"n": n, "regret_sbs_rel_%": 100 * ((vbs - values[:, sbs]) / vbs).mean(),
                    "regret_selector_rel_%": 100 * ((vbs - v_sel) / vbs).mean(),
                    "closed_gap_%": 100 * (g_sbs - (vbs - v_sel).sum()) / g_sbs if g_sbs > 0 else np.nan})
    gap = pd.DataFrame(gap).set_index("n")
    out = sep.join(gap)
    out.to_csv(root / "pca" / "feat4_robustness.csv")
    print(out.round(3).to_string())


if __name__ == "__main__":
    main()
