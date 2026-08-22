"""Translation of ``mx.tec.meta.Selector``."""

from abc import ABC, abstractmethod

from javacompat import Random
from metah.individual import Individual


class Selector(ABC):
    """Defines the methods to create and handle selection operators to be used by a genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, seed: int):
        """Creates a new instance of ``SelectionOperator``.

        :param seed: The seed for the random number generator to be used by this selector.
        """
        #: The random number generator to be used in all random operations within this selector.
        self.random = Random(seed)

    @abstractmethod
    def select(self, population: list, objective) -> list:
        """Selects the solutions to be used for crossover.

        :param population: The solutions contained in the current population.
        :param objective: The objective of the evolutionary process regarding the
            objective function (maximize or minimize).
        :return: The solutions to be used for crossover.
        """
