#!/usr/bin/env bash
# Reproduces Table 5.3 (right) and Table 5.4 of Chapter 5 with the A* build.
# Usage: bash tools/ch5_mutation/run.sh   (from the repository root)
set -euo pipefail
SRC=A1star_EvolutionaryGenerator_v2.1_Java/src
BIN=tools/ch5_mutation/bin
OUT=runs/ch5_mutation
mkdir -p "$BIN"
javac -nowarn -d "$BIN" $(find "$SRC" -name "*.java") tools/ch5_mutation/Ch5Rerun.java
for pm in 0.1 0.02; do
  for t in DEFAULT_EASY MAX_PROFIT_WEIGHT_HARD; do
    for s in 1 2 3 4 5; do
      java -cp "$BIN" Ch5Rerun "$OUT/theta2_pm$pm" $t 50 100 17 33 $pm $((100003*3+1009*s)) 2 ${t}_s$s
    done
  done
done
for lam in 11 50 200; do
  pm=$(python3 -c "print($lam/2000)")
  for t in DEFAULT_EASY DEFAULT_HARD MIN_WEIGHT_EASY MIN_WEIGHT_HARD MAX_PROFIT_EASY MAX_PROFIT_HARD MAX_PROFIT_WEIGHT_EASY MAX_PROFIT_WEIGHT_HARD; do
    for s in 1 2; do
      seed=$((100003*10+1009*s))
      java -cp "$BIN" Ch5Rerun "$OUT/lambda$lam" $t 100 25625 1024 1024 $pm $seed 2 ${t}_s$seed
    done
  done
done
python3 tools/ch5_mutation/score.py "$OUT"
