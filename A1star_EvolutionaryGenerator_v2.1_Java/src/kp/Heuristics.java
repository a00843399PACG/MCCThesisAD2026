package kp;

import java.util.Arrays;
import java.util.Comparator;

public final class Heuristics {

    public static final String DEFAULT = "DEFAULT";
    public static final String MAX_PROFIT = "MAX_PROFIT";
    public static final String MAX_PROFIT_WEIGHT = "MAX_PROFIT/WEIGHT";
    public static final String MIN_WEIGHT = "MIN_WEIGHT";
    public static final String[] ALL = {DEFAULT, MIN_WEIGHT, MAX_PROFIT_WEIGHT, MAX_PROFIT};

    private Heuristics() {
    }

    public static Integer[] order(int[] weights, double[] profits, String heuristic) throws NoSuchHeuristicException {
        int n = weights.length;
        Integer[] index = new Integer[n];
        for (int i = 0; i < n; i++) {
            index[i] = i;
        }
        Comparator<Integer> key;
        switch (heuristic) {
            case DEFAULT:
                return index;
            case MAX_PROFIT:
                key = (a, b) -> Double.compare(profits[b], profits[a]);
                break;
            case MAX_PROFIT_WEIGHT:
                key = (a, b) -> Double.compare(profits[b] / weights[b], profits[a] / weights[a]);
                break;
            case MIN_WEIGHT:
                key = (a, b) -> Integer.compare(weights[a], weights[b]);
                break;
            default:
                throw new NoSuchHeuristicException("Heuristic '" + heuristic + "' is not recognized by the system.");
        }
        Arrays.sort(index, key);
        return index;
    }

    public static double value(int[] weights, double[] profits, int capacity, String heuristic) throws NoSuchHeuristicException {
        Integer[] order = order(weights, profits, heuristic);
        int residual = capacity;
        double total = 0.0;
        for (int i : order) {
            if (weights[i] <= residual) {
                residual -= weights[i];
                total += profits[i];
            }
        }
        return total;
    }
}
