"""Translation of ``mx.tec.meta.gp.GPGenerator``."""

from javacompat import Random
from metah.generator import Generator
from metah.gp.gp_individual import GPIndividual
from metah.individual import Individual


class GPGenerator(Generator):
    """Defines the methods to generate individuals within genetic programing.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 1.0
    """

    MAXDEPTH = 3

    def __init__(self, seed: int):
        """Creates a new instance of ``GPGenerator``.

        :param seed: The seed to initialize the random number generator.
        """
        self.random = Random(seed)

    def generate(self) -> Individual:
        return GPIndividual(GPGenerator.MAXDEPTH, self.random.next_long())
