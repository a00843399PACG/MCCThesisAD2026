"""Stage IB. Compares the four heuristic profits of every emitted instance, as computed by the
analysis implementation (tools/characterise.py, column v_* of each campaign's features.csv), with
the profits computed by the generator's own kp.Heuristics class (the class KPEvaluator calls to
build the objective vector) on the same .kp files.

HeuristicAgreement.java embeds the source of A1star_EvolutionaryGenerator_v2.1_Java/src/kp/
Heuristics.java verbatim (checked by diff in run.sh), so it runs with any Java 11+ launcher.

    sh tools/heuristic_agreement/run.sh
"""
import os
import sys
import pandas as pd

RUNS = sys.argv[1] if len(sys.argv) > 1 else "runs"
OUT = sys.argv[2] if len(sys.argv) > 2 else "runs/heuristic_agreement"
SETS = {"S2": "pisinger_main", "S4": "holdout_s4", "S5 lambda": "sweep_s5_lambda",
        "S5 mu30": "sweep_s5_mu30", "S5 n1000": "sweep_s5_lambda3_n1000", "S6": "fixed_m_s6"}
COLS = [("v_def", "j_def"), ("v_minw", "j_minw"), ("v_maxpw", "j_maxpw"), ("v_maxp", "j_maxp")]

rows = []
for name, d in SETS.items():
    j = pd.read_csv(os.path.join(OUT, d + ".csv"))
    p = pd.read_csv(os.path.join(RUNS, d, "features.csv")).rename(columns={"file": "fname"})
    j["c"] = j.file.str.extract(r"_c(\d+)")[0].astype(int)
    j["fname"] = j.file.str.split("/").str[-1]
    keys = ["fname", "c"]
    if d == "sweep_s5_lambda":
        j["lam"] = j.file.str.extract(r"_c\d+_m(\d+)/")[0].astype(int)
        p["lam"] = p["lambda_m"].round().astype(int)
        keys.append("lam")
    m = p.merge(j, on=keys, how="outer", indicator=True)
    rows.append({"set": name, "files": len(m), "unmatched": int((m._merge != "both").sum()),
                 "values": 4 * len(m),
                 "mismatches": sum(int((m[a] != m[b]).sum()) for a, b in COLS)})
res = pd.DataFrame(rows)
res.loc[len(res)] = ["total", res.files.sum(), res.unmatched.sum(), res["values"].sum(), res.mismatches.sum()]
res.to_csv(os.path.join(OUT, "summary.csv"), index=False)
print(res.to_string(index=False))
