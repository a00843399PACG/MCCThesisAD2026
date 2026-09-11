"""Faithful port of the subset of ``java.util.BitSet`` used by the generator.

A Java ``BitSet`` grows on demand and every bit that has never been set reads as
``false``.  It is modelled here with an arbitrary precision Python integer, which
provides exactly the same semantics.

:author: Paola Azeneth Castillo Gutiérrez
"""


class BitSet:
    """Provides the methods to create and use sets of bits."""

    def __init__(self, nbits: int = 64):
        """Creates a new instance of ``BitSet``.

        :param nbits: The initial capacity of this set of bits.  As in Java, it is
            only a hint: the set grows as needed.
        """
        if nbits < 0:
            raise ValueError("nbits < 0: %d" % nbits)
        self._bits = 0

    def get(self, from_index: int, to_index: int = None):
        """Mirrors the two ``get`` overloads available in Java.

        ``get(index)`` returns the value of one bit while ``get(from, to)`` returns
        a **new** set of bits with the bits in [from, to), where the bit ``from``
        becomes the bit 0 of the resulting set.
        """
        if to_index is None:
            if from_index < 0:
                raise ValueError("fromIndex < 0: %d" % from_index)
            return (self._bits >> from_index) & 1 == 1
        if from_index < 0 or to_index < from_index:
            raise ValueError("invalid range: [%d, %d)" % (from_index, to_index))
        bits = BitSet()
        bits._bits = (self._bits >> from_index) & ((1 << (to_index - from_index)) - 1)
        return bits

    def set(self, index: int, value: bool = True) -> None:
        """Sets the bit at the position provided as argument to the given value."""
        if index < 0:
            raise ValueError("index < 0: %d" % index)
        if value:
            self._bits |= 1 << index
        else:
            self._bits &= ~(1 << index)

    def clear(self, index: int) -> None:
        """Sets the bit at the position provided as argument to ``false``."""
        self.set(index, False)

    def flip(self, index: int) -> None:
        """Flips the bit at the position provided as argument."""
        if index < 0:
            raise ValueError("index < 0: %d" % index)
        self._bits ^= 1 << index

    def next_set_bit(self, from_index: int) -> int:
        """Returns the index of the first bit set from the position provided.

        :return: The index of the first bit set, -1 if there is no such bit.
        """
        if from_index < 0:
            raise ValueError("fromIndex < 0: %d" % from_index)
        bits = self._bits >> from_index
        if bits == 0:
            return -1
        return from_index + (bits & -bits).bit_length() - 1

    def length(self) -> int:
        """Returns the index of the highest bit set plus one."""
        return self._bits.bit_length()

    def cardinality(self) -> int:
        """Returns the number of bits set in this set of bits."""
        return bin(self._bits).count("1")

    def clone(self) -> "BitSet":
        """Returns a copy of this set of bits."""
        bits = BitSet()
        bits._bits = self._bits
        return bits

    def __eq__(self, other) -> bool:
        return isinstance(other, BitSet) and self._bits == other._bits

    def __hash__(self) -> int:
        return hash(self._bits)

    def __str__(self) -> str:
        indices = [str(i) for i in range(self.length()) if self.get(i)]
        return "{" + ", ".join(indices) + "}"
