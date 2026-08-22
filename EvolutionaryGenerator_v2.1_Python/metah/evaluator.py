"""Translation of ``mx.tec.meta.Evaluator``."""

from abc import ABC, abstractmethod

from metah.individual import Individual


class Evaluator(ABC):
    """Defines the methods that every evaluator used by the meta heuristics must implement.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self):
        """Creates a new instance of ``Evaluator``."""
        self.nb_evaluations = 0

    @abstractmethod
    def evaluate(self, solution: Individual) -> float:
        """Returns the evaluation of a solution.

        :param solution: The solution to be evaluated.
        :return: The evaluation of a solution.
        """

    def get_nb_evaluations(self) -> int:
        """Returns the number of evaluations executed by this evaluator.

        :return: The number of evaluations executed by this evaluator.
        """
        return self.nb_evaluations

    def reset(self) -> None:
        """Resets the number of evaluations executed by this evaluator."""
        self.nb_evaluations = 0
