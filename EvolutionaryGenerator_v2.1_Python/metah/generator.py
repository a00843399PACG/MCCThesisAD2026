"""Translation of ``mx.tec.meta.Generator``."""

from abc import ABC, abstractmethod

from metah.individual import Individual


class Generator(ABC):
    """Defines the methods that need to be implemented by a generator to be used by the meta heuristics.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    @abstractmethod
    def generate(self) -> Individual:
        """Generates a new random instance of ``Solution``.

        :return: A random solution.
        """
