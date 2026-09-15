"""Does an order tie change the label? For every .kp of a campaign, the fitness of its own type
is computed with the shipped tie-break (equal keys in index order) and with the reverse
tie-break; the instance counts when the sign of the fitness differs.

    /opt/anaconda3/bin/python tools/order_tie_sign.py --campaign runs/pisinger_main
"""
import argparse
import concurrent.futures
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from ties_plot import HEURS, greedy, keys  # noqa: E402

EPS = 5e-324
DMAX = sys.float_info.max


def fitness(v, heur, side):
    others = [v[h] for h in HEURS if h != heur]
    return v[heur] - max(others + [EPS]) if side == "EASY" else min(others + [DMAX]) - v[heur]


def evaluate(path):
    lines = Path(path).read_text().split("\n")
    c = int(lines[0].split(",")[1])
    data = np.array([l.split(",") for l in lines[1:] if l.strip()], dtype=float)
    w, p = data[:, 0].astype(np.int64), data[:, 1]
    idx = np.arange(len(w))
    wl, pl = w.tolist(), p.tolist()
    heur, side = path.parent.name.rsplit("_", 1)
    forward = {h: greedy(wl, pl, c, np.lexsort((idx, k)).tolist()) for h, k in keys(w, p).items()}
    # DEFAULT's order is the index itself, so it has no tie to break and keeps the forward pass.
    reverse = {h: forward[h] if h == "DEFAULT" else greedy(wl, pl, c, np.lexsort((-idx, k)).tolist())
               for h, k in keys(w, p).items()}
    f0, f1 = fitness(forward, heur, side), fitness(reverse, heur, side)
    cell = path.parent.parent.name
    return {"file": path.name, "type": path.parent.name, "cell": cell,
            "n": int(cell[1:].split("_")[0]), "bits": int(cell.split("_b")[1].split("_")[0]),
            "f_forward": f0, "f_reverse": f1, "value_changed": forward != reverse,
            "sign_changed": np.sign(f0) != np.sign(f1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign", default="runs/pisinger_main")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    paths = sorted(Path(args.campaign).rglob("*.kp"))
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        df = pd.DataFrame(list(pool.map(evaluate, paths, chunksize=64)))
    out = Path(args.campaign) / "ties" / "order_tie_sign.csv"
    df.to_csv(out, index=False)
    print(f"{len(df)} instances; value changed {df['value_changed'].sum()}; "
          f"sign changed {df['sign_changed'].sum()}")
    print(df.groupby("bits")[["value_changed", "sign_changed"]].sum())
    print(df.groupby("n")[["value_changed", "sign_changed"]].sum())
    flips = df[df["sign_changed"]]
    print(flips.groupby("type").size())
    print(flips[["cell", "type", "f_forward", "f_reverse"]].to_string(index=False))


if __name__ == "__main__":
    main()
