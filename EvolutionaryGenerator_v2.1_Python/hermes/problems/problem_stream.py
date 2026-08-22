"""Translation of ``mx.tec.hermes.problems.ProblemStream``."""

import os
import sys

from javacompat import Random


class ProblemStream:
    """Provides the methods to create and handle problem streams supported by HERMES.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, path: str, seed: int):
        """Creates a new instance of ``ProblemStream``.

        :param path: The path where the instances are contained.
        :param seed: The seed to initialize the random number generator.
        """
        if not os.path.exists(path) or not os.path.isdir(path):
            print("The path '" + path + "'is not a valid directory.", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        self.random = Random(seed)
        tmp = sorted(os.listdir(path))
        self.file_names = []
        for file_name in tmp:
            self.file_names.append(path + "/" + file_name)

    def next(self) -> str:
        """Returns the next filename in this stream.

        :return: The next filename in this stream.
        """
        index = self.random.next_int(len(self.file_names))
        return self.file_names[index]
