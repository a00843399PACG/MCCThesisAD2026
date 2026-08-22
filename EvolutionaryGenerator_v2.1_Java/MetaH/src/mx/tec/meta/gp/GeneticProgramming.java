package mx.tec.meta.gp;

import mx.tec.meta.Evaluator;
import mx.tec.meta.Generator;
import mx.tec.meta.Individual;
import mx.tec.meta.Selector;
import mx.tec.meta.ga.GeneticAlgorithm;
import mx.tec.meta.ga.GeneticAlgorithm.Type;

/**
 *
 * @author jcobayliss
 */
public class GeneticProgramming {
    
    private final GeneticAlgorithm geneticAlgorithm;
     
    /**
     * Creates a new instance of <code>GeneticProgramming</code>.
     *
     * @param evaluator The evaluator of the performance of the individuals in this process.
     * @param generator The generator of the solutions in this genetic algorithm.
     * @param selector The selector to be used by the genetic algorithm.
     * @param objective The objective of the evolutionary process regarding the objective function (maximize or minimize).
     */
    public GeneticProgramming(Evaluator evaluator, Generator generator, Selector selector, GeneticAlgorithm.Objective objective) {
        geneticAlgorithm = new GeneticAlgorithm(evaluator, generator, selector, objective);
    }
    
    /**
     * Runs the evolutionary process and returns the best individual found.
     *
     * @param populationSize The size of the population in the evolutionary process.
     * @param maxEvaluations The maximum number of calls to the evaluation function this evolutionary process is allowed to execute.
     * @param crossoverRate The crossover rate to be used by the evolutionary process.
     * @param mutationRate The mutation rate to be used by the evolutionary process.     
     * @param printMode A flag indicating if some data about the evolutionary process should be printed on screen.
     * @return The best solution found by the evolutionary process.
     */
    public Individual run(int populationSize, long maxEvaluations, double crossoverRate, double mutationRate, boolean printMode) {
        return (GPIndividual) geneticAlgorithm.run(populationSize, maxEvaluations, crossoverRate, mutationRate, Type.GENERATIONAL, printMode);
    }
}
