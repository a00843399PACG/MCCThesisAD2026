#!/usr/bin/env python3
"""Checks that the Python translation reproduces the output of the Java original.

``expected_java_output.txt`` was produced by ``java/Reference.java``, a harness
compiled against the sources of ``EvolutionaryGenerator_v2.1_Java``.  This module runs the
very same scenario through the Python translation and compares both outputs line
by line.  Every floating point number is printed as its raw IEEE 754 bit pattern,
so the comparison is exact and no formatting difference between the two languages
can hide a real divergence.

Run it with::

    python3 tests/test_equivalence.py

The scenario covers the statistical helpers, the encoding of the individuals, the
four constructive heuristics, dynamic programming, the problem sets and streams,
the genetic algorithm (generational and steady state), the micro genetic algorithm
(both types), the evolutionary strategy, the S-expressions and genetic programming.

:author: Paola Azeneth Castillo Gutiérrez
"""

import os
import struct
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))

from hermes.problems.kp.generator.kp_evaluator import InstanceType, KPEvaluator
from hermes.problems.kp.generator.kp_generator import KPGenerator
from hermes.problems.kp.generator.kp_individual import KPIndividual
from hermes.problems.kp.kp import KP
from hermes.problems.problem_set import ProblemSet, Subset
from hermes.problems.problem_stream import ProblemStream
from hermes.utils import statistical as Statistical
from metah.es.evolutionary_strategy import EvolutionaryStrategy
from metah.ga.genetic_algorithm import GeneticAlgorithm, Objective
from metah.gp.gp_generator import GPGenerator
from metah.gp.s_expression import SExpression
from metah.mga import micro_genetic_algorithm as mga_module
from metah.mga.micro_genetic_algorithm import MicroGeneticAlgorithm
from metah.tournament_selector import TournamentSelector

EXPECTED = os.path.join(_HERE, "expected_java_output.txt")
#: The reference output embeds this relative path, so the scenario runs from ``tests``.
POOL = "instances"


def _bits(value) -> str:
    """Returns the raw IEEE 754 bit pattern of a number, as Java's doubleToRawLongBits does."""
    return "%x" % struct.unpack("<Q", struct.pack("<d", float(value)))[0]


def f(value) -> str:
    if isinstance(value, list):
        return " ".join(_bits(x) for x in value)
    return _bits(value)


def jlist(items: list) -> str:
    """Formats a list the way ``java.util.List.toString`` does."""
    return "[" + ", ".join(str(item) for item in items) + "]"


def run_scenario(pool: str, out) -> None:
    """Runs the same scenario ``java/Reference.java`` runs, writing to ``out``."""

    def say(line):
        print(line, file=out)

    v = [3.5, -1.25, 7.0, 2.0, -9.5, 4.25]
    w = [1.0, 2.0, 3.0, 4.0, 5.0, 6.5]
    neg = [-1.0, -2.0, -3.0]
    say("=== STATISTICAL ===")
    say("mean " + f(Statistical.mean(v)))
    say("stdev " + f(Statistical.stdev(v)))
    say("median " + f(Statistical.median(v)))
    say("correlation " + f(Statistical.correlation(v, w)))
    say("lowerQuartile " + f(Statistical.lower_quartile(v)))
    say("upperQuartile " + f(Statistical.upper_quartile(v)))
    say("sort " + f(Statistical.sort(v)))
    say("max " + f(Statistical.max(v)))
    say("min " + f(Statistical.min(v)))
    say("range " + f(Statistical.range_(v)))
    say("maxOfNegatives " + f(Statistical.max(neg)))
    say("meanEmpty " + f(Statistical.mean([])))
    say("stdevSingle " + f(Statistical.stdev([5.0])))

    say("=== KPINDIVIDUAL ===")
    KPIndividual.set_capacity(20)
    KPIndividual.set_max_weight_per_item(20)
    KPIndividual.set_max_profit_per_item(50)
    KPIndividual.set_nb_items(10)
    a = KPIndividual(7)
    b = KPIndividual(99)
    say("a " + str(a))
    say("b " + str(b))
    say("aKP " + str(a.to_kp()))
    kids = a.combine(b, 1.0)
    say("kid0 " + str(kids[0]))
    say("kid1 " + str(kids[1]))
    kids[0].mutate(0.3)
    say("kid0mut " + str(kids[0]))
    say("copy " + str(kids[0].copy()))
    KPIndividual.set_max_weight_per_item(100)
    KPIndividual.set_max_profit_per_item(1000)
    KPIndividual.set_nb_items(4)
    say("nbBitsWide " + str(KPIndividual(3).to_kp()))
    KPIndividual.set_max_weight_per_item(20)
    KPIndividual.set_max_profit_per_item(50)
    KPIndividual.set_nb_items(10)

    say("=== SOLVE CA / X ===")
    problem_set = ProblemSet(pool)
    file = problem_set.get_files()[0]
    problem = KP(file)
    problem.solve_ca(["MAX_PROFIT", "MIN_WEIGHT"], [0, 1, 1])
    say("solveCA " + f(problem.get_obj_value()) + " " + str(problem.get_solution()))
    say("knapsack " + str(problem.get_knapsack()))
    say("size " + str(problem.get_size()) + " items " + jlist(problem.get_items()))
    solve_x = KP(file)
    _redirect(out, lambda: solve_x.solve_x(file, KP.HEURISTICS, 2020))

    say("=== PROBLEM SET / STREAM ===")
    train = ProblemSet(pool, Subset.TRAIN, 0.5, 77)
    test = ProblemSet(pool, Subset.TEST, 0.5, 77)
    say("train " + jlist(train.get_files()) + " size " + str(train.get_size()))
    say("test " + jlist(test.get_files()) + " size " + str(test.get_size()))
    stream = ProblemStream(pool, 5)
    for _ in range(6):
        say("stream " + stream.next())

    say("=== GA STEADY STATE ===")
    ga = GeneticAlgorithm(KPEvaluator(InstanceType.MIN_VARIANCE), KPGenerator(11),
                          TournamentSelector(3, 13), Objective.MINIMIZE)
    best = _redirect(out, lambda: ga.run(6, 200, 0.9, 0.05, GeneticAlgorithm.Type.STEADY_STATE, True))
    say("best " + str(best))

    say("=== GA GENERATIONAL ===")
    gag = GeneticAlgorithm(KPEvaluator(InstanceType.MAX_PROFIT_WEIGHT_HARD), KPGenerator(61),
                           TournamentSelector(4, 63), Objective.MAXIMIZE)
    best = _redirect(out, lambda: gag.run(6, 180, 1.0, 0.1, GeneticAlgorithm.Type.GENERATIONAL, True))
    say("best " + str(best))

    say("=== MGA GENERATIONAL ===")
    mga = MicroGeneticAlgorithm(KPEvaluator(InstanceType.MAX_VARIANCE), KPGenerator(21),
                                TournamentSelector(2, 23), Objective.MAXIMIZE)
    best = _redirect(out, lambda: mga.run(4, 120, mga_module.Type.GENERATIONAL, True))
    say("best " + str(best))

    say("=== MGA STEADY STATE ===")
    mga2 = MicroGeneticAlgorithm(KPEvaluator(InstanceType.PAIRED_DEF_MAXP), KPGenerator(31),
                                 TournamentSelector(2, 33), Objective.MAXIMIZE)
    best = _redirect(out, lambda: mga2.run(4, 120, mga_module.Type.STEADY_STATE, True))
    say("best " + str(best))

    say("=== ES ===")
    es = EvolutionaryStrategy(KPEvaluator(InstanceType.DEFAULT_HARD))
    best = _redirect(out, lambda: es.run(KPIndividual(41), 50, 0.2, True))
    say("best " + str(best))

    say("=== SEXPRESSION ===")
    SExpression.init(["w", "p", "R"], ["+", "-", "*", "/", "^", "exp", "log", "log10"], 1234)
    SExpression.set_variable("w", 3.0)
    SExpression.set_variable("p", 12.0)
    for _ in range(5):
        s_expression = SExpression(0)
        say("se " + str(s_expression) + " size " + str(s_expression.get_size())
            + " eval " + f(s_expression.evaluate()) + " copy " + str(s_expression.copy()))

    say("=== GP ===")
    SExpression.init(["w", "p", "R"], ["+", "-", "*", "/"], 4321)
    gp_generator = GPGenerator(51)
    g1 = gp_generator.generate()
    g2 = gp_generator.generate()
    say("g1 " + str(g1))
    say("g2 " + str(g2))
    gp_kids = g1.combine(g2, 1.0)
    say("gkid0 " + str(gp_kids[0]))
    say("gkid1 " + str(gp_kids[1]))
    gp_kids[0].mutate(1.0)
    say("gkid0mut " + str(gp_kids[0]))
    kp_se = KP(file)
    kp_se.solve_with_s_expression(SExpression(0))
    say("solveSE " + f(kp_se.get_obj_value()))

    say("=== SOLVE SE SET ===")
    say(KP().solve_set_with_s_expressions(problem_set, [SExpression(0), SExpression(0)]))


def _redirect(out, function):
    """Runs a function capturing whatever it writes to the standard output."""
    saved = sys.stdout
    sys.stdout = out
    try:
        return function()
    finally:
        sys.stdout = saved


def test_python_matches_java():
    """The Python translation must produce the very same output as the Java original."""
    import io

    buffer = io.StringIO()
    directory = os.getcwd()
    os.chdir(_HERE)
    try:
        run_scenario(POOL, buffer)
    finally:
        os.chdir(directory)
    produced = buffer.getvalue().strip().splitlines()
    with open(EXPECTED, "r") as file:
        expected = file.read().strip().splitlines()
    differences = []
    for i in range(max(len(produced), len(expected))):
        line_a = expected[i] if i < len(expected) else "<missing>"
        line_b = produced[i] if i < len(produced) else "<missing>"
        if line_a != line_b:
            differences.append((i + 1, line_a, line_b))
    assert not differences, "\n".join(
        "line %d:\n  java  : %s\n  python: %s" % difference for difference in differences[:20])
    return len(expected)


if __name__ == "__main__":
    try:
        nb_lines = test_python_matches_java()
    except AssertionError as error:
        print("FAILED: the translation diverges from the Java original.")
        print(error)
        sys.exit(1)
    print("OK: the Python translation reproduces the %d lines of the Java original exactly." % nb_lines)
