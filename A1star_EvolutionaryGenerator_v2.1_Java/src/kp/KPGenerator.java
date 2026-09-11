package kp;

import java.util.Random;
import meta.Generator;
import meta.Individual;

public class KPGenerator extends Generator {

    private final Random random;
    private final KPConfiguration configuration;

    public KPGenerator(long seed, KPConfiguration configuration) {
        random = new Random(seed);
        this.configuration = configuration;
    }

    public KPConfiguration getConfiguration() {
        return configuration;
    }

    @Override
    public Individual generate() {
        return new KPIndividual(random.nextLong(), configuration);
    }

}
