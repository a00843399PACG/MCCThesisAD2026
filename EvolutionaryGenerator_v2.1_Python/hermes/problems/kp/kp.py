"""Translation of ``mx.tec.hermes.problems.kp.KP``."""

import sys

from hermes.exceptions import NoSuchFeatureException, NoSuchHeuristicException
from hermes.problems.kp.item import Item
from hermes.problems.kp.knapsack import Knapsack
from hermes.problems.problem import Problem
from hermes.problems.problem_set import ProblemSet
from hermes.utils import files as Files
from hermes.utils import statistical as Statistical
from javacompat import DOUBLE_MAX_VALUE, DecimalFormat, Random
from metah.gp.s_expression import SExpression


class KP(Problem):
    """Provides the methods to create and solve knapsack problems.

    :author: Paola Azeneth Castillo Gutiérrez (Python translation)
    :original author: José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
    :original version: 2.0
    """

    FEATURES = ["NORM_MEAN_WEIGHT", "NORM_MEAN_PROFIT", "NORM_MEAN_PROFIT_WEIGHT", "NORM_CORRELATION"]
    HEURISTICS = ["DEFAULT", "MAX_PROFIT", "MAX_PROFIT/WEIGHT", "MIN_WEIGHT"]

    def __init__(self, source=None, capacity: int = None):
        """Mirrors the three constructors available in the Java version.

        ``KP()`` creates an empty instance, ``KP(file_name)`` reads the instance from
        a file and ``KP(items, capacity)`` builds the instance from a list of items.

        :param source: The name of the file to initialize this problem, or the items
            in this problem.
        :param capacity: The capacity of the knapsack in this problem, when the items
            are provided.
        """
        super().__init__()
        if source is None:
            #
            # Creates an empty instance of KP.
            #
            self.capacity = 0
            self.items = []
            self.problem_id = "Undefined"
            self.knapsack = Knapsack(self.capacity)
            self.solved = False
            self.nb_items = 0
        elif isinstance(source, str):
            #
            # Creates a new instance of KP from a file.
            #
            file_name = source
            string = Files.load(file_name)
            file_tokenizer = [line for line in string.split("\n") if line.strip() != ""]
            line_tokenizer = _tokenize(file_tokenizer[0].strip())
            self.items = []
            self.capacity = int(line_tokenizer[1])
            i = 0
            for line in file_tokenizer[1:]:
                line_tokenizer = _tokenize(line.strip())
                weight = int(line_tokenizer[0].strip())
                profit = float(line_tokenizer[1].strip())
                self.items.append(Item(i, profit, weight))
                i += 1
            self.problem_id = file_name[file_name.rfind("/") + 1:]
            self.knapsack = Knapsack(self.capacity)
            self.solved = False
            self.nb_items = len(self.items)
        else:
            #
            # Creates a new instance of KP from a list of items.
            #
            items = source
            self.capacity = capacity
            self.items = []
            for item in items:
                self.items.append(item)
            self.problem_id = "Undefined"
            self.knapsack = Knapsack(capacity)
            self.solved = False
            self.nb_items = len(items)

    @staticmethod
    def generate(type, nb_instances: int, id: str, path: str, nb_items: int, capacity: int,
                 max_weight: int, max_profit: int, population_size: int, crossover_rate: float,
                 mutation_rate: float, tournament_size: int, seed: int) -> None:
        """Creates a new set of instances of ``KP`` by using a genetic algorithm.

        :param type: The type of instances to generate.
        :param nb_instances: The number of instances to generate.
        :param id: The prefix identifier of the problems in this set.
        :param path: The path where the generated instances will be saved.
        :param nb_items: The number of items in each instance.
        :param capacity: The capacity of the knapsack in each instance.
        :param max_weight: The maximum weight per item in each instance.
        :param max_profit: The maximum profit per item in each instance.
        :param population_size: The population size to be used by the genetic algorithm.
        :param crossover_rate: The crossover rate to be used by the genetic algorithm.
        :param mutation_rate: The mutation rate to be used by the genetic algorithm.
        :param tournament_size: The tournament size to be used by the genetic algorithm.
        :param seed: The seed to initialize the random number generator.
        """
        from hermes.problems.kp.generator.kp_evaluator import KPEvaluator
        from hermes.problems.kp.generator.kp_generator import KPGenerator
        from hermes.problems.kp.generator.kp_individual import KPIndividual
        from metah.ga.genetic_algorithm import GeneticAlgorithm, Objective
        from metah.tournament_selector import TournamentSelector

        random = Random(seed)
        format = DecimalFormat("000")
        for i in range(nb_instances):
            genetic_algorithm = GeneticAlgorithm(KPEvaluator(type), KPGenerator(random.next_long()),
                                                 TournamentSelector(tournament_size, random.next_long()),
                                                 Objective.MAXIMIZE)
            KPIndividual.set_capacity(capacity)
            KPIndividual.set_max_weight_per_item(max_weight)
            KPIndividual.set_max_profit_per_item(max_profit)
            KPIndividual.set_nb_items(nb_items)
            genetic_algorithm.run(population_size, 100000, crossover_rate, mutation_rate,
                                  GeneticAlgorithm.Type.GENERATIONAL, True).to_kp().save(
                path + id + "_" + str(max_weight) + "_" + str(max_profit) + "_" + str(nb_items)
                + "_" + format.format(i) + ".kp")

    def solve(self, heuristic: str) -> None:
        try:
            item = self._next_item(heuristic)
            while item is not None:
                self.knapsack.pack(item)
                self.items.remove(item)
                item = self._next_item(heuristic)
            self.solved = True
        except NoSuchHeuristicException as exception:
            print(exception, file=sys.stderr)
            print("KP.java/solve", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)

    def solve_with_dynamic_programming(self) -> None:
        """Solves this instance by using dynamic programming.

        This is the translation of the Java method ``solve()``.
        """
        table = [[0.0] * len(self.items) for _ in range(self.knapsack.get_capacity() + 1)]
        for i in range(len(table[0])):
            item = self.items[i]
            for row_capacity in range(len(table)):
                if item.get_weight() <= row_capacity:
                    tmp_profit = item.get_profit()
                    if i == 0:
                        table[row_capacity][i] = tmp_profit
                    else:
                        table[row_capacity][i] = int(max(
                            table[row_capacity][i - 1],
                            tmp_profit + table[row_capacity - item.get_weight()][i - 1]))
                else:
                    if i > 0:
                        table[row_capacity][i] = table[row_capacity][i - 1]
        row = self.knapsack.get_capacity()
        for i in range(len(self.items) - 1, 0, -1):
            if table[row][i] != table[row][i - 1]:
                item = self.items.pop(i)
                self.knapsack.pack(item)
                row = row - item.get_weight()
        if table[row][0] != 0:
            item = self.items.pop(0)
            self.knapsack.pack(item)
        self.solved = True

    def solve_set_with_dynamic_programming(self, set: ProblemSet) -> str:
        """Solves a problem set by using dynamic programming.

        This is the translation of the Java method ``solve(ProblemSet)``.

        :param set: The set of instances to solve.
        :return: The results of solving a problem set by using dynamic programming.
        """
        format = DecimalFormat("0.0000")
        string = []
        string.append("INSTANCE\tDP\r\n")
        try:
            for file in set.get_files():
                problem = KP(file)
                obj_values = []
                string.append(problem.get_problem_id() + "\t")
                problem.solve_with_dynamic_programming()
                obj_values.append(format.format(problem.get_obj_value()) + "\t")
                string.append("".join(obj_values) + "\r\n")
            self.solved = True
        except Exception as e:
            print(e, file=sys.stderr)
            print("KP.java/solve", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)
        return "".join(string).strip()

    def solve_ca(self, heuristics: list, sequence: list) -> None:
        """Solves this instance by alternating two heuristics following a sequence.

        :param heuristics: The two heuristics to alternate.
        :param sequence: The sequence that decides which heuristic applies at each step.
        """
        i = 0
        try:
            item = self._next_item(heuristics[0]) if sequence[i] == 0 else self._next_item(heuristics[1])
            i += 1
            while item is not None:
                self.knapsack.pack(item)
                self.items.remove(item)
                if i == len(sequence):
                    i = 0
                item = self._next_item(heuristics[0]) if sequence[i] == 0 else self._next_item(heuristics[1])
                i += 1
            self.solved = True
        except NoSuchHeuristicException as exception:
            print(exception, file=sys.stderr)
            print("KP.java/solveCA", file=sys.stderr)
            print("The system will halt.", file=sys.stderr)
            sys.exit(1)

    def solve_with_s_expression(self, s_expression: SExpression) -> None:
        """Solves this instance by using an S-expression as the heuristic.

        This is the translation of the Java method ``solve(SExpression)``.

        :param s_expression: The S-expression that selects the next item to pack.
        """
        item = self._next_item_with_s_expression(s_expression)
        while item is not None:
            self.knapsack.pack(item)
            self.items.remove(item)
            item = self._next_item_with_s_expression(s_expression)
        self.solved = True

    def get_size(self) -> int:
        return len(self.items)

    def get_solution(self) -> list:
        """Returns the current solution to this problem.

        :return: The current solution to this problem.
        """
        return self.knapsack.get_solution(self.nb_items)

    def get_items(self) -> list:
        """Returns the items that have not been packed yet.

        :return: The items in this problem.
        """
        tmp = []
        for item in self.items:
            tmp.append(item)
        return tmp

    # DEbería devolver una copia.  ["It should return a copy." -- comment left by the
    # author in the Java original, kept verbatim.]
    def get_knapsack(self) -> Knapsack:
        """Returns the knapsack in this problem.

        :return: The knapsack in this problem.
        """
        return self.knapsack.copy()

    def get_obj_value(self) -> float:
        if self.solved:
            return self.knapsack.get_sum_of_profit()
        return float("nan")

    def get_feature(self, feature: str) -> float:
        if feature == "NORM_MEAN_WEIGHT":
            x = [item.get_weight() for item in self.items]
            return Statistical.mean(x) / Statistical.max(x)
        elif feature == "NORM_MEAN_PROFIT":
            x = [item.get_profit() for item in self.items]
            return Statistical.mean(x) / Statistical.max(x)
        elif feature == "NORM_MEAN_PROFIT_WEIGHT":
            x = [item.get_profit_per_weight_unit() for item in self.items]
            return Statistical.mean(x) / Statistical.max(x)
        elif feature == "NORM_CORRELATION":
            x = [item.get_weight() for item in self.items]
            y = [item.get_profit() for item in self.items]
            return Statistical.correlation(x, y) / 2 + 0.5
        else:
            raise NoSuchFeatureException("Feature '" + feature + "' is not recognized by the system.")

    def solve_x(self, file_name: str, heuristics: list, seed: int) -> None:
        """Combines the solutions produced by a set of heuristics at random.

        :param file_name: The name of the file that contains the instance to solve.
        :param heuristics: The heuristics to be used to solve the instance.
        :param seed: The seed to initialize the random number generator.
        """
        n = 0
        text = []
        text.append(file_name + "\t")
        solutions = [None] * len(heuristics)
        costs = [0.0] * len(heuristics)
        for i in range(len(heuristics)):
            problem = KP(file_name)
            n = len(problem.items)
            problem.solve(heuristics[i])
            solutions[i] = problem.get_solution()
            costs[i] = problem.get_obj_value()
            text.append(str(problem.get_obj_value()) + "\t")

        random = Random(seed)
        for k in range(97):
            #
            # for i in range(3):
            #     print(solutions[i])
            #
            problem = KP(file_name)
            solution = [0] * n
            for i in range(n):
                id = random.next_int(3)
                solution[i] = solutions[id][i]
                if solution[i] == 1:
                    item = problem.items[i]
                    problem.knapsack.pack(item)
            for i in range(len(solution)):
                if solution[i] == 0:
                    problem.knapsack.pack(problem.items[i])
            id = 0
            cost = -DOUBLE_MAX_VALUE
            for i in range(len(heuristics)):
                if costs[i] > cost:
                    id = i
                    cost = costs[i]
            cost = problem.get_obj_value()
            if cost < costs[id]:
                costs[id] = cost
                solutions[id] = problem.get_solution()
            # print(solution)
            # print(problem.get_obj_value())
            # print(problem.knapsack.get_capacity())
            id = 0
            cost = DOUBLE_MAX_VALUE
            for i in range(len(heuristics)):
                if costs[i] < cost:
                    id = i
                    cost = costs[i]
            # text.append(str(problem.get_obj_value()) + "\t")
            text.append(str(cost) + "\t")
        print("".join(text))

    def save(self, file_name: str) -> None:
        """Saves this problem into a file.

        :param file_name: The name of the file.
        """
        string = []
        string.append(str(len(self.items)) + ", " + str(self.capacity) + "\r\n")
        format = DecimalFormat("0.000")
        for item in self.items:
            string.append(str(item.get_weight()) + ", " + format.format(item.get_profit()) + "\r\n")
        Files.save("".join(string).strip(), file_name)

    def __str__(self) -> str:
        string = []
        string.append(str(len(self.items)) + ", " + str(self.capacity) + "\n")
        for item in self.items:
            string.append(str(item) + "\n")
        string.append(str(self.knapsack))
        return "".join(string).strip()

    def _next_item(self, heuristic: str) -> Item:
        """Returns the next item to pack.

        :param heuristic: The heuristic to select the next item to pack.
        :return: The next item to pack.
        :raises NoSuchHeuristicException: If the heuristic is not recognized.
        """
        selected = None
        if heuristic == "DEFAULT":
            for item in self.items:
                if self.knapsack.can_pack(item):
                    selected = item
                    break
            return selected
        elif heuristic == "MAX_PROFIT":
            best = -DOUBLE_MAX_VALUE
            for item in self.items:
                if self.knapsack.can_pack(item) and item.get_profit() > best:
                    selected = item
                    best = selected.get_profit()
            return selected
        elif heuristic == "MAX_PROFIT/WEIGHT":
            best = -DOUBLE_MAX_VALUE
            for item in self.items:
                if self.knapsack.can_pack(item) and item.get_profit_per_weight_unit() > best:
                    selected = item
                    best = selected.get_profit_per_weight_unit()
            return selected
        elif heuristic == "MIN_WEIGHT":
            best = DOUBLE_MAX_VALUE
            for item in self.items:
                if self.knapsack.can_pack(item) and item.get_weight() < best:
                    selected = item
                    best = selected.get_weight()
            return selected
        raise NoSuchHeuristicException("Heuristic '" + heuristic + "' is not recognized by the system.")

    def _next_item_with_s_expression(self, s_expression: SExpression) -> Item:
        """Returns the next item to pack.

        :param s_expression: The S-expression to select the next item.
        :return: The next item to pack.
        """
        selected = None
        best = -DOUBLE_MAX_VALUE
        for item in self.items:
            SExpression.set_variable("w", item.get_weight())
            SExpression.set_variable("p", item.get_profit())
            tmp = s_expression.evaluate()
            if self.knapsack.can_pack(item) and tmp > best:
                selected = item
                best = tmp
        return selected


def _tokenize(line: str) -> list:
    """Splits a line the way ``StringTokenizer(line, ", \\t")`` does."""
    tokens = []
    token = []
    for character in line:
        if character in (",", " ", "\t"):
            if token:
                tokens.append("".join(token))
                token = []
        else:
            token.append(character)
    if token:
        tokens.append("".join(token))
    return tokens
