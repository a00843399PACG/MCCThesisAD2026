"""Translation of ``mx.tec.hermes.problems.kp.generator.KPIndividual``."""

import math

from hermes.problems.kp.item import Item
from hermes.problems.kp.kp import KP
from javacompat import BitSet
from metah.individual import Individual


class KPIndividual(Individual):
    """Provides the methods to create and use individuals that encode knapsack problems
    that can be evolved by a genetic algorithm.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    # These four values are static in the Java version: every individual created
    # within the same run shares the same encoding.
    max_weight_per_item = 20
    max_profit_per_item = 50
    nb_items = 10
    capacity = 20
    nb_bits = 10 * int(math.ceil(math.log10(20) / math.log10(2)) + math.ceil(math.log10(50) / math.log10(2)))

    @classmethod
    def set_capacity(cls, capacity: int) -> None:
        """Sets the capacity of the knapsack in the resulting knapsack problem.

        :param capacity: The capacity of the knapsack in the resulting knapsack problem.
        """
        KPIndividual.capacity = capacity

    @classmethod
    def set_max_weight_per_item(cls, max_weight_per_item: int) -> None:
        """Sets the maximum weight per item in the resulting knapsack problem.

        :param max_weight_per_item: The maximum weight per item in the resulting knapsack problem.
        """
        KPIndividual.max_weight_per_item = max_weight_per_item
        KPIndividual.nb_bits = KPIndividual.nb_items * int(
            math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2))
            + math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))

    @classmethod
    def set_max_profit_per_item(cls, max_profit_per_item: int) -> None:
        """Sets the maximum profit per item in the resulting knapsack problem.

        :param max_profit_per_item: The maximum profit per item in the resulting knapsack problem.
        """
        KPIndividual.max_profit_per_item = max_profit_per_item
        KPIndividual.nb_bits = KPIndividual.nb_items * int(
            math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2))
            + math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))

    @classmethod
    def set_nb_items(cls, nb_items: int) -> None:
        """Sets the number of items in the resulting knapsack problem.

        :param nb_items: The number of items in the resulting knapsack problem.
        """
        KPIndividual.nb_items = nb_items
        KPIndividual.nb_bits = KPIndividual.nb_items * int(
            math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2))
            + math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))

    def __init__(self, seed: int = None, individual: "KPIndividual" = None):
        """Mirrors the two constructors available in the Java version.

        ``KPIndividual(seed)`` creates a new random individual while
        ``KPIndividual(individual=...)`` is the (private) copy constructor.

        :param seed: The seed to initialize the random number generator.
        :param individual: The instance of ``KPIndividual`` to copy.
        """
        if individual is not None:
            super().__init__(individual.get_evaluation(), individual.random.next_long())
            self.chromosome = individual.chromosome.clone()
        else:
            super().__init__(0, seed)
            self.chromosome = BitSet(KPIndividual.nb_bits)
            for i in range(KPIndividual.nb_bits):
                self.chromosome.set(i, self.random.next_boolean())

    def combine(self, individual: Individual, crossover_rate: float) -> list:
        offspring = [self, individual]
        crossover_point = self.random.next_int(KPIndividual.nb_bits)
        tmp = offspring[1].chromosome.clone()
        for i in range(crossover_point):
            offspring[1].chromosome.set(i, offspring[0].chromosome.get(i))
        for i in range(crossover_point):
            offspring[0].chromosome.set(i, tmp.get(i))
        return offspring

    def mutate(self, mutation_rate: float) -> None:
        for i in range(KPIndividual.nb_bits):
            if self.random.next_double() < mutation_rate:
                self.chromosome.flip(i)

    def copy(self) -> Individual:
        return KPIndividual(individual=self)

    def to_kp(self) -> KP:
        """Returns a new instance of ``KP`` based on the information contained in this individual.

        :return: A new instance of ``KP``.
        """
        items = []
        bits_block = int(math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2))
                         + math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))
        bits_weight = int(math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2)))
        bits_profit = int(math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))
        for i in range(KPIndividual.nb_items):
            from_index = i * bits_block
            bits = self.chromosome.get(from_index, from_index + bits_weight)
            weight = KPIndividual.to_integer(bits)
            from_index = from_index + bits_weight
            bits = self.chromosome.get(from_index, from_index + bits_profit)
            profit = KPIndividual.to_integer(bits)
            # hack, borrar!  ["hack, delete!" -- commented out block left by the author
            # in the Java original, kept verbatim.]
            #
            # profit = int((profit + 1) / 128.0 * 100)
            # if profit == 0 or profit > 100:
            #     print("Out of range generation.")
            #     print(profit)
            #     sys.exit(1)
            #
            items.append(Item(i, profit, weight))
        return KP(items, KPIndividual.capacity)

    def __str__(self) -> str:
        string = []
        bits_block = int(math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2))
                         + math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))
        bits_weight = int(math.ceil(math.log10(KPIndividual.max_weight_per_item) / math.log10(2)))
        bits_profit = int(math.ceil(math.log10(KPIndividual.max_profit_per_item) / math.log10(2)))
        for i in range(KPIndividual.nb_items):
            from_index = i * bits_block
            bits = self.chromosome.get(from_index, from_index + bits_weight)
            tmp_string = []
            for j in range(bits_weight):
                tmp_string.append("1" if bits.get(j) else "0")
            string.append("".join(reversed(tmp_string)) + " (" + str(KPIndividual.to_integer(bits)) + ") ")
            from_index = from_index + bits_weight
            bits = self.chromosome.get(from_index, from_index + bits_profit)
            tmp_string = []
            for j in range(bits_profit):
                # The Java version reads bits.get(j + from) here, which is out of the
                # range of the extracted bits.  It is kept as it is on purpose.
                tmp_string.append("1" if bits.get(j + from_index) else "0")
            string.append("".join(reversed(tmp_string)) + " (" + str(KPIndividual.to_integer(bits)) + ") ")
        return "".join(string)

    @staticmethod
    def to_integer(bits: BitSet) -> int:
        """Returns the value as integer of the bits provided as argument.

        :param bits: The bits whose integer value is required.
        :return: The value as integer of the bits provided as argument.
        """
        value = 0
        i = bits.next_set_bit(0)
        while i >= 0:
            value += int(math.pow(2, i))
            i = bits.next_set_bit(i + 1)
        return value + 1
