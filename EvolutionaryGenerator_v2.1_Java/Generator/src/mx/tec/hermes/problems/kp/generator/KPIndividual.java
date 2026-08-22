package mx.tec.hermes.problems.kp.generator;

import mx.tec.hermes.problems.kp.Item;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.List;
import mx.tec.hermes.problems.kp.KP;
import mx.tec.meta.Individual;

/**
 * Provides the methods to create and use individuals that encode knapsack problems that can be evolved by a genetic
 * algorithm.
 *
 * @author José Carlos Ortiz Bayliss (jcobayliss@tec.mx)
 * @version 2.0
 */
public class KPIndividual extends Individual {

    protected static int maxWeightPerItem = 20, maxProfitPerItem = 50, nbItems = 10, capacity = 20;
    protected static int nbBits = nbItems * (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
    protected final BitSet chromosome;

    /**
     * Sets the capacity of the knapsack in the resulting knapsack problem.
     *
     * @param capacity The capacity of the knapsack in the resulting knapsack problem.
     */
    public static void setCapacity(int capacity) {
        KPIndividual.capacity = capacity;
    }

    /**
     * Sets the maximum weight per item in the resulting knapsack problem.
     *
     * @param maxWeightPerItem The maximum weight per item in the resulting knapsack problem.
     */
    public static void setMaxWeightPerItem(int maxWeightPerItem) {
        KPIndividual.maxWeightPerItem = maxWeightPerItem;
        nbBits = nbItems * (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
    }

    /**
     * Sets the maximum profit per item in the resulting knapsack problem.
     *
     * @param maxProfitPerItem The maximum profit per item in the resulting knapsack problem.
     */
    public static void setMaxProfitPerItem(int maxProfitPerItem) {
        KPIndividual.maxProfitPerItem = maxProfitPerItem;
        nbBits = nbItems * (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
    }

    /**
     * Sets the number of items in the resulting knapsack problem.
     *
     * @param nbItems The number of items in the resulting knapsack problem.
     */
    public static void setNbItems(int nbItems) {
        KPIndividual.nbItems = nbItems;
        nbBits = nbItems * (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
    }

    /**
     * Creates a new instance of <code>KPIndividual</code>.
     * 
     * @param seed The seed to initialize the random number generator.
     */
    public KPIndividual(long seed) {
        super(0, seed);
        chromosome = new BitSet(nbBits);
        for (int i = 0; i < nbBits; i++) {
            chromosome.set(i, random.nextBoolean());
        }
    }

    @Override
    public Individual[] combine(Individual individual, double crossoverRate) {
        int crossoverPoint;
        BitSet tmp;
        KPIndividual[] offspring;
        offspring = new KPIndividual[]{(KPIndividual) this, (KPIndividual) individual};
        crossoverPoint = random.nextInt(nbBits);
        tmp = (BitSet) offspring[1].chromosome.clone();
        for (int i = 0; i < crossoverPoint; i++) {
            offspring[1].chromosome.set(i, offspring[0].chromosome.get(i));
        }
        for (int i = 0; i < crossoverPoint; i++) {
            offspring[0].chromosome.set(i, tmp.get(i));
        }
        return offspring;
    }

    @Override
    public void mutate(double mutationRate) {
        for (int i = 0; i < nbBits; i++) {
            if (random.nextDouble() < mutationRate) {
                chromosome.flip(i);
            }
        }
    }

    @Override
    public Individual copy() {
        return new KPIndividual(this);
    }

    /**
     * Returns a new instance of <code>KP</code> based on the information contained in this individual.
     *
     * @return A new instance of <code>KP</code>.
     */
    public KP toKP() {
        int profit, weight, bitsBlock, bitsWeight, bitsProfit, from;
        BitSet bits;
        List<Item> items;
        items = new ArrayList(nbItems);
        bitsBlock = (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
        bitsWeight = (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)));
        bitsProfit = (int) (Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
        for (int i = 0; i < nbItems; i++) {
            from = i * bitsBlock;
            bits = chromosome.get(from, from + bitsWeight);
            weight = toInteger(bits);
            from = from + bitsWeight;
            bits = chromosome.get(from, from + bitsProfit);
            profit = toInteger(bits);
            // hack, borrar!
            /*
            profit = (int) ((profit + 1) / 128.0 * 100);
            if (profit == 0 || profit > 100) {
                System.out.println("Out of range generation.");
                System.out.println(profit);
                System.exit(1);
            }*/
            items.add(new Item(i, profit, weight));
        }
        return new KP(items, capacity);
    }
    
    @Override
    public String toString() {
        int bitsBlock, bitsWeight, bitsProfit, from;
        BitSet bits;
        StringBuilder string, tmpString;
        string = new StringBuilder();
        bitsBlock = (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)) + Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
        bitsWeight = (int) (Math.ceil(Math.log10(maxWeightPerItem) / Math.log10(2)));
        bitsProfit = (int) (Math.ceil(Math.log10(maxProfitPerItem) / Math.log10(2)));
        for (int i = 0; i < nbItems; i++) {
            from = i * bitsBlock;
            bits = chromosome.get(from, from + bitsWeight);
            tmpString = new StringBuilder();
            for (int j = 0; j < bitsWeight; j++) {
                tmpString.append(bits.get(j) ? "1" : "0");
            }
            string.append(tmpString.reverse().toString()).append(" (").append(toInteger(bits)).append(") ");
            from = from + bitsWeight;
            bits = chromosome.get(from, from + bitsProfit);
            tmpString = new StringBuilder();
            for (int j = 0; j < bitsProfit; j++) {
                tmpString.append(bits.get(j + from) ? "1" : "0");
            }
            string.append(tmpString.reverse().toString()).append(" (").append(toInteger(bits)).append(") ");

        }
        return string.toString();
    }

    /**
     * Creates a new instance of <code>KPIndividual</code>. This is a copy constructor.
     *
     * @param individual The instance of <code>KPIndividual</code> to copy.
     */
    private KPIndividual(KPIndividual individual) {
        super(individual.getEvaluation(), individual.random.nextLong());
        this.chromosome = (BitSet) individual.chromosome.clone();
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
