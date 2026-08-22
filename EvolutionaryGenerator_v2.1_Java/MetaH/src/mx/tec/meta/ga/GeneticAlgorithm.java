package mx.tec.meta.ga;

import mx.tec.meta.Generator;
import mx.tec.meta.Individual;
import mx.tec.meta.Evaluator;
import mx.tec.meta.Selector;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Provides the methods to use a genetic algorithm.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 1.0
 */
public final class GeneticAlgorithm {

    private Individual best;
    private List<Individual> population;
    private final Evaluator evaluator;
    private final Generator generator;
    private final Selector selector;
    private final Objective objective;

    /**
     * Defines the type of the genetic algorithm to use.
     */
    public enum Type {
        GENERATIONAL,
        STEADY_STATE
    }

    /**
     * Defines the objective of the evolutionary process regarding the objective
     * function.
     */
    public enum Objective {
        MAXIMIZE,
        MINIMIZE
    }

    /**
     * Creates a new instance of <code>GeneticAlgorithm</code>.
     *
     * @param evaluator The evaluator of the performance of the individuals in  this genetic algorithm.
     * @param generator The generator of the solutions in this genetic algorithm.
     * @param selector The selector to be used by the genetic algorithm.
     * @param objective The objective of the evolutionary process regarding the objective function (maximize or minimize).
     */
    public GeneticAlgorithm(Evaluator evaluator, Generator generator, Selector selector, Objective objective) {
        this.evaluator = evaluator;
        this.generator = generator;
        this.selector = selector;
        this.objective = objective;
    }

    /**
     * Runs the genetic algorithm and returns the best individual found.
     *
     * @param populationSize The size of the population in this genetic algorithm.
     * @param maxEvaluations The maximum number of calls to the evaluation function this genetic algorithm is allowed to execute.
     * @param crossoverRate The crossover rate to be used by this genetic algorithm.
     * @param mutationRate The mutation rate to be used by this genetic algorithm.
     * @param type The type of the genetic algorithm to be used.
     * @param printMode A flag indicating if some data about the evolutionary process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    public Individual run(int populationSize, long maxEvaluations, double crossoverRate, double mutationRate, Type type, boolean printMode) {
        if (populationSize < 2) {
            System.err.println("The population must contain at least two individuals in order to run the genetic algorithm.");
            System.err.println("The system will halt.");
            System.exit(1);
        }
        population = new ArrayList(populationSize);
        for (int i = 0; i < populationSize; i++) {
            population.add((Individual) generator.generate());            
        }        
        if (crossoverRate < 0) {
            crossoverRate = 0.0;
        }
        if (crossoverRate > 1) {
            crossoverRate = 1.0;
        }
        if (mutationRate < 0) {
            mutationRate = 0.0;
        }
        if (mutationRate > 1) {
            mutationRate = 1.0;
        }
        for (Individual individual : population) {
            individual.setEvaluation(evaluator.evaluate(individual));
        }
        if (objective == Objective.MINIMIZE) {
            Collections.sort(population);
        } else {
            Collections.sort(population, Collections.reverseOrder());
        }
        best = population.get(0).copy();
        switch (type) {
            case GENERATIONAL:
                return runGenerational(maxEvaluations, crossoverRate, mutationRate, printMode);
            case STEADY_STATE:
                return runSteadyState(maxEvaluations, crossoverRate, mutationRate, printMode);
        }
        return null;
    }

    /**
     * Runs a generational genetic algorithm.
     *
     * @param maxEvaluations The maximum number of generations that this genetic
     * algorithm is allowed to run.
     * @param crossoverRate The crossover rate to be used by this genetic
     * algorithm.
     * @param mutationRate The mutation rate to be used by this genetic
     * algorithm.
     * @param printMode A flag indicating if some data about the evolutionary
     * process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    private Individual runGenerational(long maxEvaluations, double crossoverRate, double mutationRate, boolean printMode) {
        int i;
        double[] fitness;
        DecimalFormat format;
        Individual[] parents, offspring;
        List<Individual> nextPopulation;
        //format = new DecimalFormat("0.0000");
        format = new DecimalFormat("00.0000E00");
        fitness = new double[population.size()];
        for (int j = 0; j < population.size(); j++) {
            fitness[j] = population.get(j).getEvaluation();
        }
        if (printMode) {
            System.out.println("ITERATIONS, EVALUATIONS, BEST, MEAN, DEVIATION");
            System.out.println("0, " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
        }
        i = 0;
        while (evaluator.getNbEvaluations() < maxEvaluations) {
            nextPopulation = new ArrayList(population.size());
            while (nextPopulation.size() < population.size()) {
                parents = selector.select(population, objective);
                offspring = parents[0].combine(parents[1], crossoverRate);
                for (Individual individual : offspring) {
                    individual.mutate(mutationRate);
                    individual.setEvaluation(evaluator.evaluate(individual));
                    nextPopulation.add(individual);
                }
            }
            population = nextPopulation;
            if (objective == Objective.MINIMIZE) {
                Collections.sort(population);
                if (population.get(0).getEvaluation() < best.getEvaluation()) {
                    best = population.get(0).copy();
                }
            } else {
                Collections.sort(population, Collections.reverseOrder());
                if (population.get(0).getEvaluation() > best.getEvaluation()) {
                    best = population.get(0).copy();
                }
            }
            fitness = new double[population.size()];
            for (int j = 0; j < population.size(); j++) {
                fitness[j] = population.get(j).getEvaluation();
            }
            if (printMode) {
                System.out.println((i + 1) + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
            }
            i++;
        }
        return best;
    }

    /**
     * Runs a steady state genetic algorithm.
     *
     * @param maxEvaluations The maximum number of generations that this genetic
     * algorithm is allowed to run.
     * @param crossoverRate The crossover rate to be used by this genetic
     * algorithm.
     * @param mutationRate The mutation rate to be used by this genetic
     * algorithm.
     * @param printMode A flag indicating if some data about the evolutionary
     * process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    private Individual runSteadyState(long maxEvaluations, double crossoverRate, double mutationRate, boolean printMode) {
        int i;
        double[] fitness;
        Individual[] parents, offspring;
        DecimalFormat format;
        format = new DecimalFormat("0.0000");
        fitness = new double[population.size()];
        for (int j = 0; j < population.size(); j++) {
            fitness[j] = population.get(j).getEvaluation();
        }
        if (printMode) {
            System.out.println("ITERATIONS, EVALUATIONS, BEST, MEAN, DEVIATION");
            System.out.println("0, " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
        }
        i = 0;
        while (evaluator.getNbEvaluations() < maxEvaluations) {
            parents = selector.select(population, objective);
            offspring = parents[0].combine(parents[1], crossoverRate);
            for (Individual individual : offspring) {
                individual.mutate(mutationRate);
                individual.setEvaluation(evaluator.evaluate(individual));
                population.add(individual);
            }
            if (objective == Objective.MINIMIZE) {
                Collections.sort(population);
                if (population.get(0).getEvaluation() < best.getEvaluation()) {
                    best = population.get(0).copy();
                }
            } else {
                Collections.sort(population, Collections.reverseOrder());
                if (population.get(0).getEvaluation() > best.getEvaluation()) {
                    best = population.get(0).copy();
                }
            }
            for (Individual individual : offspring) {
                population.remove(population.size() - 1);
            }
            fitness = new double[population.size()];
            for (int j = 0; j < population.size(); j++) {
                fitness[j] = population.get(j).getEvaluation();
            }
            if (printMode) {
                System.out.println((i + 1) + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
            }
            i++;
        }
        return best;
    }

    /**
     * Returns the mean of the values provided as argument.
     *
     * @param values The values to analyze.
     * @return The mean of the values provided as argument.
     */
    public static double mean(double[] values) {
        double mean = 0;
        if (values.length == 0) {
            return 0;
        }
        for (int i = 0; i < values.length; i++) {
            mean += values[i];
        }
        return mean / values.length;
    }

    /**
     * Returns the standard deviation of the values provided as argument.
     *
     * @param values The values to analyze.
     * @return The standard deviation of the values provided as argument.
     */
    private static double stdev(double[] values) {
        double mean, stdev;
        mean = mean(values);
        stdev = 0;
        for (int i = 0; i < values.length; i++) {
            stdev += Math.pow((values[i] - mean), 2);
        }
        if (values.length > 1) {
            return Math.sqrt(stdev / (values.length - 1));
        } else {
            return 0;
        }
    }

}
