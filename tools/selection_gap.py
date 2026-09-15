"""Algorithm-selection view of a campaign: the regret of the single best heuristic against the
per-instance oracle, and how much of that gap a selector trained on the seven features closes.

For each n the instances of every (bits, alpha) cell are pooled; the selectors see Phi plus the
realised capacity ratio (a user choosing a heuristic knows n and c). Folds are grouped by seed so
the two instances of a generator call never sit on both sides of a split.

Two selectors. "classifier" predicts the label of the best heuristic and is scored as usual; it
treats every mistake alike, so it can beat the single best on accuracy and lose to it on profit.
"cost" regresses the relative regret of each heuristic and picks the smallest prediction, which is
the selector the closed-gap metric is meant for.

    closed gap = (regret(SBS) - regret(selector)) / (regret(SBS) - regret(VBS)),  regret(VBS) = 0

    /opt/anaconda3/bin/python tools/selection_gap.py --campaign runs/pisinger_main
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import GroupKFold

FEAT7 = ["w_mean", "w_median", "w_std", "p_mean", "p_median", "p_std", "rho01"]
VALUES = ["v_def", "v_minw", "v_maxpw", "v_maxp"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--folds", type=int, default=5)
    args = ap.parse_args()
    root = Path(args.campaign)
    feats = pd.read_csv(root / "pca" / "feat7.csv")
    table = pd.read_csv(root / "features.csv")
    assert list(feats["file"]) == list(table["file"]), "feat7.csv and features.csv out of order"
    df = pd.concat([table, feats[FEAT7]], axis=1)
    df["seed"] = df["file"].str.extract(r"_s(\d+)_")[0].astype(int)
    df["strict"] = df["fitness"] > 0

    rows = []
    for subset, frame in (("all", df), ("strict", df[df["strict"]])):
        for n, cell in frame.groupby("n"):
            values = cell[VALUES].to_numpy()
            vbs = values.max(axis=1)
            best = values.argmax(axis=1)            # first maximum: ties go to the earlier column
            sbs_col = int(np.argmax(values.sum(axis=0)))
            X = cell[FEAT7 + ["alpha_real"]].to_numpy()
            regret = (vbs[:, None] - values) / vbs[:, None]
            chosen = {"classifier": np.empty(len(cell), dtype=int), "cost": np.empty(len(cell), dtype=int)}
            for train, test in GroupKFold(args.folds).split(X, best, cell["seed"]):
                if len(set(best[train])) == 1:
                    chosen["classifier"][test] = best[train][0]
                else:
                    clf = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, random_state=0, n_jobs=-1)
                    clf.fit(X[train], best[train])
                    chosen["classifier"][test] = clf.predict(X[test])
                reg = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=0, n_jobs=-1)
                reg.fit(X[train], regret[train])
                chosen["cost"][test] = reg.predict(X[test]).argmin(axis=1)
            gap_sbs = (vbs - values[:, sbs_col]).sum()
            for name, pick in chosen.items():
                v_sel = values[np.arange(len(cell)), pick]
                gap_sel = (vbs - v_sel).sum()
                rows.append({
                    "subset": subset, "n": n, "selector": name, "instances": len(cell),
                    "sbs": VALUES[sbs_col],
                    "sbs_is_best_%": 100 * (values[:, sbs_col] == vbs).mean(),
                    "accuracy_%": 100 * (v_sel == vbs).mean(),
                    "regret_sbs_rel_%": 100 * ((vbs - values[:, sbs_col]) / vbs).mean(),
                    "regret_selector_rel_%": 100 * ((vbs - v_sel) / vbs).mean(),
                    "closed_gap_%": 100 * (gap_sbs - gap_sel) / gap_sbs if gap_sbs > 0 else np.nan,
                })
    out = pd.DataFrame(rows)
    out.to_csv(root / "selection_gap.csv", index=False)
    pd.set_option("display.width", 200)
    print(out.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
