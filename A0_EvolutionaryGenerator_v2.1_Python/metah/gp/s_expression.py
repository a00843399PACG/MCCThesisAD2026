"""Translation of ``mx.tec.meta.gp.SExpression``."""

import math
import sys

from javacompat import DecimalFormat, Random


class SExpression:
    """Provides the methods to create and use S-expressions.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 1.0
    """

    # The state below is static in the Java version, so it is shared by every
    # S-expression created within the same run.
    _terminals = None
    _operators = None
    _format = DecimalFormat("0.0000")
    MAX_DEPTH = 3
    _random = Random()
    _variables = None

    @staticmethod
    def init(terminals: list, operators: list, seed: int) -> None:
        """Initializes the elements shared by all the S-expressions.

        :param terminals: The terminals available to build S-expressions.
        :param operators: The operators available to build S-expressions.
        :param seed: The seed to initialize the random number generator.
        """
        SExpression._terminals = terminals
        SExpression._operators = operators
        SExpression._variables = {}
        SExpression._random = Random(seed)

    @staticmethod
    def set_variable(variable: str, value: float) -> None:
        """Sets the value of one of the variables available to the S-expressions.

        This is the translation of the static method ``SExpression.set(String, double)``.
        The name changes because the Java class also defines two instance methods
        called ``set`` and Python does not support overloading.

        :param variable: The name of the variable.
        :param value: The value of the variable.
        """
        SExpression._variables[variable] = value

    def __init__(self, depth: int = None, label: str = None, nb_children: int = None):
        """Mirrors the two constructors available in the Java version.

        ``SExpression(depth)`` builds a random S-expression from the given depth,
        while ``SExpression(label=..., nb_children=...)`` builds a single node with
        the label provided and the given number of (still undefined) children.
        """
        if depth is not None:
            nb_children = 2
            if (SExpression._random.next_double() < (1 - math.pow(2, depth) / math.pow(2, SExpression.MAX_DEPTH))
                    and depth < SExpression.MAX_DEPTH):
                id = SExpression._random.next_int(len(SExpression._operators))
                self.label = SExpression._operators[id]
                if self.label in ("exp", "log", "log10"):
                    nb_children = 1
                self.children = [None] * nb_children
                for i in range(nb_children):
                    self.children[i] = SExpression(depth + 1)
            else:
                id = SExpression._random.next_int(len(SExpression._terminals))
                if SExpression._terminals[id] == "R":
                    self.label = SExpression._format.format(SExpression._random.next_double(-1, 1))
                else:
                    self.label = SExpression._terminals[id]
                self.children = []
        else:
            self.label = label
            self.children = [None] * nb_children

    def set(self, index: int, label: str, nb_children: int = 0) -> "SExpression":
        """Sets one of the children of this S-expression.

        :param index: The position of the child to set.
        :param label: The label of the new child.
        :param nb_children: The number of children of the new child.
        :return: The S-expression that was set as a child.
        """
        s_expression = SExpression(label=label, nb_children=nb_children)
        self.children[index] = s_expression
        return s_expression

    def get_children(self) -> list:
        """Returns the children of this S-expression."""
        return self.children

    def get_size(self) -> int:
        """Returns the number of nodes in this S-expression."""
        size = 1
        for child in self.children:
            size += child.get_size()
        return size

    def pick(self, id: int, counter: list, parent: "SExpression", index: int) -> list:
        """Detaches the node with the identifier provided as argument.

        :param id: The identifier of the node to pick.
        :param counter: A one element list used as a mutable counter (an ``int[]`` in Java).
        :param parent: The parent of the current node.
        :param index: The position of the current node within its parent.
        :return: A pair with the parent of the node picked and the node picked.
        """
        if id == counter[0]:
            if id > 0:
                parent.get_children()[index] = None
            return [parent, self]
        else:
            for i in range(len(self.children)):
                counter[0] += 1
                s_expressions = self.children[i].pick(id, counter, self, i)
                if s_expressions is not None:
                    return s_expressions
        return None

    def evaluate(self) -> float:
        """Returns the value of this S-expression."""
        if len(self.children) > 0:
            if self.label == "+":
                return self.children[0].evaluate() + self.children[1].evaluate()
            elif self.label == "-":
                return self.children[0].evaluate() - self.children[1].evaluate()
            elif self.label == "*":
                return self.children[0].evaluate() * self.children[1].evaluate()
            elif self.label == "/":
                tmp = self.children[1].evaluate()
                if tmp != 0:
                    return self.children[0].evaluate() / tmp
                else:
                    return 0
            elif self.label == "^":
                return math.pow(self.children[0].evaluate(), self.children[1].evaluate())
            elif self.label == "exp":
                return math.exp(self.children[0].evaluate())
            elif self.label == "log":
                tmp = self.children[0].evaluate()
                if tmp != 0:
                    return 1
                return math.log(abs(self.children[0].evaluate()))
            elif self.label == "log10":
                tmp = self.children[0].evaluate()
                if tmp != 0:
                    return 1
                return math.log10(abs(self.children[0].evaluate()))
            else:
                print("Operation not supported for this S-Expression.", file=sys.stderr)
                print("The system will halt.", file=sys.stderr)
                sys.exit(1)
        else:
            if self.label in SExpression._variables:
                return SExpression._variables[self.label]
            else:
                return float(self.label)
        sys.exit(1)
        return float("nan")

    def copy(self) -> "SExpression":
        """Returns a deep copy of this S-expression."""
        s_expression = SExpression(label=self.label, nb_children=len(self.children))
        for i in range(len(self.children)):
            s_expression.children[i] = self.children[i].copy()
        return s_expression

    def __str__(self) -> str:
        """Returns the string representation of this S-expression."""
        string = []
        if len(self.children) > 0:
            string.append("(")
            string.append(self.label)
            for child in self.children:
                if child is None:
                    string.append(" NULL")
                else:
                    string.append(" " + str(child))
            string.append(")")
        else:
            string.append(self.label)
        return "".join(string)
