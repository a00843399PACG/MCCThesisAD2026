"""Translation of ``mx.tec.meta.gp.GPIndividual``."""

from metah.gp.s_expression import SExpression
from metah.individual import Individual


class GPIndividual(Individual):
    """Provides the methods to create and handle individuals that encode S-expressions.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: jcobayliss
    """

    def __init__(self, max_depth: int = None, seed: int = None, individual: "GPIndividual" = None):
        """Mirrors the two constructors available in the Java version.

        ``GPIndividual(max_depth, seed)`` builds a new random individual while
        ``GPIndividual(individual=...)`` is the copy constructor.
        """
        if individual is not None:
            super().__init__(individual.get_evaluation(), individual.random.next_long())
            self.max_depth = individual.max_depth
            self.s_expression = individual.s_expression.copy()
        else:
            super().__init__(0, seed)
            self.max_depth = max_depth
            self.s_expression = SExpression(0)

    def get_s_expression(self) -> SExpression:
        """Returns the S-expression encoded by this individual."""
        return self.s_expression

    def set_s_expression(self, s_expression: SExpression) -> None:
        """Sets the S-expression encoded by this individual."""
        self.s_expression = s_expression.copy()

    def remove(self) -> list:
        """Detaches a random sub-tree from the S-expression encoded by this individual."""
        id = self.random.next_int(0, self.s_expression.get_size())
        return self.s_expression.pick(id, [0], None, 0)

    def combine(self, individual: Individual, crossover_rate: float) -> list:
        parent_a = self
        parent_b = individual
        if self.random.next_double() < crossover_rate:
            # print(">> " + str(parent_a))
            # print(">> " + str(parent_b))
            s_expressions_a = parent_a.remove()
            s_expressions_b = parent_b.remove()
            # print("<< " + str(s_expressions_a[1]))
            # print("<< " + str(s_expressions_b[1]))
            if s_expressions_a[0] is None:
                parent_a.set_s_expression(s_expressions_b[1])
            else:
                children = s_expressions_a[0].get_children()
                for i in range(len(children)):
                    if children[i] is None:
                        children[i] = s_expressions_b[1]
            if s_expressions_b[0] is None:
                parent_b.set_s_expression(s_expressions_a[1])
            else:
                children = s_expressions_b[0].get_children()
                for i in range(len(children)):
                    if children[i] is None:
                        children[i] = s_expressions_a[1]
        return [parent_a, parent_b]

    def mutate(self, mutation_rate: float) -> None:
        from metah.gp.gp_generator import GPGenerator

        if self.random.next_double() < mutation_rate:
            generator = GPGenerator(self.random.next_long())
            s_expressions = self.remove()
            if s_expressions[0] is None:
                self.set_s_expression(s_expressions[1])
            else:
                children = s_expressions[0].get_children()
                for i in range(len(children)):
                    if children[i] is None:
                        children[i] = generator.generate().get_s_expression()

    def copy(self) -> Individual:
        return GPIndividual(individual=self)

    def __str__(self) -> str:
        return str(self.s_expression)
