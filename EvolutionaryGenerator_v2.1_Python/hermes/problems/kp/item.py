"""Translation of ``mx.tec.hermes.problems.kp.Item``."""


class Item:
    """Provides the methods to create and use items for the knapsack problem.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0

    Please note that this class deliberately does not define ``__eq__``: the Java
    version does not override ``equals`` either, so ``items.remove(item)`` removes
    the item by identity in both versions.
    """

    def __init__(self, id: int, profit: float, weight: int):
        """Creates a new instance of ``Item``.

        :param id: The identifier of this item.
        :param profit: The profit of this item.
        :param weight: The weight of this item.
        """
        self.id = id
        # The Java constructor declares the profit as a double, so an integer
        # profit is widened before it is stored.  Keeping that conversion here
        # makes both versions print exactly the same items.
        self.profit = float(profit)
        self.weight = weight

    def get_id(self) -> int:
        """Returns the identifier of this item.

        :return: The identifier of this item.
        """
        return self.id

    def get_profit(self) -> float:
        """Returns the profit of this item.

        :return: The profits of this item.
        """
        return self.profit

    def get_weight(self) -> int:
        """Returns the weight of this item.

        :return: The weight of this item.
        """
        return self.weight

    def get_profit_per_weight_unit(self) -> float:
        """Returns the profit per weight unit of this item.

        :return: The profit per weight unit of this item.
        """
        return self.profit / self.weight

    def __str__(self) -> str:
        """Returns the string representation of this item.

        :return: The string representation of this item.
        """
        return "(" + str(self.id) + ", " + str(self.weight) + ", " + str(self.profit) + ")"
