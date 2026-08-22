"""Small compatibility layer that reproduces the behaviour of the pieces of the
Java runtime the original generator depends on.

It exists so that the Python translation produces exactly the same results as the
Java version when both are given the same seed.

:author: Paola Azeneth Castillo Gutiérrez
"""

from javacompat.bitset import BitSet
from javacompat.decimal_format import DecimalFormat
from javacompat.java_random import (
    DOUBLE_MAX_VALUE,
    DOUBLE_MIN_VALUE,
    Random,
)

__all__ = ["BitSet", "DecimalFormat", "Random", "DOUBLE_MAX_VALUE", "DOUBLE_MIN_VALUE"]

#: Version of this project.  It matches the version of the Java original this
#: translation reproduces (see README.md, section "Authorship and version").
__version__ = "2.1.0"
