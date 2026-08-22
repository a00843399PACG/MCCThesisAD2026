"""Translation of ``mx.tec.meta.gp.GeneticProgramming``."""

from metah.evaluator import Evaluator
from metah.ga.genetic_algorithm import GeneticAlgorithm, Objective, Type
from metah.generator import Generator
from metah.individual import Individual
from metah.selector import Selector


class GeneticProgramming:
    """Provides the methods to run a genetic programming process.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: jcobayliss
    """

    def __init__(self, evaluator: Evaluator, generator: Generator, selector: Selector, objective: Objective):
        """Creates a new instance of ``GeneticProgramming``.

        :param evaluator: The evaluator of the performance of the individuals in this process.
        :param generator: The generator of the solutions in this genetic algorithm.
        :param selector: The selector to be used by the genetic algorithm.
        :param objective: The objective of the evolutionary process regarding the
            objective function (maximize or minimize).
        """
        self.genetic_algorithm = GeneticAlgorithm(evaluator, generator, selector, objective)

    def run(self, population_size: int, max_evaluations: int, crossover_rate: float,
            mutation_rate: float, print_mode: bool) -> Individual:
        """Runs the evolutionary process and returns the best individual found.

        :param population_size: The size of the population in the evolutionary process.
        :param max_evaluations: The maximum number of calls to the evaluation function
            this evolutionary process is allowed to execute.
        :param crossover_rate: The crossover rate to be used by the evolutionary process.
        :param mutation_rate: The mutation rate to be used by the evolutionary process.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        return self.genetic_algorithm.run(population_size, max_evaluations, crossover_rate,
                                          mutation_rate, Type.GENERATIONAL, print_mode)
