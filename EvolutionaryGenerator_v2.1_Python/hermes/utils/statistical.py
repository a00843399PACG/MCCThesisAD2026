"""Translation of ``mx.tec.hermes.utils.Statistical``."""

import math

from javacompat import DOUBLE_MAX_VALUE, DOUBLE_MIN_VALUE

NAN = float("nan")


def mean(values: list) -> float:
    """Returns the mean of the values provided as argument.

    :param values: The values to analyze.
    :return: The mean of the values provided as argument.
    """
    mean = 0
    if len(values) == 0:
        return 0
    for i in range(len(values)):
        mean += values[i]
    return mean / len(values)


def stdev(values: list) -> float:
    """Returns the standard deviation of the values provided as argument.

    :param values: The values to analyze.
    :return: The standard deviation of the values provided as argument.
    """
    m = mean(values)
    stdev = 0
    for i in range(len(values)):
        stdev += math.pow((values[i] - m), 2)
    if len(values) > 1:
        return math.sqrt(stdev / (len(values) - 1))
    else:
        return 0


def median(values: list) -> float:
    """Returns the median of a values provided as argument.

    :param values: The values to analyze.
    :return: The median of the values provided as argument.
    """
    #
    # Safety check.
    #
    if len(values) == 0:
        return NAN
    ordered_values = sort(values)
    if len(ordered_values) % 2 == 1:
        median = ordered_values[int(len(ordered_values) / 2)]
    else:
        median = (ordered_values[int(len(ordered_values) / 2) - 1]
                  + ordered_values[int(len(ordered_values) / 2)]) / 2
    return median


def correlation(x: list, y: list) -> float:
    """Returns the correlation coefficient of the values provided as argument.

    :param x: The values to analyze.
    :param y: The values to analyze.
    :return: The correlation coefficient of the values provided as argument.
    """
    if len(x) != len(y):
        return NAN
    a = 0
    b = 0
    c = 0
    d = 0
    e = 0
    for i in range(len(x)):
        a += x[i] * y[i]
        b += x[i]
        c += y[i]
        d += math.pow(x[i], 2)
        e += math.pow(y[i], 2)
    return ((len(x) * a - b * c)
            / (math.sqrt(len(x) * d - math.pow(b, 2)) * math.sqrt(len(x) * e - math.pow(c, 2))))


def lower_quartile(values: list) -> float:
    """Returns the lower quartile of the values provided as argument.

    :param values: The values to analyze.
    :return: The lower quartile of the values provided as argument.
    """
    #
    # Safety check.
    #
    if len(values) == 0:
        return NAN
    return median(_lower_sub_set(values))


def upper_quartile(values: list) -> float:
    """Returns the upper quartile of the values provided as argument.

    :param values: The values to analyze.
    :return: The upper quartile of the values provided as argument.
    """
    #
    # Safety check.
    #
    if len(values) == 0:
        return NAN
    return median(_upper_sub_set(values))


def sort(values: list) -> list:
    """Sorts the values provided as argument.

    :param values: The values to sort.
    :return: The values sorted in ascending order.
    """
    ordered_values = list(values)
    n = len(values)
    while True:
        swapped = False
        for i in range(n - 1):
            if ordered_values[i] > ordered_values[i + 1]:
                ordered_values[i], ordered_values[i + 1] = ordered_values[i + 1], ordered_values[i]
                swapped = True
        n = n - 1
        if not swapped:
            break
    return ordered_values


def max(values: list) -> float:
    """Returns the maximum value in the values provided as argument.

    :param values: The values to analyze.
    :return: The maximum value in the values provided as argument.

    Please note that the accumulator starts at ``Double.MIN_VALUE``, which in Java
    is the smallest *positive* double and not the most negative one.  The original
    code therefore returns 4.9E-324 when every value is negative.  The behaviour is
    preserved here on purpose so both versions produce identical results.
    """
    max_value = DOUBLE_MIN_VALUE
    #
    # Safety check.
    #
    if len(values) == 0:
        return NAN
    for i in range(len(values)):
        if values[i] > max_value:
            max_value = values[i]
    return max_value


def min(values: list) -> float:
    """Returns the minimum value in the values provided as argument.

    :param values: The values to analyze.
    :return: The minimum value in the values provided as argument.
    """
    min_value = DOUBLE_MAX_VALUE
    #
    # Safety check.
    #
    if len(values) == 0:
        return NAN
    for i in range(len(values)):
        if values[i] < min_value:
            min_value = values[i]
    return min_value


def range_(values: list) -> float:
    """Returns the range of the values provided as argument.

    :param values: The values to analyze.
    :return: The range of the values provided as argument.
    """
    return max(values) - min(values)


def _lower_sub_set(values: list) -> list:
    """Generates a set that contains only those values that are less or equal than
    the mean of the values provided as argument.

    :param values: The values to analyze.
    :return: The values that are less or equal than the mean of the values provided as argument.
    """
    median_value = median(values)
    ordered_values = sort(values)
    sub_set = [0.0] * (int(len(ordered_values) / 2) + 1)
    i = 0
    while ordered_values[i] < median_value:
        sub_set[i] = ordered_values[i]
        i += 1
    sub_set[i] = median_value
    return sub_set


def _upper_sub_set(values: list) -> list:
    """Generates a set that contains only those values that are greater or equal than
    the mean of the values provided as argument.

    :param values: The values to analyze.
    :return: The values that are greater or equal than the mean of the values provided as argument.
    """
    j = 0
    median_value = median(values)
    ordered_values = sort(values)
    sub_set = [0.0] * (int(len(ordered_values) / 2) + 1)
    if len(ordered_values) % 2 == 0:
        sub_set[j] = median_value
        j += 1
    for i in range(int(len(ordered_values) / 2), len(ordered_values)):
        sub_set[j] = ordered_values[i]
        j += 1
    return sub_set


class Statistical:
    """Provides a small set of statistical functions.

    The Java class only contains static methods, so the module level functions above
    are the actual translation.  This class is kept so that the call sites read the
    same way they do in the Java version (``Statistical.max(values)``).

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@gmail.com)
    :original version: 1.0
    """

    mean = staticmethod(mean)
    stdev = staticmethod(stdev)
    median = staticmethod(median)
    correlation = staticmethod(correlation)
    lower_quartile = staticmethod(lower_quartile)
    upper_quartile = staticmethod(upper_quartile)
    sort = staticmethod(sort)
    max = staticmethod(max)
    min = staticmethod(min)
    range = staticmethod(range_)
