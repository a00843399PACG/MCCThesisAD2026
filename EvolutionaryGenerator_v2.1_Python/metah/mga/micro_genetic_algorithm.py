"""Translation of ``mx.tec.meta.mga.MicroGeneticAlgorithm``."""

import math
from enum import Enum

from javacompat import DecimalFormat
from javacompat import collections as java_collections
from metah.evaluator import Evaluator
from metah.ga.genetic_algorithm import Objective
from metah.generator import Generator
from metah.individual import Individual
from metah.selector import Selector


class Type(Enum):
    """Defines the type of the micro genetic algorithm to use."""

    GENERATIONAL = "GENERATIONAL"
    STEADY_STATE = "STEADY_STATE"


class MicroGeneticAlgorithm:
    """Provides the methods to use a micro genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    MIN_FITNESS_DEVIATION = 0.00001

    Type = Type

    def __init__(self, evaluator: Evaluator, generator: Generator, selector: Selector, objective: Objective):
        """Creates a new instance of ``MicroGeneticAlgorithm``.

        :param evaluator: The evaluator of the performance of the individuals in this micro genetic algorithm.
        :param generator: The generator of the solutions in this micro genetic algorithm.
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

    def run(self, population_size: int, max_evaluations: int, type: Type, print_mode: bool) -> Individual:
        """Runs the micro genetic algorithm and returns the best solution found by the evolutionary process.

        :param population_size: The size of the population in this micro genetic algorithm.
        :param max_evaluations: The maximum number of calls to the evaluation function
            this genetic algorithm is allowed to execute.
        :param type: The type of the micro genetic algorithm to be used.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        self.population = []
        for _ in range(population_size):
            self.population.append(self.generator.generate())
        for individual in self.population:
            individual.set_evaluation(self.evaluator.evaluate(individual))
        if self.objective == Objective.MINIMIZE:
            java_collections.sort(self.population)
        else:
            java_collections.sort(self.population, reverse=True)
        self.best = self.population[0].copy()
        if type == Type.STEADY_STATE:
            return self._run_steady_state(max_evaluations, print_mode)
        else:
            return self._run_generational(max_evaluations, print_mode)

    def _run_generational(self, max_evaluations: int, print_mode: bool) -> Individual:
        """Runs the micro genetic algorithm.

        :param max_evaluations: The maximum number of calls to the evaluation function
            this genetic algorithm is allowed to execute.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best individual found by the evolutionary process.
        """
        format = DecimalFormat("0.0000")
        fitness = [individual.get_evaluation() for individual in self.population]
        if print_mode:
            # print("Generation, Iteration, Evaluations, Best.fitness, Average.fitness, StdDev.fitness")
            print("0, 0, 0, 0, 0 ,0")
            print("0, 0, " + str(self.evaluator.get_nb_evaluations()) + ", "
                  + format.format(self.best.get_evaluation()) + ", "
                  + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
        i = 0
        while self.evaluator.get_nb_evaluations() < max_evaluations:
            next_population = [self.population[0]]
            for j in range(1, len(self.population)):
                next_population.append(self.generator.generate())
            self.population = next_population
            for individual in self.population:
                individual.set_evaluation(self.evaluator.evaluate(individual))
            if print_mode:
                print(str(i + 1) + ", 0" + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                      + format.format(self.best.get_evaluation()) + ", "
                      + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
            j = 0
            while self.evaluator.get_nb_evaluations() < max_evaluations:
                next_population = []
                k = 0
                while len(next_population) < len(self.population):
                    parents = self.selector.select(self.population, Objective.MAXIMIZE)
                    offspring = parents[0].combine(parents[1], 1.0)
                    for individual in offspring:
                        individual.set_evaluation(self.evaluator.evaluate(individual))
                        next_population.append(individual)
                        fitness[k] = individual.get_evaluation()
                        k += 1
                self.population = next_population
                if self.objective == Objective.MINIMIZE:
                    java_collections.sort(self.population)
                    if self.population[0].get_evaluation() < self.best.get_evaluation():
                        self.best = self.population[0].copy()
                else:
                    java_collections.sort(self.population, reverse=True)
                    if self.population[0].get_evaluation() > self.best.get_evaluation():
                        self.best = self.population[0].copy()
                if print_mode:
                    print(str(i + 1) + ", " + str(j + 1) + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                          + format.format(self.best.get_evaluation()) + ", "
                          + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
                if stdev(fitness) < MicroGeneticAlgorithm.MIN_FITNESS_DEVIATION:
                    break
                j += 1
            i += 1
        return self.best

    def _run_steady_state(self, max_evaluations: int, print_mode: bool) -> Individual:
        """Runs the micro genetic algorithm.

        :param max_evaluations: The maximum number of calls to the evaluation function
            this genetic algorithm is allowed to execute.
        :param print_mode: A flag indicating if some data about the evolutionary process
            should be printed on screen.
        :return: The best solution found by the evolutionary process.
        """
        format = DecimalFormat("0.0000")
        fitness = [individual.get_evaluation() for individual in self.population]
        if print_mode:
            print("0, 0, 0, 0, 0 ,0")
            print("0, 0, " + str(self.evaluator.get_nb_evaluations()) + ", "
                  + format.format(self.best.get_evaluation()) + ", "
                  + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
        i = 0
        while self.evaluator.get_nb_evaluations() < max_evaluations:
            next_population = [self.population[0]]
            for j in range(1, len(self.population)):
                next_population.append(self.generator.generate())
            self.population = next_population
            for individual in self.population:
                individual.set_evaluation(self.evaluator.evaluate(individual))
            if print_mode:
                print(str(i + 1) + ", 0" + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                      + format.format(self.best.get_evaluation()) + ", "
                      + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
            j = 0
            while self.evaluator.get_nb_evaluations() < max_evaluations:
                parents = self.selector.select(self.population, Objective.MAXIMIZE)
                offspring = parents[0].combine(parents[1], 1.0)
                offspring[0].set_evaluation(self.evaluator.evaluate(offspring[0]))
                self.population.append(offspring[0])
                java_collections.sort(self.population)
                self.population.pop(len(self.population) - 1)
                if self.objective == Objective.MINIMIZE:
                    java_collections.sort(self.population)
                    if self.population[0].get_evaluation() < self.best.get_evaluation():
                        self.best = self.population[0].copy()
                else:
                    java_collections.sort(self.population, reverse=True)
                    if self.population[0].get_evaluation() > self.best.get_evaluation():
                        self.best = self.population[0].copy()
                k = 0
                for individual in self.population:
                    fitness[k] = individual.get_evaluation()
                    k += 1
                if print_mode:
                    print(str(i + 1) + ", " + str(j + 1) + ", " + str(self.evaluator.get_nb_evaluations()) + ", "
                          + format.format(self.best.get_evaluation()) + ", "
                          + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)))
                if stdev(fitness) < MicroGeneticAlgorithm.MIN_FITNESS_DEVIATION:
                    break
                j += 1
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


MicroGeneticAlgorithm.mean = staticmethod(mean)
MicroGeneticAlgorithm.stdev = staticmethod(stdev)
