"""Translation of the ``mx.tec.hermes.exceptions`` package."""


class NoSuchFeatureException(Exception):
    """Defines an exception for handling events where a feature is not defined for the problem.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, message: str):
        """Creates a new instance of ``NoSuchFeatureException``.

        :param message: The message to describe the exception.
        """
        super().__init__(message)


class NoSuchHeuristicException(Exception):
    """Defines an exception for handling events where a heuristic is not defined for the problem.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, message: str):
        """Creates a new instance of ``NoSuchHeuristicException``.

        :param message: The message to describe the exception.
        """
        super().__init__(message)


__all__ = ["NoSuchFeatureException", "NoSuchHeuristicException"]
