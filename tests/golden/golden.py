#!/usr/bin/env python3
"""The golden-file kit of Section 14 of the formalization.

The golden file is a fixed grid of 544 .kp files with one SHA-256 each. It is the only
instrument that separates a change of code from a change of generator: a candidate build
passes when it re-emits all 544 with the same hashes.

  record  compile a source tree, run the grid, store the files and MANIFEST.sha256
  verify  compile a candidate tree, run the same grid, compare against the manifest
  label   report which emitted EASY/HARD files have no strict winner (Remark 3)

The grid is 16 instance types x 4 configurations x (5,5,5,2) seeds x 2 instances = 544,
at mu=10, pc=0.8, pm=0.1, k=3, budget 100000, Locale.US. pc is 0.8 and not 1.0 so that
the crossover guard is exercised.

The manifest is the oracle of A1 (equivalently of A1*, which is output-identical to it).
A0 -- the as-received tree, whose combine() ignores crossoverRate -- is a different
generator and is expected to fail verify on most files. That is Proposition 10, not a bug.
"""

import argparse
import concurrent.futures
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NB_THETAS = 4
NB_TYPES = 16
HEURISTICS = ("DEFAULT", "MIN_WEIGHT", "MAX_PROFIT/WEIGHT", "MAX_PROFIT")

# Seeds per configuration: 5 for theta0..theta2, 2 for theta3 (n=100 is the expensive one).
def seeds_for(theta_index, seeds_small, seeds_large):
    return seeds_large if theta_index == NB_THETAS - 1 else seeds_small


# --------------------------------------------------------------------------- build


def compile_tree(src, out_bin):
    """Compiles every .java under src into out_bin. Works for both package layouts."""
    src = Path(src)
    out_bin = Path(out_bin)
    out_bin.mkdir(parents=True, exist_ok=True)
    sources = sorted(str(p) for p in src.rglob("*.java"))
    if not sources:
        raise SystemExit(f"no .java under {src}")
    argfile = out_bin / "sources.txt"
    argfile.write_text("\n".join(sources), encoding="utf-8")
    r = subprocess.run(
        ["javac", "-encoding", "UTF-8", "-nowarn", "-d", str(out_bin), f"@{argfile}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        raise SystemExit(f"compilation of {src} failed")
    # The driver itself, compiled against whichever layout is present.
    driver = Path(__file__).with_name("GoldenGrid.java")
    r = subprocess.run(
        ["javac", "-encoding", "UTF-8", "-nowarn", "-cp", str(out_bin), "-d", str(out_bin), str(driver)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        raise SystemExit("compilation of GoldenGrid.java failed")
    return out_bin


# ------------------------------------------------------------------------ generate


def _shard(bin_dir, out_dir, theta, type_index, seeds, nb_instances):
    r = subprocess.run(
        ["java", "-Duser.language=en", "-Duser.country=US", "-cp", str(bin_dir),
         "GoldenGrid", str(out_dir), str(theta), str(seeds), str(nb_instances), str(type_index)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return f"theta{theta} type{type_index}: {r.stderr.strip()[:400]}"
    return None


def generate(bin_dir, out_dir, seeds_small, seeds_large, nb_instances, jobs):
    """Runs the whole grid, one process per (configuration, type) pair."""
    tasks = [
        (t, ti, seeds_for(t, seeds_small, seeds_large))
        for t in range(NB_THETAS)
        for ti in range(NB_TYPES)
    ]
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(_shard, bin_dir, out_dir, t, ti, s, nb_instances): (t, ti)
            for (t, ti, s) in tasks
        }
        for fut in concurrent.futures.as_completed(futures):
            err = fut.result()
            if err:
                raise SystemExit("generation failed: " + err)
            done += 1
            print(f"\r  {done}/{len(tasks)} shards", end="", flush=True)
    print()


# ------------------------------------------------------------------------ manifest


def manifest(root):
    root = Path(root)
    out = {}
    for p in sorted(root.rglob("*.kp")):
        out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def write_manifest(path, m):
    Path(path).write_text(
        "".join(f"{h}  {k}\n" for k, h in sorted(m.items())), encoding="utf-8"
    )


def read_manifest(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, k = line.split("  ", 1)
            out[k] = h
    return out


def first_diff(a, b):
    la = Path(a).read_text(encoding="utf-8").splitlines()
    lb = Path(b).read_text(encoding="utf-8").splitlines()
    for i, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            return (i, x, y)
    if len(la) != len(lb):
        return (min(len(la), len(lb)) + 1, "<eof>" if len(la) < len(lb) else la[len(lb)],
                "<eof>" if len(lb) < len(la) else lb[len(la)])
    return None


# ----------------------------------------------------------- the shipped heuristics


def read_kp(path):
    lines = [l for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    n, c = (int(x) for x in lines[0].split(","))
    weights, profits = [], []
    for line in lines[1:]:
        w, p = line.split(",")
        weights.append(int(w))
        profits.append(float(p))
    return weights, profits, c


def value(weights, profits, capacity, heuristic):
    """Mirrors Heuristics.value: a stable sort by the key, then one first-fit pass."""
    idx = range(len(weights))
    if heuristic == "DEFAULT":
        order = list(idx)
    elif heuristic == "MAX_PROFIT":
        order = sorted(idx, key=lambda i: -profits[i])
    elif heuristic == "MAX_PROFIT/WEIGHT":
        order = sorted(idx, key=lambda i: -(profits[i] / weights[i]))
    elif heuristic == "MIN_WEIGHT":
        order = sorted(idx, key=lambda i: weights[i])
    else:
        raise ValueError(heuristic)
    residual, total = capacity, 0.0
    for i in order:
        if weights[i] <= residual:
            residual -= weights[i]
            total += profits[i]
    return total


EPS = 5e-324                 # Double.MIN_VALUE, the seed of Statistical.max
DMAX = sys.float_info.max    # Double.MAX_VALUE, the seed of Statistical.min


def fitness(path, type_name):
    """The labelled objective of Definition 9, with the guarded extrema of Section 7.1."""
    weights, profits, c = read_kp(path)
    v = {h: value(weights, profits, c, h) for h in HEURISTICS}
    target = {
        "DEFAULT": "DEFAULT", "MIN_WEIGHT": "MIN_WEIGHT",
        "MAX_PROFIT": "MAX_PROFIT", "MAX_PROFIT_WEIGHT": "MAX_PROFIT/WEIGHT",
    }[type_name.rsplit("_", 1)[0]]
    others = [v[h] for h in HEURISTICS if h != target]
    if type_name.endswith("_EASY"):
        return v[target] - max(others + [EPS])
    return min(others + [DMAX]) - v[target]


def type_of(filename):
    """DEFAULT_EASY_s1_20_50_10_000.kp -> DEFAULT_EASY"""
    stem = Path(filename).name
    return stem.split("_s", 1)[0]


# ------------------------------------------------------------------------ commands


def cmd_record(args):
    golden = Path(args.golden)
    if golden.exists() and any(golden.rglob("*.kp")) and not args.force:
        raise SystemExit(f"{golden} already holds a grid; pass --force to overwrite")
    if golden.exists():
        shutil.rmtree(golden)
    golden.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        print("compiling", args.src)
        bin_dir = compile_tree(args.src, Path(tmp) / "bin")
        print("running the grid")
        generate(bin_dir, golden, args.seeds_small, args.seeds_large, args.nb_instances, args.jobs)
    m = manifest(golden)
    write_manifest(golden / "MANIFEST.sha256", m)
    print(f"\nrecorded {len(m)} files into {golden}")
    print(f"manifest: {golden / 'MANIFEST.sha256'}")


def cmd_verify(args):
    expected = read_manifest(Path(args.golden) / "MANIFEST.sha256")
    with tempfile.TemporaryDirectory() as tmp:
        print("compiling", args.src)
        compile_tree(args.src, Path(tmp) / "bin")
        print("regenerating the grid with the candidate sources")
        generate(Path(tmp) / "bin", Path(tmp) / "out", args.seeds_small, args.seeds_large,
                 args.nb_instances, args.jobs)
        got = manifest(Path(tmp) / "out")
        missing = sorted(set(expected) - set(got))
        extra = sorted(set(got) - set(expected))
        changed = sorted(k for k in expected if k in got and got[k] != expected[k])
        print(f"\nfiles expected {len(expected)}, produced {len(got)}, "
              f"identical {len(expected) - len(missing) - len(changed)}")
        for k in missing:
            print(f"  MISSING  {k}")
        for k in extra:
            print(f"  EXTRA    {k}")
        for k in changed[:20]:
            d = first_diff(Path(args.golden) / k, Path(tmp) / "out" / k)
            print(f"  CHANGED  {k}" + (f"   first diff at line {d[0]}: golden='{d[1]}' candidate='{d[2]}'" if d else ""))
        if len(changed) > 20:
            print(f"  ... and {len(changed) - 20} more changed files")
        ok = not (missing or extra or changed)
        print("\nRESULT:", "IDENTICAL, the candidate is output-equivalent on the grid"
              if ok else "NOT IDENTICAL")
        sys.exit(0 if ok else 1)


def cmd_label(args):
    """Remark 3: which EASY/HARD files were emitted without a strict winner."""
    golden = Path(args.golden)
    rows, bad = {}, []
    for p in sorted(golden.rglob("*.kp")):
        t = type_of(p)
        if not (t.endswith("_EASY") or t.endswith("_HARD")):
            continue
        f = fitness(p, t)
        rows.setdefault(t, []).append(f)
        if f <= 0:
            bad.append((str(p.relative_to(golden)), f))
    total = sum(len(v) for v in rows.values())
    print(f"labelled files: {total}, not well labelled: {len(bad)} "
          f"({100 * len(bad) / total:.1f}%)\n")
    print(f"{'type':<26}{'files':>6}{'not well labelled':>20}{'min':>12}{'median':>12}")
    for t in sorted(rows):
        v = sorted(rows[t])
        nbad = sum(1 for x in v if x <= 0)
        med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
        print(f"{t:<26}{len(v):>6}{nbad:>20}{v[0]:>12.1f}{med:>12.1f}")
    out = golden / "NOT_WELL_LABELLED.txt"
    out.write_text("".join(f"{k}\t{f:.4f}\n" for k, f in bad), encoding="utf-8")
    print(f"\nwritten: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn, needs_src in (("record", cmd_record, True),
                                ("verify", cmd_verify, True),
                                ("label", cmd_label, False)):
        q = sub.add_parser(name)
        q.set_defaults(func=fn)
        if needs_src:
            q.add_argument("--src", required=True, help="root of the source tree to compile")
            q.add_argument("--seeds-small", type=int, default=5)
            q.add_argument("--seeds-large", type=int, default=2)
            q.add_argument("--nb-instances", type=int, default=2)
            q.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
        q.add_argument("--golden", default=str(Path(__file__).with_name("reference")))
        if name == "record":
            q.add_argument("--force", action="store_true")
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
