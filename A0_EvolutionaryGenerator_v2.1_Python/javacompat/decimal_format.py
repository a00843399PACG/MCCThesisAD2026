"""Faithful port of the subset of ``java.text.DecimalFormat`` used by the generator.

The original code formats its reports with the patterns ``000``, ``0.000``,
``0.0000`` and ``00.0000E00``.  Java rounds using HALF_EVEN over the exact decimal
value of the double, which is what ``decimal.Decimal`` does here.

:author: Paola Azeneth Castillo Gutiérrez
"""

from decimal import Decimal, ROUND_HALF_EVEN
import math

NAN = "NaN"
INFINITY = "∞"


class DecimalFormat:
    """Provides the methods to format numbers the way ``DecimalFormat`` does."""

    def __init__(self, pattern: str):
        """Creates a new instance of ``DecimalFormat``.

        :param pattern: The pattern that describes the format of the numbers.
        """
        self.pattern = pattern
        mantissa, _, exponent = pattern.partition("E")
        integer, _, fraction = mantissa.partition(".")
        self._min_integer_digits = integer.count("0")
        self._min_fraction_digits = fraction.count("0")
        self._max_fraction_digits = len(fraction)
        self._exponent_digits = len(exponent)
        self._scientific = bool(exponent)

    def format(self, value: float) -> str:
        """Returns the string representation of the value provided as argument."""
        if isinstance(value, Decimal):
            value = float(value)
        if math.isnan(value):
            return NAN
        if math.isinf(value):
            return ("-" if value < 0 else "") + INFINITY
        if self._scientific:
            return self._format_scientific(value)
        return self._format_plain(value)

    def _format_plain(self, value: float) -> str:
        quantum = Decimal(1).scaleb(-self._max_fraction_digits)
        number = Decimal(value).quantize(quantum, rounding=ROUND_HALF_EVEN)
        sign = "-" if number.is_signed() and number != 0 else ""
        digits = "{:f}".format(abs(number))
        integer, _, fraction = digits.partition(".")
        integer = integer.rjust(self._min_integer_digits, "0")
        fraction = fraction.ljust(self._min_fraction_digits, "0")[: self._max_fraction_digits]
        return sign + integer + ("." + fraction if fraction else "")

    def _format_scientific(self, value: float) -> str:
        """Formats a number in scientific notation.

        When the pattern uses the same number of minimum and maximum integer
        digits (the case of ``00.0000E00``), Java shifts the exponent so that the
        mantissa always shows exactly that number of integer digits.
        """
        number = Decimal(value)
        integer_digits = self._min_integer_digits
        quantum = Decimal(1).scaleb(-self._max_fraction_digits)
        if number == 0:
            exponent = 0
            mantissa = Decimal(0).quantize(quantum, rounding=ROUND_HALF_EVEN)
        else:
            exponent = number.adjusted() - (integer_digits - 1)
            mantissa = number.scaleb(-exponent).quantize(quantum, rounding=ROUND_HALF_EVEN)
            # The rounding may push the mantissa out of its range of digits.
            if abs(mantissa) >= Decimal(10) ** integer_digits:
                exponent += 1
                mantissa = number.scaleb(-exponent).quantize(quantum, rounding=ROUND_HALF_EVEN)
        sign = "-" if mantissa.is_signed() and mantissa != 0 else ""
        digits = "{:f}".format(abs(mantissa))
        integer, _, fraction = digits.partition(".")
        integer = integer.rjust(integer_digits, "0")
        fraction = fraction.ljust(self._min_fraction_digits, "0")[: self._max_fraction_digits]
        exponent_sign = "-" if exponent < 0 else ""
        return "%s%s%sE%s%s" % (
            sign,
            integer,
            ("." + fraction if fraction else ""),
            exponent_sign,
            str(abs(exponent)).rjust(self._exponent_digits, "0"),
        )

    def __str__(self) -> str:
        return self.pattern
