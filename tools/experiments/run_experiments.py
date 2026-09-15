"""Runs the three experiments on why A1* cannot label the MAX_PROFIT/WEIGHT-dominated types at large n.

  1. trajectory  the best fitness against evaluations, random start, to the campaign budget (100k)
  2. budget      the same runs carried on to 1M evaluations (= 100k * n/100 at n = 1000)
  3. seeded      the population starts on the tie boundary (fitness exactly 0), see SeededIndividuals

Experiments 1 and 2 share each run: its trace up to 100k is the campaign's run. One file per run
under --out; a run whose file already holds its final line is not redone.

    caffeinate -i nohup python3 tools/experiments/run_experiments.py > runs/experiments.log 2>&1 &
"""
import argparse
import concurrent.futures
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLASSPATH = f"{ROOT}/A1star_EvolutionaryGenerator_v2.1_Java/bin:{ROOT}/tools/experiments/bin"
TYPES = ["DEFAULT_EASY", "MAX_PROFIT_EASY", "MIN_WEIGHT_EASY", "MAX_PROFIT_WEIGHT_HARD"]


def run(job, out):
    init, type_name, n, seed, bits, alpha, budget, lambda_m, mu, pc, k = job
    path = out / f"{init}_{type_name}_n{n}_s{seed}.csv"
    if path.exists() and "final," in path.read_text():
        return path, "skipped"
    c = int(alpha * n * ((1 << bits) + 1) / 2)
    pm = lambda_m / (n * 2 * bits)
    cmd = ["java", "-cp", CLASSPATH, "GAExperiment", type_name, str(n), str(c), str(1 << bits),
           str(1 << bits), str(mu), str(pc), repr(pm), str(k), str(seed), str(budget), init]
    started = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return path, f"FAILED {r.stderr.strip()[:300]}"
    header = f"# init={init} type={type_name} n={n} bits={bits} alpha={alpha} c={c} pm={pm} seed={seed}\n"
    path.write_text(header + r.stdout)
    return path, f"{time.time() - started:.0f}s"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="runs/experiments")
    ap.add_argument("--n", type=int, nargs="+", default=[100, 200, 500, 1000])
    ap.add_argument("--types", nargs="+", default=TYPES)
    ap.add_argument("--inits", nargs="+", default=["random", "seeded"])
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--bits", type=int, default=10)
    ap.add_argument("--alpha", type=float, default=0.25)
    ap.add_argument("--budget", type=int, default=1_000_000)
    ap.add_argument("--lambda-m", type=float, default=11.0)
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    jobs = [(init, t, n, 1000 + s, args.bits, args.alpha, args.budget, args.lambda_m, 10, 0.8, 3)
            for n in sorted(args.n, reverse=True) for init in args.inits for t in args.types
            for s in range(args.seeds)]
    print(f"{len(jobs)} runs, {args.jobs} at a time", flush=True)
    started = time.time()
    with concurrent.futures.ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(run, job, out) for job in jobs]
        for done, f in enumerate(concurrent.futures.as_completed(futures), 1):
            path, status = f.result()
            print(f"[{time.strftime('%H:%M:%S')}] {done}/{len(jobs)} {path.name} {status}"
                  f"  elapsed {(time.time() - started) / 60:.0f} min", flush=True)


if __name__ == "__main__":
    main()
