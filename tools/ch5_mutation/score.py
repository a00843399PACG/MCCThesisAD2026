import sys, glob, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "golden"))
import golden

TYPES = ["DEFAULT_EASY", "DEFAULT_HARD", "MIN_WEIGHT_EASY", "MIN_WEIGHT_HARD",
         "MAX_PROFIT_EASY", "MAX_PROFIT_HARD", "MAX_PROFIT_WEIGHT_EASY", "MAX_PROFIT_WEIGHT_HARD"]


def score(folder, types):
    values, per = [], []
    for t in types:
        fs = [golden.fitness(f, t) for f in sorted(glob.glob(f"{folder}/{t}_*.kp"))]
        values += fs
        per.append(f"{t}:{sum(x > 0 for x in fs)}/{len(fs)}")
    return values, per


out = sys.argv[1]
for pm in ["0.1", "0.02"]:
    for t in ["DEFAULT_EASY", "MAX_PROFIT_WEIGHT_HARD"]:
        v, _ = score(f"{out}/theta2_pm{pm}", [t])
        print(f"theta2 pm={pm} {t}: strict {sum(x > 0 for x in v)}/{len(v)} median {statistics.median(v)}")
for lam in [11, 50, 200]:
    v, per = score(f"{out}/lambda{lam}", TYPES)
    print(f"lambda={lam}: strict {sum(x > 0 for x in v)}/{len(v)} median {statistics.median(v)}")
    print("   " + " ".join(per))
