"""Translation of ``mx.tec.hermes.problems.Problem``."""

import sys
from abc import ABC, abstractmethod

from hermes.exceptions import NoSuchFeatureException
from hermes.problems.problem_set import ProblemSet
from javacompat import DecimalFormat


class Problem(ABC):
    """Provides the basic functionality for all the problems supported by HERMES.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.1
    """

    def __init__(self):
        #: The problem Id associated to this problem.
        self.problem_id = "Not available"

    def get_problem_id(self) -> str:
        """Returns the problem Id associated to this problem.

        :return: The problem Id associated to this problem.
        """
        return self.problem_id

    @abstractmethod
    def get_size(self) -> int:
        """Returns the size of this problem.

        :return: The size of this problem. Please note that the size might mean
            different things according to the problem.
        """

    @abstractmethod
    def get_feature(self, feature: str) -> float:
        """Returns the current value of a given feature.

        :param feature: The name of the feature.
        :return: The current value of a given feature.
        :raises NoSuchFeatureException: If the feature is not recognized.
        """

    @abstractmethod
    def get_obj_value(self) -> float:
        """Returns the objective function value of the current solution to this problem.

        :return: The objective function value of the current solution to this problem.
        """

    @abstractmethod
    def solve(self, heuristic: str) -> None:
        """Solves this problem by using a specific heuristic.

        :param heuristic: The heuristic to solve this problem.
        """

    def characterize(self, set: ProblemSet, features: list) -> str:
        """Characterizes a problem set by using a set of features.

        :param set: The set of instances to characterize.
        :param features: The features to be used to characterize the set.
        :return: The characterization a problem set by using a set of features.
        """
        format = DecimalFormat("0.0000")
        string = []
        string.append("INSTANCE\t")
        for feature in features:
            string.append(feature + "\t")
        string.append("\r\n")
        try:
            for file in set.get_files():
                # The Java version reaches the single argument constructor by
                # reflection; here the type of the instance plays the same role.
                constructor = type(self)
                problem = constructor(file)
                feature_values = []
                string.append(problem.get_problem_id() + "\t")
                for feature in features:
                    problem = constructor(file)
                    feature_values.append(format.format(problem.get_feature(feature)) + "\t")
                string.append("".join(feature_values) + "\r\n")
        except (NoSuchFeatureException, TypeError, AttributeError) as e:
            print(e, file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        return "".join(string).strip()

    def solve_set(self, set: ProblemSet, heuristics: list) -> str:
        """Solves a problem set by using a set of heuristics.

        This is the translation of ``Problem.solve(ProblemSet, String[])``.  It is
        renamed because Python does not support overloading and the class already
        declares an abstract ``solve(heuristic)``.

        :param set: The set of instances to solve.
        :param heuristics: The heuristics to be used to solve the set.
        :return: The results of solving a problem set by using a set of heuristics.
        """
        # format = DecimalFormat("0.0000")
        format = DecimalFormat("00.0000E00")
        string = []
        string.append("INSTANCE\t")
        for heuristic in heuristics:
            string.append(heuristic + "\t")
        string.append("\r\n")
        try:
            for file in set.get_files():
                constructor = type(self)
                problem = constructor(file)
                obj_values = []
                string.append(problem.get_problem_id() + "\t")
                for heuristic in heuristics:
                    problem = constructor(file)
                    problem.solve(heuristic)
                    obj_values.append(format.format(problem.get_obj_value()) + "\t")
                string.append("".join(obj_values) + "\r\n")
        except (TypeError, AttributeError) as e:
            print(e, file=sys.stderr)
            print("Problem.java/solve", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        return "".join(string).strip()

    def solve_set_with_s_expressions(self, set: ProblemSet, s_expressions: list) -> str:
        """Solves a problem set by using a set of S-expressions.

        This is the translation of ``Problem.solve(ProblemSet, SExpression[])``.

        :param set: The set of instances to solve.
        :param s_expressions: The S-expressions to be used to solve the set.
        :return: The results of solving a problem set by using a set of heuristics.
        """
        format = DecimalFormat("0.0000")
        string = []
        string.append("INSTANCE\t")
        for _ in s_expressions:
            string.append("SE" + "\t")
        string.append("\r\n")
        try:
            for file in set.get_files():
                constructor = type(self)
                problem = constructor(file)
                obj_values = []
                string.append(problem.get_problem_id() + "\t")
                for s_expression in s_expressions:
                    problem = constructor(file)
                    problem.solve_with_s_expression(s_expression)
                    obj_values.append(format.format(problem.get_obj_value()) + "\t")
                string.append("".join(obj_values) + "\r\n")
        except (TypeError, AttributeError) as e:
            print(e, file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        return "".join(string).strip()

    @abstractmethod
    def __str__(self) -> str:
        """Returns the string representation of this problem.

        :return: The string representation of this problem.
        """
