"""Translation of ``mx.tec.meta.TournamentSelector``."""

from javacompat import collections as java_collections
from metah.ga.genetic_algorithm import Objective
from metah.individual import Individual
from metah.selector import Selector


class TournamentSelector(Selector):
    """Provides the methods to use a tournament selector to be used by a genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, tournament_size: int, seed: int):
        """Creates a new instance of ``TournamentSelector``.

        :param tournament_size: The size of the tournament.
        :param seed: The seed to initialize the random number generator to be used by this selector.
        """
        super().__init__(seed)
        self.tournament_size = tournament_size

    def select(self, population: list, objective: Objective) -> list:
        individuals = [None, None]
        for i in range(len(individuals)):
            tmp = []
            for _ in range(self.tournament_size):
                tmp.append(population[self.random.next_int(len(population))])
            if objective == Objective.MINIMIZE:
                java_collections.sort(tmp)
            else:
                java_collections.sort(tmp, reverse=True)
            individuals[i] = tmp[0].copy()
        return individuals
