package mx.tec.meta;

import java.util.Random;

/**
 * Provides the methods to create and handle individuals to be used by a genetic algorithm.
 * The coding of the solution is left completely to the user on purpose, as it depends on their needs.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 1.0
 */
public abstract class Individual implements Comparable<Individual> {

    protected double evaluation;
    protected final Random random;

    /**
     * Creates a new instance of <code>Individual</code>.
     *
     * @param evaluation The initial evaluation of this individual.
     * @param seed The seed to initialize the random number generator.
     */
    protected Individual(double evaluation, long seed) {
        setEvaluation(evaluation);
        random = new Random(seed);
    }

    /**
     * Sets the evaluation of this individual.
     *
     * @param evaluation The evaluation of this individual.
     */    
    public final void setEvaluation(double evaluation) {
        this.evaluation = evaluation;
    }

    /**
     * Returns the evaluation of this individual.
     *
     * @return The new evaluation of this individual.
     */    
    public final double getEvaluation() {
        return evaluation;
    }

    /**
     * Combines the individuals given as parameters to produce new ones.
     *
     * @param individual The individuals to be combined with this individual.
     * @param crossoverRate The crossover rate to be used by the crossover operator.
     * @return The individuals resulting from the combination of the individuals given as parameters.
     */
    public abstract Individual[] combine(Individual individual, double crossoverRate);

    /**
     * Mutates this individual.
     *
     * @param mutationRate The mutation rate to be used by the mutation operator.
     */
    public abstract void mutate(double mutationRate);

    /**
     * Returns a deep copy of this individual.
     *
     * @return A deep copy of this individual.
     */
    public abstract Individual copy();

    /**
     * Compares two individuals based on their evaluations.
     *
     * @param individual The solution to compare.
     * @return 1 if the evaluation of this solution is larger than the evaluation of the one provided as argument, 0
     * if their evaluations are equal and -1 if the evaluation of this solution is smaller than the evaluation of the
     * solution provided as argument.
     */
    @Override
    public final int compareTo(Individual individual) {
        double evaluationA, evaluationB;
        evaluationA = getEvaluation();
        evaluationB = individual.getEvaluation();
        if (evaluationA < evaluationB) {
            return -1;
        } else if (evaluationA == evaluationB) {
            return 0;
        }
        return 1;
    }

    @Override
    /**
     * Returns the string representation of this individual.
     *
     * @return The string representation of this individual.
     */
    public abstract String toString();
}
