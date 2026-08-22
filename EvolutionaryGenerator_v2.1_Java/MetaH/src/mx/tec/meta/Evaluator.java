package mx.tec.meta;

/**
 * Defines the methods that every evaluator used by the meta heuristics must implement.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public abstract class Evaluator {

    protected long nbEvaluations;
    
    /**
     * Creates a new instance of <code>Evaluator</code>.
     */
    public Evaluator() {
        nbEvaluations = 0;
    }
    
    /**
     * Returns the evaluation of a solution
     *
     * @param solution The solution to be evaluated.
     * @return The evaluation of a solution.
     */
    public abstract double evaluate(Individual solution);

    /**
     * Returns the number of evaluations executed by this evaluator.
     *
     * @return The number of evaluations executed by this evaluator.
     */
    public final long getNbEvaluations() {
        return nbEvaluations;
    }
    
    public final void reset() {
        nbEvaluations = 0;
    }
}
