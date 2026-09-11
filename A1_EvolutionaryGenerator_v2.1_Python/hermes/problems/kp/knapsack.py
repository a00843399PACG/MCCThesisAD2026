"""Translation of ``mx.tec.hermes.problems.kp.Knapsack``."""

from hermes.problems.kp.item import Item


class Knapsack:
    """Provides the methods to create and use knapsacks for the knapsack problem.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    def __init__(self, capacity: int):
        """Creates a new instance of ``Knapsack``.

        :param capacity: The capacity of this knapsack.
        """
        self.capacity = capacity
        self.s_profit = 0.0
        self.p_profit = 1.0
        self.items = []

    def get_capacity(self) -> int:
        """Returns the current capacity of this knapsack.

        :return: The current capacity of this knapsack.
        """
        return self.capacity

    def get_sum_of_profit(self) -> float:
        """Returns the current sum of profits in this knapsack.

        :return: The current sum of profits in this knapsack.
        """
        return self.s_profit

    def get_product_of_profit(self) -> float:
        """Returns the current product of profits in this knapsack.

        :return: The current product of profits in this knapsack.
        """
        return self.p_profit

    def get_solution(self, nb_items: int) -> list:
        """Returns the current solution as a vector of zeros and ones.

        :param nb_items: The number of items in the problem this knapsack belongs to.
        :return: The current solution to the problem this knapsack belongs to.
        """
        solution = [0] * nb_items
        for item in self.items:
            solution[item.get_id()] = 1
        return solution

    def can_pack(self, item: Item) -> bool:
        """Revises if the item provided can be packed in this knapsack.

        :param item: The item to be packed.
        :return: ``True`` if the item can be packed in this knapsack, ``False`` otherwise.
        """
        return item.get_weight() <= self.get_capacity()

    def pack(self, item: Item) -> bool:
        """Packs an item into this knapsack.

        :param item: The item to pack.
        :return: ``True`` if the item was successfully packed, ``False`` otherwise.
        """
        if item.get_weight() <= self.capacity:
            self.items.append(item)
            self.capacity -= item.get_weight()
            self.s_profit += item.get_profit()
            self.p_profit *= item.get_profit()
            return True
        return False

    def copy(self) -> "Knapsack":
        """Clones this knapsack.

        :return: A deep copy of this knapsack.
        """
        tmp = Knapsack(self.capacity)
        for item in self.items:
            tmp.pack(item)
        return tmp

    def __str__(self) -> str:
        """Returns the string representation of this knapsack.

        :return: The string representation of this knapsack.
        """
        string = []
        for item in self.items:
            string.append(str(item) + " ")
        return "".join(string).strip()
