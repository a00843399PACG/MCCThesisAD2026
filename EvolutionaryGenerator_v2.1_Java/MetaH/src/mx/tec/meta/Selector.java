package mx.tec.meta;

import mx.tec.meta.Individual;
import java.util.List;
import java.util.Random;
import mx.tec.meta.ga.GeneticAlgorithm.Objective;

/**
 * Defines the methods to create and handle selection operators to be used by a genetic algorithm.
 * 
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public abstract class Selector {
       
    /**
     * The random number generator to be used in all random operations within this selector.
     */
    protected final Random random;
    
    /**
     * Creates a new instance of <code>SelectionOperator</code>.
     * 
     * @param seed The seed for the random number generator to be used by this selector.
     */
    protected Selector(long seed) {        
        random = new Random(seed);
    }   

    /**
     * Selects the solutions to be used for crossover.
     * 
     * @param population The solutions contained in the current population.
     * @param objective The objective of the evolutionary process regarding the objective function (maximize or minimize).
     * @return The solutions to be used for crossover.
     */
    public abstract Individual[] select(List<Individual> population, Objective objective);
}
