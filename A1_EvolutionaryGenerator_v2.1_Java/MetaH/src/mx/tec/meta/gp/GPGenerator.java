package mx.tec.meta.gp;

import java.util.Random;
import mx.tec.meta.Generator;
import mx.tec.meta.Individual;

/**
 * Defines the methods to generate individuals within genetic programing.
 * 
 * @author Jose Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 1.0
 */
public class GPGenerator extends Generator {

    private final static int MAXDEPTH = 3;
    private final Random random;

    /**
     * Creates a new instance of <code>GPGenerator</code>.
     *
     * @param seed The seed to initialize the random number generator.
     */
    public GPGenerator(long seed) {
        random = new Random(seed);
    }
    
    @Override
    public Individual generate() {
        return new GPIndividual(MAXDEPTH, random.nextLong());
    }
    
}
