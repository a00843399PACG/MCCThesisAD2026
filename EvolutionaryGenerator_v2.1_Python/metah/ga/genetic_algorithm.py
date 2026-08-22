"""Translation of ``mx.tec.meta.ga.GeneticAlgorithm``."""

import math
import sys
from enum import Enum

from javacompat import DecimalFormat
from javacompat import collections as java_collections
from metah.evaluator import Evaluator
from metah.generator import Generator
from metah.individual import Individual
from metah.selector import Selector


class Type(Enum):
    """Defines the type of the genetic algorithm to use."""

    GENERATIONAL = "GENERATIONAL"
    STEADY_STATE = "STEADY_STATE"


class Objective(Enum):
    """Defines the objective of the evolutionary process regarding the objective function."""

    MAXIMIZE = "MAXIMIZE"
    MINIMIZE = "MINIMIZE"


class GeneticAlgorithm:
    """Provides the methods to use a genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 1.0
    """

    #: Exposed as nested types, as they are in the Java version.
    Type = Type
    Objective = Objective

    def __init__(self, evaluator: Evaluator, generator: Generator, selector: Selector, objective: Objective):
        """Creates a new instance of ``GeneticAlgorithm``.

        :param evaluator: The evaluator of the performance of the individuals in this genetic algorithm.
        :param generator: The generator of the solutions in this genetic algorithm.
        :param selector: The selector to be used by the genetic algorithm.
        :param objective: The objective of the evolutionary process regarding the
            objective function (maximize or minimize).
        """
        self.evaluator = evaluator
        self.generator = generator
        self.selector = selector
        self.objective = objective
        self.best = None
        self.population = None

    def run(self, population_size: int, max_evaluations: int, crossover_rate: float,
            mutation_rate: float, type: Type, print_mode: bool) -> Individual:
        """Runs the genetic algorithm and returns the best individual found.

        :param population_size: The size of the population in this genetic algorithm.
        :param max_evaluations: The maximum number of calls to the evaluation function
            this genetic algorithm is allowed to execute.
        :param crossover_rate: The crossover rate to be used by this genetic algorithm.
        :param mutation_rate: The mutation rate to be used by this genetic algorithm.
        :param type: The type of the genetic algorithm to be used.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        if population_size < 2:
            print("The population must contain at least two individuals in order to run the genetic algorithm.",
                  file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        self.population = []
        for _ in range(population_size):
            self.population.append(self.generator.generate())
        if crossover_rate < 0:
            crossover_rate = 0.0
        if crossover_rate > 1:
            crossover_rate = 1.0
        if mutation_rate < 0:
            mutation_rate = 0.0
        if mutation_rate > 1:
            mutation_rate = 1.0
        for individual in self.population:
            individual.set_evaluation(self.evaluator.evaluate(individual))
        if self.objective == Objective.MINIMIZE:
            java_collections.sort(self.population)
        else:
            java_collections.sort(self.population, reverse=True)
        self.best = self.population[0].copy()
        if type == Type.GENERATIONAL:
            return self._run_generational(max_evaluations, crossover_rate, mutation_rate, print_mode)
        if type == Type.STEADY_STATE:
            return self._run_steady_state(max_evaluations, crossover_rate, mutation_rate, print_mode)
        return None

    def _run_generational(self, max_evaluations: int, crossover_rate: float,
                          mutation_rate: float, print_mode: bool) -> Individual:
        """Runs a generational genetic algorithm.

        :param max_evaluations: The maximum number of generations that this genetic
            algorithm is allowed to run.
        :param crossover_rate: The crossover rate to be used by this genetic algorithm.
        :param mutation_rate: The mutation rate to be used by this genetic algorithm.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        # format = DecimalFormat("0.0000")
        format = DecimalFormat("00.0000E00")
        fitness = [individual.get_evaluation() for individual in self.population]
        if print_mode:
            print("ITERATIONS, EVALUATIONS, BEST, MEAN, DEVIATION")
            print("0, " + str(self.evaluator.get_nb_evaluations()) + ", "
                  + format.format(self.best.get_evaluation()) + ", "
                  + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
        i = 0
        while self.evaluator.get_nb_evaluations() < max_evaluations:
            next_population = []
            while len(next_population) < len(self.population):
                parents = self.selector.select(self.population, self.objective)
                offspring = parents[0].combine(parents[1], crossover_rate)
                for individual in offspring:
                    individual.mutate(mutation_rate)
                    individual.set_evaluation(self.evaluator.evaluate(individual))
                    next_population.append(individual)
            self.population = next_population
            if self.objective == Objective.MINIMIZE:
                java_collections.sort(self.population)
                if self.population[0].get_evaluation() < self.best.get_evaluation():
                    self.best = self.population[0].copy()
            else:
                java_collections.sort(self.population, reverse=True)
                if self.population[0].get_evaluation() > self.best.get_evaluation():
                    self.best = self.population[0].copy()
            fitness = [individual.get_evaluation() for individual in self.population]
            if print_mode:
                print(str(i + 1) + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                      + format.format(self.best.get_evaluation()) + ", "
                      + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
            i += 1
        return self.best

    def _run_steady_state(self, max_evaluations: int, crossover_rate: float,
                          mutation_rate: float, print_mode: bool) -> Individual:
        """Runs a steady state genetic algorithm.

        :param max_evaluations: The maximum number of generations that this genetic
            algorithm is allowed to run.
        :param crossover_rate: The crossover rate to be used by this genetic algorithm.
        :param mutation_rate: The mutation rate to be used by this genetic algorithm.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        format = DecimalFormat("0.0000")
        fitness = [individual.get_evaluation() for individual in self.population]
        if print_mode:
            print("ITERATIONS, EVALUATIONS, BEST, MEAN, DEVIATION")
            print("0, " + str(self.evaluator.get_nb_evaluations()) + ", "
                  + format.format(self.best.get_evaluation()) + ", "
                  + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
        i = 0
        while self.evaluator.get_nb_evaluations() < max_evaluations:
            parents = self.selector.select(self.population, self.objective)
            offspring = parents[0].combine(parents[1], crossover_rate)
            for individual in offspring:
                individual.mutate(mutation_rate)
                individual.set_evaluation(self.evaluator.evaluate(individual))
                self.population.append(individual)
            if self.objective == Objective.MINIMIZE:
                java_collections.sort(self.population)
                if self.population[0].get_evaluation() < self.best.get_evaluation():
                    self.best = self.population[0].copy()
            else:
                java_collections.sort(self.population, reverse=True)
                if self.population[0].get_evaluation() > self.best.get_evaluation():
                    self.best = self.population[0].copy()
            for _ in offspring:
                self.population.pop(len(self.population) - 1)
            fitness = [individual.get_evaluation() for individual in self.population]
            if print_mode:
                print(str(i + 1) + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                      + format.format(self.best.get_evaluation()) + ", "
                      + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
            i += 1
        return self.best


def mean(values: list) -> float:
    """Returns the mean of the values provided as argument.

    :param values: The values to analyze.
    :return: The mean of the values provided as argument.
    """
    mean = 0
    if len(values) == 0:
        return 0
    for i in range(len(values)):
        mean += values[i]
    return mean / len(values)


def stdev(values: list) -> float:
    """Returns the standard deviation of the values provided as argument.

    :param values: The values to analyze.
    :return: The standard deviation of the values provided as argument.
    """
    m = mean(values)
    stdev = 0
    for i in range(len(values)):
        stdev += math.pow((values[i] - m), 2)
    if len(values) > 1:
        return math.sqrt(stdev / (len(values) - 1))
    else:
        return 0


# The Java version declares these as static methods of the class.
GeneticAlgorithm.mean = staticmethod(mean)
GeneticAlgorithm.stdev = staticmethod(stdev)
