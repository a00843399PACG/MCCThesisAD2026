#!/usr/bin/env python3
"""Generate a corpus with A1* at chosen configurations and characterise what comes out.

The question this answers is not "are these instances hard" but "what does this generator
actually emit at a given scale". Everything measured here is a property of the emitted
.kp file, so the same table can be built for any configuration, including the four of the
golden grid, and compared across them.

The capacity is the parameter that needs care. Pisinger sets c as a fraction of the total
weight; here c is a fixed number of the configuration, while the total weight varies with
the instance. So a configuration is given as (n, bits, alpha) and c is derived from the
expected total weight under the uniform law:

    E[sum w] = n (2^bw + 1) / 2 ,      c = round(alpha * E[sum w])

which puts the run in the regime alpha, rather than wherever a copied c happens to land.
(theta3 of the golden grid has alpha = 0.007: a nearly empty knapsack.)

usage:
    python3 tools/characterise.py --out runs/pisinger --alphas 0.05 0.25 0.5 \
        --bits 10 --n 100 --instances 2 --seeds 2 --jobs 8
"""

import argparse
import concurrent.futures
import csv
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
A1STAR = REPO / "A1star_EvolutionaryGenerator_v2.1_Java"
sys.path.insert(0, str(REPO / "tests" / "golden"))
from golden import read_kp, value, HEURISTICS, EPS, DMAX  # noqa: E402

LABELLED = [
    "DEFAULT_EASY", "DEFAULT_HARD",
    "MIN_WEIGHT_EASY", "MIN_WEIGHT_HARD",
    "MAX_PROFIT_EASY", "MAX_PROFIT_HARD",
    "MAX_PROFIT_WEIGHT_EASY", "MAX_PROFIT_WEIGHT_HARD",
]

TARGET = {
    "DEFAULT": "DEFAULT", "MIN_WEIGHT": "MIN_WEIGHT",
    "MAX_PROFIT": "MAX_PROFIT", "MAX_PROFIT_WEIGHT": "MAX_PROFIT/WEIGHT",
}

SHORT = {"DEFAULT": "def", "MIN_WEIGHT": "minw",
         "MAX_PROFIT/WEIGHT": "maxpw", "MAX_PROFIT": "maxp"}


def expected_total_weight(n, bits):
    return n * ((1 << bits) + 1) / 2.0


def capacity_for(n, bits, alpha):
    return max(1, round(alpha * expected_total_weight(n, bits)))


# ------------------------------------------------------------------ generation


def build():
    r = subprocess.run(["./build.sh"], cwd=A1STAR, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit("A1* build failed")
    return A1STAR / "bin"


def cell_dir(n, bits, alpha, c, lam=None):
    """The mutation component is appended only when lambda_m is an axis of the design.

    A campaign that holds lambda_m fixed keeps the shorter name, so a run started before
    the sweep existed still resumes: shard_done looks for the same directory it wrote.
    """
    name = f"n{n}_b{bits}_a{alpha:g}_c{c}"
    return name if lam is None else f"{name}_m{lam:g}"


def parse_cell(name):
    """n100_b10_a0.25_c12812[_m11] -> (100, 10, 0.25, 12812, 11.0 or None)"""
    parts = {p[0]: p[1:] for p in name.split("_")}
    return (int(parts["n"]), int(parts["b"]), float(parts["a"]), int(parts["c"]),
            float(parts["m"]) if "m" in parts else None)


def shard_files(path, ident, bits, n, instances):
    w = p = 1 << bits
    return [Path(path) / f"{ident}_{w}_{p}_{n}_{i:03d}.kp" for i in range(instances)]


def shard_done(path, ident, bits, n, instances):
    """True when this shard's files are all present and complete.

    A campaign of this length will be interrupted, so a rerun must not redo what is
    already on disk. Completeness is checked, not just existence: a run killed mid-write
    leaves a truncated file, which would otherwise be taken for a finished one. An
    instance has one header line plus one line per item.
    """
    for f in shard_files(path, ident, bits, n, instances):
        try:
            if sum(1 for line in f.open(encoding="utf-8") if line.strip()) != n + 1:
                return False
        except OSError:
            return False
    return True


def _run_one(bin_dir, out_dir, type_name, n, c, bits, alpha, instances, seed, mu, pc, pm, k,
             force=False, lam_tag=None):
    path = Path(out_dir) / cell_dir(n, bits, alpha, c, lam_tag) / type_name
    path.mkdir(parents=True, exist_ok=True)
    ident = f"{type_name}_s{seed}"
    if not force and shard_done(path, ident, bits, n, instances):
        return "skipped"
    for f in shard_files(path, ident, bits, n, instances):
        f.unlink(missing_ok=True)          # drop any truncated leftovers
    cmd = ["java", "-cp", str(bin_dir), "Run", type_name, str(instances), ident,
           str(path) + "/", str(n), str(c), str(1 << bits), str(1 << bits),
           str(mu), str(pc), repr(pm), str(k), str(seed)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return f"{type_name} seed {seed}: {r.stderr.strip()[:300]}"
    return None


def mutation_rate(n, bits, pm, lambda_m):
    """Remark 6: mutate() flips every bit with probability pm, so the expected number of
    flips per offspring is lambda_m = pm * L. Holding pm fixed while L grows changes the
    search regime, not just its strength; holding lambda_m fixed is what keeps a level
    of the axis meaning the same thing across configurations."""
    if lambda_m is None:
        return pm
    return lambda_m / (n * 2 * bits)


def generate(bin_dir, out_dir, configs, types, seeds, instances, jobs, mu, pc, pm, k,
             lambdas, force=False):
    # The seed is the OUTERMOST loop on purpose. A long campaign is then useful before it
    # finishes: after one pass over the seeds there are `instances` instances in every cell
    # of the design, rather than a complete first configuration and nothing else.
    sweeping = len(lambdas) > 1
    tasks = []
    for s in range(1, seeds + 1):
        for (n, bits, alpha) in configs:
            c = capacity_for(n, bits, alpha)
            for lam in lambdas:
                rate = mutation_rate(n, bits, pm, lam)
                tag = (rate * n * 2 * bits) if sweeping else None
                for t in types:
                    # The seed ignores lambda_m as it ignores alpha: the levels of the
                    # mutation axis are then compared on shared random numbers.
                    tasks.append((bin_dir, out_dir, t, n, c, bits, alpha, instances,
                                  100003 * bits + 1009 * s + 7 * n, mu, pc, rate, k,
                                  force, tag))
    done, failures, skipped, started = 0, [], 0, time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(_run_one, *t) for t in tasks]
        for f in concurrent.futures.as_completed(futs):
            err = f.result()
            done += 1
            if err == "skipped":
                skipped += 1
                err = None
            if err:
                # A long campaign must not lose every completed run to one bad shard;
                # the .kp files already on disk stay, and --skip-generate rebuilds the
                # table from whatever finished.
                failures.append(err)
                print(f"  FAILED {err}", flush=True)
            if done % 10 == 0 or done == len(tasks):
                elapsed = time.time() - started
                fresh = done - skipped
                # Skipped shards cost nothing, so the estimate must be built from the
                # ones actually run, or a resumed campaign reports a wild eta.
                eta = (elapsed / fresh * (len(tasks) - done)) if fresh else 0
                print(f"  [{time.strftime('%H:%M:%S')}] {done}/{len(tasks)} runs"
                      + (f" ({skipped} already on disk)" if skipped else "")
                      + f", elapsed {elapsed / 60:.0f} min, eta {eta / 60:.0f} min",
                      flush=True)
    if skipped:
        print(f"\n{skipped} shards were already complete and were not rerun.")
    if failures:
        print(f"{len(failures)} of {len(tasks)} runs failed; the rest were kept.")


# ----------------------------------------------------------------- the features


def features(path, type_name, bits, alpha_nominal, pm):
    """Everything below is read off the emitted file; nothing needs the generator."""
    w, p, c = read_kp(path)
    n = len(w)
    total_w = sum(w)
    v = {h: value(w, p, c, h) for h in HEURISTICS}

    def packed(h):
        idx = range(n)
        order = {"DEFAULT": list(idx),
                 "MAX_PROFIT": sorted(idx, key=lambda i: -p[i]),
                 "MAX_PROFIT/WEIGHT": sorted(idx, key=lambda i: -(p[i] / w[i])),
                 "MIN_WEIGHT": sorted(idx, key=lambda i: w[i])}[h]
        r, m = c, 0
        for i in order:
            if w[i] <= r:
                r -= w[i]
                m += 1
        return m

    target = TARGET[type_name.rsplit("_", 1)[0]]
    others = [v[h] for h in HEURISTICS if h != target]
    if type_name.endswith("_EASY"):
        fit = v[target] - max(others + [EPS])
    else:
        fit = min(others + [DMAX]) - v[target]

    vmax, vmin = max(v.values()), min(v.values())
    winner = max(v, key=lambda h: v[h])
    loser = min(v, key=lambda h: v[h])
    try:
        rho = statistics.correlation(w, [float(x) for x in p])
    except Exception:
        rho = float("nan")

    return {
        "file": Path(path).name,
        "type": type_name,
        "target": SHORT[target],
        "side": "easy" if type_name.endswith("_EASY") else "hard",
        "n": n, "bits": bits, "c": c,
        "L": n * 2 * bits, "pm": pm, "lambda_m": pm * n * 2 * bits,
        "sum_w": total_w,
        "alpha": alpha_nominal,
        "alpha_real": c / total_w,
        "w_mean": statistics.mean(w), "w_sd": statistics.pstdev(w),
        "w_min": min(w), "w_max": max(w),
        "p_mean": statistics.mean(p), "p_sd": statistics.pstdev(p),
        "rho_wp": rho,
        "v_def": v["DEFAULT"], "v_minw": v["MIN_WEIGHT"],
        "v_maxpw": v["MAX_PROFIT/WEIGHT"], "v_maxp": v["MAX_PROFIT"],
        "m_def": packed("DEFAULT"), "m_minw": packed("MIN_WEIGHT"),
        "m_maxpw": packed("MAX_PROFIT/WEIGHT"), "m_maxp": packed("MAX_PROFIT"),
        # selection hardness of Section 7.5: how much the portfolio disagrees
        "sigma": (vmax - vmin) / vmax if vmax > 0 else 0.0,
        "fitness": fit,
        "well_labelled": fit > 0,
        "winner": SHORT[winner], "loser": SHORT[loser],
    }


def collect(out_dir, pm, lambdas):
    single = lambdas[0] if len(lambdas) == 1 else None
    rows = []
    for kp in sorted(Path(out_dir).rglob("*.kp")):
        type_name = kp.parent.name
        n, bits, alpha, _c, lam = parse_cell(kp.parent.parent.name)
        rows.append(features(kp, type_name, bits, alpha,
                             mutation_rate(n, bits, pm, lam if lam is not None else single)))
    return rows


# ------------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="runs/pisinger")
    ap.add_argument("--n", type=int, nargs="+", default=[100])
    ap.add_argument("--bits", type=int, nargs="+", default=[10],
                    help="bw = bp; Wmax = Pmax = 2^bits. Pisinger R=10^3 -> 10, R=10^4 -> 14")
    ap.add_argument("--alphas", type=float, nargs="+", default=[0.05, 0.25, 0.50])
    ap.add_argument("--types", nargs="+", default=LABELLED)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--instances", type=int, default=2)
    ap.add_argument("--mu", type=int, default=10)
    ap.add_argument("--pc", type=float, default=0.8)
    ap.add_argument("--pm", type=float, default=0.1)
    ap.add_argument("--lambda-m", type=float, nargs="+", default=None,
                    help="expected flips per offspring; overrides --pm as pm = lambda_m / L. "
                         "Several values make it an axis of the design, swept like n or alpha.")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--skip-generate", action="store_true",
                    help="build the table from the .kp already on disk, generating nothing")
    ap.add_argument("--force", action="store_true",
                    help="regenerate shards that are already complete")
    args = ap.parse_args()

    out = Path(args.out)
    configs = [(n, b, a) for n in args.n for b in args.bits for a in args.alphas]
    lambdas = args.lambda_m if args.lambda_m else [None]

    print(f"{'n':>6} {'bits':>5} {'Wmax=Pmax':>10} {'L':>8} {'alpha':>6} {'c':>10} "
          f"{'pm':>10} {'lambda_m':>9}")
    for (n, bits, a) in configs:
        for lam in lambdas:
            rate = mutation_rate(n, bits, args.pm, lam)
            print(f"{n:>6} {bits:>5} {1 << bits:>10} {n * 2 * bits:>8} {a:>6g} "
                  f"{capacity_for(n, bits, a):>10} {rate:>10.2e} {rate * n * 2 * bits:>9.1f}")
    cells = len(configs) * len(lambdas)
    total = cells * len(args.types) * args.seeds * args.instances
    print(f"\n{total} instances over {cells} cells "
          f"({len(configs)} configurations x {len(lambdas)} mutation levels) "
          f"x {len(args.types)} types\n")

    if not args.skip_generate:
        bin_dir = build()
        generate(bin_dir, out, configs, args.types, args.seeds, args.instances,
                 args.jobs, args.mu, args.pc, args.pm, args.k, lambdas, args.force)

    rows = collect(out, args.pm, lambdas)
    if not rows:
        raise SystemExit(f"no .kp under {out}")
    csv_path = out / "features.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"\n{len(rows)} instances characterised -> {csv_path}")


if __name__ == "__main__":
    main()
