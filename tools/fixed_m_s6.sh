#!/bin/sh
# S6, the fixed-m design of Definition "The fixed-m design and its predictions".
# Six cells: target m of 20 and 60, each at n = 100, 300 and 1000, b = 10.
# The alpha of each cell is chosen so that the capacity is the one the definition states,
# c = floor(alpha * n * (2^10 + 1) / 2); m is then held while n moves by a decade.
# Resumable: rerunning skips shards already on disk.
cd "$(dirname "$0")/.." || exit 1
JOBS=${JOBS:-8}
OUT=runs/fixed_m_s6

run() {  # n alpha label
    echo "=== $3: n=$1 alpha=$2 === $(date)"
    python3 tools/characterise.py --out "$OUT" --no-build --jobs "$JOBS" \
        --n "$1" --bits 10 --alphas "$2" --seeds 10 --instances 2 \
        --mu 10 --pc 0.8 --k 3 --lambda-m 11
}

run 100  0.053135 "m20"   # c = 2723
run 300  0.009017 "m20"   # c = 1386
run 1000 0.00129  "m20"   # c = 661
run 100  0.361    "m60"   # c = 18501
run 300  0.06125  "m60"   # c = 9417
run 1000 0.008767 "m60"   # c = 4493
echo "=== done === $(date)"
