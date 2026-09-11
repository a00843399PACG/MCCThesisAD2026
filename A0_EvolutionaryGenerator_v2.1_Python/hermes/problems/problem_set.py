"""Translation of ``mx.tec.hermes.problems.ProblemSet``."""

import math
import os
import sys
from enum import Enum

from javacompat import Random
from javacompat import collections as java_collections


class Subset(Enum):
    """Defines the fraction of the set that will be used according to the purpose of the instances."""

    #: A subset of problems is used for training purposes.
    TRAIN = "TRAIN"
    #: A subset of instances is used for testing purposes.
    TEST = "TEST"


class ProblemSet:
    """Provides the methods to create and handle problem sets supported by HERMES.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    Subset = Subset

    def __init__(self, path: str, type: Subset = Subset.TEST, proportion: float = 1.0, seed: int = 0):
        """Creates a new instance of ``ProblemSet``.

        The Java version provides two constructors: ``ProblemSet(path)`` delegates to
        ``ProblemSet(path, Subset.TEST, 1.0, 0)``, which is what the default values
        of the arguments do here.

        :param path: The path where the instances are contained.
        :param type: The type of set to be created (training or test).
        :param proportion: The proportion of the instances used for training.
        :param seed: The seed to initialize the random number generator.
        """
        if not os.path.exists(path) or not os.path.isdir(path):
            print("The path '" + path + "' is not a valid directory.", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        tmp = sorted(os.listdir(path))
        self.file_names = []
        for file_name in tmp:
            self.file_names.append(path + "/" + file_name)
        if proportion != 1.0:
            n = int(math.ceil(proportion * len(self.file_names)))
            java_collections.shuffle(self.file_names, Random(seed))
            if type == Subset.TRAIN:
                self.file_names = self.file_names[0:n]
            else:
                self.file_names = self.file_names[n:len(self.file_names)]

    def get_size(self) -> int:
        """Returns the size of this problem set.

        :return: The size of this problem set.
        """
        return len(self.file_names)

    def get_files(self) -> list:
        """Returns the names of the files in this problem set.

        :return: The names of the files in this problem set.
        """
        return self.file_names
