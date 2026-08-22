"""Translation of ``mx.tec.meta.es.EvolutionaryStrategy``."""

from javacompat import DecimalFormat
from metah.evaluator import Evaluator
from metah.individual import Individual


class EvolutionaryStrategy:
    """Provides the methods to use the evolutionary strategy 1 + 1 EA.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, evaluator: Evaluator):
        """Creates a new instance of ``EvolutionaryStrategy``.

        :param evaluator: The evaluator of the performance of the individuals in this evolutionary strategy.
        """
        self.evaluator = evaluator

    def run(self, individual: Individual, max_evaluations: int, mutation_rate: float,
            print_mode: bool) -> Individual:
        """Runs the evolutionary strategy and returns the best individual found.

        :param individual: The initial individual to start the process.
        :param max_evaluations: The maximum number of calls to the evaluation function
            this evolutionary strategy is allowed to execute.
        :param mutation_rate: The mutation rate to be used by the mutation operator.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best individual found by the evolutionary process.
        """
        format = DecimalFormat("0.0000")
        #
        # Evaluates the initial individual.
        #
        individual.set_evaluation(self.evaluator.evaluate(individual))
        #
        # Executes the evolutionary process.
        #
        i = 0
        while self.evaluator.get_nb_evaluations() < max_evaluations:
            #
            # Creates the next population.
            #
            offspring = individual.copy()
            offspring.mutate(mutation_rate)
            offspring.set_evaluation(self.evaluator.evaluate(offspring))
            #
            # If the new individual is better than the parent, the parent is replaced by the offspring.
            #
            if offspring.get_evaluation() < individual.get_evaluation():
                individual = offspring
            if print_mode:
                print(str(i + 1) + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                    + format.format(individual.get_evaluation()))
            i += 1
        return individual
