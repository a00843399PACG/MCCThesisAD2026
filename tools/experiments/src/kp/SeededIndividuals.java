package kp;

import java.util.Arrays;
import java.util.Comparator;
import java.util.Random;

/**
 * Builds individuals that sit exactly on the tie boundary of a labelled type, so a run can start
 * at fitness 0 instead of from a uniform genome. It lives in package kp only to reach the
 * chromosome of KPIndividual; nothing in the generator is changed.
 *
 * DEFAULT_EASY           items stored in MAX_PROFIT/WEIGHT order, so DEFAULT = MAX_PROFIT/WEIGHT
 * MAX_PROFIT_EASY        every weight equal, so MAX_PROFIT = MAX_PROFIT/WEIGHT
 * MIN_WEIGHT_EASY        every profit equal, so MIN_WEIGHT = MAX_PROFIT/WEIGHT
 * MAX_PROFIT_WEIGHT_HARD every weight and every profit equal, so all four heuristics coincide
 */
public final class SeededIndividuals {

    private SeededIndividuals() {
    }

    public static KPIndividual build(KPEvaluator.InstanceType type, KPConfiguration configuration, long seed) {
        KPIndividual individual = new KPIndividual(seed, configuration);
        Random random = new Random(seed ^ 0x5DEECE66DL);
        int n = configuration.nbItems;
        int[] weights = new int[n];
        double[] profits = new double[n];
        individual.decodeInto(weights, profits);
        int midWeight = (configuration.maxWeightPerItem + 1) / 2;
        int midProfit = (configuration.maxProfitPerItem + 1) / 2;
        switch (type) {
            case DEFAULT_EASY: {
                Integer[] order = new Integer[n];
                for (int i = 0; i < n; i++) {
                    order[i] = i;
                }
                final int[] w = weights;
                final double[] p = profits;
                // The same key and the same stable sort as Heuristics.order, so the stored order
                // is exactly the order MAX_PROFIT/WEIGHT follows.
                Arrays.sort(order, (Comparator<Integer>) (a, b) -> Double.compare(p[b] / w[b], p[a] / w[a]));
                int[] sortedW = new int[n];
                double[] sortedP = new double[n];
                for (int i = 0; i < n; i++) {
                    sortedW[i] = w[order[i]];
                    sortedP[i] = p[order[i]];
                }
                weights = sortedW;
                profits = sortedP;
                break;
            }
            case MAX_PROFIT_EASY:
                Arrays.fill(weights, midWeight);
                break;
            case MIN_WEIGHT_EASY:
                Arrays.fill(profits, midProfit);
                break;
            case MAX_PROFIT_WEIGHT_HARD:
                Arrays.fill(weights, midWeight);
                Arrays.fill(profits, midProfit);
                break;
            default:
                throw new IllegalArgumentException("no seeding defined for " + type);
        }
        encode(individual, weights, profits);
        return individual;
    }

    private static void encode(KPIndividual individual, int[] weights, double[] profits) {
        KPConfiguration configuration = individual.configuration;
        for (int i = 0; i < configuration.nbItems; i++) {
            int from = i * configuration.bitsBlock;
            writeField(individual, from, configuration.bitsWeight, weights[i]);
            writeField(individual, from + configuration.bitsWeight, configuration.bitsProfit, (int) profits[i]);
        }
    }

    /** Inverse of KPIndividual.readField: the field stores value - 1, least significant bit first. */
    private static void writeField(KPIndividual individual, int from, int width, int value) {
        int stored = value - 1;
        for (int j = 0; j < width; j++) {
            individual.chromosome.set(from + j, ((stored >> j) & 1) == 1);
        }
    }
}
