package mx.tec.hermes.problems.kp;

import mx.tec.hermes.problems.kp.generator.KPIndividual;
import mx.tec.hermes.problems.kp.generator.KPGenerator;
import mx.tec.hermes.exceptions.NoSuchFeatureException;
import mx.tec.hermes.exceptions.NoSuchHeuristicException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.StringTokenizer;
import mx.tec.meta.ga.GeneticAlgorithm;
import mx.tec.meta.ga.GeneticAlgorithm.Objective;
import mx.tec.meta.TournamentSelector;
import mx.tec.hermes.problems.ProblemSet;
import mx.tec.hermes.problems.kp.generator.KPEvaluator;
import mx.tec.hermes.utils.Files;
import mx.tec.hermes.utils.Statistical;
import mx.tec.meta.gp.SExpression;

/**
 * Provides the methods to create and solve knapsack problems.
 *
 * @author José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class KP extends mx.tec.hermes.problems.Problem {

    protected boolean solved;
    private final int capacity, nbItems;
    protected final Knapsack knapsack;
    protected final List<Item> items;
    
    public static String[] FEATURES = new String[]{"NORM_MEAN_WEIGHT", "NORM_MEAN_PROFIT", "NORM_MEAN_PROFIT_WEIGHT", "NORM_CORRELATION"};
    public static String[] HEURISTICS = new String[]{"DEFAULT", "MAX_PROFIT", "MAX_PROFIT/WEIGHT", "MIN_WEIGHT"};
    
    /**
     * Creates an empty instance of <code>KP</code>.
     */
    public KP() {
        capacity = 0;
        items = new ArrayList(0);
        problemId = "Undefined";
        knapsack = new Knapsack(capacity);
        solved = false;
        nbItems = 0;
    }

    /**
     * Creates a new instance of <code>KP</code>.
     *
     * @param fileName The name of the file to initialize this problem.
     */
    public KP(String fileName) {
        int weight, i;
        double profit;
        String string;
        StringTokenizer fileTokenizer, lineTokenizer;
        string = Files.load(fileName);
        fileTokenizer = new StringTokenizer(string, "\n");
        lineTokenizer = new StringTokenizer(fileTokenizer.nextToken().trim(), ", \t");
        items = new ArrayList(Integer.parseInt(lineTokenizer.nextToken()));
        capacity = Integer.parseInt(lineTokenizer.nextToken());
        i = 0;
        while (fileTokenizer.hasMoreTokens()) {
            lineTokenizer = new StringTokenizer(fileTokenizer.nextToken().trim(), ", \t");
            weight = Integer.parseInt(lineTokenizer.nextToken().trim());
            profit = Double.parseDouble(lineTokenizer.nextToken().trim());
            items.add(new Item(i, profit, weight));            
            i++;
        }
        this.problemId = fileName.substring(fileName.lastIndexOf('/') + 1);
        knapsack = new Knapsack(capacity);
        solved = false;
        nbItems = items.size();
    }

    /**
     * Creates a new instance of <code>KP</code>.
     *
     * @param items The items in this problem.
     * @param capacity The capacity of the knapsack in this problem.
     */
    public KP(List<Item> items, int capacity) {
        this.capacity = capacity;
        this.items = new ArrayList(items.size());
        for (Item item : items) {
            this.items.add(item);
        }
        problemId = "Undefined";
        knapsack = new Knapsack(capacity);
        solved = false;
        nbItems = items.size();
    }

    /**
     * Creates a new set of instances of <code>KP</code> by using a genetic algorithm.
     *
     * @param type The type of instances to generate.
     * @param nbInstances The number of instances to generate.
     * @param id The prefix identifier of the problems in this set.
     * @param path The path where the generated instances will be saved.
     * @param nbItems The number of items in each instance.
     * @param capacity The capacity of the knapsack in each instance.
     * @param maxWeight The maximum weight per item in each instance.
     * @param maxProfit The maximum profit per item in each instance.
     * @param populationSize The population size to be used by the genetic algorithm.
     * @param crossoverRate The crossover rate to be used by the genetic algorithm.
     * @param mutationRate The mutation rate to be used by the genetic algorithm.
     * @param tournamentSize The tournament size to be used by the genetic algorithm.
     * @param seed The seed to initialize the random number generator.
     */
    public static void generate(KPEvaluator.InstanceType type, int nbInstances, String id, String path, int nbItems, int capacity, int maxWeight, int maxProfit, int populationSize, double crossoverRate, double mutationRate, int tournamentSize, long seed) {
        Random random;
        DecimalFormat format;
        GeneticAlgorithm geneticAlgorithm;
        random = new Random(seed);
        format = new DecimalFormat("000");        
        for (int i = 0; i < nbInstances; i++) {
            geneticAlgorithm = new GeneticAlgorithm(new KPEvaluator(type), new KPGenerator(random.nextLong()), new TournamentSelector(tournamentSize, random.nextLong()), Objective.MAXIMIZE);
            KPIndividual.setCapacity(capacity);
            KPIndividual.setMaxWeightPerItem(maxWeight);
            KPIndividual.setMaxProfitPerItem(maxProfit);
            KPIndividual.setNbItems(nbItems);       
            ((KPIndividual) geneticAlgorithm.run(populationSize, 100000, crossoverRate, mutationRate, GeneticAlgorithm.Type.GENERATIONAL, true)).toKP().save(path + id + "_" + maxWeight + "_" + maxProfit + "_" + nbItems + "_" + format.format(i) + ".kp");            
        }
    }
   
    @Override
    public void solve(String heuristic) {
        Item item;        
        try {                                    
            item = nextItem(heuristic);
            while (item != null) {
                knapsack.pack(item);
                items.remove(item);
                item = nextItem(heuristic);
            }
            solved = true;
        } catch (NoSuchHeuristicException exception) {
            System.err.println(exception);
            System.err.println("KP.java/solve");
            System.err.println("The system will halt.");
            System.exit(1);
        }
    }   

    /**
     * Solves this instance by using dynamic programming.
     */
    public void solve() {
        int row;
        double tmpProfit;
        double[][] table;
        Item item;
        table = new double[knapsack.getCapacity() + 1][items.size()];
        for (int i = 0; i < table[0].length; i++) {
            item = items.get(i);
            for (int rowCapacity = 0; rowCapacity < table.length; rowCapacity++) {
                if (item.getWeight() <= rowCapacity) {
                    tmpProfit = item.getProfit();
                    if (i == 0) {
                        table[rowCapacity][i] = tmpProfit;
                    } else {
                        table[rowCapacity][i] = (int) Math.max(table[rowCapacity][i - 1], tmpProfit + table[rowCapacity - item.getWeight()][i - 1]);
                    }
                } else {
                    if (i > 0) {
                        table[rowCapacity][i] = table[rowCapacity][i - 1];
                    }
                }
            }
        }
        row = knapsack.getCapacity();
        for (int i = items.size() - 1; i > 0; i--) {
            if (table[row][i] != table[row][i - 1]) {
                item = items.remove(i);
                knapsack.pack(item);
                row = row - item.getWeight();
            }
        }
        if (table[row][0] != 0) {
            item = items.remove(0);
            knapsack.pack(item);
        }
        solved = true;
    }
    
    /**
     * Solves a problem set by using dynamic programming.
     *
     * @param set The set of instances to solve.     
     * @return The results of solving a problem set by using dynamic programming.
     */
    public final String solve(ProblemSet set) {
        DecimalFormat format;
        StringBuilder string, objValues;
        KP problem;
        format = new DecimalFormat("0.0000");
        string = new StringBuilder();
        string.append("INSTANCE\tDP\r\n");                
        try {
            for (String file : set.getFiles()) {
                problem = new KP(file);
                objValues = new StringBuilder();
                string.append(problem .getProblemId()).append("\t");                    
                    problem.solve();
                    objValues.append(format.format(problem.getObjValue())).append("\t");
                    string.append(objValues).append("\r\n");
                }
            solved = true;
        } catch (Exception e) {
            System.err.println(e);
            System.err.println("KP.java/solve");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        return string.toString().trim();
    }
    
    public void solveCA(String[] heuristics, int[] sequence) {
        int i;
        Item item;
        i = 0;
        try {
            item = sequence[i++] == 0? nextItem(heuristics[0]) : nextItem(heuristics[1]);
            while (item != null) {
                knapsack.pack(item);
                items.remove(item);
                if (i == sequence.length) {
                    i = 0;
                }
                item = sequence[i++] == 0? nextItem(heuristics[0]) : nextItem(heuristics[1]);
            }
            solved = true;
        } catch (NoSuchHeuristicException exception) {
            System.err.println(exception);
            System.err.println("KP.java/solveCA");
            System.err.println("The system will halt.");
            System.exit(1);
        }
    }
    
    public void solve(SExpression sExpression) {
        Item item;        
        item = nextItem(sExpression);        
        while (item != null) {
            knapsack.pack(item);
            items.remove(item);
            item = nextItem(sExpression);
        }
        solved = true;
    }
    
    @Override        
    public int getSize() {
        return items.size();
    }
       
    /**
     * Returns the current solution to this problem.
     * 
     * @return The current solution to this problem.
     */
    public int[] getSolution() {
        return knapsack.getSolution(nbItems);        
    }
    
    public List<Item> getItems() {
        List<Item> tmp;
        tmp = new ArrayList(items.size());
        for (Item item : items) {
            tmp.add(item);
        }
        return tmp;
    }
    
    // DEbería devolver una copia.
    /**
     * Returns the knapsack in this problem.
     * 
     * @return The knapsack in this problem.
     */
    public Knapsack getKnapsack() {                        
        return knapsack.copy();
    }
    
    @Override
    public double getObjValue() {
        if (solved) {
            return knapsack.getSumOfProfit();
        }
        return Double.NaN;
    }

    @Override
    public double getFeature(String feature) throws NoSuchFeatureException {
        int i;
        double[] x, y;
        switch (feature) {
            case "NORM_MEAN_WEIGHT":
                i = 0;
                x = new double[items.size()];
                for (Item item : items) {
                    x[i++] = item.getWeight();
                }
                return Statistical.mean(x) / Statistical.max(x);
            case "NORM_MEAN_PROFIT":
                i = 0;
                x = new double[items.size()];
                for (Item item : items) {
                    x[i++] = item.getProfit();
                }
                return Statistical.mean(x) / Statistical.max(x);
            case "NORM_MEAN_PROFIT_WEIGHT":
                i = 0;
                x = new double[items.size()];
                for (Item item : items) {
                    x[i++] = item.getProfitPerWeightUnit();
                }
                return Statistical.mean(x) / Statistical.max(x);            
            case "NORM_CORRELATION":
                i = 0;
                x = new double[items.size()];
                y = new double[items.size()];
                for (Item item : items) {
                    x[i] = item.getWeight();
                    y[i++] = item.getProfit();
                }
                return Statistical.correlation(x, y) / 2 + 0.5;            
            default:
                throw new NoSuchFeatureException("Feature \'" + feature + "\' is not recognized by the system.");
        }
    }
    
    public void solveX(String fileName, String[] heuristics, long seed) {
        int n = 0, id;
        int[][] solutions;
        int[] solution;
        double cost;
        double[] costs;
        KP problem;
        Random random; 
        Item item;
        StringBuilder text = new StringBuilder();
        text.append(fileName).append("\t");        
        solutions = new int[heuristics.length][];
        costs = new double[heuristics.length];
        for (int i = 0; i < heuristics.length; i++) {
            problem = new KP(fileName);
            n = problem.items.size();
            problem.solve(heuristics[i]);
            solutions[i] = problem.getSolution();
            costs[i] = problem.getObjValue();
            text.append(problem.getObjValue()).append("\t");
        }
        
        random = new Random(seed);
        for (int k = 0; k < 97; k++) {
            /*
            for (int i = 0; i < 3; i++) {
                System.out.println(Arrays.toString(solutions[i]));
            }
            */                        
            problem = new KP(fileName);
            solution = new int[n];
            for (int i = 0; i < n; i++) {
                id = random.nextInt(3);
                solution[i] = solutions[id][i];
                if (solution[i] == 1) {
                    item = problem.items.get(i);
                    problem.knapsack.pack(item);
                }
            }
            for (int i = 0; i < solution.length; i++) {
                if (solution[i] == 0) {
                    problem.knapsack.pack(problem.items.get(i));
                }
            }
            id = 0;
            cost = -Double.MAX_VALUE;
            for (int i = 0; i < heuristics.length; i++) {
                if (costs[i] > cost) {
                    id = i;
                    cost = costs[i];
                }
            }
            cost = problem.getObjValue();
            if (cost < costs[id]) {
                costs[id] = cost;
                solutions[id] = problem.getSolution();
            }
            //System.out.println(Arrays.toString(solution));
            //System.out.println(problem.getObjValue());
            //System.out.println(problem.knapsack.getCapacity());
            id = 0;
            cost = Double.MAX_VALUE;
            for (int i = 0; i < heuristics.length; i++) {
                if (costs[i] < cost) {
                    id = i;
                    cost = costs[i];
                }
            }
            //text.append(problem.getObjValue()).append("\t");
            text.append(cost).append("\t");
        }
        System.out.println(text.toString());
    }

    /**
     * Saves this problem into an XML file.
     *
     * @param fileName The name of the XML file.
     */
    public void save(String fileName) {
        StringBuilder string;
        DecimalFormat format;
        string = new StringBuilder();
        string.append(items.size()).append(", ").append(capacity).append("\r\n");
        format = new DecimalFormat("0.000");
        for (Item item : items) {
            string.append(item.getWeight()).append(", ").append(format.format(item.getProfit())).append("\r\n");
        }        
        Files.save(string.toString().trim(), fileName);        
    }

    @Override
    public String toString() {
        StringBuilder string;
        string = new StringBuilder();
        string.append(items.size()).append(", ").append(capacity).append("\n");
        for (Item item : items) {
            string.append(item.toString()).append("\n");
        }
        string.append(knapsack.toString());
        return string.toString().trim();
    }
   
    /**
     * Returns the next item to pack.
     *
     * @param heuristic The heuristic to select the next item to pack.
     * @return The next item to pack.
     * @throws mx.tec.hermes.exceptions.NoSuchHeuristicException
     */
    private Item nextItem(String heuristic) throws NoSuchHeuristicException {
        double best;
        Item selected;
        selected = null;
        switch (heuristic) {
            case "DEFAULT":
                for (Item item : items) {
                    if (knapsack.canPack(item)) {
                        selected = item;
                        break;
                    }
                }
                return selected;
            case "MAX_PROFIT":
                best = -Double.MAX_VALUE;
                for (Item item : items) {
                    if (knapsack.canPack(item) && item.getProfit() > best) {
                        selected = item;
                        best = selected.getProfit();
                    }
                }
                return selected;
            case "MAX_PROFIT/WEIGHT":
                best = -Double.MAX_VALUE;
                for (Item item : items) {
                    if (knapsack.canPack(item) && item.getProfitPerWeightUnit() > best) {
                        selected = item;
                        best = selected.getProfitPerWeightUnit();
                    }
                }
                return selected;
            case "MIN_WEIGHT":
                best = Double.MAX_VALUE;
                for (Item item : items) {
                    if (knapsack.canPack(item) && item.getWeight() < best) {
                        selected = item;
                        best = selected.getWeight();
                    }
                }
                return selected;
        }
        throw new NoSuchHeuristicException("Heuristic \'" + heuristic + "\' is not recognized by the system.");
    }

    /**
     * Returns the next item to pack.
     *
     * @param heuristic The heuristic to select the next item.
     * @return The next item to pack.
     * @throws mx.tec.hermes.exceptions.NoSuchHeuristicException
     */
    private Item nextItem(SExpression sExpression) {
        double best, tmp;
        Item selected;
        selected = null;
        best = -Double.MAX_VALUE;        
        for (Item item : items) {
            SExpression.set("w", item.getWeight());
            SExpression.set("p", item.getProfit());
            tmp = sExpression.evaluate();
            if (knapsack.canPack(item) && tmp > best) {
                selected = item;
                best = tmp;
            }
        }    
        return selected; 
    }
}
