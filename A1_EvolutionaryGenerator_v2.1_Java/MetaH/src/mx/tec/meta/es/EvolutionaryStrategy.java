package mx.tec.meta.es;

import java.text.DecimalFormat;
import mx.tec.meta.Evaluator;
import mx.tec.meta.Individual;

/**
 * Provides the methods to use the evolutionary strategy 1 + 1 EA.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public final class EvolutionaryStrategy {
            
    private final Evaluator evaluator;        

    /**
     * Creates a new instance of <code>EvolutionaryStrategy</code>.
     * 
     * @param evaluator The evaluator of the performance of the individuals in  this evolutionary strategy.
     */
    public EvolutionaryStrategy(Evaluator evaluator) {
        this.evaluator = evaluator;        
    }

    /**
     * Runs the evolutionary strategy and returns the best individual found.
     * 
     * @param individual The initial individual to start the process.
     * @param maxEvaluations The maximum number of calls to the evaluation function this evolutionary strategy is allowed to execute.
     * @param mutationRate The mutation rate to be used by the mutation operator.
     * @param printMode A flag indicating if some data about the evolutionary process should be
     * printed on screen.     
     * @return The best individual found by the evolutionary process.
     */
    public Individual run(Individual individual, int maxEvaluations, double mutationRate, boolean printMode) {
        int i;
        Individual offspring;
        DecimalFormat format;
        format = new DecimalFormat("0.0000");
        /* 
         * Evaluates the initial individual.
         */
        individual.setEvaluation(evaluator.evaluate(individual));
        /*
         * Executes the evolutionary process.
         */
        i = 0;
        while (evaluator.getNbEvaluations() < maxEvaluations) {
            /*
             * Creates the next population.
             */
            offspring = individual.copy();
            offspring.mutate(mutationRate);
            offspring.setEvaluation(evaluator.evaluate(offspring));            
            /*
             * If the new individual is better than the parent, the parent is replaced by the offspring.
             */            
            if (offspring.getEvaluation() < individual.getEvaluation()) {
                individual = offspring;
            }
            if (printMode) {
                System.out.println((i + 1) + ", " + evaluator.getNbEvaluations() + ", " + format.format(individual.getEvaluation()));
            }            
            i++;
        }
        return individual;
    }
    
}
