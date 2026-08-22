#!/usr/bin/env python3
"""Entry point of the Python translation of the 2019 knapsack instance generator.

The NetBeans project ``Generator`` declares ``main.class=Run`` in
``nbproject/project.properties``, but ``Run.java`` is not part of the sources that
were handed over, so there is no original ``main`` to translate.  This module
rebuilds that entry point from the public API of the translated classes: every
command below is a direct call to one of the methods the Java version exposes.

Examples
--------
Generate 5 instances biased towards the MAX_PROFIT heuristic::

    python3 main.py generate --type MAX_PROFIT_EASY --nb-instances 5 --path ./instances/

Solve every instance in a folder with the four heuristics::

    python3 main.py solve --path ./instances

Characterize every instance in a folder::

    python3 main.py characterize --path ./instances

Solve every instance in a folder to optimality (dynamic programming)::

    python3 main.py solve-dp --path ./instances

:author: Paola Azeneth Castillo Gutiérrez
"""

import argparse
import os
import sys

from hermes import __version__
from hermes.problems.kp.generator.kp_evaluator import InstanceType
from hermes.problems.kp.kp import KP
from hermes.problems.problem_set import ProblemSet, Subset


def _generate(args: argparse.Namespace) -> None:
    """Runs ``KP.generate``, which evolves and saves a set of instances."""
    path = args.path
    if not path.endswith("/"):
        # KP.generate concatenates the path and the identifier with no separator.
        path = path + "/"
    os.makedirs(path, exist_ok=True)
    KP.generate(InstanceType[args.type], args.nb_instances, args.id, path, args.nb_items,
                args.capacity, args.max_weight, args.max_profit, args.population_size,
                args.crossover_rate, args.mutation_rate, args.tournament_size, args.seed)


def _solve(args: argparse.Namespace) -> None:
    """Runs ``Problem.solve(ProblemSet, String[])`` over a folder of instances."""
    problem_set = ProblemSet(args.path, Subset[args.subset], args.proportion, args.seed)
    print(KP().solve_set(problem_set, args.heuristics))


def _characterize(args: argparse.Namespace) -> None:
    """Runs ``Problem.characterize(ProblemSet, String[])`` over a folder of instances."""
    problem_set = ProblemSet(args.path, Subset[args.subset], args.proportion, args.seed)
    print(KP().characterize(problem_set, args.features))


def _solve_dp(args: argparse.Namespace) -> None:
    """Runs ``KP.solve(ProblemSet)``, which solves the set with dynamic programming."""
    problem_set = ProblemSet(args.path, Subset[args.subset], args.proportion, args.seed)
    print(KP().solve_set_with_dynamic_programming(problem_set))


def _add_set_arguments(parser: argparse.ArgumentParser) -> None:
    """Adds the arguments that describe how a ``ProblemSet`` is built."""
    parser.add_argument("--path", required=True, help="the folder that contains the instances")
    parser.add_argument("--subset", default="TEST", choices=[subset.name for subset in Subset],
                        help="the fraction of the set to use (default: TEST)")
    parser.add_argument("--proportion", type=float, default=1.0,
                        help="the proportion of the instances used for training (default: 1.0)")
    parser.add_argument("--seed", type=int, default=0,
                        help="the seed to initialize the random number generator (default: 0)")


def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version="EvolutionaryGenerator %s (Python)" % __version__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="evolves a set of knapsack instances")
    generate.add_argument("--type", default="MAX_PROFIT_EASY",
                          choices=[instance_type.name for instance_type in InstanceType],
                          help="the type of the instances to generate (default: MAX_PROFIT_EASY)")
    generate.add_argument("--nb-instances", type=int, default=1, help="the number of instances to generate")
    generate.add_argument("--id", default="KP", help="the prefix identifier of the instances")
    generate.add_argument("--path", default="./instances/", help="the folder where the instances are saved")
    generate.add_argument("--nb-items", type=int, default=10, help="the number of items per instance")
    generate.add_argument("--capacity", type=int, default=20, help="the capacity of the knapsack")
    generate.add_argument("--max-weight", type=int, default=20, help="the maximum weight per item")
    generate.add_argument("--max-profit", type=int, default=50, help="the maximum profit per item")
    generate.add_argument("--population-size", type=int, default=20, help="the size of the population")
    generate.add_argument("--crossover-rate", type=float, default=1.0, help="the crossover rate")
    generate.add_argument("--mutation-rate", type=float, default=0.1, help="the mutation rate")
    generate.add_argument("--tournament-size", type=int, default=3, help="the size of the tournament")
    generate.add_argument("--seed", type=int, default=0,
                          help="the seed to initialize the random number generator (default: 0)")
    generate.set_defaults(function=_generate)

    solve = subparsers.add_parser("solve", help="solves a set of instances with a set of heuristics")
    _add_set_arguments(solve)
    solve.add_argument("--heuristics", nargs="+", default=KP.HEURISTICS,
                       help="the heuristics to use (default: %s)" % " ".join(KP.HEURISTICS))
    solve.set_defaults(function=_solve)

    characterize = subparsers.add_parser("characterize", help="characterizes a set of instances")
    _add_set_arguments(characterize)
    characterize.add_argument("--features", nargs="+", default=KP.FEATURES,
                              help="the features to use (default: %s)" % " ".join(KP.FEATURES))
    characterize.set_defaults(function=_characterize)

    solve_dp = subparsers.add_parser("solve-dp", help="solves a set of instances with dynamic programming")
    _add_set_arguments(solve_dp)
    solve_dp.set_defaults(function=_solve_dp)

    args = parser.parse_args(argv)
    args.function(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
