"""Translation of ``Utils.Statistical``.

The ``Utils`` NetBeans project holds a copy of this class that is identical to
``mx.tec.hermes.utils.Statistical`` except for the package it belongs to, so the
translation simply re-exports it.

:author: Paola Azeneth Castillo Gutiérrez
"""

from hermes.utils.statistical import (  # noqa: F401
    Statistical,
    correlation,
    lower_quartile,
    max,
    mean,
    median,
    min,
    range_,
    sort,
    stdev,
    upper_quartile,
)

__all__ = ["Statistical", "correlation", "lower_quartile", "max", "mean", "median", "min",
           "range_", "sort", "stdev", "upper_quartile"]
