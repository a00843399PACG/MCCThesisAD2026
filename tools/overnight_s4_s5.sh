#!/bin/sh
# Held-out design S4 (preregistered in be8b79e), then the engine sweep S5.
# Runs alongside tools/experiments/run_experiments.py; --no-build keeps bin/ intact for it.
# Every step is resumable: rerunning this script skips shards already on disk.
cd "$(dirname "$0")/.." || exit 1
JOBS=${JOBS:-4}
PY=python3

echo "=== S4 held-out: n 300 700, b 12, alpha 0.15 0.40, 30 seeds x 2 === $(date)"
$PY tools/characterise.py --out runs/holdout_s4 --no-build --jobs "$JOBS" \
    --n 300 700 --bits 12 --alphas 0.15 0.40 --seeds 30 --instances 2 \
    --mu 10 --pc 0.8 --k 3 --lambda-m 11

echo "=== S5a engine sweep: lambda_m 3 and 33, mu 10 === $(date)"
$PY tools/characterise.py --out runs/sweep_s5_lambda --no-build --jobs "$JOBS" \
    --n 100 500 --bits 10 --alphas 0.25 --seeds 10 --instances 2 \
    --mu 10 --pc 0.8 --k 3 --lambda-m 3 33

echo "=== S5b engine sweep: mu 30, lambda_m 11 === $(date)"
$PY tools/characterise.py --out runs/sweep_s5_mu30 --no-build --jobs "$JOBS" \
    --n 100 500 --bits 10 --alphas 0.25 --seeds 10 --instances 2 \
    --mu 30 --pc 0.8 --k 3 --lambda-m 11

echo "=== done === $(date)"
