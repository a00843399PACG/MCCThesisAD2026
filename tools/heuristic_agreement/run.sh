#!/bin/bash
# Stage IB: agreement of the analysis implementation with the generator's own Heuristics class.
cd "$(dirname "$0")/../.." || exit 1
SRC=A1star_EvolutionaryGenerator_v2.1_Java/src/kp/Heuristics.java
J=tools/heuristic_agreement/HeuristicAgreement.java
diff <(sed -n '/final class Heuristics/,$p' "$J" | sed 's/^final class/public final class/') \
     <(sed -n '/public final class Heuristics/,$p' "$SRC") >/dev/null || { echo "Heuristics source differs"; exit 1; }
OUT=runs/heuristic_agreement; mkdir -p "$OUT"
for d in pisinger_main holdout_s4 sweep_s5_lambda sweep_s5_mu30 sweep_s5_lambda3_n1000 fixed_m_s6; do
    java "$J" "runs/$d" "$OUT/$d.csv"
done
python3 tools/heuristic_agreement/compare.py runs "$OUT"
