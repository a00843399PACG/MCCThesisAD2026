"""Translation of the ``mx.tec.meta`` package (the ``MetaH`` NetBeans project).

It contains the meta heuristics (genetic algorithm, micro genetic algorithm,
evolutionary strategy and genetic programming) and the abstract classes that any
problem must implement in order to be optimized by them.
"""

from metah.evaluator import Evaluator
from metah.generator import Generator
from metah.individual import Individual
from metah.selector import Selector
from metah.tournament_selector import TournamentSelector

__all__ = ["Evaluator", "Generator", "Individual", "Selector", "TournamentSelector"]

#: Version of this project.  It matches the version of the Java original this
#: translation reproduces (see README.md, section "Authorship and version").
__version__ = "2.1.0"
