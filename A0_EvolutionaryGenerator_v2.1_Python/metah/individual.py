"""Translation of ``mx.tec.meta.Individual``."""

from abc import ABC, abstractmethod

from javacompat import Random


class Individual(ABC):
    """Provides the methods to create and handle individuals to be used by a genetic algorithm.

    The coding of the solution is left completely to the user on purpose, as it
    depends on their needs.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 1.0
    """

    def __init__(self, evaluation: float, seed: int):
        """Creates a new instance of ``Individual``.

        :param evaluation: The initial evaluation of this individual.
        :param seed: The seed to initialize the random number generator.
        """
        self.set_evaluation(evaluation)
        self.random = Random(seed)

    def set_evaluation(self, evaluation: float) -> None:
        """Sets the evaluation of this individual.

        :param evaluation: The evaluation of this individual.
        """
        self.evaluation = evaluation

    def get_evaluation(self) -> float:
        """Returns the evaluation of this individual.

        :return: The new evaluation of this individual.
        """
        return self.evaluation

    @abstractmethod
    def combine(self, individual: "Individual", crossover_rate: float) -> list:
        """Combines the individuals given as parameters to produce new ones.

        :param individual: The individuals to be combined with this individual.
        :param crossover_rate: The crossover rate to be used by the crossover operator.
        :return: The individuals resulting from the combination of the individuals
            given as parameters.
        """

    @abstractmethod
    def mutate(self, mutation_rate: float) -> None:
        """Mutates this individual.

        :param mutation_rate: The mutation rate to be used by the mutation operator.
        """

    @abstractmethod
    def copy(self) -> "Individual":
        """Returns a deep copy of this individual.

        :return: A deep copy of this individual.
        """

    def compare_to(self, individual: "Individual") -> int:
        """Compares two individuals based on their evaluations.

        :param individual: The solution to compare.
        :return: 1 if the evaluation of this solution is larger than the evaluation
            of the one provided as argument, 0 if their evaluations are equal and -1
            if the evaluation of this solution is smaller than the evaluation of the
            solution provided as argument.
        """
        evaluation_a = self.get_evaluation()
        evaluation_b = individual.get_evaluation()
        if evaluation_a < evaluation_b:
            return -1
        elif evaluation_a == evaluation_b:
            return 0
        return 1

    def __lt__(self, individual: "Individual") -> bool:
        return self.compare_to(individual) < 0

    @abstractmethod
    def __str__(self) -> str:
        """Returns the string representation of this individual.

        :return: The string representation of this individual.
        """
