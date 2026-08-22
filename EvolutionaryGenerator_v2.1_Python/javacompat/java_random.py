"""Faithful port of ``java.util.Random`` (and of the ``RandomGenerator`` default
methods used by the original code).

The Java version of the generator relies on ``java.util.Random`` seeded with an
explicit seed in order to make the experiments reproducible.  Python's ``random``
module uses a completely different engine (Mersenne Twister), so reproducing the
exact same stream of numbers requires re-implementing Java's 48-bit linear
congruential generator.  This class does exactly that: given the same seed, it
produces the very same sequence as the Java original.

:author: Paola Azeneth Castillo Gutiérrez
"""

import time

_INT_MASK = 0xFFFFFFFF
_LONG_MASK = 0xFFFFFFFFFFFFFFFF

#: ``Double.MIN_VALUE`` in Java is the smallest *positive* value, not the most
#: negative one.  The original code relies on it (see ``Statistical.max``).
DOUBLE_MIN_VALUE = 4.9e-324
#: ``Double.MAX_VALUE``.
DOUBLE_MAX_VALUE = 1.7976931348623157e308


def to_signed_int(value: int) -> int:
    """Returns the value provided as argument as a 32 bits signed integer."""
    value &= _INT_MASK
    return value - (1 << 32) if value & 0x80000000 else value


def to_signed_long(value: int) -> int:
    """Returns the value provided as argument as a 64 bits signed integer."""
    value &= _LONG_MASK
    return value - (1 << 64) if value & 0x8000000000000000 else value


def next_down(value: float) -> float:
    """Equivalent of ``Math.nextDown(double)``."""
    return math_next_after(value, float("-inf"))


def math_next_after(start: float, direction: float) -> float:
    from math import nextafter

    return nextafter(start, direction)


class Random:
    """Provides the same pseudo random number generator used by ``java.util.Random``."""

    _MULTIPLIER = 0x5DEECE66D
    _ADDEND = 0xB
    _MASK = (1 << 48) - 1

    def __init__(self, seed: int = None):
        """Creates a new instance of ``Random``.

        :param seed: The seed to initialize the random number generator.  When no
            seed is provided a time based one is used, as Java does.
        """
        if seed is None:
            seed = time.time_ns()
        self.set_seed(seed)

    def set_seed(self, seed: int) -> None:
        """Sets the seed of this random number generator."""
        self._seed = (to_signed_long(seed) ^ self._MULTIPLIER) & self._MASK

    def _next(self, bits: int) -> int:
        """Returns the next pseudo random number of ``bits`` bits."""
        self._seed = (self._seed * self._MULTIPLIER + self._ADDEND) & self._MASK
        return to_signed_int(self._seed >> (48 - bits))

    def next_int(self, a: int = None, b: int = None) -> int:
        """Mirrors the three ``nextInt`` overloads available in Java.

        ``next_int()`` returns any integer, ``next_int(bound)`` returns a value in
        [0, bound) and ``next_int(origin, bound)`` returns a value in
        [origin, bound).  Please note that ``next_int(0, n)`` and ``next_int(n)``
        do **not** produce the same value: they consume the underlying stream in a
        different way, exactly as they do in Java.
        """
        if a is None:
            return self._next(32)
        if b is None:
            return self._next_int_bound(a)
        return self._bounded_next_int(a, b)

    def _next_int_bound(self, bound: int) -> int:
        """Equivalent of ``Random.nextInt(int)``."""
        if bound <= 0:
            raise ValueError("bound must be positive")
        r = self._next(31)
        m = bound - 1
        if (bound & m) == 0:
            # The bound is a power of two.
            return to_signed_int((bound * r) >> 31)
        u = r
        r = u % bound
        while to_signed_int(u - r + m) < 0:
            u = self._next(31)
            r = u % bound
        return r

    def _bounded_next_int(self, origin: int, bound: int) -> int:
        """Equivalent of ``RandomSupport.boundedNextInt(rng, origin, bound)``."""
        r = self._next(32)
        if origin < bound:
            n = bound - origin
            m = n - 1
            if (n & m) == 0:
                r = (r & m) + origin
            elif n > 0:
                u = (r & _INT_MASK) >> 1
                r = u % n
                while to_signed_int(u + m - r) < 0:
                    u = (self._next(32) & _INT_MASK) >> 1
                    r = u % n
                r += origin
            else:
                while r < origin or r >= bound:
                    r = self._next(32)
        return r

    def next_long(self) -> int:
        """Equivalent of ``Random.nextLong()``."""
        return to_signed_long((self._next(32) << 32) + self._next(32))

    def next_boolean(self) -> bool:
        """Equivalent of ``Random.nextBoolean()``."""
        return self._next(1) != 0

    def next_double(self, origin: float = None, bound: float = None) -> float:
        """Mirrors the ``nextDouble`` overloads available in Java."""
        if origin is None:
            return ((self._next(26) << 27) + self._next(27)) * (2.0 ** -53)
        return self._bounded_next_double(origin, bound)

    def _bounded_next_double(self, origin: float, bound: float) -> float:
        """Equivalent of ``RandomSupport.boundedNextDouble(rng, origin, bound)``."""
        r = self.next_double()
        if origin < bound:
            if bound - origin < float("inf"):
                r = r * (bound - origin) + origin
            else:
                half_origin = 0.5 * origin
                r = (r * (0.5 * bound - half_origin) + half_origin) * 2.0
            if r >= bound:
                r = next_down(bound)
        return r
