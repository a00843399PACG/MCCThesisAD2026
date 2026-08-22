package mx.tec.meta;

/**
 * Defines the methods that need to be implemented by a generator to be used by the meta heuristics.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public abstract class Generator {

    /**
     * Generates a new random instance of <code>Solution</code>.
     *
     * @return A random solution.
     */
    public abstract Individual generate();

}
