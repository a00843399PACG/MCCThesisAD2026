package mx.tec.hermes.exceptions;

/**
 * Defines an exception for handling events where a heuristic is not defined for the problem.
 * <p>
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public final class NoSuchHeuristicException extends Exception {

    /**
     * Creates a new instance of <code>NoSuchHeuristicException</code>.
     *
     * @param message The message to describe the exception.
     */
    public NoSuchHeuristicException(String message) {
        super(message);
    }

}
