"""PCA of the seven Plata-Gonzalez et al. (2019) features, coloured by instance type.

Reads every .kp under a campaign directory, computes FEAT7 (normalised mean, median and sd of
weights and profits, and (rho+1)/2), and projects onto the first two principal components after
z-scoring: once per configuration cell (n, bits, alpha) and once pooling every cell. Colour is the
targeted heuristic, filled markers are EASY and hollow ones HARD.

    /opt/anaconda3/bin/python tools/pca_feat7.py --campaign runs/pisinger_main
"""
import argparse
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEAT7 = ["w_mean", "w_median", "w_std", "p_mean", "p_median", "p_std", "rho01"]
HEURS = ["DEFAULT", "MAX_PROFIT", "MAX_PROFIT_WEIGHT", "MIN_WEIGHT"]
COLOURS = dict(zip(HEURS, ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]))
CELL = re.compile(r"n(\d+)_b(\d+)_a([\d.]+)_c(\d+)")


def feat7(path):
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    w, p = data[:, 0], data[:, 1]
    r = np.corrcoef(w, p)[0, 1] if w.std() > 0 and p.std() > 0 else 0.0
    return [w.mean() / w.max(), np.median(w) / w.max(), w.std(ddof=1) / w.max(),
            p.mean() / p.max(), np.median(p) / p.max(), p.std(ddof=1) / p.max(), (r + 1) / 2]


def load(campaign):
    rows = []
    for kp in sorted(Path(campaign).rglob("*.kp")):
        n, bits, alpha, _ = CELL.fullmatch(kp.parent.parent.name).groups()
        heur, side = kp.parent.name.rsplit("_", 1)
        rows.append([kp.name, heur, side, int(n), int(bits), float(alpha), *feat7(kp)])
    return pd.DataFrame(rows, columns=["file", "heur", "side", "n", "bits", "alpha", *FEAT7])


def project(df):
    X = StandardScaler().fit_transform(df[FEAT7])
    pca = PCA(n_components=2).fit(X)
    Z = pca.transform(X)
    labels = df["heur"] + "_" + df["side"]
    sil = {
        "type": silhouette_score(X, labels),
        "heur": silhouette_score(X, df["heur"]),
        "side": silhouette_score(X, df["side"]),
    }
    return Z, pca, sil


def scatter(ax, df, Z, size):
    for heur in HEURS:
        for side, face in (("EASY", COLOURS[heur]), ("HARD", "none")):
            m = ((df["heur"] == heur) & (df["side"] == side)).to_numpy()
            ax.scatter(Z[m, 0], Z[m, 1], s=size, facecolors=face, edgecolors=COLOURS[heur],
                       linewidths=0.6, alpha=0.7, label=f"{heur} {side}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--out", default=None, help="default: <campaign>/pca")
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()
    out = Path(args.out or Path(args.campaign) / "pca")
    cells_dir = out / "cells"
    cells_dir.mkdir(parents=True, exist_ok=True)

    df = load(args.campaign)
    df.to_csv(out / "feat7.csv", index=False)
    print(f"{len(df)} instances")

    cells = sorted(df.groupby(["n", "bits", "alpha"]).groups)
    ns, cols = sorted(df["n"].unique()), [(b, a) for b in sorted(df["bits"].unique())
                                          for a in sorted(df["alpha"].unique())]
    fig, axes = plt.subplots(len(ns), len(cols), figsize=(3.2 * len(cols), 3.0 * len(ns)))
    summary = []
    for (n, bits, alpha) in cells:
        sub = df[(df["n"] == n) & (df["bits"] == bits) & (df["alpha"] == alpha)].reset_index(drop=True)
        Z, pca, sil = project(sub)
        ax = axes[ns.index(n), cols.index((bits, alpha))]
        scatter(ax, sub, Z, 8)
        ev = pca.explained_variance_ratio_
        ax.set_title(f"n={n} b={bits} α={alpha}\nPC1 {ev[0]:.0%} PC2 {ev[1]:.0%} sil={sil['type']:.2f}",
                     fontsize=8)
        ax.tick_params(labelsize=6)
        one, ax1 = plt.subplots(figsize=(6, 5))
        scatter(ax1, sub, Z, 14)
        ax1.set_title(f"n={n}, bits={bits}, α={alpha}   silhouette={sil['type']:.2f}")
        ax1.set_xlabel(f"PC1 ({ev[0]:.0%})")
        ax1.set_ylabel(f"PC2 ({ev[1]:.0%})")
        ax1.legend(fontsize=7, loc="best")
        one.tight_layout()
        one.savefig(cells_dir / f"pca_n{n}_b{bits}_a{alpha}.png", dpi=args.dpi)
        plt.close(one)
        summary.append({"n": n, "bits": bits, "alpha": alpha, "count": len(sub),
                        "pc1": ev[0], "pc2": ev[1], "sil_type": sil["type"],
                        "sil_heur": sil["heur"], "sil_side": sil["side"]})
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out / "pca_per_cell.png", dpi=args.dpi)
    plt.close(fig)

    Z, pca, sil = project(df)
    summary.append({"n": "all", "bits": "all", "alpha": "all", "count": len(df),
                    "pc1": pca.explained_variance_ratio_[0], "pc2": pca.explained_variance_ratio_[1],
                    "sil_type": sil["type"], "sil_heur": sil["heur"], "sil_side": sil["side"]})
    pd.DataFrame(pca.components_, columns=FEAT7, index=["PC1", "PC2"]).to_csv(out / "loadings_all.csv")

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    scatter(axes[0], df, Z, 4)
    axes[0].set_title("All cells, by type")
    for key, ax, title in (("n", axes[1], "All cells, by n"), ("alpha", axes[2], "All cells, by α")):
        pts = ax.scatter(Z[:, 0], Z[:, 1], c=np.log10(df[key]) if key == "n" else df[key],
                         s=3, cmap="viridis", alpha=0.6)
        fig.colorbar(pts, ax=ax, label="log10 n" if key == "n" else "α")
        ax.set_title(title)
    ev = pca.explained_variance_ratio_
    for ax in axes:
        ax.set_xlabel(f"PC1 ({ev[0]:.0%})")
        ax.set_ylabel(f"PC2 ({ev[1]:.0%})")
    axes[0].legend(fontsize=7, markerscale=2)
    fig.tight_layout()
    fig.savefig(out / "pca_all.png", dpi=args.dpi)
    plt.close(fig)

    s = pd.DataFrame(summary)
    s.to_csv(out / "summary.csv", index=False)
    pd.set_option("display.width", 200)
    print(s.round(3).to_string(index=False))
    print(pd.DataFrame(pca.components_, columns=FEAT7, index=["PC1", "PC2"]).round(2))


if __name__ == "__main__":
    main()
