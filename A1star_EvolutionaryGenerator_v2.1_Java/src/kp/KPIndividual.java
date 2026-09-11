package kp;

import java.util.ArrayList;
import java.util.BitSet;
import java.util.List;
import meta.Individual;

public class KPIndividual extends Individual {

    protected final KPConfiguration configuration;
    protected final BitSet chromosome;

    public KPIndividual(long seed, KPConfiguration configuration) {
        super(0, seed);
        this.configuration = configuration;
        chromosome = new BitSet(configuration.nbBits);
        for (int i = 0; i < configuration.nbBits; i++) {
            chromosome.set(i, random.nextBoolean());
        }
    }

    private KPIndividual(KPIndividual individual) {
        super(individual.getEvaluation(), individual.random.nextLong());
        this.configuration = individual.configuration;
        this.chromosome = (BitSet) individual.chromosome.clone();
    }

    public KPConfiguration getConfiguration() {
        return configuration;
    }

    @Override
    public Individual[] combine(Individual individual, double crossoverRate) {
        int crossoverPoint;
        BitSet tmp;
        KPIndividual[] offspring;
        offspring = new KPIndividual[]{this, (KPIndividual) individual};
        if (random.nextDouble() < crossoverRate) {
            crossoverPoint = random.nextInt(configuration.nbBits);
            tmp = (BitSet) offspring[1].chromosome.clone();
            for (int i = 0; i < crossoverPoint; i++) {
                offspring[1].chromosome.set(i, offspring[0].chromosome.get(i));
            }
            for (int i = 0; i < crossoverPoint; i++) {
                offspring[0].chromosome.set(i, tmp.get(i));
            }
        }
        return offspring;
    }

    @Override
    public void mutate(double mutationRate) {
        for (int i = 0; i < configuration.nbBits; i++) {
            if (random.nextDouble() < mutationRate) {
                chromosome.flip(i);
            }
        }
    }

    @Override
    public Individual copy() {
        return new KPIndividual(this);
    }

    public void decodeInto(int[] weights, double[] profits) {
        int from;
        for (int i = 0; i < configuration.nbItems; i++) {
            from = i * configuration.bitsBlock;
            weights[i] = readField(from, configuration.bitsWeight);
            profits[i] = readField(from + configuration.bitsWeight, configuration.bitsProfit);
        }
    }

    public KP toKP() {
        List<Item> items = new ArrayList<>(configuration.nbItems);
        int from;
        for (int i = 0; i < configuration.nbItems; i++) {
            from = i * configuration.bitsBlock;
            int weight = readField(from, configuration.bitsWeight);
            int profit = readField(from + configuration.bitsWeight, configuration.bitsProfit);
            items.add(new Item(i, profit, weight));
        }
        return new KP(items, configuration.capacity);
    }

    private int readField(int from, int width) {
        int value = 0;
        for (int j = 0; j < width; j++) {
            if (chromosome.get(from + j)) {
                value |= 1 << j;
            }
        }
        return value + 1;
    }

    @Override
    public String toString() {
        int from;
        BitSet bits;
        StringBuilder string, tmpString;
        string = new StringBuilder();
        for (int i = 0; i < configuration.nbItems; i++) {
            from = i * configuration.bitsBlock;
            bits = chromosome.get(from, from + configuration.bitsWeight);
            tmpString = new StringBuilder();
            for (int j = 0; j < configuration.bitsWeight; j++) {
                tmpString.append(bits.get(j) ? "1" : "0");
            }
            string.append(tmpString.reverse().toString()).append(" (").append(toInteger(bits)).append(") ");
            from = from + configuration.bitsWeight;
            bits = chromosome.get(from, from + configuration.bitsProfit);
            tmpString = new StringBuilder();
            for (int j = 0; j < configuration.bitsProfit; j++) {
                tmpString.append(bits.get(j + from) ? "1" : "0");
            }
            string.append(tmpString.reverse().toString()).append(" (").append(toInteger(bits)).append(") ");

        }
        return string.toString();
    }

    /**
     * Returns the value as integer of the bits provided as argument.
     *
     * @param bits The bits whose integer value is required.
     * @return The value as integer of the bits provided as argument.
     */
    protected static int toInteger(BitSet bits) {
        int i, value;
        value = 0;
        i = bits.nextSetBit(0);
        while (i >= 0) {
            value += Math.pow(2, i);
            i = bits.nextSetBit(i + 1);
        }
        return value + 1;
    }

}
