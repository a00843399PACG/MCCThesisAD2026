"""Translation of ``mx.tec.hermes.problems.kp.generator.KPGenerator``."""

from hermes.problems.kp.generator.kp_individual import KPIndividual
from javacompat import Random
from metah.generator import Generator
from metah.individual import Individual


class KPGenerator(Generator):
    """Provides the methods to create knapsack problems.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, seed: int):
        """Creates a new instance of ``KPGenerator``.

        :param seed: The seed to initialize the random number generator.
        """
        self.random = Random(seed)

    def generate(self) -> Individual:
        return KPIndividual(self.random.next_long())
