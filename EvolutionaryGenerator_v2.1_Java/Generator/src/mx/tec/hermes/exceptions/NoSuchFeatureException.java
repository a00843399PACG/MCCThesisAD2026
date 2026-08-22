package mx.tec.hermes.exceptions;

/**
 * Defines an exception for handling events where a feature is not defined for the problem.
 *
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public final class NoSuchFeatureException extends Exception {

    /**
     * Creates a new instance of <code>NoSuchFeatureException</code>.
     *
     * @param message The message to describe the exception.
     */
    public NoSuchFeatureException(String message) {
        super(message);
    }

}
