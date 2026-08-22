# EvolutionaryGenerator v2.1 (Python)

A faithful Python translation of the knapsack problem instance generator
originally written in Java in `EvolutionaryGenerator_v2.1_Java`.

**Translation author:** Paola Azeneth Castillo Gutiérrez
**Original author (Java):** José Carlos Ortiz Bayliss (jcobayliss@tec.mx)

The translation is faithful in a verifiable sense: given the same seed, the Python
version produces exactly the same numbers, the same instances and the same output
lines as the Java version. The equivalence is checked automatically (see
[Verification](#5-verification)).

---

## 1. What the system does

The system **evolves synthetic knapsack problem instances** that favour (or
penalise) one particular heuristic against the others. In other words, it does not
solve knapsacks: it **builds knapsacks to order**.

The four constructive heuristics that compete against each other are:

| Heuristic           | Criterion to choose the next item      |
|---------------------|----------------------------------------|
| `DEFAULT`           | the first one that fits                |
| `MAX_PROFIT`        | the one with the largest profit        |
| `MAX_PROFIT/WEIGHT` | the one with the largest profit per weight unit |
| `MIN_WEIGHT`        | the one with the smallest weight       |

### Generator flow

```
                    ┌──────────────────────────────────────────────┐
                    │  KP.generate(type, n, ..., seed)             │
                    └───────────────────────┬──────────────────────┘
                                            │  repeated n times
                                            ▼
        ┌────────────────────────────────────────────────────────────────┐
        │                    GeneticAlgorithm (GENERATIONAL)             │
        │                                                                │
        │  KPGenerator ──▶ population of KPIndividual (bit chromosome)   │
        │                                                                │
        │  loop until 100,000 evaluations:                               │
        │     TournamentSelector ──▶ 2 parents                           │
        │     combine()  (one point crossover over the BitSet)           │
        │     mutate()   (bit flipping)                                  │
        │     KPEvaluator.evaluate() ──▶ fitness                         │
        └───────────────────────────────┬────────────────────────────────┘
                                        │  best individual
                                        ▼
                    KPIndividual.to_kp() ──▶ KP ──▶ save("*.kp")
```

### How an individual is evaluated

Every individual is a bit string that encodes the items of a knapsack.
`KPEvaluator.evaluate()` decodes it, solves it **four times** (once per heuristic)
and combines the four results according to the requested `InstanceType`:

- `*_EASY` — the target heuristic must beat the best of the other three:
  `target_result − max(the others)`.
- `*_HARD` — the target heuristic must fall below the worst of the others:
  `min(the others) − target_result`.
- `MAX_VARIANCE` / `MIN_VARIANCE` — pushes the four heuristics to differ as much
  (or as little) as possible from each other.
- `PAIRED_*` — pushes **two** specific heuristics to win together and with similar
  results between them (the difference is penalised with `lambda = 2`).

The genetic algorithm always **maximises** that fitness.

### Chromosome encoding

```
nb_bits = nb_items × ( ⌈log₂(max_weight)⌉ + ⌈log₂(max_profit)⌉ )
```

With the default values (`max_weight=20`, `max_profit=50`, `nb_items=10`) that is
5 weight bits + 6 profit bits = 11 bits per item, 110 bits in total. The integer
value of each block is computed by `to_integer()`, which **adds 1** to the result
(so no item ends up with zero weight or zero profit).

### `.kp` instance format

```
10, 20          ← number of items, knapsack capacity
10, 37.000      ← weight, profit
4, 46.000
...
```

---

## 2. Project structure

The three Java NetBeans projects map to three Python packages, plus one
compatibility layer:

| Java project  | Java package              | Python package | Contents |
|---------------|---------------------------|----------------|----------|
| `Generator`   | `mx.tec.hermes`           | `hermes/`      | the knapsack problem and the generator |
| `MetaH`       | `mx.tec.meta`             | `metah/`       | the meta heuristics |
| `Utils`       | `Utils`                   | `utils/`       | utilities (a copy of the ones in `hermes.utils`) |
| —             | (pieces of `java.*`)      | `javacompat/`  | compatibility layer for the Java runtime |

```
EvolutionaryGenerator_v2.1_Python/
├── main.py                          entry point (see §4)
├── javacompat/                      java.util.Random, BitSet, DecimalFormat, Collections
├── metah/                           ← MetaH
│   ├── individual.py                Individual
│   ├── generator.py                 Generator
│   ├── evaluator.py                 Evaluator
│   ├── selector.py                  Selector
│   ├── tournament_selector.py       TournamentSelector
│   ├── ga/genetic_algorithm.py      GeneticAlgorithm (generational and steady state)
│   ├── mga/micro_genetic_algorithm.py   MicroGeneticAlgorithm
│   ├── es/evolutionary_strategy.py  EvolutionaryStrategy (1+1 EA)
│   └── gp/                          SExpression, GPIndividual, GPGenerator, GeneticProgramming
├── hermes/                          ← Generator
│   ├── exceptions/                  NoSuchFeatureException, NoSuchHeuristicException
│   ├── utils/                       Files, Statistical
│   └── problems/
│       ├── problem.py               Problem (characterize / solve problem sets)
│       ├── problem_set.py           ProblemSet (TRAIN / TEST)
│       ├── problem_stream.py        ProblemStream
│       └── kp/
│           ├── kp.py                KP  (heuristics, dynamic programming, save)
│           ├── item.py              Item
│           ├── knapsack.py          Knapsack
│           └── generator/           KPIndividual, KPGenerator, KPEvaluator
├── utils/                           ← Utils (Files, Statistical, Timer)
└── tests/                           verification against the Java version (see §5)
```

---

## 3. Requirements

Python 3.9 or later. **There are no external dependencies**: everything is
standard library. (The Java project declared `json-simple-1.1.1.jar`, but no class
ever used it, so nothing was translated on that front.)

---

## 4. How to run it

The Java project declares `main.class=Run` in
`Generator/nbproject/project.properties`, but **`Run.java` does not exist** among
the sources that were handed over: there is no original `main` to translate.
`main.py` rebuilds that entry point by calling directly the public methods the
Java version already exposed.

```bash
# Generate 5 instances that are easy for MAX_PROFIT
python3 main.py generate --type MAX_PROFIT_EASY --nb-instances 5 --path ./instances/

# Solve a set with the four heuristics
python3 main.py solve --path ./instances

# Characterize a set (the four features)
python3 main.py characterize --path ./instances

# Solve to optimality with dynamic programming
python3 main.py solve-dp --path ./instances
```

`python3 main.py <command> --help` lists every parameter. The defaults of
`generate` are the same as the ones in the `KPIndividual` class (`nb_items=10`,
`capacity=20`, `max_weight=20`, `max_profit=50`).

It can also be used as a library, the same way the Java code was:

```python
from hermes.problems.kp.kp import KP
from hermes.problems.kp.generator.kp_evaluator import InstanceType

KP.generate(InstanceType.MAX_PROFIT_EASY, 2, "KP", "./instances/",
            10, 20, 20, 50, 10, 1.0, 0.1, 3, 12345)
```

> **A note on running time:** `KP.generate` has 100,000 evaluations per instance
> hard coded (that is how it is in the Java original). Each instance takes around
> 30 s in Python against ~2 s in Java. That is the expected cost of the change of
> language; the results are identical.

---

## 5. Verification

```bash
python3 tests/test_equivalence.py
# OK: the Python translation reproduces the 405 lines of the Java original exactly.
```

`tests/expected_java_output.txt` was produced by `tests/java/Reference.java`, a
program compiled against the original sources of `EvolutionaryGenerator_v2.1_Java`.
The test runs the very same scenario in Python and compares it line by line. Every
floating point number is compared through its **raw IEEE 754 bit pattern**, so no
formatting difference between the two languages can hide a real divergence.

The scenario covers: the statistical helpers, the encoding and the genetic
operators of `KPIndividual`, the four heuristics, `solveCA`, `solveX`, dynamic
programming, `ProblemSet` (with TRAIN/TEST shuffling), `ProblemStream`, the genetic
algorithm (generational and steady state), the micro genetic algorithm (both
types), the evolutionary strategy, the S-expressions and genetic programming.

The full generator flow was checked as well: `KP.generate` with seed 12345 produces
in Python the **same 20,014 trace lines** and the same `.kp` files, byte for byte,
as the Java version.

---

## 6. Notes on the fidelity of the translation

### 6.1 The `javacompat` layer

This is the piece that makes the exact equivalence possible:

- **`Random`** — reimplements the 48 bit linear congruential generator of
  `java.util.Random`. Python's `random` module uses Mersenne Twister, which would
  produce a completely different sequence. It provides `next_int`,
  `next_int(bound)`, `next_int(origin, bound)`, `next_long`, `next_double`,
  `next_double(origin, bound)` and `next_boolean`. Note that `next_int(0, n)` and
  `next_int(n)` do **not** consume the stream in the same way, exactly as in Java.
- **`BitSet`** — reproduces `java.util.BitSet`, including the fact that
  `get(from, to)` returns a new set whose bit 0 is the bit `from`.
- **`DecimalFormat`** — reproduces the patterns `000`, `0.000`, `0.0000` and
  `00.0000E00`, with HALF_EVEN rounding over the exact decimal value of the double.
- **`collections`** — `sort` (stable, with a reversed comparator for `MAXIMIZE`)
  and `shuffle`, which follows the exact algorithm of
  `Collections.shuffle(List, Random)`.

### 6.2 Behaviours of the original that were kept on purpose

A faithful translation keeps the quirks too. They are all marked with comments in
the code:

1. **`Statistical.max`** starts at `Double.MIN_VALUE`, which in Java is the
   smallest **positive** double (4.9E-324) and not the most negative one. If every
   value is negative, it returns 4.9E-324.
2. **`KPIndividual.__str__`** reads `bits.get(j + from_index)` over the bits that
   were already extracted, out of range: that is why the profit part is always
   printed as `000000` even though the value in parentheses is correct.
3. **`KPIndividual.combine`** ignores `crossover_rate` and modifies the parents in
   place (crossover always happens).
4. **`Knapsack.copy`** builds the copy with the *remaining* capacity and then packs
   the items again, which reduces it once more.
5. **`SExpression.evaluate`** inverts the condition in `log` and `log10`: it
   returns 1 when the argument is **not** zero.
6. **`EvolutionaryStrategy`** always accepts the offspring when its evaluation is
   *smaller*, regardless of the declared objective.
7. **`MARKOVITZ_EASY` / `MARKOVITZ_HARD`** are declared in the enum but never
   implemented; they fall into the branch that halts the program, just as in Java.
8. `KP.solve_with_dynamic_programming` truncates to integer (`(int) Math.max(...)`)
   even though the table holds doubles.

### 6.3 Translation conventions

- **Method overloading.** Python does not have it, so overloaded methods are split
  with explicit names, or given default arguments when the meaning is the same:

  | Java | Python |
  |------|--------|
  | `KP.solve(String)` | `solve(heuristic)` |
  | `KP.solve()` | `solve_with_dynamic_programming()` |
  | `KP.solve(ProblemSet)` | `solve_set_with_dynamic_programming(set)` |
  | `KP.solve(SExpression)` | `solve_with_s_expression(se)` |
  | `Problem.solve(ProblemSet, String[])` | `solve_set(set, heuristics)` |
  | `Problem.solve(ProblemSet, SExpression[])` | `solve_set_with_s_expressions(set, ses)` |
  | `SExpression.set(String, double)` (static) | `set_variable(name, value)` |
  | multiple constructors (`KP`, `KPIndividual`, `GPIndividual`, `SExpression`) | one `__init__` that dispatches on its arguments |

- **Reflection.** `Problem.characterize` and `Problem.solve` created instances
  through `getClass().getConstructor(String.class)`; in Python `type(self)(file)`
  plays the same role.
- **Naming.** Classes in `CamelCase` and methods in `snake_case`, following PEP 8.
  The getters are kept (`get_obj_value`, `get_profit`, …) so the code reads like
  the original, and the attributes are public as well.
- **Documentation.** The Javadoc comments became docstrings, including the
  original author's own comments (such as `# DEbería devolver una copia.` or the
  `# hack, borrar!` block). Those two are quoted verbatim in Spanish because they
  are the original author's words; an English gloss is given next to each one.

### 6.4 Unavoidable differences

- `Utils.Timer` used `ThreadMXBean.getCurrentThreadCpuTime()`; Python uses
  `time.thread_time_ns()`, its closest equivalent. (No class in the generator
  actually uses `Timer`.)
- The fatal errors of the original (`System.exit(1)` after writing to `stderr`) are
  kept as `sys.exit(1)`.

---

## 7. Authorship and version

### Authorship

This follows the usual convention for a translation between languages: **whoever
translates signs the translation, and the original author keeps the credit for the
design**. Every translated class carries the three tags, for instance in
`hermes/problems/problem.py`:

```
:author: Paola Azeneth Castillo Gutiérrez (Python translation)
:original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
:original version: 2.1
```

The files that do **not** exist in the original — `javacompat/`, `main.py`,
`tests/`, and the re-exporting modules in `utils/` — carry a single author, the
one who translated, because they were written from scratch for this version.

### Version

The project is **v2.1**, the same as the Java original: 2.1 is the highest
`@version` tag in the Java sources (`Problem.java`; every other class is at 2.0 or
1.0). This is the *parallel implementations* convention (the one used by projects
such as protobuf, with a single version shared across C++, Java and Python): this
is not different software, it is the same software in another language. It is
particularly justified here because the equivalence is **proven bit for bit**
(§5), not merely claimed.

```python
>>> import hermes
>>> hermes.__version__
'2.1.0'
```

```bash
python3 main.py --version     # EvolutionaryGenerator 2.1.0 (Python)
```

The `:original version:` tag on each class keeps the `@version` that class carried
in Java (1.0, 2.0 or 2.1 depending on the case). It documents which version of
*that class* was the starting point and should not be confused with the version of
the project.
