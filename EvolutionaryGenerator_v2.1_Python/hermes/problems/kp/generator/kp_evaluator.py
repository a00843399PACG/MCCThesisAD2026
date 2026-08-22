"""Translation of ``mx.tec.hermes.problems.kp.generator.KPEvaluator``."""

import sys
from enum import Enum

from hermes.utils import statistical as Statistical
from metah.evaluator import Evaluator
from metah.individual import Individual


class InstanceType(Enum):
    """Defines the type of the instances the evaluator asks the genetic algorithm to produce."""

    DEFAULT_EASY = "DEFAULT_EASY"
    DEFAULT_HARD = "DEFAULT_HARD"
    MIN_WEIGHT_EASY = "MIN_WEIGHT_EASY"
    MIN_WEIGHT_HARD = "MIN_WEIGHT_HARD"
    MAX_PROFIT_EASY = "MAX_PROFIT_EASY"
    MAX_PROFIT_HARD = "MAX_PROFIT_HARD"
    MAX_PROFIT_WEIGHT_EASY = "MAX_PROFIT_WEIGHT_EASY"
    MAX_PROFIT_WEIGHT_HARD = "MAX_PROFIT_WEIGHT_HARD"
    MARKOVITZ_EASY = "MARKOVITZ_EASY"
    MARKOVITZ_HARD = "MARKOVITZ_HARD"
    MIN_VARIANCE = "MIN_VARIANCE"
    MAX_VARIANCE = "MAX_VARIANCE"
    PAIRED_DEF_MAXP = "PAIRED_DEF_MAXP"
    PAIRED_DEF_MAXPW = "PAIRED_DEF_MAXPW"
    PAIRED_DEF_MINW = "PAIRED_DEF_MINW"
    PAIRED_MAXP_MAXPW = "PAIRED_MAXP_MAXPW"
    PAIRED_MAXP_MINW = "PAIRED_MAXP_MINW"
    PAIRED_MAXPW_MINW = "PAIRED_MAXPW_MINW"


class KPEvaluator(Evaluator):
    """Provides the methods to evaluate individuals for the automatic generation of
    knapsack problems by using a genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    InstanceType = InstanceType

    def __init__(self, type: InstanceType):
        """Creates a new instance of ``KPEvaluator``.

        :param type: The type of the instances to produce.
        """
        super().__init__()
        self.type = type

    def evaluate(self, individual: Individual) -> float:
        self.nb_evaluations += 1
        problem = individual.to_kp()
        problem.solve("DEFAULT")
        result_default = problem.get_obj_value()
        problem = individual.to_kp()
        problem.solve("MIN_WEIGHT")
        result_min_weight = problem.get_obj_value()
        problem = individual.to_kp()
        problem.solve("MAX_PROFIT/WEIGHT")
        result_max_profit_per_weight_unit = problem.get_obj_value()
        problem = individual.to_kp()
        problem.solve("MAX_PROFIT")
        result_max_profit = problem.get_obj_value()
        lambda_ = 2
        type = self.type
        if type == InstanceType.DEFAULT_EASY:
            results = [result_min_weight, result_max_profit, result_max_profit_per_weight_unit]
            return result_default - Statistical.max(results)
        elif type == InstanceType.DEFAULT_HARD:
            results = [result_min_weight, result_max_profit, result_max_profit_per_weight_unit]
            return Statistical.min(results) - result_default
        elif type == InstanceType.MIN_WEIGHT_EASY:
            results = [result_default, result_max_profit, result_max_profit_per_weight_unit]
            return result_min_weight - Statistical.max(results)
        elif type == InstanceType.MIN_WEIGHT_HARD:
            results = [result_default, result_max_profit, result_max_profit_per_weight_unit]
            return Statistical.min(results) - result_min_weight
        elif type == InstanceType.MAX_PROFIT_EASY:
            results = [result_default, result_min_weight, result_max_profit_per_weight_unit]
            return result_max_profit - Statistical.max(results)
        elif type == InstanceType.MAX_PROFIT_HARD:
            results = [result_default, result_min_weight, result_max_profit_per_weight_unit]
            return Statistical.min(results) - result_max_profit
        elif type == InstanceType.MAX_PROFIT_WEIGHT_EASY:
            results = [result_default, result_min_weight, result_max_profit]
            return result_max_profit_per_weight_unit - Statistical.max(results)
        elif type == InstanceType.MAX_PROFIT_WEIGHT_HARD:
            results = [result_default, result_min_weight, result_max_profit]
            return Statistical.min(results) - result_max_profit_per_weight_unit
        elif type == InstanceType.MAX_VARIANCE:
            results = [result_default, result_min_weight, result_max_profit, result_max_profit_per_weight_unit]
            return Statistical.stdev(results)
        elif type == InstanceType.MIN_VARIANCE:
            results = [result_default, result_min_weight, result_max_profit, result_max_profit_per_weight_unit]
            return -1 * Statistical.stdev(results)
        elif type == InstanceType.PAIRED_DEF_MAXP:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_default, result_max_profit)
                    - _max(result_max_profit_per_weight_unit, result_min_weight)
                    - lambda_ * abs(result_default - result_max_profit))
        elif type == InstanceType.PAIRED_DEF_MAXPW:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_default, result_max_profit_per_weight_unit)
                    - _max(result_max_profit, result_min_weight)
                    - lambda_ * abs(result_default - result_max_profit_per_weight_unit))
        elif type == InstanceType.PAIRED_DEF_MINW:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_default, result_min_weight)
                    - _max(result_max_profit, result_max_profit_per_weight_unit)
                    - lambda_ * abs(result_default - result_min_weight))
        elif type == InstanceType.PAIRED_MAXP_MAXPW:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_max_profit, result_max_profit_per_weight_unit)
                    - _max(result_default, result_min_weight)
                    - lambda_ * abs(result_max_profit - result_max_profit_per_weight_unit))
        elif type == InstanceType.PAIRED_MAXP_MINW:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_max_profit, result_min_weight)
                    - _max(result_default, result_max_profit_per_weight_unit)
                    - lambda_ * abs(result_max_profit - result_min_weight))
        elif type == InstanceType.PAIRED_MAXPW_MINW:
            max = Statistical.max([result_default, result_max_profit,
                                   result_max_profit_per_weight_unit, result_min_weight])
            result_default = result_default / max
            result_max_profit = result_max_profit / max
            result_max_profit_per_weight_unit = result_max_profit_per_weight_unit / max
            result_min_weight = result_min_weight / max
            return (_min(result_max_profit_per_weight_unit, result_min_weight)
                    - _max(result_default, result_max_profit)
                    - lambda_ * abs(result_max_profit_per_weight_unit - result_min_weight))
        else:
            # MARKOVITZ_EASY and MARKOVITZ_HARD are declared but not implemented in
            # the Java version either, so they fall into this branch.
            print("The option is not recognized by the system.", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        return 0


def _min(a: float, b: float) -> float:
    """Equivalent of ``Math.min(double, double)``."""
    return a if a < b else b


def _max(a: float, b: float) -> float:
    """Equivalent of ``Math.max(double, double)``."""
    return a if a > b else b
