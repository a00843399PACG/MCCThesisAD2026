"""Separation of the eight types in the seven-feature space, split into signal and sampling noise.

Per configuration cell, on all instances and on the strict ones only:
  within   mean over types and features of the standard deviation of Phi inside a type
  between  mean Euclidean distance between the type centroids in raw Phi units
  ratio    between / within
  sil_*    silhouettes on standardised Phi by type, by heuristic and by side
and, for reference, the within-type spread of Phi on uniform instances of the same n and bits,
which is the noise floor a generator with no preference at all would show.

    /opt/anaconda3/bin/python tools/feature_separation.py --campaign runs/pisinger_main
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEAT7 = ["w_mean", "w_median", "w_std", "p_mean", "p_median", "p_std", "rho01"]


def uniform_spread(n, bits, draws, rng):
    top = 1 << bits
    W = rng.integers(1, top + 1, (draws, n)).astype(float)
    P = rng.integers(1, top + 1, (draws, n)).astype(float)
    rho = np.array([np.corrcoef(w, p)[0, 1] for w, p in zip(W, P)])
    phi = np.c_[W.mean(1) / W.max(1), np.median(W, 1) / W.max(1), W.std(1, ddof=1) / W.max(1),
                P.mean(1) / P.max(1), np.median(P, 1) / P.max(1), P.std(1, ddof=1) / P.max(1),
                (rho + 1) / 2]
    return float(phi.std(0).mean())


def separation(cell):
    types = cell["heur"] + "_" + cell["side"]
    counts = types.value_counts()
    keep = types.isin(counts[counts >= 5].index)
    cell, types = cell[keep], types[keep]
    if types.nunique() < 2:
        return None
    within = float(cell.groupby(types)[FEAT7].std().to_numpy().mean())
    centroids = cell.groupby(types)[FEAT7].mean().to_numpy()
    k = len(centroids)
    between = float(np.mean([np.linalg.norm(centroids[i] - centroids[j])
                             for i in range(k) for j in range(i + 1, k)]))
    X = StandardScaler().fit_transform(cell[FEAT7])
    return {"types": k, "within": within, "between": between, "ratio": between / within,
            "sil_type": silhouette_score(X, types),
            "sil_heur": silhouette_score(X, cell["heur"]) if cell["heur"].nunique() > 1 else np.nan,
            "sil_side": silhouette_score(X, cell["side"]) if cell["side"].nunique() > 1 else np.nan}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--uniform-draws", type=int, default=1000)
    args = ap.parse_args()
    root = Path(args.campaign)
    feats = pd.read_csv(root / "pca" / "feat7.csv")
    table = pd.read_csv(root / "features.csv")
    assert list(feats["file"]) == list(table["file"])
    feats["strict"] = (table["fitness"] > 0).to_numpy()
    rng = np.random.default_rng(20260914)
    floor = {}
    rows = []
    for (n, bits, alpha), cell in feats.groupby(["n", "bits", "alpha"]):
        if (n, bits) not in floor:
            floor[(n, bits)] = uniform_spread(n, bits, args.uniform_draws, rng)
        for subset, frame in (("all", cell), ("strict", cell[cell["strict"]])):
            res = separation(frame)
            if res:
                rows.append({"n": n, "bits": bits, "alpha": alpha, "subset": subset,
                             "uniform_within": floor[(n, bits)], **res})
    out = pd.DataFrame(rows)
    out.to_csv(root / "pca" / "separation.csv", index=False)
    pd.set_option("display.width", 200)
    summary = out.groupby(["subset", "n"])[["types", "uniform_within", "within", "between", "ratio",
                                           "sil_type", "sil_heur", "sil_side"]].mean()
    print(summary.round(3).to_string())
    print("\nwithin * sqrt(n):")
    print((out.groupby(["subset", "n"])["within"].mean()
           * np.sqrt(out.groupby(["subset", "n"])["n"].first())).round(3).to_string())


if __name__ == "__main__":
    main()
