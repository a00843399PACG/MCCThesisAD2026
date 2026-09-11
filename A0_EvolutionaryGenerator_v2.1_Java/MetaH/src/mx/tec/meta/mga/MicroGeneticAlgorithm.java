package mx.tec.meta.mga;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import mx.tec.meta.Evaluator;
import mx.tec.meta.Generator;
import mx.tec.meta.Individual;
import mx.tec.meta.Selector;
import mx.tec.meta.ga.GeneticAlgorithm.Objective;

/**
 * Provides the methods to use a micro genetic algorithm.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public final class MicroGeneticAlgorithm {

    private static final double MIN_FITNESS_DEVIATION = 0.00001;
    
    private Individual best;
    private List<Individual> population;
    private final Evaluator evaluator;
    private final Generator generator;
    private final Selector selector;
    private final Objective objective;

    /**
     * Defines the type of the micro genetic algorithm to use.
     */
    public enum Type {
        GENERATIONAL,
        STEADY_STATE
    }
    
    /**
     * Creates a new instance of <code>MicroGeneticAlgorithm</code>.
     *
     * @param evaluator The evaluator of the performance of the individuals in this micro genetic algorithm.
     * @param generator The generator of the solutions in this micro genetic algorithm.
     * @param selector The selector to be used by the genetic algorithm.
     * @param objective The objective of the evolutionary process regarding the objective function (maximize or minimize).
     */
    public MicroGeneticAlgorithm(Evaluator evaluator, Generator generator, Selector selector, Objective objective) {
        this.evaluator = evaluator;
        this.generator = generator;
        this.selector = selector;
        this.objective = objective;
    }
    
    /**
     * Runs the micro genetic algorithm and returns the best solution found by the evolutionary process.
     *
     * @param populationSize The size of the population in this micro genetic algorithm.
     * @param maxEvaluations The maximum number of calls to the evaluation function this genetic algorithm is allowed to
     * execute.
     * @param type The type of the micro genetic algorithm to be used.
     * @param printMode A flag indicating if some data about the evolutionary process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    public Individual run(int populationSize, long maxEvaluations, Type type, boolean printMode) {
        population = new ArrayList(populationSize);
        for (int i = 0; i < populationSize; i++) {
            population.add((Individual) generator.generate());
        }
        for (Individual individual : population) {
            individual.setEvaluation(evaluator.evaluate(individual));
        }
        if (objective == Objective.MINIMIZE) {
            Collections.sort(population);
        } else {
            Collections.sort(population, Collections.reverseOrder());
        }
        best = this.population.get(0).copy();        
        if (type == MicroGeneticAlgorithm.Type.STEADY_STATE) {
            return runSteadyState(maxEvaluations, printMode);
        } else {
            return runGenerational(maxEvaluations, printMode);    
        }
    }

    /**
     * Runs the micro genetic algorithm.
     *
     * @param maxEvaluations The maximum number of calls to the evaluation function this genetic algorithm is allowed to
     * execute.
     * @param printMode A flag indicating if some data about the evolutionary process should be printed on screen.
     * @param stopValue The desired objective value to stop the evolutionary process.
     * @return The best individual found by the evolutionary process.
     */
    private Individual runGenerational(long maxEvaluations, boolean printMode) {
        int i, j, k;        
        double[] fitness;
        DecimalFormat format;
        Individual[] parents;
        Individual[] offspring;
        List<Individual> nextPopulation;
        format = new DecimalFormat("0.0000");
        fitness = new double[population.size()];
        for (i = 0; i < population.size(); i++) {
            fitness[i] = population.get(i).getEvaluation();
        }
        if (printMode) {
            //System.out.println("Generation, Iteration, Evaluations, Best.fitness, Average.fitness, StdDev.fitness");
            System.out.println("0, 0, 0, 0, 0 ,0");
            System.out.println("0, 0, " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness))  + ", " + format.format(stdev(fitness)));            
        }
        i = 0;
        while (evaluator.getNbEvaluations() < maxEvaluations) {
            nextPopulation = new ArrayList(population.size());
            nextPopulation.add(population.get(0));
            for (j = 1; j < population.size(); j++) {
                nextPopulation.add((Individual) generator.generate());
            }
            population = nextPopulation;
            for (Individual individual : population) {
                individual.setEvaluation(evaluator.evaluate(individual));               
            }
            if (printMode) {
                System.out.println((i + 1) + ", 0" + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));                
            }
            j = 0;
            while (evaluator.getNbEvaluations() < maxEvaluations) {
                nextPopulation = new ArrayList(population.size());
                k = 0;
                while (nextPopulation.size() < population.size()) {
                    parents = selector.select(population, Objective.MAXIMIZE);
                    offspring = parents[0].combine(parents[1], 1.0);
                    for (Individual individual : offspring) {
                        individual.setEvaluation(evaluator.evaluate(individual));
                        nextPopulation.add(individual);
                        fitness[k++] = individual.getEvaluation();
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
                if (printMode) {
                    System.out.println((i + 1) + ", " + (j + 1) + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
                }                
                if (stdev(fitness) < MIN_FITNESS_DEVIATION) {
                    break;
                }
                j++;
            }
            i++;
        }
        return best;
    }
    
    /**
     * Runs the micro genetic algorithm.
     *
     * @param maxEvaluations The maximum number of calls to the evaluation function this genetic algorithm is allowed to
     * execute.
     * @param printMode A flag indicating if some data about the evolutionary process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    private Individual runSteadyState(long maxEvaluations, boolean printMode) {
        int i, j, k;
        double[] fitness;
        DecimalFormat format;
        Individual[] parents;
        Individual[] offspring;
        List<Individual> nextPopulation;
        format = new DecimalFormat("0.0000");
        fitness = new double[population.size()];
        for (i = 0; i < population.size(); i++) {
            fitness[i] = population.get(i).getEvaluation();
        }
        if (printMode) {            
            System.out.println("0, 0, 0, 0, 0 ,0");
            System.out.println("0, 0, " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness))  + ", " + format.format(stdev(fitness)));            
        }
        i = 0;
        while (evaluator.getNbEvaluations() < maxEvaluations) {
            nextPopulation = new ArrayList(population.size());
            nextPopulation.add(population.get(0));
            for (j = 1; j < population.size(); j++) {
                nextPopulation.add((Individual) generator.generate());
            }
            population = nextPopulation;            
            for (Individual individual : population) {
                individual.setEvaluation(evaluator.evaluate(individual));               
            }
            if (printMode) {
                System.out.println((i + 1) + ", 0" + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
            }
            j = 0;
            while (evaluator.getNbEvaluations() < maxEvaluations) {
                parents = selector.select(population, Objective.MAXIMIZE);
                offspring = parents[0].combine(parents[1], 1.0);                
                offspring[0].setEvaluation(evaluator.evaluate(offspring[0]));                                   
                population.add(offspring[0]);                
                Collections.sort(population);
                population.remove(population.size() - 1);                                
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
                k = 0;
                for (Individual individual : population) {
                    fitness[k++] = individual.getEvaluation();
                }
                if (printMode) {
                    System.out.println((i + 1) + ", " + (j + 1) + ", " + evaluator.getNbEvaluations() + ", " + format.format(best.getEvaluation()) + ", " + format.format(mean(fitness)) + ", " + format.format(stdev(fitness)));
                }                
                if (stdev(fitness) < MIN_FITNESS_DEVIATION) {
                    break;
                }
                j++;
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
