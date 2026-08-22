"""Faithful port of the ``java.util.Collections`` operations used by the generator.

:author: Paola Azeneth Castillo Gutiérrez
"""

from functools import cmp_to_key


def sort(items: list, reverse: bool = False) -> None:
    """Sorts a list in place the way ``Collections.sort`` does.

    :param items: The list of ``Comparable`` elements to sort.
    :param reverse: ``True`` to sort with ``Collections.reverseOrder()``.

    Both Java's and Python's sorting algorithms are stable, so elements that
    compare as equal keep their relative order in either language.
    """
    if reverse:
        items.sort(key=cmp_to_key(lambda a, b: b.compare_to(a)))
    else:
        items.sort(key=cmp_to_key(lambda a, b: a.compare_to(b)))


def shuffle(items: list, random) -> None:
    """Shuffles a list in place the way ``Collections.shuffle(List, Random)`` does.

    :param items: The list to shuffle.
    :param random: The random number generator to be used in the process.
    """
    for i in range(len(items), 1, -1):
        j = random.next_int(i)
        items[i - 1], items[j] = items[j], items[i - 1]
