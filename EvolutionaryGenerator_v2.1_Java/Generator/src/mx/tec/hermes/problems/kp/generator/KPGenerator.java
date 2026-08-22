package mx.tec.hermes.problems.kp.generator;

import java.util.Random;
import mx.tec.meta.Generator;
import mx.tec.meta.Individual;

/**
 * Provides the methods to create knapsack problems.
 *
 * @author José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class KPGenerator extends Generator {

    private final Random random;

    /**
     * Creates a new instance of <code>KPGenerator</code>.
     *
     * @param seed The seed to initialize the random number generator.
     */
    public KPGenerator(long seed) {
        random = new Random(seed);
    }

    @Override
    public Individual generate() {
        return new KPIndividual(random.nextLong());
    }

}
